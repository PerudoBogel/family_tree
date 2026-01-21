from PySide6.QtWidgets import (
    QApplication, QWidget, QListWidget, QLineEdit, QTextEdit,
    QPushButton, QFileDialog, QLabel, QHBoxLayout, QVBoxLayout,
    QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsTextItem,
    QMessageBox, QComboBox, QListWidgetItem
)
from PySide6.QtGui import QPen, QBrush, QImage, QPainter
from PySide6.QtCore import Qt

from typing import List
from people_list_editor import PeopleListEditor
from person import Person

class PersonEditor:

    def __init__(self):
        super().__init__()
        self.people: List[Person] = []
        self.current_person: Person = None
        self.selected_index: int = 0
        self.refresh_callback = None

        self.name_edit = QLineEdit()
        self.birth_edit = QLineEdit()
        
        self.parents_list = PeopleListEditor([])
        self.partners_list = PeopleListEditor([])
        self.kids_list = PeopleListEditor([])

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

        available_people: List[Person] = [x for x in self.people if x != self.current_person]

        self.parents_list.set_data(available_people, [x for x in self.people if x.id in self.current_person.parents])
        self.partners_list.set_data(available_people, [x for x in self.people if x.id in self.current_person.partners])
        self.kids_list.set_data(available_people, [x for x in self.people if x.id in self.current_person.kids])

    def save_changes(self):
        if not self.current_person:
            return
        self.current_person.name = self.name_edit.text()
        self.current_person.birth_date = self.birth_edit.text()
        self.current_person.parents = [x.id for x in self.parents_list.current_people]
        self.current_person.partners = [x.id for x in self.partners_list.current_people]
        self.current_person.kids = [x.id for x in self.kids_list.current_people]

        def update_target_list(self_list, list_name):
            try:
                add_diff: List[Person] = getattr(self, self_list, None).diff_added
                rem_diff: List[Person] = getattr(self, self_list, None).diff_removed
            except:
                print("wrong list name: " + str(self_list))
                return
            for target_person in add_diff:
                tar_list = getattr(target_person, list_name, None)
                try:
                    tar_list.append(self.current_person.id)
                except:
                    pass

            for target_person in rem_diff:
                tar_list = getattr(target_person, list_name, None)
                try:
                    tar_list.remove(self.current_person.id)
                except:
                    pass
            add_diff.clear()
            rem_diff.clear()

        update_target_list("parents_list", "kids")
        update_target_list("partners_list", "partners")
        update_target_list("kids_list", "parents")

        if self.refresh_callback:
            self.refresh_callback()