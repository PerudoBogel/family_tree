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

class FamilyRoots(QGraphicsItem):
    GEN_OFFSET: int = GraphPerson.HEIGHT + MARGIN_UNITS

    def __init__(self, reference_person: Person, people: List[Person], parent=None):
        super().__init__(parent)

        self.max_gen_num = 0
        self.gen_counter = 0
        self.ref_unit: FamilyUnit = self.build_unit(reference_person, people)

        self.y_offset = self.max_gen_num * self.GEN_OFFSET
        self.draw_unit(self.ref_unit,0)
        self.ref_unit.setPos(0,self.y_offset)
        self.ref_unit.draw_heads_connection()

    def build_unit(self, person: Person, people: List[Person]) -> FamilyUnit:
        unit: FamilyUnit = FamilyUnit(person, people, self)      

        units: List[FamilyUnit] = []
        for id in [head.parents[0] for head in unit.unit_head if head.parents]:
            for person in (person for person in people if id == person.id):
                self.gen_counter += 1
                units.append(self.build_unit(person, people))
                self.max_gen_num = max(self.max_gen_num, self.gen_counter)
                self.gen_counter -= 1
        unit.add_parent_units(units)
        return unit
    
    def draw_unit(self, unit: FamilyUnit, parent_offset_x: int) -> FamilyUnit:
        parents_width = 0
        offset_x = parent_offset_x
        unit.align(unit.get_width(with_parents=True))

        for par_unit in unit.parents_units:
            self.y_offset -= self.GEN_OFFSET
            par_unit.setPos(parent_offset_x, self.y_offset)
            self.draw_unit(par_unit,parent_offset_x)
            self.y_offset += self.GEN_OFFSET
            parent_offset_x += par_unit.get_width(with_parents=True) + MARGIN_UNITS
            parents_width += par_unit.get_width(with_parents=True)
        
        parents_width += (len(unit.parents_units) - 1) * MARGIN_UNITS if len(unit.parents_units) > 0 else 0
        
        if parents_width < unit.get_width(with_parents=True):
            parent_offset_x = offset_x + (unit.get_width(with_parents=True) - parents_width) / 2
            for parent_unit in unit.parents_units:
                parent_unit.setPos(parent_offset_x, parent_unit.y())
                parent_offset_x += parent_unit.get_width(with_parents=True) + MARGIN_UNITS
        
        for par_unit in unit.parents_units:
            par_unit.draw_heads_connection()
    
    def get_width(self):
        return self.ref_unit.get_width(with_parents=True)
    
    def get_height(self):
        return self.max_gen_num * GraphPerson.HEIGHT + (self.max_gen_num) * MARGIN_UNITS
    
    def boundingRect(self):
        # Expand height to accommodate potential parents rows
        return QRectF(0, 0, self.get_width(), self.get_height())

    def paint(self, painter, option, widget):
        # Optional: Add connectors or debug frames here
        pass

# class FamilyTree(QWidget):
    
people_data: List[Person] = [
    
    # Generation 0
    {
        "id": 13, "name": "A", "birth_date": "1950-05-12",
        "partners": [14], "kids": [1]
    },
    {
        "id": 14, "name": "B", "birth_date": "1952-08-20",
        "partners": [13], "kids": [1]
    },
    # {
    #     "id": 15, "name": "C", "birth_date": "1950-05-12",
    #     "partners": [16], "kids": [2]
    # },
    {
        "id": 16, "name": "D", "birth_date": "1952-08-20",
        "partners": [], "kids": [2]
    },
    {
        "id": 17, "name": "E", "birth_date": "1950-05-12",
        "partners": [18], "kids": [11]
    },
    {
        "id": 18, "name": "F", "birth_date": "1952-08-20",
        "partners": [17], "kids": [11]
    },
    {
        "id": 19, "name": "G", "birth_date": "1950-05-12",
        "partners": [20], "kids": [12]
    },
    {
        "id": 20, "name": "H", "birth_date": "1952-08-20",
        "partners": [19], "kids": [12]
    },

    # Generation 1
    {
        "id": 1, "name": "Arthur Dent", "birth_date": "1950-05-12",
        "parents": [13, 14], "partners": [2], "kids": [3, 5]
    },
    {
        "id": 2, "name": "Beryl Dent", "birth_date": "1952-08-20",
        "parents": [16], "partners": [1], "kids": [3, 5]
    },
    {
        "id": 11, "name": "Arthur Rent", "birth_date": "1950-05-12",
        "parents": [17, 18], "partners": [12], "kids": [6]
    },
    {
        "id": 12, "name": "Beryl Rent", "birth_date": "1952-08-20",
        "parents": [19, 20], "partners": [11], "kids": [6]
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
        "partners": [5], "parents": [11, 12], "kids": [8, 9, 10]
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
    
    branches = FamilyRoots(people[-1], people)
    
    scene = QGraphicsScene(0, 0, 1600, 600)
    view = QGraphicsView(scene)
    view.setRenderHint(QPainter.Antialiasing)

    # Add to scene
    branches.setPos(MARGIN, MARGIN)
    scene.addItem(branches)

    view.show()
    sys.exit(app.exec())