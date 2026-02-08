import os
import json


class ProjectManager:
    def __init__(self):
        self.project_dir = None
        self.project_file = None
        self.project_data = None

    def create_project(self, tsp_path: str, name: str) -> bool:
        try:
            data = {
                "name": name,
                "version": 1
            }

            with open(tsp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)

            return True

        except Exception as e:
            print("Create project error:", e)
            return False

    def is_workspace(self, folder: str) -> bool:
        return any(f.endswith(".tsp") for f in os.listdir(folder))

    def open_project(self, folder: str):
        tsp_files = [f for f in os.listdir(folder) if f.endswith(".tsp")]
        if not tsp_files:
            raise RuntimeError("Invalid workspace")

        self.project_dir = folder
        self.project_file = os.path.join(folder, tsp_files[0])

        with open(self.project_file, "r", encoding="utf-8") as f:
            self.project_data = json.load(f)
