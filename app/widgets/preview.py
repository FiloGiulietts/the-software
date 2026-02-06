from PyQt6.QtWidgets import QLabel, QScrollArea
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt


class PreviewWidget(QScrollArea):
    """Scroll area per mostrare il PNG generato"""
    def __init__(self):
        super().__init__()
        self.label = QLabel()
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setWidget(self.label)
        self.setWidgetResizable(True)

    def update_image(self, image_path: str):
        pixmap = QPixmap(image_path)
        self.label.setPixmap(pixmap)
