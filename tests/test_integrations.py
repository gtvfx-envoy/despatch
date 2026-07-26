import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from Qt import QtCore, QtGui

from despatch import _icons, _platform, _single_instance


def testProductIconUsesRepositoryResources(qapp):
    icon_path = _icons._findResourceIcon("despatch.svg")

    assert icon_path == Path(__file__).parents[1] / "resources" / "icons" / "despatch.svg"
    assert not _icons.loadProductIcon().isNull()


def testEmbeddedSvgImageProducesSquareIcon(qapp, tmp_path):
    image = QtGui.QImage(30, 10, QtGui.QImage.Format_ARGB32)
    image.fill(QtGui.QColor(0, 0, 0, 0))
    painter = QtGui.QPainter(image)
    painter.fillRect(0, 0, 10, 10, QtGui.QColor("magenta"))
    painter.fillRect(20, 0, 10, 10, QtGui.QColor("black"))
    painter.end()
    buffer = QtCore.QBuffer()
    buffer.open(QtCore.QIODevice.WriteOnly)
    image.save(buffer, "PNG")
    encoded_image = bytes(buffer.data().toBase64()).decode("ascii")
    icon_path = tmp_path / "wordmark.svg"
    icon_path.write_text(
        (
            '<svg xmlns="http://www.w3.org/2000/svg" '
            'xmlns:xlink="http://www.w3.org/1999/xlink">'
            f'<image id="embedded" xlink:href="data:image/png;base64,{encoded_image}"/>'
            '<use xlink:href="#embedded"/>'
            "</svg>"
        ),
        encoding="utf-8",
    )

    icon = _icons.loadPathIcon(icon_path)
    available_sizes = icon.availableSizes()

    assert not icon.isNull()
    assert available_sizes
    assert available_sizes[0].width() == available_sizes[0].height()


def testGlobalShortcutOwnsQtSignal(qapp):
    shortcut = _platform.WindowsGlobalShortcut(qapp)
    received = []

    shortcut.activated.connect(lambda: received.append(True))
    shortcut.activated.emit()

    assert received == [True]
    assert shortcut._parseShortcut("Ctrl+Alt+Space") == (0x0003, 0x20)


def testSingleInstanceNotifiesPrimary(qapp):
    server_name = f"despatch.test.{uuid.uuid4().hex}"
    primary = _single_instance.SingleInstance(server_name=server_name)
    received = []
    event_loop = QtCore.QEventLoop()

    def recordActivation():
        received.append(True)
        event_loop.quit()

    primary.activationRequested.connect(recordActivation)

    def notifyPrimary():
        secondary = _single_instance.SingleInstance(server_name=server_name)
        try:
            return secondary.acquireOrNotify()
        finally:
            secondary.close()

    try:
        assert primary.acquireOrNotify() is True
        with ThreadPoolExecutor(max_workers=1) as executor:
            notification = executor.submit(notifyPrimary)
            QtCore.QTimer.singleShot(1000, event_loop.quit)
            event_loop.exec()
            assert notification.result(timeout=1) is False
        assert received == [True], (
            f"pending={primary._server.hasPendingConnections()} "
            f"error={primary._server.errorString()}"
        )
    finally:
        primary.close()
