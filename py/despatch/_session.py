"""Central session orchestrator for envoy_despatch."""

import datetime
from typing import Optional

from . import _app_store
from . import _config
from . import _process
from . import _stack


class Session:
    """Manages the active envoy session state.

    Coordinates between the application store, user configuration, stack
    state, and running processes. Acts as the central hub for launch operations
    and UI updates.

    Args:
        config: User configuration instance. Defaults to platform default path.

    """

    _instance: Optional["Session"] = None

    def __init__(self, config: _config.Config | None = None):
        self._config = config or _config.Config()
        self._app_store = _app_store.ApplicationStore()
        self._stack_type: _stack.StackType = _stack.getStackType(
            self._config.active_stack
        )
        self._active_processes: dict[str, _process.Process] = {}
        self._main_window = None
        self._tray_icon = None  # Will be set by __main__.py after creation

    @classmethod
    def getInstance(cls) -> Optional["Session"]:
        """Return the global session singleton.

        Returns:
            The Session instance, or None if not initialized.

        """
        return cls._instance

    @classmethod
    def setInstance(cls, session: "Session") -> None:
        """Store the global session singleton.

        Args:
            session: Session instance to store.

        """
        cls._instance = session

    @property
    def config(self) -> _config.Config:
        """User configuration."""
        return self._config

    @property
    def tray_icon(self):
        """The DespatchTrayIcon instance, if set."""
        return self._tray_icon

    @tray_icon.setter
    def tray_icon(self, icon) -> None:
        """Set the tray icon reference.

        Args:
            icon: DespatchTrayIcon instance.

        """
        self._tray_icon = icon

    @property
    def app_store(self) -> _app_store.ApplicationStore:
        """Current application store."""
        return self._app_store

    @property
    def stack_type(self) -> _stack.StackType:
        """Current stack type/state."""
        return self._stack_type

    @property
    def active_stack_name(self) -> str | None:
        """Name of the currently active stack."""
        return self._config.active_stack

    @property
    def all_stacks(self) -> list[_stack.StackType]:
        """List all available stacks.

        Returns:
            List of StackType instances.

        """
        # In a full implementation, this would query the envoy backend
        return self._app_store.stacks

    @property
    def is_caching_active(self) -> bool:
        """Check if caching is currently active.

        Returns:
            True if caching is in progress.

        """
        return False  # Placeholder - would track cache manager state

    @property
    def time_machine_expiration(self) -> datetime.datetime | None:
        """Get the Time Machine expiration datetime.

        Returns:
            Datetime when Time Machine mode expires, or None.

        """
        if self._config.time_machine_expiration:
            return datetime.datetime.fromisoformat(
                self._config.time_machine_expiration
            )
        return None

    def popupMainWindow(self) -> None:
        """Show the main application window."""
        if self._main_window is not None:
            self._main_window.show()
            self._main_window.raise_()
            self._main_window.activateWindow()
        else:
            from . import _main_window
            self._main_window = _main_window.MainWindow(self)
            self._main_window.show()

    def launch(
        self,
        command: str,
        args: list | None = None,
        label: str = "",
        in_terminal: bool = False,
    ) -> _process.Process | None:
        """Launch an application.

        Args:
            command: Command or script to execute.
            args: Additional arguments.
            label: Human-readable label for the process.
            in_terminal: If True, launch in a new terminal window.

        Returns:
            Process instance if launched successfully, None otherwise.

        """
        proc = _process.Process(
            command=command,
            args=args or [],
            label=label,
            in_terminal=in_terminal,
        )
        if proc.start():
            self._active_processes[label] = proc
            # Mark as used in config
            return proc
        return None

    def refresh(self) -> None:
        """Refresh the application store and stack state."""
        # In a full implementation, this would re-discover stacks and apps
        # from the envoy backend. For now, it's a no-op placeholder.

    def restart(self) -> None:
        """Restart the session (refresh + reload)."""
        self.refresh()

    def setStack(
        self, name: str, explicit: bool = True
    ) -> None:
        """Switch to a different stack.

        Args:
            name: Stack name to activate.
            explicit: If True, user explicitly chose this stack (not auto).

        """
        self._config.active_stack = name
        self._stack_type = _stack.getStackType(name)
        
        # Check if we're entering Time Machine mode
        if explicit and self._config.time_machine_expiration:
            expiration_dt = datetime.datetime.fromisoformat(
                self._config.time_machine_expiration
            )
            if expiration_dt > datetime.datetime.now(datetime.UTC) and self._tray_icon:
                self._tray_icon.setIconState("checkpoint")

    def quit(self) -> None:
        """Terminate all active processes and exit."""
        for proc in list(self._active_processes.values()):
            if proc.is_running:
                proc.terminate()
        self._active_processes.clear()

    def groupedStacks(self) -> list[tuple]:
        """Get stacks grouped by their group attribute.

        Returns:
            List of (group_name, [stacks]) tuples.

        """
        groups: dict[str, list[_stack.StackType]] = {}
        for stack in self.all_stacks:
            group = stack.group or "Uncategorized"
            if group not in groups:
                groups[group] = []
            groups[group].append(stack)
        
        return sorted(groups.items(), key=lambda x: x[0])

    def __repr__(self) -> str:
        return f"Session(stack={self.active_stack_name!r})"


def getSession() -> Session | None:
    """Return the global session instance.

    Returns:
        The Session singleton, or None if not initialized.

    """
    return Session.getInstance()
