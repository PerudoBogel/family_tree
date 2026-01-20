import sys
from typing import List
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QComboBox, QListWidget, QListWidgetItem, 
                             QLabel, QPushButton)

class NameListEditor(QWidget):
    def __init__(self, available_names):
        super().__init__()
        self.all_names = []
        self.current_names = []
        self._callbacks = [] # List of registered callback functions
        self.diff_added = []
        self.diff_removed = []
        
        # UI Setup
        self.layout = QVBoxLayout(self)
        self.combo = QComboBox()
        self.combo.activated.connect(self._on_combo_activated)
        
        self.list_widget = QListWidget()
        
        self.layout.addWidget(QLabel("Available Names:"))
        self.layout.addWidget(self.combo)
        self.layout.addWidget(QLabel("Selected Names:"))
        self.layout.addWidget(self.list_widget)
        
        self.set_data(available_names)

    # --- Callback Interface ---
    def register_callback(self, func):
        """Registers a function to be called when items are added or removed.
        The function should accept two arguments: (action: str, name: str)
        """
        if func not in self._callbacks:
            self._callbacks.append(func)

    def _notify(self, action, name):
        """Internal helper to trigger all registered callbacks."""
        for callback in self._callbacks:
            try:
                callback(action, name)
            except Exception as e:
                print(f"Error in callback: {e}")

    # --- Public API for Data Management ---
    def set_data(self, available_names, current_names:List[str]=None):
        """Resets the widget with new data pools."""
        self.all_names = sorted(list(set(available_names)))
        self.current_names = []
        self.list_widget.clear()
        
        if current_names:
            for name in current_names:
                if name in self.all_names:
                    self.add_item(name, notify=False) # Don't notify on bulk load
        
        self.update_combo_options()

    def add_item(self, name, notify=True):
        """Programmatic interface to add an item."""
        if name in self.all_names and name not in self.current_names:
            self.current_names.append(name)
            self._create_list_row(name)
            self.update_combo_options()
            if notify:
                if name in self.diff_removed:
                    self.diff_removed.remove(name)
                else:
                    self.diff_added.append(name)
                self._notify("added", name)
            return True
        return False

    def remove_item(self, name, notify=True):
        """Programmatic interface to remove an item."""
        if name in self.current_names:
            self.current_names.remove(name)
            # Find the widget item associated with this name
            for i in range(self.list_widget.count()):
                item = self.list_widget.item(i)
                # We store the name in the item data or look it up via the widget
                row_widget = self.list_widget.itemWidget(item)
                if row_widget.findChild(QLabel).text() == name:
                    self.list_widget.takeItem(i)
                    break
            
            self.update_combo_options()
            if notify:
                if name in self.diff_added:
                    self.diff_added.remove(name)
                else:
                    self.diff_removed.append(name)
                self._notify("removed", name)
            return True
        return False

    # --- Internal UI Logic ---
    def update_combo_options(self):
        self.combo.clear()
        remaining = [n for n in self.all_names if n not in self.current_names]
        if remaining:
            self.combo.addItem("Select to add...")
            self.combo.addItems(remaining)
        else:
            self.combo.addItem("No more items")

    def _on_combo_activated(self, index):
        name = self.combo.itemText(index)
        if name not in ["Select to add...", "No more items"]:
            self.add_item(name)

    def _create_list_row(self, name):
        """Creates the visual row with label and button."""
        item = QListWidgetItem(self.list_widget)
        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(5, 2, 5, 2)
        
        label = QLabel(name)
        btn = QPushButton("X")
        btn.setFixedWidth(30)
        btn.clicked.connect(lambda: self.remove_item(name))
        
        row_layout.addWidget(label)
        row_layout.addStretch()
        row_layout.addWidget(btn)
        
        item.setSizeHint(row_widget.sizeHint())
        self.list_widget.setItemWidget(item, row_widget)

# --- Example Usage ---
def my_logger(action, name):
    print(f"NOTIFICATION: Item '{name}' was {action}.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    manager = NameListEditor(["Python", "Rust", "Swift", "Kotlin"])
    manager.register_callback(my_logger)
    manager.show()

    # Demonstration of programmatic API
    from PySide6.QtCore import QTimer
    QTimer.singleShot(2000, lambda: manager.add_item("Rust"))
    QTimer.singleShot(4000, lambda: manager.remove_item("Rust"))

    sys.exit(app.exec())
