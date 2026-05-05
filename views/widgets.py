"""Shared reusable UI widgets"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
                             QListWidget, QListWidgetItem, QFrame, QLabel,
                             QCompleter, QApplication)
from PyQt6.QtCore import Qt, pyqtSignal, QStringListModel
from PyQt6.QtGui import QFont


# ── Shared style helpers ───────────────────────────────────────────────────────

SHARED_INPUT_STYLE = """
    QLineEdit {
        padding: 10px 14px;
        border: 1.5px solid #d1d5db;
        border-radius: 8px;
        font-size: 13px;
        background-color: #f9fafb;
        color: #111827;
        font-family: 'Segoe UI', sans-serif;
    }
    QLineEdit:focus {
        border: 1.5px solid #2563eb;
        background-color: #ffffff;
    }
"""

SHARED_BTN_STYLE = """
    QPushButton {{
        background-color: {bg};
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        font-size: 13px;
        padding: 10px 22px;
        font-family: 'Segoe UI', sans-serif;
        letter-spacing: 0.2px;
    }}
    QPushButton:hover {{
        background-color: {hover};
    }}
    QPushButton:pressed {{
        background-color: {pressed};
    }}
    QPushButton:disabled {{
        background-color: #d1d5db;
        color: #9ca3af;
    }}
"""

SHARED_TABLE_STYLE = """
    QTableWidget {
        border: none;
        background-color: #ffffff;
        gridline-color: #f3f4f6;
        font-family: 'Segoe UI', sans-serif;
        font-size: 13px;
        selection-background-color: #eff6ff;
    }
    QTableWidget::item {
        padding: 12px 16px;
        color: #1f2937;
        border-bottom: 1px solid #f3f4f6;
    }
    QTableWidget::item:selected {
        background-color: #dbeafe;
        color: #1e3a8a;
    }
    QTableWidget::item:hover {
        background-color: #f0f9ff;
    }
    QHeaderView::section {
        background-color: #f8fafc;
        color: #374151;
        padding: 13px 16px;
        border: none;
        border-bottom: 2px solid #e5e7eb;
        font-weight: 700;
        font-size: 12px;
        font-family: 'Segoe UI', sans-serif;
        letter-spacing: 0.3px;
        text-transform: uppercase;
    }
"""

def btn_style(bg, hover, pressed=None):
    return SHARED_BTN_STYLE.format(bg=bg, hover=hover, pressed=pressed or hover)

def section_label(text):
    lbl = QLabel(text)
    lbl.setStyleSheet("""
        font-size: 12px;
        font-weight: 600;
        color: #374151;
        font-family: 'Segoe UI', sans-serif;
        margin-bottom: 4px;
    """)
    return lbl


# ── Searchable Combo Box (QLineEdit + QCompleter) ──────────────────────────────

class SearchableComboBox(QWidget):
    """
    Reliable searchable dropdown using QLineEdit + QCompleter.
    Type to filter. Click a suggestion to select.
    Emits selection_changed(data_id: int, display_text: str).
    """
    selection_changed = pyqtSignal(int, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._all_items = []   # list of (label_str, data_id)
        self._label_to_id = {} # fast lookup: label -> data_id
        self._selected_id = None
        self._setup_ui()

    def _setup_ui(self):
        self.setFixedHeight(46)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Type to search customer…")
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 10px 14px;
                border: 1.5px solid #d1d5db;
                border-radius: 8px;
                font-size: 13px;
                background-color: #f9fafb;
                color: #111827;
                font-family: 'Segoe UI', sans-serif;
            }
            QLineEdit:focus {
                border: 1.5px solid #2563eb;
                background-color: #ffffff;
            }
        """)
        self.search_input.textEdited.connect(self._on_text_edited)
        layout.addWidget(self.search_input)

        # QCompleter for autocomplete suggestions
        self._completer = QCompleter([])
        self._completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self._completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self._completer.activated.connect(self._on_completer_activated)
        self._completer.popup().setStyleSheet("""
            QListView {
                border: 1.5px solid #2563eb;
                border-radius: 8px;
                background: #ffffff;
                font-size: 13px;
                font-family: 'Segoe UI', sans-serif;
                padding: 4px;
                color: #111827;
            }
            QListView::item {
                padding: 8px 12px;
                border-radius: 5px;
            }
            QListView::item:hover {
                background-color: #eff6ff;
                color: #1d4ed8;
            }
            QListView::item:selected {
                background-color: #dbeafe;
                color: #1e40af;
                font-weight: 600;
            }
        """)
        self.search_input.setCompleter(self._completer)

    def _on_text_edited(self, text):
        """Clear selection when user manually types"""
        self._selected_id = None

    def _on_completer_activated(self, text):
        """Called when user clicks or presses Enter on a suggestion"""
        if text in self._label_to_id:
            self._selected_id = self._label_to_id[text]
            self.search_input.setText(text)
            self.selection_changed.emit(self._selected_id, text)

    # ── Public API ─────────────────────────────────────────────────────────────

    def populate(self, items):
        """
        items: list of (label_str, data_id)
        Rebuilds the completer and lookup map.
        """
        self._all_items = items
        self._label_to_id = {label: data_id for label, data_id in items}
        labels = [label for label, _ in items]
        model = QStringListModel(labels)
        self._completer.setModel(model)

    def set_selection_by_id(self, data_id):
        for label, did in self._all_items:
            if did == data_id:
                self._selected_id = data_id
                self.search_input.setText(label)
                return

    def current_data(self):
        """
        Returns the selected data_id.
        Also validates that the typed text matches a real entry.
        """
        text = self.search_input.text().strip()
        if text in self._label_to_id:
            return self._label_to_id[text]
        return None

    def clear_selection(self):
        self._selected_id = None
        self.search_input.clear()