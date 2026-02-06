import os


class ProjectManager:
    PROJECT_FILE = ".pup"

    def __init__(self):
        self.project_path = None

    def create_project(self, folder: str) -> bool:
        pup_path = os.path.join(folder, self.PROJECT_FILE)
        if os.path.exists(pup_path):
            return False

        with open(pup_path, "w") as f:
            f.write("plantuml project\n")

        return True

    def is_workspace(self, folder: str) -> bool:
        return os.path.exists(os.path.join(folder, self.PROJECT_FILE))

    def open_project(self, folder: str):
        self.project_path = folder
