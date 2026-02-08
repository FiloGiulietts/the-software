from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QFileDialog
)
from PyQt6.QtCore import Qt
import os


class NewProjectDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("New Project")
        self.setMinimumWidth(400)

        self.project_name = QLineEdit()
        self.base_dir = QLineEdit()
        self.base_dir.setReadOnly(True)

        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self._browse)

        create_btn = QPushButton("Create")
        create_btn.clicked.connect(self.accept)
        create_btn.setDefault(True)

        layout = QVBoxLayout()

        layout.addWidget(QLabel("Project name"))
        layout.addWidget(self.project_name)

        layout.addWidget(QLabel("Project location"))

        dir_layout = QHBoxLayout()
        dir_layout.addWidget(self.base_dir)
        dir_layout.addWidget(browse_btn)
        layout.addLayout(dir_layout)

        layout.addWidget(create_btn, alignment=Qt.AlignmentFlag.AlignRight)

        self.setLayout(layout)

    def _browse(self):
        folder = QFileDialog.getExistingDirectory(self, "Select base directory")
        if folder:
            self.base_dir.setText(folder)

    def get_data(self):
        name = self.project_name.text().strip()
        folder = self.base_dir.text().strip()

        if not name or not folder:
            return None

        return folder, name

