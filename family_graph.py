from typing import List
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
from family_unit import FamilyUnit, MARGIN, MARGIN_UNITS

class FamilyBranches(QGraphicsItem):
    GEN_OFFSET: int = GraphPerson.HEIGHT + MARGIN_UNITS

    def __init__(self, reference_person: Person, people: List[Person], parent=None):
        super().__init__(parent)

        self.max_gen_num = 0
        self.gen_counter = 0
        self.ref_unit: FamilyUnit = self.build_unit(reference_person, people)

        self.ref_unit.setPos(0,0)
        self.y_offset = 0
        self.draw_unit(self.ref_unit,0)
        self.draw_connections(self.ref_unit)

    def build_unit(self, person: Person, people: List[Person]) -> FamilyUnit:
        unit: FamilyUnit = FamilyUnit(person, people, self)
        children_units: List[FamilyUnit] = []
        for kid_id in person.kids:
            for kid in (kid for kid in people if kid_id == kid.id):
                self.gen_counter += 1
                children_units.append(self.build_unit(kid, people))
                self.max_gen_num = max(self.max_gen_num, self.gen_counter)
                self.gen_counter -= 1
        unit.add_children_units(children_units)
        return unit
    
    def draw_unit(self, unit: FamilyUnit, parent_offset_x: int) -> FamilyUnit:
        children_width = 0
        child_offset_x = parent_offset_x

        for kid_unit in unit.children_units:
            self.y_offset += self.GEN_OFFSET
            kid_unit.setPos(child_offset_x, self.y_offset)
            self.draw_unit(kid_unit,child_offset_x)
            child_offset_x += kid_unit.get_width()+ MARGIN_UNITS
            self.y_offset -= self.GEN_OFFSET
            children_width += kid_unit.get_width()
        
        children_width += (len(unit.children_units) - 1) * MARGIN_UNITS if len(unit.children_units) > 0 else 0

        if children_width < unit.get_width():
            child_offset_x = parent_offset_x + (unit.get_width() - children_width) / 2
            for child_unit in unit.children_units:
                child_unit.setPos(child_offset_x, child_unit.y())
                child_offset_x += child_unit.get_width() + MARGIN_UNITS

        return unit

    def draw_connections(self, unit: FamilyUnit):
        pass
    
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
    
people_data: List[Person] = [
    # Generation 1
    {
        "id": 1, "name": "Arthur Dent", "birth_date": "1950-05-12",
        "partners": [2], "kids": [3, 5]
    },
    {
        "id": 2, "name": "Beryl Dent", "birth_date": "1952-08-20",
        "partners": [1], "kids": [3, 5]
    },
    
    # Generation 2
    {
        "id": 3, "name": "Charles Dent", "birth_date": "1975-03-15",
        "parents": [1, 2], "partners": [4], "kids": [7]
    },
    {
        "id": 4, "name": "Elena Dent", "birth_date": "1978-11-02",
        "partners": [3], "kids": [7]
    },
    {
        "id": 5, "name": "Daisy Miller", "birth_date": "1980-01-25",
        "parents": [1, 2], "partners": [6], "kids": [8, 9, 10]
    },
    {
        "id": 6, "name": "George Miller", "birth_date": "1979-06-30",
        "partners": [5], "kids": [8, 9, 10]
    },

    # Generation 3
    {
        "id": 7, "name": "Finn Dent", "birth_date": "2005-12-12",
        "parents": [3, 4], "partners": [], "kids": []
    },
    {
        "id": 8, "name": "Holly Miller", "birth_date": "2010-04-05",
        "parents": [5, 6], "partners": [], "kids": []
    },
    {
        "id": 9, "name": "Ian Miller", "birth_date": "2012-09-18",
        "parents": [5, 6], "partners": [], "kids": []
    },
    {
        "id": 10, "name": "May Miller", "birth_date": "2012-09-09",
        "parents": [5, 6], "partners": [], "kids": []
    }
]

# Create the List[Person]
people: List[Person] = [Person.from_dict(p) for p in people_data]

import sys
# Example Test: Print family names and birth years
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    branches = FamilyBranches(people[0], people)
    
    scene = QGraphicsScene(0, 0, 1600, 600)
    view = QGraphicsView(scene)
    view.setRenderHint(QPainter.Antialiasing)

    # Add to scene
    branches.setPos(MARGIN, MARGIN)
    scene.addItem(branches)

    view.show()
    sys.exit(app.exec())