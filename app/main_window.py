import os
from PyQt6.QtWidgets import (
    QMainWindow, QFileDialog, QSplitter, QMessageBox, QTabWidget
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction, QKeySequence

from app.project_manager import ProjectManager

from app.widgets.file_tree import FileTreeWidget
from app.widgets.editor import EditorWidget
from app.widgets.preview import PreviewWidget
from app.plantuml_renderer import AsyncPlantUMLPreview
from app.widgets.topbar import TopBar

from app.dialogs.new_project_dialog import NewProjectDialog


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PlantUML Editor")
        self.resize(1300, 800)

        self.project_manager = ProjectManager()
        self.open_editors = {}  # path -> EditorWidget

        # =========================
        # Renderer asincrono
        # =========================
        self.preview = PreviewWidget()
        self.renderer = AsyncPlantUMLPreview(
            jar_path="tools/plantuml.jar",
            preview_widget=self.preview
        )

        self.topbar = TopBar(self)
        self.setMenuBar(self.topbar.get_menu_bar())

        self._create_layout()
        self._connect_signals()

        self.render_timer = QTimer()
        self.render_timer.setInterval(500)  # debounce per live preview
        self.render_timer.setSingleShot(True)
        self.render_timer.timeout.connect(self.render_preview)


    # =========================
    # LAYOUT
    # =========================
    def _create_layout(self):
        main_splitter = QSplitter(Qt.Orientation.Horizontal)

        # File tree
        self.file_tree = FileTreeWidget()
        main_splitter.addWidget(self.file_tree)

        # Tab widget editor
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        main_splitter.addWidget(self.tab_widget)

        # Preview widget già creato
        main_splitter.addWidget(self.preview)

        # Imposta proporzioni iniziali
        total = 1200
        main_splitter.setSizes([total // 6, total // 3, total // 2])

        self.setCentralWidget(main_splitter)

    def _connect_signals(self):
        self.file_tree.itemClicked.connect(self.open_file)
        self.tab_widget.currentChanged.connect(self.schedule_render)

    # =========================
    # FILE HANDLING
    # =========================
    def open_file(self, item, column):
        path = item.data(0, Qt.ItemDataRole.UserRole)
        if not path or not os.path.exists(path):
            return

        if path in self.open_editors:
            index = self.tab_widget.indexOf(self.open_editors[path])
            self.tab_widget.setCurrentIndex(index)
            return

        editor = EditorWidget()
        editor.load_file(path)
        editor.textChanged.connect(self.schedule_render)
        editor.textChanged.connect(lambda: self.mark_tab_dirty(editor))

        self.open_editors[path] = editor
        filename = os.path.basename(path)
        self.tab_widget.addTab(editor, filename)
        self.tab_widget.setCurrentWidget(editor)

        self.schedule_render()

    def save_current_file(self):
        editor = self.tab_widget.currentWidget()
        if not editor or not editor.current_file:
            return
        editor.save()
        index = self.tab_widget.currentIndex()
        filename = os.path.basename(editor.current_file)
        self.tab_widget.setTabText(index, filename)

    def mark_tab_dirty(self, editor):
        index = self.tab_widget.indexOf(editor)
        if index != -1:
            tab_text = self.tab_widget.tabText(index)
            if not tab_text.startswith("*"):
                self.tab_widget.setTabText(index, "*" + tab_text)

    def close_tab(self, index):
        editor = self.tab_widget.widget(index)
        if editor:
            tab_text = self.tab_widget.tabText(index)
            if tab_text.startswith("*"):
                res = QMessageBox.question(
                    self,
                    "Unsaved Changes",
                    "File non salvato. Vuoi salvarlo prima di chiudere?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if res == QMessageBox.StandardButton.Yes:
                    editor.save()
            path = editor.current_file
            if path in self.open_editors:
                del self.open_editors[path]

        self.tab_widget.removeTab(index)

    # =========================
    # PREVIEW ASINCRONA
    # =========================
    def schedule_render(self):
        """Debounce: avvia render asincrono dopo pochi ms di inattività"""
        self.render_timer.start()

    def render_preview(self):
        """Chiama il renderer asincrono"""
        editor = self.tab_widget.currentWidget()
        if not editor:
            return

        text = editor.toPlainText().strip()
        if not text:
            self.preview.update_image(None)
            editor.clear_error_highlight()
            self.statusBar().clearMessage()
            return

        self.renderer.render(text)  # aggiorna preview in background

    # =========================
    # PROJECT HANDLING
    # =========================
    def create_project(self):
        dialog = NewProjectDialog(self)
        if dialog.exec() != dialog.DialogCode.Accepted:
            return

        result = dialog.get_data()
        if not result:
            QMessageBox.warning(self, "Error", "Invalid project data")
            return

        folder, name = result
        tsp_path = os.path.join(folder, f"{name}.tsp")

        if os.path.exists(tsp_path):
            QMessageBox.warning(self, "Error", "Project already exists in this folder")
            return

        if not self.project_manager.create_project(tsp_path, name):
            QMessageBox.warning(self, "Error", "Unable to create project")
            return

        self.load_project(folder)

    def open_project(self):
        tsp_file, _ = QFileDialog.getOpenFileName(
            self,
            "Open Project",
            "",
            "TSP Project (*.tsp)"
        )

        if not tsp_file:
            return

        folder = os.path.dirname(tsp_file)

        if not self.project_manager.is_workspace(folder):
            QMessageBox.warning(self, "Error", "Invalid workspace")
            return

        self.load_project(folder)


    def load_project(self, folder):
        self.project_manager.open_project(folder)
        self.file_tree.load_puml_files(folder)
