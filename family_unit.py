from typing import List
from person import Person
from graph_person import GraphPerson
from PySide6.QtWidgets import (
    QApplication, QWidget, QListWidget, QLineEdit, QTextEdit,
    QPushButton, QFileDialog, QLabel, QHBoxLayout, QVBoxLayout,
    QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsTextItem,
    QMessageBox, QComboBox, QListWidgetItem, QFrame, QGraphicsItem, QGraphicsEllipseItem,
    QGraphicsLineItem
)
from PySide6.QtGui import QPen, QBrush, QColor, QFont, QPainter
from PySide6.QtCore import QRectF, Qt, QLine

MARGIN: int = 20
MARGIN_UNITS: int = 80

def get_x_offset(x_offset: int, item: QGraphicsItem):
    parent = item
    while parent:
        x_offset += parent.x()
        parent = parent.parentItem()
    return x_offset

class FamilyUnit(QGraphicsItem):

    def __init__(self, person: Person, people: List[Person], parent, click_callback):
        super().__init__(parent)
        self.unit_head: List[Person] = []
        self.unit_head.append(person)
        for per in people:
            if per.id in person.partners:
                self.unit_head.append(per)
        
        self.head_graph: List[GraphPerson] = []
        for head in self.unit_head:
            self.head_graph.append(GraphPerson(head, self, click_callback))

        self.children_units: List["FamilyUnit"] = []
        self.parents_units: List["FamilyUnit"] = []
        self.display_width = 0
        self.x_offset = 0
    
    def add_children_units(self, units: List["FamilyUnit"], update_parent: bool = True):
        self.children_units += units
        if update_parent:
            for unit in self.children_units:
                unit.add_parent_units([self],False)
    
    def add_parent_units(self, units: List["FamilyUnit"], update_parent: bool = True):
        self.parents_units += units
        if update_parent:
            for unit in self.parents_units:
                unit.add_children_units([self],False)

    def align(self, width):
        head_count = len(self.head_graph)
        self.x_offset = (width - (head_count * GraphPerson.WIDTH + (head_count - 1) * MARGIN))/2
        i=0
        for head in self.head_graph:
            head.setPos(self.x_offset + i * (GraphPerson.WIDTH + MARGIN), 0)
            i += 1
        self.display_width = i * (GraphPerson.WIDTH) + (i - 1) * MARGIN

    def get_width(self, with_parents = False, with_children = False):
        children_width = 0
        if with_children:
            for unit in self.children_units:
                children_width += unit.get_width(False,with_children)
            if len(self.children_units) > 0:
                children_width += (len(self.children_units) - 1) * MARGIN_UNITS
    
        parents_width = 0
        if with_parents:
            for unit in self.parents_units:
                parents_width += unit.get_width(with_parents,False)
            if len(self.parents_units) > 0:
                parents_width += (len(self.parents_units) - 1) * MARGIN_UNITS

        width = 0
        if len(self.unit_head) > 0:
            width += (len(self.unit_head) - 1) * MARGIN
            width += len(self.unit_head) * GraphPerson.WIDTH
        
        return max(children_width, parents_width, width)

    def draw_heads_connection(self):
        segments = []
        mid_point_x = None
        if len(self.head_graph) > 1:
            # Define pen style (color, width)

            vert_y: int = int(self.head_graph[0].y() + GraphPerson.HEIGHT + MARGIN_UNITS/4)
            vert_x1: int = int(self.head_graph[0].x() + GraphPerson.WIDTH/2)
            vert_x2: int = int(self.head_graph[1].x() + GraphPerson.WIDTH/2)
            mid_point_x = (vert_x1 + vert_x2) / 2
            segments += [
                QGraphicsLineItem(vert_x1, vert_y - MARGIN_UNITS/4, vert_x1, vert_y,self),
                QGraphicsLineItem(vert_x2, vert_y - MARGIN_UNITS/4, vert_x2, vert_y,self),
                QGraphicsLineItem(vert_x1, vert_y, vert_x2, vert_y,self),
            ]
        elif len(self.head_graph) == 1:
            vert_y: int = int(self.head_graph[0].y() + GraphPerson.HEIGHT + MARGIN_UNITS/4)
            mid_point_x = int(self.head_graph[0].x() + GraphPerson.WIDTH/2)
            if len(self.children_units)>0:
                segments.append(QGraphicsLineItem(mid_point_x, vert_y - MARGIN_UNITS/4, mid_point_x, vert_y,self))

        if len(self.children_units)>0 and mid_point_x:
            start_point_x = mid_point_x
            start_point_y = vert_y + MARGIN_UNITS/2
            segments.append(QGraphicsLineItem(start_point_x, vert_y, start_point_x, start_point_y,self))
            children = []
            for head in self.unit_head:
                children += [x for x in head.kids if not x in children]
            for unit in self.children_units:
                kid: GraphPerson = next(x for x in unit.head_graph if x.person.id in children)
                if kid:
                    mid_offest = get_x_offset(start_point_x, self)
                    kid_offest = get_x_offset(GraphPerson.WIDTH / 2, kid)
                    x_offset = mid_offest - kid_offest
                    end_point_x = start_point_x - x_offset 
                    end_point_y = start_point_y + MARGIN_UNITS/4
                    segments.append(QGraphicsLineItem(start_point_x, start_point_y, end_point_x, start_point_y,self))
                    segments.append(QGraphicsLineItem(end_point_x, start_point_y, end_point_x, end_point_y,self))

        pen = QPen(Qt.black, 3)
        for segment in segments:
            segment.setPen(pen)

    def trace(self):
        names: str = "head: "
        for x in self.unit_head:
            names += str(x.name) + " "
        print(names)
        for x in self.children_units:
            x.trace()
    
    def boundingRect(self):
        # Expand height to accommodate potential children rows
        return QRectF(0, 0, self.display_width, GraphPerson.HEIGHT)

    def paint(self, painter, option, widget):
        # Optional: Add connectors or debug frames here
        pass