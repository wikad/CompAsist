import os
import json
from datetime import datetime
import difflib

import config

class ProjectManager:
    def __init__(self, base_dir=config.PROJECTS_DIR, projects_db=config.PROJECTS_DB):
        self.base_dir = base_dir
        self.projects_db = projects_db
        self.projects = self._load_db()

    def _load_db(self):
        if os.path.exists(self.projects_db):
            with open(self.projects_db, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def _save_db(self):
        os.makedirs(os.path.dirname(self.projects_db), exist_ok=True)
        with open(self.projects_db, 'w', encoding='utf-8') as f:
            json.dump(self.projects, f, ensure_ascii=False, indent=4)

    def find_best_match(self, name):
        """Urozmaicenie: Szuka najbardziej podobnej nazwy projektu."""
        matches = difflib.get_close_matches(name, self.projects.keys(), n=1, cutoff=0.6)
        return matches[0] if matches else None

    def open_in_vs_code(self, project_name):
        path = self.projects[project_name]["path"]
        # Aktualizacja metadanych (urozmaicenie)
        self.projects[project_name]["last_opened"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._save_db()
        
        os.system(f'start code "{path}"')
        return f"Otwieram {project_name}."

    def create_project(self, project_name):
        path = os.path.join(self.base_dir, project_name)
        os.makedirs(path, exist_ok=True)
        self.projects[project_name] = {
            "path": path,
            "created_at": datetime.now().strftime("%Y-%m-%d"),
            "last_opened": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self._save_db()
        os.system(f'start code "{path}"')
        return f"Utworzono i otwarto nowy projekt: {project_name}."