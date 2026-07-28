import threading
import time
from pathlib import Path

from despatch import _models, _stack_monitor


def makeSelection(name="studio"):
    return _models.StackSelection(name, name, Path(f"{name}.estack"))


def makeFileState(marker, name="studio"):
    return _models.StackFileState(Path(f"{name}.estack"), marker, marker, marker)


def waitFor(qapp, predicate, timeout=1.0):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        qapp.processEvents()
        if predicate():
            return
        time.sleep(0.005)
    assert predicate()


def testStableChangeRequiresConfirmationBeforeNotification(qapp):
    baseline = makeFileState(1)
    changed = makeFileState(2)
    calls = []
    changes = []
    monitor = _stack_monitor.StackMonitor(
        lambda selection: calls.append(selection) or changed,
        interval_seconds=60,
        confirmation_seconds=0.01,
        slow_seconds=1,
    )
    monitor.changeDetected.connect(changes.append)
    monitor.configure(makeSelection(), baseline)
    monitor._timer.stop()

    monitor.checkNow()

    waitFor(qapp, lambda: bool(changes))
    assert changes == [changed]
    assert len(calls) == 2
    monitor.stop()


def testUnchangedStackSchedulesWithoutNotification(qapp):
    baseline = makeFileState(1)
    calls = []
    changes = []
    monitor = _stack_monitor.StackMonitor(
        lambda selection: calls.append(selection) or baseline,
        interval_seconds=60,
        slow_seconds=1,
    )
    monitor.changeDetected.connect(changes.append)
    monitor.configure(makeSelection(), baseline)
    monitor._timer.stop()

    monitor.checkNow()

    waitFor(qapp, lambda: monitor._active_token is None)
    assert len(calls) == 1
    assert changes == []
    monitor.stop()


def testTwoProbeFailuresWarnAndSuccessClearsWarning(qapp):
    baseline = makeFileState(1)
    attempts = []
    warnings = []

    def probeStack(selection):
        attempts.append(selection)
        if len(attempts) <= 2:
            raise OSError("network unavailable")
        return baseline

    monitor = _stack_monitor.StackMonitor(
        probeStack,
        interval_seconds=0.01,
        slow_seconds=1,
    )
    monitor.warningChanged.connect(warnings.append)
    monitor.configure(makeSelection(), baseline)

    waitFor(qapp, lambda: len(attempts) >= 3 and warnings and warnings[-1] is None)
    visible_warnings = [warning for warning in warnings if warning is not None]
    assert len(visible_warnings) == 1
    assert "last loaded catalog" in visible_warnings[0].message
    monitor.stop()


def testSlowProbeWarnsAndCannotOverlap(qapp):
    release_probe = threading.Event()
    calls = []
    warnings = []
    baseline = makeFileState(1)

    def probeStack(selection):
        calls.append(selection)
        release_probe.wait(1)
        return baseline

    monitor = _stack_monitor.StackMonitor(
        probeStack,
        interval_seconds=60,
        slow_seconds=0.02,
    )
    monitor.warningChanged.connect(warnings.append)
    monitor.configure(makeSelection(), baseline)
    monitor._timer.stop()

    monitor.checkNow()
    waitFor(qapp, lambda: any(warning is not None for warning in warnings))
    monitor.checkNow()

    assert len(calls) == 1
    release_probe.set()
    waitFor(qapp, lambda: monitor._active_token is None)
    assert warnings[-1] is None
    monitor.stop()


def testResultFromPreviousSelectionIsIgnored(qapp):
    release_probe = threading.Event()
    changes = []
    old_changed = makeFileState(2, "old")
    new_baseline = makeFileState(1, "new")

    def probeStack(selection):
        release_probe.wait(1)
        return old_changed

    monitor = _stack_monitor.StackMonitor(probeStack, interval_seconds=60, slow_seconds=1)
    monitor.changeDetected.connect(changes.append)
    monitor.configure(makeSelection("old"), makeFileState(1, "old"))
    monitor._timer.stop()
    monitor.checkNow()

    monitor.configure(makeSelection("new"), new_baseline)
    release_probe.set()

    waitFor(qapp, lambda: monitor._active_token is None)
    monitor._timer.stop()
    assert changes == []
    monitor.stop()


def testAutomaticModeCanDisablePendingMonitoring(qapp):
    calls = []
    monitor = _stack_monitor.StackMonitor(
        lambda selection: calls.append(selection) or makeFileState(1),
        interval_seconds=0.01,
    )
    monitor.configure(makeSelection(), makeFileState(1))

    monitor.disable()
    monitor.checkNow()
    deadline = time.monotonic() + 0.05
    while time.monotonic() < deadline:
        qapp.processEvents()
        time.sleep(0.005)

    assert calls == []
    assert not monitor.is_enabled


def testFailureBackoffCapsAtFiveMinutesWithoutShorteningLongIntervals(qapp):
    monitor = _stack_monitor.StackMonitor(lambda selection: makeFileState(1), 60)

    monitor._failure_count = 1
    assert monitor._failureDelay() == 60
    monitor._failure_count = 2
    assert monitor._failureDelay() == 120
    monitor._failure_count = 3
    assert monitor._failureDelay() == 240
    monitor._failure_count = 4
    assert monitor._failureDelay() == 300

    monitor.setInterval(600)
    assert monitor._failureDelay() == 600


def testReloadFailureKeepsOldBaselineAndSchedulesRetry(qapp):
    baseline = makeFileState(1)
    changed = makeFileState(2)
    changes = []
    warnings = []
    monitor = _stack_monitor.StackMonitor(
        lambda selection: changed,
        interval_seconds=60,
        confirmation_seconds=0.01,
    )
    monitor.changeDetected.connect(changes.append)
    monitor.warningChanged.connect(warnings.append)
    monitor.configure(makeSelection(), baseline)
    monitor._timer.stop()
    monitor.checkNow()
    waitFor(qapp, lambda: bool(changes))

    monitor.resumeAfterReloadFailure("invalid YAML")

    assert monitor._baseline == baseline
    assert monitor._candidate == changed
    assert monitor._timer.isActive()
    assert warnings[-1].details == "invalid YAML"
    monitor.stop()
