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

class PersonEditor(QWidget):

    def __init__(self):
        super().__init__()
        self.resize(650, 650)
        self.people: List[Person] = []
        self.current_person: Person = None
        self.selected_index: int = 0
        self.refresh_callback = None

        self.name_edit = QLineEdit()
        self.middle_name_edit = QLineEdit()
        self.last_name_edit = QLineEdit()
        self.family_name_edit = QLineEdit()
        self.birth_edit = QLineEdit()
        self.death_edit = QLineEdit()
        self.notes_edit = QTextEdit()
        
        self.parents_list = PeopleListEditor([])
        self.partners_list = PeopleListEditor([])
        self.kids_list = PeopleListEditor([])

        self.save_btn = QPushButton("Save Changes")
        self.save_btn.clicked.connect(self.save_changes)
        
        self.name_layout = QVBoxLayout()
        self.name_layout.addWidget(QLabel("Name"))
        self.name_layout.addWidget(self.name_edit)
        self.middle_name_layout = QVBoxLayout()
        self.middle_name_layout.addWidget(QLabel("Middle Names"))
        self.middle_name_layout.addWidget(self.middle_name_edit)
        self.names_layout = QHBoxLayout()
        self.names_layout.addLayout(self.name_layout)
        self.names_layout.addLayout(self.middle_name_layout)
        
        self.last_name_layout = QVBoxLayout()
        self.last_name_layout.addWidget(QLabel("Last Name"))
        self.last_name_layout.addWidget(self.last_name_edit)
        self.family_name_layout = QVBoxLayout()
        self.family_name_layout.addWidget(QLabel("Family Name"))
        self.family_name_layout.addWidget(self.family_name_edit)
        self.last_names_layout = QHBoxLayout()
        self.last_names_layout.addLayout(self.last_name_layout)
        self.last_names_layout.addLayout(self.family_name_layout)

        self.birth_layout = QVBoxLayout()
        self.birth_layout.addWidget(QLabel("Birth Date (YYYY-MM-DD)"))
        self.birth_layout.addWidget(self.birth_edit)
        self.death_layout = QVBoxLayout()
        self.death_layout.addWidget(QLabel("Death Date (YYYY-MM-DD)"))
        self.death_layout.addWidget(self.death_edit)
        self.life_layout = QHBoxLayout()
        self.life_layout.addLayout(self.birth_layout)
        self.life_layout.addLayout(self.death_layout)

        self.left_layout = QVBoxLayout()
        self.left_layout.addLayout(self.names_layout,2)
        self.left_layout.addLayout(self.last_names_layout,2)
        self.left_layout.addLayout(self.life_layout,2)
        self.left_layout.addWidget(QLabel("Notes"),1)
        self.left_layout.addWidget(self.notes_edit,10)
        self.left_layout.addWidget(self.save_btn,1)
        
        self.right_layout = QVBoxLayout()
        self.right_layout.addWidget(QLabel("Parents"))
        self.right_layout.addWidget(self.parents_list)
        self.right_layout.addWidget(QLabel("Partners"))
        self.right_layout.addWidget(self.partners_list)
        self.right_layout.addWidget(QLabel("Kids"))
        self.right_layout.addWidget(self.kids_list)
        
        self.main_layout = QHBoxLayout()
        self.main_layout.addLayout(self.left_layout)
        self.main_layout.addLayout(self.right_layout)

        self.setLayout(self.main_layout)

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
        self.middle_name_edit.setText(self.current_person.middle_name)
        self.last_name_edit.setText(self.current_person.last_name)
        self.family_name_edit.setText(self.current_person.family_name)
        self.birth_edit.setText(self.current_person.birth_date)
        self.death_edit.setText(self.current_person.death_date)
        self.notes_edit.setText(self.current_person.notes)

        available_people: List[Person] = [x for x in self.people if x != self.current_person]

        self.parents_list.set_data(available_people, [x for x in self.people if x.id in self.current_person.parents])
        self.partners_list.set_data(available_people, [x for x in self.people if x.id in self.current_person.partners])
        self.kids_list.set_data(available_people, [x for x in self.people if x.id in self.current_person.kids])

    def save_changes(self):
        if not self.current_person:
            return
        self.current_person.name = self.name_edit.text()
        self.current_person.middle_name = self.middle_name_edit.text()
        self.current_person.last_name = self.last_name_edit.text()
        self.current_person.family_name = self.family_name_edit.text()
        self.current_person.birth_date = self.birth_edit.text()
        self.current_person.death_date = self.death_edit.text()
        self.current_person.notes = self.notes_edit.toPlainText()

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