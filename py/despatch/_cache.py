"""Package caching manager for envoy_despatch."""

from collections.abc import Callable


class CacheTask:
    """Represents a single package cache operation.

    Args:
        name: Human-readable task name (e.g., package ID).
        status: Current task status string (pending, running, completed, failed).
        progress: Progress value from 0.0 to 1.0.

    """

    def __init__(self, name: str):
        self._name = name
        self._status = "pending"
        self._progress: float = 0.0
        self._error: str | None = None

    @property
    def name(self) -> str:
        """Task display name."""
        return self._name

    @property
    def status(self) -> str:
        """Current task status."""
        return self._status

    @status.setter
    def status(self, value: str) -> None:
        self._status = value

    @property
    def progress(self) -> float:
        """Task progress from 0.0 to 1.0."""
        return self._progress

    @progress.setter
    def progress(self, value: float) -> None:
        self._progress = max(0.0, min(1.0, value))

    @property
    def error(self) -> str | None:
        """Error message if the task failed."""
        return self._error

    @error.setter
    def error(self, value: str) -> None:
        self._error = value
        self._status = "failed"

    def isComplete(self) -> bool:
        """Whether the task has finished (success or failure)."""
        return self._status in ("completed", "failed")

    def __repr__(self) -> str:
        return f"CacheTask(name={self._name!r}, status={self._status!r})"


class CacheManager:
    """Manages package caching operations.

    Tracks pending and running cache tasks, provides progress updates, and
    coordinates background download/caching work.

    Args:
        on_progress: Optional callback invoked with (task_name, progress).
        on_complete: Optional callback invoked when all tasks finish.

    """

    def __init__(
        self,
        on_progress: Callable[[str, float], None] | None = None,
        on_complete: Callable[[], None] | None = None,
    ):
        self._tasks: dict = {}
        self._on_progress = on_progress
        self._on_complete = on_complete

    @property
    def tasks(self) -> dict:
        """Dictionary of active cache tasks."""
        return dict(self._tasks)

    @property
    def is_active(self) -> bool:
        """Whether any cache operations are currently running."""
        return any(t.status == "running" for t in self._tasks.values())

    def add_task(self, name: str) -> CacheTask:
        """Register a new cache task.

        Args:
            name: Task identifier/name.

        Returns:
            The created CacheTask instance.

        """
        task = CacheTask(name)
        self._tasks[name] = task
        return task

    def remove_task(self, name: str) -> None:
        """Remove a completed or cancelled task.

        Args:
            name: Task identifier to remove.

        """
        self._tasks.pop(name, None)

    def update_progress(self, name: str, progress: float) -> None:
        """Update progress for a running task.

        Args:
            name: Task identifier.
            progress: New progress value (0.0 to 1.0).

        """
        task = self._tasks.get(name)
        if task and task.status == "running":
            task.progress = progress
            if self._on_progress:
                self._on_progress(name, progress)

    def complete_task(self, name: str) -> None:
        """Mark a task as completed.

        Args:
            name: Task identifier.

        """
        task = self._tasks.get(name)
        if task and not task.isComplete():
            task.status = "completed"
            task.progress = 1.0
            if self._on_progress:
                self._on_progress(name, 1.0)

    def fail_task(self, name: str, error: str) -> None:
        """Mark a task as failed with an error message.

        Args:
            name: Task identifier.
            error: Error description.

        """
        task = self._tasks.get(name)
        if task and not task.isComplete():
            task.error = error

    def check_completion(self) -> bool:
        """Check if all tasks have finished.

        Returns:
            True if all registered tasks are complete (success or failure).

        """
        if not self._tasks:
            return True
        if all(t.isComplete() for t in self._tasks.values()):
            if self._on_complete:
                self._on_complete()
            return True
        return False

    def clear(self) -> None:
        """Remove all tasks."""
        self._tasks.clear()
