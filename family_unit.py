from typing import List
from person import Person
from graph_person import GraphPerson
from PySide6.QtWidgets import (
    QApplication, QWidget, QListWidget, QLineEdit, QTextEdit,
    QPushButton, QFileDialog, QLabel, QHBoxLayout, QVBoxLayout,
    QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsTextItem,
    QMessageBox, QComboBox, QListWidgetItem, QFrame, QGraphicsItem, QGraphicsEllipseItem
)
from PySide6.QtGui import QPen, QBrush, QColor, QFont, QPainter
from PySide6.QtCore import QRectF, Qt

MARGIN: int = 20
MARGIN_UNITS: int = 80

class FamilyUnit(QGraphicsItem):

    def __init__(self, person: Person, people: List[Person], parent=None):
        super().__init__(parent)
        self.unit_head: List[Person] = []
        self.unit_head.append(person)
        for per in people:
            if per.id in person.partners:
                self.unit_head.append(per)
        
        self.head_graph: List[GraphPerson] = []
        for head in self.unit_head:
            self.head_graph.append(GraphPerson(head, self))

        self.children_units: List["FamilyUnit"] = []
        self.display_width = 0
        self.align_width(self.get_width())
    
    def add_children_units(self, childer_units: List["FamilyUnit"]):
        self.children_units = childer_units
        self.align_width(self.get_width())

    def align_width(self, width):
        head_count = len(self.head_graph)
        x_offset = (width - (head_count * GraphPerson.WIDTH + (head_count - 1) * MARGIN))/2
        i=0
        for head in self.head_graph:
            head.setPos(x_offset + i * (GraphPerson.WIDTH + MARGIN), 0)
            i += 1
        self.display_width = i * (GraphPerson.WIDTH) + (i - 1) * MARGIN

    def get_width(self):
        childer_width = 0
        for unit in self.children_units:
            childer_width += unit.get_width()
        if len(self.children_units) > 0:
            childer_width += (len(self.children_units) - 1) * MARGIN_UNITS
        
        head_width = 0
        if len(self.unit_head) > 0:
            head_width += (len(self.unit_head) - 1) * MARGIN
            head_width += len(self.unit_head) * GraphPerson.WIDTH
        
        return childer_width if childer_width > head_width else head_width

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