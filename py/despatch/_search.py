"""Search panel UI for envoy_despatch."""

import re

from . import _app_store, _qt

QtWidgets = _qt.QtWidgets
QtCore = _qt.QtCore
QtGui = _qt.QtGui


class SearchPanel(QtWidgets.QWidget):
    """Main search and launch panel.

    Provides a stack selector combobox, a fuzzy search input, and a results
    list with keyboard navigation. Double-clicking an entry launches the
    associated application.

    Args:
        parent: Parent widget. Defaults to None for top-level window.

    """

    launch_requested = QtCore.Signal(str, list)  # command, args

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("envoy_despatch — Search")
        self.setMinimumSize(500, 400)

        self._app_store: _app_store.ApplicationStore | None = None
        self._setupUi()
        self._connectSignals()

    def _setupUi(self) -> None:
        """Build the search panel widget hierarchy."""
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        # stack selector
        stack_layout = QtWidgets.QHBoxLayout()
        self._stack_combo = QtWidgets.QComboBox()
        self._stack_combo.setMinimumHeight(30)
        stack_layout.addWidget(self._stack_combo, stretch=1)
        layout.addLayout(stack_layout)

        # Search input
        self._search_input = QtWidgets.QLineEdit()
        self._search_input.setPlaceholderText("Search applications...")
        self._search_input.setMinimumHeight(36)
        self._search_input.textChanged.connect(self._onSearchChanged)
        layout.addWidget(self._search_input)

        # Results list
        self._results_list = QtWidgets.QListWidget()
        self._results_list.itemDoubleClicked.connect(self._onItemActivated)
        self._results_list.currentRowChanged.connect(self._onCurrentRowChanged)
        layout.addWidget(self._results_list, stretch=1)

    def _connectSignals(self) -> None:
        """Wire up signal/slot connections."""

    def setAppStore(self, store: _app_store.ApplicationStore) -> None:
        """Set the application store to search against.

        Args:
            store: ApplicationStore instance to search.

        """
        self._app_store = store

    def populateStacks(self, stacks: list) -> None:
        """Populate the stack combobox.

        Args:
            stacks: List of stack name strings to display.

        """
        self._stack_combo.clear()
        for name in stacks:
            self._stack_combo.addItem(name)

    def setSearchResults(self, entries: list) -> None:
        """Update the results list with search matches.

        Args:
            entries: List of ApplicationEntry instances to display.

        """
        self._results_list.clear()
        for entry in entries:
            item_text = entry.name
            if entry.description:
                item_text += f" — {entry.description}"
            item = QtWidgets.QListWidgetItem(item_text)
            item.setData(QtCore.Qt.UserRole, entry.command)
            self._results_list.addItem(item)

    def _onSearchChanged(self, text: str) -> None:
        """Handle search input changes.

        Args:
            text: Current search string.

        """
        if not self._app_store:
            return

        query = text.strip()
        if not query:
            # Show all apps sorted by favorites, used, then alphabetical
            entries = sorted(
                self._app_store.entries,
                key=lambda e: (not e.favorite, not e.used, e.name.lower()),
            )
        else:
            # Use fuzzy search
            entries = self._fuzzySearch(query)

        self.setSearchResults(entries)

    def _fuzzySearch(self, query: str) -> list[_app_store.ApplicationEntry]:
        """Perform fuzzy search on application entries.

        Implements a simple fuzzy matching algorithm that ranks results by
        relevance: exact matches first, then substring matches, then fuzzy
        character sequence matches.

        Args:
            query: Search query string.

        Returns:
            List of matching ApplicationEntry instances, sorted by relevance.

        """
        if not self._app_store:
            return []

        query_lower = query.lower()
        results = []

        for entry in self._app_store.entries:
            name_lower = entry.name.lower()
            cmd_lower = entry.command.lower()

            # Exact match (highest priority)
            if name_lower == query_lower or cmd_lower == query_lower:
                results.append((0, entry))  # Score 0 = best
                continue

            # Substring match
            if query_lower in name_lower or query_lower in cmd_lower:
                results.append((1, entry))  # Score 1
                continue

            # Fuzzy character sequence match
            if self._isFuzzyMatch(query_lower, name_lower) or \
               self._isFuzzyMatch(query_lower, cmd_lower):
                results.append((2, entry))  # Score 2

        # Sort by score (lower is better), then alphabetically
        results.sort(key=lambda x: (x[0], x[1].name.lower()))
        return [entry for _, entry in results]

    def _isFuzzyMatch(self, query: str, text: str) -> bool:
        """Check if query matches text using fuzzy character sequence matching.

        Args:
            query: Search query (lowercase).
            text: Text to match against (lowercase).

        Returns:
            True if query is a subsequence of text.

        """
        if not query or not text:
            return False

        # Build regex pattern for character sequence matching
        pattern = ".*".join(re.escape(char) for char in query)
        return bool(re.search(pattern, text))

    def _onItemActivated(self, item: QtWidgets.QListWidgetItem) -> None:
        """Handle double-click on a result item.

        Args:
            item: The activated list item.

        """
        command = item.data(QtCore.Qt.UserRole)
        if command:
            self.launch_requested.emit(command, [])

    def _onCurrentRowChanged(self, current_row: int) -> None:
        """Handle current row change for keyboard navigation feedback."""
        # Could add visual feedback here

    def focusSearch(self) -> None:
        """Set keyboard focus to the search input."""
        self._search_input.setFocus()
        self._search_input.selectAll()
