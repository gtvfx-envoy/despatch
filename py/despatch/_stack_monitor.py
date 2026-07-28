"""Non-blocking polling for changes to an explicitly selected Stack."""

from __future__ import annotations

import logging
import threading
from collections.abc import Callable
from dataclasses import dataclass

from Qt import QtCore

from . import _constants, _models

_LOG = logging.getLogger("despatch.stack_monitor")


@dataclass(frozen=True, slots=True)
class StackMonitorWarning:
    """Concise health warning plus diagnostic details for a tooltip."""

    message: str
    details: str = ""


class StackMonitor(QtCore.QObject):
    """Poll one explicit Stack without performing filesystem I/O on Qt's thread.

    Args:
        probe: Function returning the current filesystem state for a selection.
        interval_seconds: Normal delay between successful probes.
        confirmation_seconds: Delay used to confirm a changed file is stable.
        slow_seconds: Elapsed time before an in-flight probe is reported as slow.
        parent: Parent Qt object.

    """

    changeDetected = QtCore.Signal(object)
    warningChanged = QtCore.Signal(object)
    _probeFinished = QtCore.Signal(int, int, object, object)

    def __init__(
        self,
        probe: Callable[[_models.StackSelection], _models.StackFileState],
        interval_seconds: float = _constants.DEFAULT_STACK_REFRESH_INTERVAL_SECONDS,
        confirmation_seconds: float = _constants.STACK_CHANGE_CONFIRMATION_SECONDS,
        slow_seconds: float = _constants.STACK_PROBE_SLOW_SECONDS,
        parent=None,
    ):
        super().__init__(parent)
        self._probe = probe
        self._interval_seconds = float(interval_seconds)
        self._confirmation_seconds = float(confirmation_seconds)
        self._slow_seconds = float(slow_seconds)
        self._selection: _models.StackSelection | None = None
        self._baseline: _models.StackFileState | None = None
        self._candidate: _models.StackFileState | None = None
        self._generation = 0
        self._next_token = 0
        self._active_token: int | None = None
        self._enabled = False
        self._reload_pending = False
        self._failure_count = 0
        self._warning: StackMonitorWarning | None = None

        self._timer = QtCore.QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self.checkNow)
        self._slow_timer = QtCore.QTimer(self)
        self._slow_timer.setSingleShot(True)
        self._slow_timer.timeout.connect(self._onProbeSlow)
        self._probeFinished.connect(self._onProbeFinished)

    @property
    def is_enabled(self) -> bool:
        """Whether monitoring is scheduled for an explicit Stack."""
        return self._enabled and self._selection is not None

    @property
    def interval_seconds(self) -> float:
        """Normal interval between successful probes."""
        return self._interval_seconds

    def configure(
        self,
        selection: _models.StackSelection,
        baseline: _models.StackFileState | None,
        interval_seconds: float | None = None,
    ) -> None:
        """Start monitoring a selection from a successfully loaded baseline.

        Args:
            selection: Explicit Stack selection that produced the catalog.
            baseline: File state captured for that catalog, when available.
            interval_seconds: Optional new normal polling interval.

        """
        self._generation += 1
        self._selection = selection
        self._baseline = baseline
        self._candidate = None
        self._enabled = True
        self._reload_pending = False
        self._failure_count = 0
        if interval_seconds is not None:
            self._interval_seconds = float(interval_seconds)
        self._timer.stop()
        self._setWarning(None)
        if self._active_token is None:
            self._schedule(self._interval_seconds)
        else:
            self._startSlowTimer()

    def disable(self) -> None:
        """Disable monitoring and discard all selection-specific state."""
        self._generation += 1
        self._selection = None
        self._baseline = None
        self._candidate = None
        self._enabled = False
        self._reload_pending = False
        self._failure_count = 0
        self._timer.stop()
        self._slow_timer.stop()
        self._setWarning(None)

    def suspend(self) -> None:
        """Pause scheduling while preserving the current selection and baseline."""
        self._generation += 1
        self._enabled = False
        self._candidate = None
        self._reload_pending = False
        self._timer.stop()
        self._slow_timer.stop()

    def resume(self) -> None:
        """Resume a previously suspended explicit Stack monitor."""
        if self._selection is None:
            return
        self._enabled = True
        if self._active_token is None:
            self._schedule(self._interval_seconds)
        else:
            self._startSlowTimer()

    def stop(self) -> None:
        """Stop scheduling; any blocked daemon probe may finish independently."""
        self.disable()

    def setInterval(self, interval_seconds: float) -> None:
        """Apply a new normal polling interval and reschedule future work.

        Args:
            interval_seconds: New polling delay in seconds.

        """
        self._interval_seconds = float(interval_seconds)
        self._failure_count = 0
        if self.is_enabled and self._active_token is None and not self._reload_pending:
            self._schedule(self._interval_seconds)

    def checkNow(self) -> None:
        """Start one probe immediately when no other probe is in flight."""
        if not self.is_enabled or self._reload_pending or self._active_token is not None:
            return
        selection = self._selection
        if selection is None:
            return
        self._timer.stop()
        self._next_token += 1
        token = self._next_token
        generation = self._generation
        self._active_token = token
        self._startSlowTimer()
        worker = threading.Thread(
            target=self._runProbe,
            args=(token, generation, selection),
            name="despatch-stack-probe",
            daemon=True,
        )
        worker.start()

    def resumeAfterReloadFailure(self, details: str) -> None:
        """Retain the old baseline and retry a changed Stack after a load failure.

        Args:
            details: Diagnostic details from the failed catalog load.

        """
        if not self.is_enabled:
            return
        self._reload_pending = False
        self._failure_count = max(
            self._failure_count + 1,
            _constants.STACK_PROBE_FAILURE_WARNING_COUNT,
        )
        self._setWarning(
            StackMonitorWarning(
                "Stack changed but could not be reloaded; using the previous catalog.",
                details,
            )
        )
        self._schedule(self._failureDelay())

    def _runProbe(
        self,
        token: int,
        generation: int,
        selection: _models.StackSelection,
    ) -> None:
        """Run one potentially blocking probe on a daemon thread."""
        state: _models.StackFileState | None = None
        error: BaseException | None = None
        try:
            state = self._probe(selection)
        except (OSError, RuntimeError, TypeError, ValueError) as probe_error:
            error = probe_error
        except Exception as unexpected_error:
            _LOG.exception("Unexpected Stack update probe failure")
            error = unexpected_error
        try:
            self._probeFinished.emit(token, generation, state, error)
        except RuntimeError:
            return

    def _onProbeFinished(
        self,
        token: int,
        generation: int,
        state: _models.StackFileState | None,
        error: BaseException | None,
    ) -> None:
        """Apply a completed worker result on Qt's main thread."""
        if token != self._active_token:
            return
        self._active_token = None
        self._slow_timer.stop()
        if generation != self._generation or not self.is_enabled:
            if self.is_enabled:
                self._schedule(self._interval_seconds)
            return
        if error is not None:
            self._recordFailure(error)
            return
        if state is None:
            self._recordFailure(RuntimeError("Stack probe returned no filesystem state"))
            return

        self._failure_count = 0
        self._setWarning(None)
        if self._baseline is None:
            self._baseline = state
            self._candidate = None
            self._schedule(self._interval_seconds)
            return
        if state == self._baseline:
            self._candidate = None
            self._schedule(self._interval_seconds)
            return
        if state != self._candidate:
            self._candidate = state
            self._schedule(self._confirmation_seconds)
            return

        self._reload_pending = True
        self.changeDetected.emit(state)

    def _recordFailure(self, error: BaseException) -> None:
        """Record a failed probe, warn when appropriate, and schedule a retry."""
        self._failure_count += 1
        _LOG.warning("Stack update probe failed: %s", error)
        if self._failure_count >= _constants.STACK_PROBE_FAILURE_WARNING_COUNT:
            self._setWarning(
                StackMonitorWarning(
                    "Can’t check Stack updates; using the last loaded catalog.",
                    str(error) or error.__class__.__name__,
                )
            )
        self._schedule(self._failureDelay())

    def _failureDelay(self) -> float:
        """Return exponential retry delay capped at five minutes."""
        exponent = min(10, max(0, self._failure_count - 1))
        delay = self._interval_seconds * (2**exponent)
        capped_delay = min(delay, _constants.STACK_PROBE_MAX_BACKOFF_SECONDS)
        return max(self._interval_seconds, capped_delay)

    def _onProbeSlow(self) -> None:
        """Report a probe that has not returned before the health deadline."""
        if self._active_token is None or not self.is_enabled:
            return
        selection = self._selection
        details = str(selection.path) if selection is not None else ""
        self._setWarning(
            StackMonitorWarning(
                "Stack update check is taking longer than expected.",
                details,
            )
        )

    def _startSlowTimer(self) -> None:
        """Start the health deadline for the active probe."""
        if not self.is_enabled or self._active_token is None:
            return
        self._slow_timer.start(max(1, round(self._slow_seconds * 1000)))

    def _schedule(self, delay_seconds: float) -> None:
        """Schedule the next probe without accumulating missed intervals."""
        if not self.is_enabled or self._reload_pending:
            self._timer.stop()
            return
        self._timer.start(max(1, round(delay_seconds * 1000)))

    def _setWarning(self, warning: StackMonitorWarning | None) -> None:
        """Emit only meaningful Stack-health transitions."""
        if warning == self._warning:
            return
        self._warning = warning
        self.warningChanged.emit(warning)
