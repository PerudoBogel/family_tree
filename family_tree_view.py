from typing import List
from PySide6.QtWidgets import (
    QApplication, QWidget, QListWidget, QLineEdit, QTextEdit,
    QPushButton, QFileDialog, QLabel, QHBoxLayout, QVBoxLayout,
    QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsTextItem,
    QMessageBox, QComboBox
)
from PySide6.QtGui import QPen, QBrush, QImage, QPainter
from PySide6.QtCore import Qt
from family_graph import FamilyBranches, MARGIN

from person import Person

class RefSelector(QComboBox):
    def __init__(self, updated_cb):
        super().__init__()
        self.activated.connect(self._on_combo_activated)
        self.people: List[Person] = []
        self.selected: Person = None
        self.updated_cb = updated_cb
    
    def set_options(self, people: List[Person]):
        self.people = people
        
        self.clear()
        if self.people:
            self.addItem("Select to add...")
            self.addItems([x.name for x in self.people])
        else:
            self.addItem("No more items")

        if self.selected in self.people:
            self.removeItem(0)
            self.setCurrentIndex(self.people.index(self.selected))
    
    def _on_combo_activated(self, index):
        if index > 0:
            self.updated_cb(self.people[index - 1])
            self.selected = self.people[index - 1]

class FamilyTreeView(QVBoxLayout):
    def __init__(self):
        super().__init__()

        self.scene = QGraphicsScene(self)
        self.graph_view = QGraphicsView(self.scene)
        self.graph_view.setMinimumWidth(600)

        self.ref_selector = RefSelector(self.select_ref)

        self.addWidget(self.ref_selector)
        self.addWidget(self.graph_view)

        self.people: List[Person] = []
        self.ref_people: List[Person] = []
    
    def set_people(self, people: List[Person]):
        self.people = people
        self.ref_selector.set_options(people)
        self.draw_tree()

    def draw_tree(self):
        self.scene.clear()
        if not self.people:
            return
        if not self.ref_people:
            self.ref_people.append(self.people[0])
        
        self.branches = FamilyBranches(self.ref_people[0], self.people)
        self.branches.setPos(MARGIN, MARGIN)
        self.scene.addItem(self.branches)

    def export_to_jpeg(self, path: str):
        rect = self.scene.itemsBoundingRect()
        image = QImage(
            int(rect.width()) + 20,
            int(rect.height()) + 20,
            QImage.Format_ARGB32
        )
        image.fill(Qt.white)

        painter = QPainter(image)
        self.scene.render(painter)
        painter.end()

        image.save(path, "JPEG")

    def select_ref(self, person_a: Person):
        self.ref_people.clear()
        self.ref_people.append(person_a)
        self.draw_tree()