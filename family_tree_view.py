from typing import List
from PySide6.QtWidgets import (
    QApplication, QWidget, QListWidget, QLineEdit, QTextEdit,
    QPushButton, QFileDialog, QLabel, QHBoxLayout, QVBoxLayout,
    QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsTextItem,
    QMessageBox, QComboBox
)
from PySide6.QtGui import QPen, QBrush, QImage, QPainter
from PySide6.QtCore import Qt
from family_unit import MARGIN, FamilyUnit
from family_branches import FamilyBranches
from family_roots import FamilyRoots

from person import Person

class FamilyTreeView(QVBoxLayout):
    def __init__(self, click_callback):
        super().__init__()

        self.scene = QGraphicsScene(self)
        self.graph_view = QGraphicsView(self.scene)
        self.graph_view.setMinimumWidth(600)
        self.click_callback = click_callback

        self.addWidget(self.graph_view)

        self.people: List[Person] = []
        self.ref_people: List[Person] = []
    
    def set_people(self, people: List[Person]):
        self.people = people
        self.draw_tree()
    
    def erase_unit_with_children_from_graph(self, ref_unit: FamilyUnit):
        ref_unit.setVisible(False)
        for child_unit in ref_unit.children_units:
            self.erase_unit_with_children_from_graph(child_unit)
    
    def highlight_unit_or_child_unit(self, ref_unit: FamilyUnit, id: int):
        try:
            highlight_graph = next(x for x in ref_unit.head_graph if x.person.id == id)
            highlight_graph.highlight()
            highlight_graph.update()
        except:
            for child_unit in ref_unit.children_units:
                self.highlight_unit_or_child_unit(child_unit, id)

    def draw_tree(self):
        self.scene.clear()
        if not self.people:
            return
        if not self.ref_people:
            self.ref_people.append(self.people[0])
        
        draw_reference: Person = self.ref_people[0]
        ref_person: Person = self.ref_people[0]
        
        self.roots = FamilyRoots(draw_reference, self.people, self.click_callback)
        ref_unit = self.roots.ref_unit
        while len(ref_unit.parents_units) == 1:
            ref_unit = ref_unit.parents_units[0]
            self.roots.max_gen_num -= 1 
        
        draw_reference = ref_unit.unit_head[0]
        
        self.branches = FamilyBranches(draw_reference, self.people, self.click_callback)

        if draw_reference != ref_person:
            self.erase_unit_with_children_from_graph(ref_unit)

        self.highlight_unit_or_child_unit(self.branches.ref_unit, ref_person.id)

        roots_offset = self.branches.ref_unit.x_offset - ref_unit.x_offset if self.branches.get_width() > self.roots.get_width() else 0
        branches_offset = ref_unit.x_offset - self.branches.ref_unit.x_offset if self.roots.get_width() > self.branches.get_width() else 0
        
        self.roots.setPos(MARGIN + roots_offset, MARGIN)
        self.branches.setPos(MARGIN + branches_offset, self.roots.get_height() + MARGIN)

        self.scene.addItem(self.roots)
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