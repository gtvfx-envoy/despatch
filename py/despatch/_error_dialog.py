"""Actionable process and application error dialog."""

from __future__ import annotations

from Qt import QtCore, QtWidgets


class ErrorDialog(QtWidgets.QDialog):
    """Display an error summary with optional diagnostic output.

    Args:
        title: Dialog title.
        message: User-facing error summary.
        output: Optional process or diagnostic output.
        parent: Parent widget.

    """

    def __init__(self, title: str, message: str, output: str = "", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(False)
        self.resize(640, 420)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        title_label = QtWidgets.QLabel(title)
        title_label.setObjectName("productTitle")
        layout.addWidget(title_label)

        message_label = QtWidgets.QLabel(message)
        message_label.setWordWrap(True)
        layout.addWidget(message_label)

        if output:
            output_edit = QtWidgets.QPlainTextEdit()
            output_edit.setReadOnly(True)
            output_edit.setPlainText(output)
            layout.addWidget(output_edit, 1)

        button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Close)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
