import sys
from typing import List
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QComboBox, QListWidget, QListWidgetItem, 
                             QLabel, QPushButton)
from person import Person

class PeopleListEditor(QWidget):
    def __init__(self, people: List[Person]):
        super().__init__()
        self.current_people: List[Person] = []
        self._callbacks = [] # List of registered callback functions
        self.diff_added: List[Person] = []
        self.diff_removed: List[Person] = []
        self.people: List[Person] = people
        
        # UI Setup
        self.layout = QVBoxLayout(self)
        self.combo = QComboBox()
        self.combo.activated.connect(self._on_combo_activated)
        
        self.list_widget = QListWidget()
        
        self.layout.addWidget(QLabel("Available People:"))
        self.layout.addWidget(self.combo)
        self.layout.addWidget(QLabel("Selected People:"))
        self.layout.addWidget(self.list_widget)
        
        self.set_data(self.people)

    # --- Callback Interface ---
    def register_callback(self, func):
        """Registers a function to be called when items are added or removed.
        The function should accept two arguments: (action: str, person: Person)
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
    def set_data(self, people: List[Person], current_people: List[int] = []):
        self.people: List[Person] = people
        self.current_people = []
        self.list_widget.clear()
        
        if current_people:
            for person in current_people:
                self.add_item(person, notify=False)
        
        self.update_combo_options()

    def add_item(self, person: Person, notify=True):
        if person in self.people and person not in self.current_people:
            self.current_people.append(person)
            self._create_list_row(person)
            self.update_combo_options()
            if notify:
                if person in self.diff_removed:
                    self.diff_removed.remove(person)
                else:
                    self.diff_added.append(person)
                self._notify("added", person)
            return True
        return False

    def remove_item(self, person: Person, notify=True):
        if person in self.current_people:
            self.current_people.remove(person)
            # Find the widget item associated with this name
            for i in range(self.list_widget.count()):
                item = self.list_widget.item(i)
                # We store the name in the item data or look it up via the widget
                row_widget = self.list_widget.itemWidget(item)
                if row_widget.findChild(QLabel).text() == person.search_name:
                    self.list_widget.takeItem(i)
                    break
            
            self.update_combo_options()
            if notify:
                if person in self.diff_added:
                    self.diff_added.remove(person)
                else:
                    self.diff_removed.append(person)
                self._notify("removed", person)
            return True
        return False

    # --- Internal UI Logic ---
    def update_combo_options(self):
        self.combo.clear()
        self.selection: List[Person] = [x for x in self.people if x not in self.current_people]
        if self.selection:
            self.combo.addItem("Select to add...")
            self.combo.addItems([x.search_name for x in self.selection])
        else:
            self.combo.addItem("No more items")

    def _on_combo_activated(self, index):
        if index > 0:
            self.add_item(self.selection[index - 1])

    def _create_list_row(self, person: Person):
        """Creates the visual row with label and button."""
        item = QListWidgetItem(self.list_widget)
        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(5, 2, 5, 2)
        
        label = QLabel(person.search_name)
        btn = QPushButton("X")
        btn.setFixedWidth(30)
        btn.clicked.connect(lambda: self.remove_item(person))
        
        row_layout.addWidget(label)
        row_layout.addStretch()
        row_layout.addWidget(btn)
        
        item.setSizeHint(row_widget.sizeHint())
        self.list_widget.setItemWidget(item, row_widget)

# --- Example Usage ---
def my_logger(action, person: Person):
    print(f"NOTIFICATION: Item '{person}' was {action}.")

def get_mock_people():
    return [
        Person(id=1, name="Alice Smith", birth_date="1990-01-01"),
        Person(id=2, name="Bob Jones", birth_date="1985-05-12"),
        Person(id=3, name="Charlie Brown", birth_date="2010-07-20"),
        Person(id=4, name="Diana Prince", birth_date="1988-11-30"),
    ]

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    people = get_mock_people()
    manager = PeopleListEditor(people)
    manager.register_callback(my_logger)
    manager.show()

    # Demonstration of programmatic API
    from PySide6.QtCore import QTimer
    QTimer.singleShot(2000, lambda: manager.add_item(people[0]))
    QTimer.singleShot(4000, lambda: manager.remove_item(people[0]))

    sys.exit(app.exec())
