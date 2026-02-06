import os
from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor, QBrush


class FileTreeWidget(QTreeWidget):
    def __init__(self):
        super().__init__()
        self.setHeaderHidden(True)

        # =========================
        # STILE DARK
        # =========================
        font = QFont("Fira Code", 11)
        self.setFont(font)

        # Colori sfondo e selezione
        self.setStyleSheet("""
            QTreeWidget {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: none;
            }
            QTreeWidget::item:selected {
                background-color: #264f78;
                color: #ffffff;
            }
        """)

        # Spaziatura e indent
        self.setIndentation(15)
        self.setUniformRowHeights(True)

    def load_puml_files(self, project_path: str):
        self.clear()

        for root, _, files in os.walk(project_path):
            for file in files:
                if file.endswith(".puml"):
                    full_path = os.path.join(root, file)
                    # Mostra solo il nome del file
                    item = QTreeWidgetItem(self, [file])
                    # Salva il percorso completo in UserRole
                    item.setData(0, Qt.ItemDataRole.UserRole, full_path)
                    # Opzionale: colore dei file
                    item.setForeground(0, QBrush(QColor("#d4d4d4")))
