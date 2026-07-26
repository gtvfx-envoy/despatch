"""Process launch and monitoring for envoy_despatch."""

import os
import subprocess
import sys


class Process:
    """Manages a launched application process.

    Tracks process state (running, exited, error) and provides methods to
    start, monitor, terminate, and capture output from the process.

    Args:
        command: Command or script to execute.
        args: Additional arguments for the command.
        label: Human-readable label for this process (e.g., application name).
        working_dir: Working directory for the process. Defaults to current dir.
        in_terminal: If True, launch in a new terminal window.

    """

    def __init__(
        self,
        command: str,
        args: list | None = None,
        label: str = "",
        working_dir: str | None = None,
        in_terminal: bool = False,
    ):
        self._command = command
        self._args = args or []
        self._label = label or command
        self._working_dir = working_dir or os.getcwd()
        self._in_terminal = in_terminal
        self._process: subprocess.Popen | None = None
        self._exit_code: int | None = None
        self._running = False
        self._stdout: str = ""
        self._stderr: str = ""

    @property
    def label(self) -> str:
        """Human-readable label for this process."""
        return self._label

    @property
    def is_running(self) -> bool:
        """Whether the process is currently active."""
        if self._process is None:
            return False
        return self._process.poll() is None

    @property
    def exit_code(self) -> int | None:
        """Exit code of the process, or None if still running."""
        if self._process is not None and self._exit_code is None:
            self._exit_code = self._process.poll()
        return self._exit_code

    @property
    def command_line(self) -> str:
        """Full command line string for this process."""
        parts = [self._command] + list(self._args)
        return " ".join(parts)

    @property
    def captured_output(self) -> str:
        """Get all captured stdout and stderr output.

        Returns:
            Combined stdout and stderr as a single string.

        """
        if self._process and not self._running:
            try:
                if self._process.stdout:
                    self._stdout = self._process.stdout.read().decode(
                        "utf-8", errors="replace"
                    )
                if self._process.stderr:
                    self._stderr = self._process.stderr.read().decode(
                        "utf-8", errors="replace"
                    )
            except (AttributeError, UnicodeDecodeError):
                pass
        return f"{self._stdout}\n{self._stderr}"

    @property
    def has_errors(self) -> bool:
        """Check if the process exited with an error.

        Returns:
            True if exit code is non-zero or stderr has content.

        """
        if self.exit_code is not None and self.exit_code != 0:
            return True
        return bool(self._stderr.strip())

    def start(self) -> bool:
        """Start the process.

        Returns:
            True if the process was started successfully, False otherwise.

        """
        if self.is_running:
            return False

        try:
            # Determine if we should use shell execution
            use_shell = self._in_terminal or os.name == "nt"

            # Set creation flags for Windows terminal launch
            creationflags = 0
            if self._in_terminal and os.name == "nt":
                creationflags = subprocess.CREATE_NEW_CONSOLE  # type: ignore[attr-defined]

            # Prepare command as list for non-shell execution
            cmd_list = [self._command] + list(self._args) if not use_shell else None

            self._process = subprocess.Popen(
                cmd_list if cmd_list else self.command_line,
                shell=use_shell,
                cwd=self._working_dir,
                stdout=subprocess.PIPE if not self._in_terminal else None,
                stderr=subprocess.STDOUT if not self._in_terminal else None,
                creationflags=creationflags,
            )
            self._running = True
            return True
        except (OSError, subprocess.SubprocessError):
            return False

    def terminate(self) -> bool:
        """Terminate the running process.

        Returns:
            True if termination was requested successfully.

        """
        if not self.is_running or self._process is None:
            return False
        try:
            self._process.terminate()
            return True
        except OSError:
            return False

    def kill(self) -> bool:
        """Forcefully kill the process.

        Returns:
            True if kill was successful.

        """
        if not self.is_running or self._process is None:
            return False
        try:
            self._process.kill()
            return True
        except OSError:
            return False

    def wait(self, timeout: float | None = None) -> int | None:
        """Wait for the process to exit.

        Args:
            timeout: Maximum seconds to wait. None means wait indefinitely.

        Returns:
            Exit code, or None if timeout reached.

        """
        if self._process is None:
            return None
        try:
            self._process.wait(timeout=timeout)
            self._exit_code = self._process.returncode
            self._running = False
            return self._exit_code
        except subprocess.TimeoutExpired:
            return None

    def __repr__(self) -> str:
        status = "running" if self.is_running else f"exited({self.exit_code})"
        return f"{self.__class__.__name__}(label={self._label!r}, {status})"


def launchInTerminal(command: str, args: list | None = None) -> bool:
    """Launch a command in a new terminal window.

    Cross-platform helper for opening applications in dedicated terminal windows.

    Args:
        command: Command to execute.
        args: Additional arguments.

    Returns:
        True if launched successfully, False otherwise.

    """
    cmd_list = [command] + (args or [])

    if sys.platform == "win32":
        # Windows: Use cmd.exe /c to launch in new console
        full_cmd = "cmd.exe /c {}".format(" ".join(cmd_list))
        try:
            subprocess.Popen(
                full_cmd,
                shell=True,
                creationflags=subprocess.CREATE_NEW_CONSOLE,  # type: ignore[attr-defined]
            )
            return True
        except OSError:
            return False

    elif sys.platform == "darwin":
        # macOS: Use open -a Terminal.app or osascript
        full_cmd = " ".join(cmd_list)
        try:
            subprocess.Popen(
                ["open", "-a", "Terminal", "--args", full_cmd],
            )
            return True
        except OSError:
            return False

    else:
        # Linux: Try common terminal emulators
        terminals = ["xterm", "gnome-terminal", "konsole", "xfce4-terminal"]
        for term in terminals:
            try:
                subprocess.Popen([term, "--"] + cmd_list)
                return True
            except FileNotFoundError:
                continue
        return False
