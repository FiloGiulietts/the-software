from PyQt6.QtWidgets import QMenuBar
from PyQt6.QtGui import QAction, QKeySequence


class TopBar:
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.menu_bar = QMenuBar(main_window)

        self._create_menus()
        self._create_shortcuts()


    def _create_menus(self):
        project_menu = self.menu_bar.addMenu("Project")

        new_project_action = QAction("New Project", self.main_window)
        new_project_action.triggered.connect(self.main_window.create_project)

        open_project_action = QAction("Open Project", self.main_window)
        open_project_action.triggered.connect(self.main_window.open_project)

        project_menu.addAction(new_project_action)
        project_menu.addAction(open_project_action)


    def _create_shortcuts(self):
        save_action = QAction("Save", self.main_window)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self.main_window.save_current_file)

        # Le shortcut globali vanno aggiunte al MainWindow
        self.main_window.addAction(save_action)


    def get_menu_bar(self):
        return self.menu_bar
