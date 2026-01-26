from PySide6.QtWidgets import (
    QApplication, QWidget, QListWidget, QLineEdit, QTextEdit,
    QPushButton, QFileDialog, QLabel, QHBoxLayout, QVBoxLayout,
    QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsTextItem,
    QMessageBox, QComboBox, QListWidgetItem, QFrame
)
from PySide6.QtGui import QPen, QBrush, QColor, QFont, QPainter
from PySide6.QtCore import Qt
from person import Person

class GraphPerson(QGraphicsRectItem):
    WIDTH = 150
    HEIGHT = 80

    def __init__(self, person: Person, parent=None):
        # Initialize with fixed dimensions
        super().__init__(0, 0, self.WIDTH, self.HEIGHT, parent)
        
        self.person = person
        
        # 1. Aesthetics (Wood and Moss)
        self.setBrush(QBrush(QColor("#F7F1DE"))) # Background
        self.setPen(QPen(QColor("#4B352A"), 2))   # Border

        # 2. Name Text (Bold Green)
        self.name_item = QGraphicsTextItem(person.name, self)
        self.name_item.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.name_item.setDefaultTextColor(QColor("#2E6F40"))
        self.name_item.setTextWidth(self.WIDTH)
        
        # Center alignment using QTextOption
        name_opt = self.name_item.document().defaultTextOption()
        name_opt.setAlignment(Qt.AlignCenter)
        self.name_item.document().setDefaultTextOption(name_opt)
        self.name_item.setPos(0, 10)

        # 3. Details Text (Brown)
        detail_text = f"{person.birth_date}\n({person.birth_year})"
        self.detail_item = QGraphicsTextItem(detail_text, self)
        self.detail_item.setFont(QFont("Segoe UI", 8))
        self.detail_item.setDefaultTextColor(QColor("#654321"))
        self.detail_item.setTextWidth(self.WIDTH)
        
        detail_opt = self.detail_item.document().defaultTextOption()
        detail_opt.setAlignment(Qt.AlignCenter)
        self.detail_item.document().setDefaultTextOption(detail_opt)
        self.detail_item.setPos(0, 38)

    def paint(self, painter, option, widget):
        """Override to draw rounded corners as per original styling."""
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(self.brush())
        painter.setPen(self.pen())
        painter.drawRoundedRect(self.rect(), 8, 8)
        
import sys
# --- Example Usage ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    scene = QGraphicsScene(0, 0, 800, 600)
    view = QGraphicsView(scene)
    view.setRenderHint(QPainter.Antialiasing)

    # Create Person from dataclass
    p1 = Person(id=1, name="Jan Kowalski", birth_date="1950-05-12")
    p2 = Person.from_dict({"id": 2, "name": "Anna Nowak", "birth_date": "1982-11-23"})

    # Add to scene
    item1 = GraphPerson(p1)
    item1.setPos(50, 50)
    scene.addItem(item1)

    item2 = GraphPerson(p2)
    item2.setPos(250, 50)
    scene.addItem(item2)

    view.show()
    sys.exit(app.exec())