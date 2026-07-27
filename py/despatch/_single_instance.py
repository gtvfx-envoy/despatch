"""Single-instance coordination using Qt local IPC."""

from __future__ import annotations

import getpass
import hashlib

from Qt import QtCore, QtNetwork

from . import _constants


class SingleInstance(QtCore.QObject):
    """Own a per-user local server or notify the existing instance."""

    activationRequested = QtCore.Signal()

    def __init__(self, parent=None, server_name: str | None = None):
        super().__init__(parent)
        user_hash = hashlib.sha256(getpass.getuser().encode("utf-8")).hexdigest()[:12]
        default_server_name = f"{_constants.IPC_SERVER_PREFIX}.{user_hash}"
        self._server_name = server_name or default_server_name
        self._server = QtNetwork.QLocalServer(self)
        self._server.newConnection.connect(self._onNewConnection)
        self._connections: list[QtNetwork.QLocalSocket] = []
        self._is_primary = False

    @property
    def is_primary(self) -> bool:
        """Whether this object owns the local server."""
        return self._is_primary

    def acquireOrNotify(self) -> bool:
        """Become the primary instance or ask it to show its window.

        Returns:
            True for the primary instance, False for a notifying secondary.

        """
        socket = QtNetwork.QLocalSocket(self)
        socket.connectToServer(self._server_name, QtCore.QIODevice.ReadWrite)  # type: ignore
        if socket.waitForConnected(250):
            socket.write(b"show\n")
            socket.flush()
            socket.waitForBytesWritten(250)
            socket.waitForReadyRead(500)
            socket.readAll()
            socket.disconnectFromServer()
            return False
        QtNetwork.QLocalServer.removeServer(self._server_name)
        if not self._server.listen(self._server_name):
            return False
        self._is_primary = True
        return True

    def close(self) -> None:
        """Close and remove the local server."""
        if self._is_primary:
            self._server.close()
            QtNetwork.QLocalServer.removeServer(self._server_name)
            self._is_primary = False

    def _onNewConnection(self) -> None:
        """Attach asynchronous readers to all pending sockets."""
        while self._server.hasPendingConnections():
            socket = self._server.nextPendingConnection()
            if socket is None:
                continue
            socket.setParent(self)
            self._connections.append(socket)
            socket.readyRead.connect(
                lambda socket_reference=socket: self._readSocket(socket_reference)
            )
            socket.disconnected.connect(
                lambda socket_reference=socket: self._onSocketDisconnected(socket_reference)
            )
            if socket.bytesAvailable():
                self._readSocket(socket)

    def _readSocket(self, socket: QtNetwork.QLocalSocket) -> None:
        """Accumulate and handle newline-delimited IPC messages."""
        previous_data = socket.property("despatchBuffer") or b""
        buffered_data = bytes(previous_data) + bytes(socket.readAll())  # type: ignore
        socket.setProperty("despatchBuffer", buffered_data)
        if b"\n" not in buffered_data:
            return
        for message in buffered_data.splitlines():
            if message == b"show":
                self.activationRequested.emit()
        socket.setProperty("despatchBuffer", b"")
        socket.write(b"ack\n")
        socket.flush()
        socket.disconnectFromServer()

    def _onSocketDisconnected(self, socket: QtNetwork.QLocalSocket) -> None:
        """Drain and release a disconnected client socket."""
        try:
            if socket.bytesAvailable():
                self._readSocket(socket)
        except RuntimeError:
            pass
        if socket in self._connections:
            self._connections.remove(socket)
        try:
            socket.readyRead.disconnect()
            socket.disconnected.disconnect()
            socket.deleteLater()
        except (RuntimeError, TypeError):
            pass
