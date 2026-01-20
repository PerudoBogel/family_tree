from PySide6.QtWidgets import (
    QApplication, QWidget, QListWidget, QLineEdit, QTextEdit,
    QPushButton, QFileDialog, QLabel, QHBoxLayout, QVBoxLayout,
    QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsTextItem,
    QMessageBox, QComboBox, QListWidgetItem
)
from PySide6.QtGui import QPen, QBrush, QImage, QPainter
from PySide6.QtCore import Qt

from typing import List
from name_list_editor import NameListEditor
from person import Person

class PersonEditor:

    def __init__(self):
        super().__init__()
        self.people = []
        self.current_person = None
        self.selected_index = 0
        self.refresh_callback = None

        self.name_edit = QLineEdit()
        self.birth_edit = QLineEdit()
        
        self.parents_list = NameListEditor([""])
        self.partners_list = NameListEditor([""])
        self.kids_list = NameListEditor([""])

        self.save_btn = QPushButton("Save Changes")
        self.save_btn.clicked.connect(self.save_changes)
        
        self.layout = QVBoxLayout()
        self.layout.addWidget(QLabel("Name"))
        self.layout.addWidget(self.name_edit)
        self.layout.addWidget(QLabel("Birth Date (YYYY-MM-DD)"))
        self.layout.addWidget(self.birth_edit)
        self.layout.addWidget(QLabel("Parents"))
        self.layout.addWidget(self.parents_list)
        self.layout.addWidget(QLabel("Partners"))
        self.layout.addWidget(self.partners_list)
        self.layout.addWidget(QLabel("Kids"))
        self.layout.addWidget(self.kids_list)
        self.layout.addWidget(self.save_btn)

    def register_refresh(self, refresh_callback):
        self.refresh_callback = refresh_callback
    
    def update_people(self, people):
        self.people = people

    def select_person(self, index):
        if index < 0 or index >= len(self.people):
            return
        self.selected_index = index
        self.current_person = self.people[self.selected_index]
        self.name_edit.setText(self.current_person.name)
        self.birth_edit.setText(self.current_person.birth_date)

        available_names: List[str] = []
        for p in self.people:
            if(p.name == self.current_person.name):
                continue
            available_names.append(str(p.name))

        self.parents_list.set_data(available_names, self.current_person.parents)
        self.partners_list.set_data(available_names, self.current_person.partners)
        self.kids_list.set_data(available_names, self.current_person.kids)

    def save_changes(self):
        if not self.current_person:
            return
        self.current_person.name = self.name_edit.text()
        self.current_person.birth_date = self.birth_edit.text()
        self.current_person.parents = [
            k.strip() for k in self.parents_list.current_names if k.strip()
        ]
        self.current_person.partners = [
            p.strip() for p in self.partners_list.current_names if p.strip()
        ]
        self.current_person.kids = [
            k.strip() for k in self.kids_list.current_names if k.strip()
        ]

        def update_target_list(self_list, list_name):
            try:
                add_diff = getattr(self, self_list, None).diff_added
                rem_diff = getattr(self, self_list, None).diff_removed
            except:
                print("wrong list name: " + str(self_list))
                return
            for target_name in add_diff:
                target_person: Person = next((obj for obj in self.people if obj.name == target_name), None)
                if not target_person:
                    continue
                tar_list = getattr(target_person, list_name, None)
                try:
                    tar_list.append(self.current_person.name)
                except:
                    pass

            for target_name in rem_diff:
                target_person: Person = next((obj for obj in self.people if obj.name == target_name), None)
                if not target_person:
                    continue
                tar_list = getattr(target_person, list_name, None)
                try:
                    tar_list.remove(self.current_person.name)
                except:
                    pass
            add_diff.clear()
            rem_diff.clear()

        update_target_list("parents_list", "kids")
        update_target_list("partners_list", "partners")
        update_target_list("kids_list", "parents")

        if self.refresh_callback:
            self.refresh_callback()