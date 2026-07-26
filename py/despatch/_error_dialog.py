"""Error output dialog for envoy_despatch application launch failures."""


from . import _qt

QtWidgets = _qt.QtWidgets
QtCore = _qt.QtCore
QtGui = _qt.QtGui


class ErrorDialog(QtWidgets.QDialog):
    """Dialog showing captured stdout/stderr from a failed application launch.

    Displays the output in a monospace text area with scroll-to-bottom button,
    allowing users to review error messages before dismissing.

    Args:
        title: Window title.
        message: Error message to display.
        output: Captured console output (stdout/stderr).
        parent: Parent QWidget. Defaults to None.

    """

    def __init__(self, title: str, message: str, output: str = "", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(800, 480)
        self._setup_ui(message, output)

    def _setupUi(self, message: str, output: str) -> None:
        """Initialize the dialog UI."""
        layout = QtWidgets.QVBoxLayout(self)

        # Output text area (monospace, read-only)
        self._output_edit = QtWidgets.QPlainTextEdit(output)
        self._output_edit.setLineWrapMode(QtWidgets.QPlainTextEdit.NoWrap)
        self._output_edit.setReadOnly(True)
        
        font = QtGui.QFont("Consolas")
        font.setStyleHint(QtGui.QFont.TypeWriter)
        self._output_edit.setFont(font)
        
        layout.addWidget(self._output_edit, 1)

        # Message label
        message_label = QtWidgets.QLabel(message)
        message_label.setWordWrap(True)
        layout.addWidget(message_label)

        # Buttons
        btn_layout = QtWidgets.QHBoxLayout()
        
        scroll_btn = QtWidgets.QPushButton("Scroll to Bottom")
        scroll_btn.clicked.connect(self._scrollToBottom)
        btn_layout.addWidget(scroll_btn)
        
        btn_layout.addStretch()
        
        ok_btn = QtWidgets.QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        btn_layout.addWidget(ok_btn)
        
        layout.addLayout(btn_layout)

    def _scrollToBottom(self) -> None:
        """Scroll the output text area to the bottom."""
        scrollbar = self._output_edit.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
