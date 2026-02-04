from typing import List
from PySide6.QtWidgets import (
    QApplication, QWidget, QListWidget, QLineEdit, QTextEdit,
    QPushButton, QFileDialog, QLabel, QHBoxLayout, QVBoxLayout,
    QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsTextItem,
    QMessageBox, QComboBox
)
from PySide6.QtGui import QPen, QBrush, QImage, QPainter
from PySide6.QtCore import Qt
from family_unit import MARGIN, FamilyUnit, get_x_offset
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
    
    def make_siblings(self):
        pass
    
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
        
        roots = FamilyRoots(draw_reference, self.people, self.click_callback)
        ref_unit = roots.ref_unit
        while len(ref_unit.parents_units) == 1:
            ref_unit = ref_unit.parents_units[0]
            roots.max_gen_num -= 1 
        
        draw_reference = ref_unit.unit_head[0]
        if draw_reference != ref_person:
            self.erase_unit_with_children_from_graph(ref_unit)

        left_branch: FamilyBranches = None
        right_branch: FamilyBranches = None
        left_ref_unit: FamilyUnit = None
        if len(ref_unit.parents_units) >= 2:
            self.erase_unit_with_children_from_graph(ref_unit.parents_units[0])
            self.erase_unit_with_children_from_graph(ref_unit.parents_units[1])

            left_siblings_person_id = ref_unit.unit_head[0].id
            right_siblings_person_id = ref_unit.unit_head[1].id

            left_branch = FamilyBranches(ref_unit.parents_units[0].unit_head[0], self.people, self.click_callback, move_child_right=left_siblings_person_id)
            right_branch = FamilyBranches(ref_unit.parents_units[1].unit_head[0], self.people, self.click_callback, move_child_left=right_siblings_person_id)

            # align y
            head_offset_y: int = ref_unit.parents_units[0].y() - left_branch.ref_unit.y()
            left_branch.setPos(left_branch.x(), left_branch.y() + head_offset_y + MARGIN)
            right_branch.setPos(right_branch.x(), right_branch.y() + head_offset_y + MARGIN)
            
            left_ref_unit = next(x for x in left_branch.ref_unit.children_units if ref_unit.unit_head[0] in x.unit_head)

            #align branches to POI children
            ref_x_offset = get_x_offset(0,ref_unit.head_graph[0])
            left_branch_x_offset = ref_x_offset - get_x_offset(0,next(x for x in left_branch.ref_unit.children_units if ref_unit.unit_head[0] in x.unit_head).head_graph[0])
            right_branch_x_offset = ref_x_offset - get_x_offset(0,next(x for x in right_branch.ref_unit.children_units if ref_unit.unit_head[1] in x.unit_head).head_graph[0])

            left_branch.setPos(left_branch.x() + left_branch_x_offset, left_branch.y())
            right_branch.setPos(right_branch.x() + right_branch_x_offset, right_branch.y())
        else:
            left_branch = FamilyBranches(draw_reference, self.people, self.click_callback)
            left_ref_unit = left_branch.ref_unit
        
        sibling_ref_offset_x = get_x_offset(0, left_ref_unit.head_graph[0])
        root_ref_offset_x = get_x_offset(0, ref_unit.head_graph[0])

        root_x_trans = sibling_ref_offset_x - root_ref_offset_x if sibling_ref_offset_x > root_ref_offset_x else 0
        branch_x_trans = root_ref_offset_x - sibling_ref_offset_x if sibling_ref_offset_x < root_ref_offset_x else 0

        #align graphs
        roots.setPos(MARGIN + root_x_trans, MARGIN)
        if left_branch:
            left_branch.setPos(MARGIN + branch_x_trans + left_branch.x(), left_branch.y())
        if right_branch:
            right_branch.setPos(MARGIN + branch_x_trans + right_branch.x(), right_branch.y())

        # #align branches heads
        if left_branch and right_branch:
            left_x_offset = get_x_offset(0,ref_unit.parents_units[0].head_graph[0]) - get_x_offset(0,left_branch.ref_unit.head_graph[0])
            left_branch.ref_unit.setPos(left_x_offset + left_branch.ref_unit.x(), left_branch.ref_unit.y())
            left_branch.ref_unit.draw_heads_connection()
            
            right_x_offset = get_x_offset(0,ref_unit.parents_units[1].head_graph[0]) - get_x_offset(0,right_branch.ref_unit.head_graph[0])
            right_branch.ref_unit.setPos(right_x_offset + right_branch.ref_unit.x(), right_branch.ref_unit.y())
            right_branch.ref_unit.draw_heads_connection()

            right_ref_unit = next(x for x in right_branch.ref_unit.children_units if ref_unit.unit_head[0] in x.unit_head)
            self.erase_unit_with_children_from_graph(right_ref_unit)

        self.highlight_unit_or_child_unit(left_branch.ref_unit, ref_person.id)

        if left_branch:
            self.scene.addItem(left_branch)
        if right_branch:
            self.scene.addItem(right_branch)
        self.scene.addItem(roots)

        self.scene.update()

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