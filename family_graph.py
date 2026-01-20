from typing import List, Dict, Set
from PySide6.QtWidgets import (
    QApplication, QWidget, QListWidget, QLineEdit, QTextEdit,
    QPushButton, QFileDialog, QLabel, QHBoxLayout, QVBoxLayout,
    QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsTextItem,
    QMessageBox, QComboBox, QListWidgetItem, QFrame, QGraphicsItem, QGraphicsEllipseItem
)
from PySide6.QtGui import QPen, QBrush, QColor, QFont, QPainter
from PySide6.QtCore import QRectF, Qt
from person import Person
from graph_person import GraphPerson
from person import Person

MARGIN: int = 20
MARGIN_UNITS: int = 80

class FamilyUnit(QGraphicsItem):

    def __init__(self, person: Person, people: List[Person], parent=None):
        super().__init__(parent)
        self.unit_head: List[Person] = []
        self.unit_head.append(person)
        for per in people:
            if per.name in person.partners:
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
    
class FamilyBranches(QGraphicsItem):
    def __init__(self, reference_person: Person, people: List[Person], parent=None):
        super().__init__(parent)
        self.pos_y = 0
        self.max_gen_num = 0
        self.gen_counter = 0
        self.ref_unit: FamilyUnit = self.build_unit(reference_person, people)
        self.ref_unit.setPos(0,0)

    def build_unit(self, person: Person, people: List[Person], parent_x_offset: int = 0) -> FamilyUnit:
        unit: FamilyUnit = FamilyUnit(person, people, self)
        children_units: List[FamilyUnit] = []
        children_width = 0
        child_unit_x_offset = parent_x_offset
        for kid_str in person.kids:
            for kid in (kid for kid in people if kid_str == kid.name):
                self.pos_y += GraphPerson.HEIGHT + MARGIN_UNITS
                children_units.append(self.build_unit(kid, people, child_unit_x_offset))
                children_units[-1].setPos(child_unit_x_offset, self.pos_y)
                child_unit_x_offset += children_units[-1].get_width()+ MARGIN_UNITS
                self.pos_y -= GraphPerson.HEIGHT + MARGIN_UNITS
                children_width += children_units[-1].get_width()
                self.gen_counter += 1
                self.max_gen_num = max(self.max_gen_num, self.gen_counter)
                self.gen_counter -= 1
        if len(children_units) > 0:
            children_width += (len(children_units) - 1) * MARGIN_UNITS
        if children_width < unit.get_width():
            child_unit_x_offset = parent_x_offset + (unit.get_width() - children_width) / 2
            for child_unit in children_units:
                child_unit.setPos(child_unit_x_offset, child_unit.y())
                child_unit_x_offset += child_unit.get_width() + MARGIN_UNITS
        
        unit.add_children_units(children_units)

        return unit
    
    def get_width(self):
        return self.ref_unit.get_width()
    
    def get_height(self):
        return self.max_gen_num * GraphPerson.HEIGHT + (self.max_gen_num - 1) + MARGIN_UNITS
    
    def boundingRect(self):
        # Expand height to accommodate potential children rows
        return QRectF(0, 0, self.get_width(), self.get_height())

    def paint(self, painter, option, widget):
        # Optional: Add connectors or debug frames here
        pass

# class FamilyTree(QWidget):
    
people_data = [
    # Generation 1: The Grandparents
    {
        "id": 1, "name": "Arthur Dent", "birth_date": "1950-05-12",
        "partners": ["Beryl Dent"], "kids": ["Charles Dent", "Daisy Miller"]
    },
    {
        "id": 2, "name": "Beryl Dent", "birth_date": "1952-08-20",
        "partners": ["Arthur Dent"], "kids": ["Charles Dent", "Daisy Miller"]
    },
    
    # Generation 2: The Children and their Spouses
    {
        "id": 3, "name": "Charles Dent", "birth_date": "1975-03-15",
        "parents": ["Arthur Dent", "Beryl Dent"], "partners": ["Elena Dent"], "kids": ["Finn Dent"]
    },
    {
        "id": 4, "name": "Elena Dent", "birth_date": "1978-11-02",
        "partners": ["Charles Dent"], "kids": ["Finn Dent"]
    },
    {
        "id": 5, "name": "Daisy Miller", "birth_date": "1980-01-25",
        "parents": ["Arthur Dent", "Beryl Dent"], "partners": ["George Miller"], "kids": ["Holly Miller", "Ian Miller", "May Miller"]
    },
    {
        "id": 6, "name": "George Miller", "birth_date": "1979-06-30",
        "partners": ["Daisy Miller"], "kids": ["Holly Miller", "Ian Miller", "May Miller"]
    },

    # Generation 3: The Grandchildren
    {
        "id": 7, "name": "Finn Dent", "birth_date": "2005-12-12",
        "parents": ["Charles Dent", "Elena Dent"]
    },
    {
        "id": 8, "name": "Holly Miller", "birth_date": "2010-04-05",
        "parents": ["Daisy Miller", "George Miller"]
    },
    {
        "id": 9, "name": "Ian Miller", "birth_date": "2012-09-18",
        "parents": ["Daisy Miller", "George Miller"]
    },
    {
        "id": 10, "name": "May Miller", "birth_date": "2012-09-9",
        "parents": ["Daisy Miller", "George Miller"]
    }
]

# Create the List[Person]
people: List[Person] = [Person.from_dict(p) for p in people_data]

import sys
# Example Test: Print family names and birth years
if __name__ == "__main__":
    app = QApplication(sys.argv)
    print(f"{'Name':<15} | {'Year':<5} | {'Parents'}")
    print("-" * 45)
    for person in people:
        parents_str = ", ".join(person.parents) if person.parents else "N/A"
        print(f"{person.name:<15} | {person.birth_year:<5} | {parents_str}")
    
    branches = FamilyBranches(people[0], people)
    
    scene = QGraphicsScene(0, 0, 1600, 600)
    view = QGraphicsView(scene)
    view.setRenderHint(QPainter.Antialiasing)

    # Add to scene
    branches.setPos(MARGIN, MARGIN)
    scene.addItem(branches)

    view.show()
    sys.exit(app.exec())