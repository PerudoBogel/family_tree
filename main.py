import json
from dataclasses import dataclass, field
from typing import List
from datetime import datetime

from PySide6.QtWidgets import (
    QApplication, QWidget, QListWidget, QLineEdit, QTextEdit,
    QPushButton, QFileDialog, QLabel, QHBoxLayout, QVBoxLayout,
    QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsTextItem,
    QMessageBox, QComboBox, QListWidgetItem, QFrame
)
from PySide6.QtGui import QPen, QBrush, QImage, QPainter
from PySide6.QtCore import Qt
from person import Person
from family_tree_view import FamilyTreeView
from person_editor import PersonEditor

# =======================
# MAIN WINDOW
# =======================

class FamilyEditor(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Family Tree Editor (Timeline)")
        self.resize(1250, 650)

        self.people: List[Person] = []
        self.current_person = None
        self.selected_index = 0
        
        self.person_editor = PersonEditor()

        self.list_widget = QListWidget()

        self.add_btn = QPushButton("Add Person")
        self.add_btn.clicked.connect(self.add_person)

        self.edit_btn = QPushButton("Edit Person")
        self.edit_btn.clicked.connect(self.open_person_editor)

        self.remove_btn = QPushButton("Remove Person")
        self.remove_btn.clicked.connect(self.remove_person)

        self.load_btn = QPushButton("Load JSON")
        self.load_btn.clicked.connect(self.load_json)

        self.save_json_btn = QPushButton("Save JSON")
        self.save_json_btn.clicked.connect(self.save_json)

        self.export_btn = QPushButton("Export Graph (JPEG)")
        self.export_btn.clicked.connect(self.export_graph)

        self.list_widget.currentRowChanged.connect(lambda select_person: self.select_person(select_person))
        self.person_editor.register_refresh(self.refresh)

        self.tree_view = FamilyTreeView()

        self.build_ui()
    
    def select_person(self, sel):
        self.person_editor.select_person(sel)
        self.tree_view.select_ref(self.person_editor.current_person)
    
    def open_person_editor(self):
        self.person_editor.show()

    def build_ui(self):
        left = QVBoxLayout()
        left.addWidget(self.list_widget)
        left.addWidget(self.edit_btn)
        left.addWidget(self.add_btn)
        left.addWidget(self.remove_btn)
        left.addWidget(self.load_btn)
        left.addWidget(self.save_json_btn)
        left.addWidget(self.export_btn)

        self.fixed_container = QFrame()
        self.fixed_container.setFixedWidth(250)  # Constrain the sidebar width
        editor = QHBoxLayout(self.fixed_container)
        editor.addLayout(left)

        layout = QHBoxLayout(self)
        layout.addWidget(self.fixed_container)
        layout.addLayout(self.tree_view)

        self.load_json_from_file("./family_info.json")

    # =======================
    # DATA LOGIC
    # =======================

    def next_id(self):
        return max((p.id for p in self.people), default=0) + 1

    def refresh(self):
        self.list_widget.clear()
        self.people.sort(key = lambda p: p.name)
        for p in self.people:
            self.list_widget.addItem(p.name_n_birth or "(Unnamed)")
        self.tree_view.set_people(self.people)
        self.tree_view.draw_tree()

    def add_person(self):
        self.people.append(Person(self.next_id(), "", "", [], []))
        self.refresh()
        self.list_widget.setCurrentRow(0)

    def remove_person(self):
        idx = self.list_widget.currentRow()
        if idx < 0:
            return
        person = self.people[idx]
        confirm = QMessageBox.question(
            self, "Confirm",
            f"Remove {person.name}?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            self.people.pop(idx)
            for p in self.people:
                if person.name in p.kids:
                    try:
                        p.parents.remove(person.name)
                    except:
                        pass
                    try:
                        p.kids.remove(person.name)
                    except:
                        pass
                    try:
                        p.partners.remove(person.name)
                    except:
                        pass
            self.current_person = None
            self.refresh()
        
    def load_json_from_file(self, filename):
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.people = [Person.from_dict(p) for p in data["people"]]
        # self.people.sort(key = lambda p: p.name)
        self.person_editor.update_people(self.people)
        self.refresh()

    def load_json(self):
        path, _ = QFileDialog.getOpenFileName(self, "Load JSON", "", "JSON Files (*.json)")
        if not path:
            return
        self.load_json_from_file(path)

    def save_json(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save JSON", "", "JSON Files (*.json)")
        if not path:
            return
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"people": [p.to_dict() for p in self.people]}, f, indent=2)

    def export_graph(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export JPEG", "", "JPEG (*.jpg)")
        if path:
            self.tree_view.export_to_jpeg(path)


# =======================
# WINDOWS ENTRY POINT
# =======================

if __name__ == "__main__":
    app = QApplication([])
    window = FamilyEditor()
    window.show()
    app.exec()
