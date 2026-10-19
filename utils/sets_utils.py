import os
import json
import subprocess

import config

class AppSetManager:
    def __init__(self, sets_path=config.APP_SETS_FILE):
        self.sets_path = sets_path
        self.app_sets = self._load_sets()

    def _load_sets(self):
        if os.path.exists(self.sets_path):
            try:
                with open(self.sets_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"❌ Błąd ładowania setów: {e}")
                return {}
        return {}

    def _save_sets(self):
        os.makedirs(os.path.dirname(self.sets_path), exist_ok=True)
        with open(self.sets_path, 'w', encoding='utf-8') as f:
            json.dump(self.app_sets, f, ensure_ascii=False, indent=4)

    def run_set(self, set_name, assistant_obj, voice):
        if not set_name:
            voice.speak("Nie podałeś nazwy zestawu.")
            return "Błąd: Brak nazwy" # Zwracamy string, nie bool

        set_name = set_name.lower().strip()

        if set_name in self.app_sets:
            voice.speak(f"Uruchamiam zestaw {set_name}.")
            for app in self.app_sets[set_name]:
                subprocess.Popen(f"start {app}", shell=True)
            return f"Uruchomiono zestaw {set_name}" # Zwracamy string

        # Jeśli nie istnieje - stwórz nowy
        self._create_new_set(set_name, assistant_obj, voice)
        return f"Utworzono zestaw {set_name}" # Zwracamy string

    def _create_new_set(self, set_name, assistant_obj, voice):
        voice.speak(f"Nie znam zestawu {set_name}. Jakie aplikacje mam do niego dodać? Powiedz gotowe, aby zapisać.")
        
        new_apps = []
        while True:
            app_input = assistant_obj.listen_for_speech()
            if app_input:
                app_clean = app_input.lower().strip()
                if app_clean in ["gotowe", "koniec", "zapisz"]:
                    break
                
                new_apps.append(app_clean)
                voice.speak(f"Dodałam {app_clean}. Dalej?")
        
        if new_apps:
            self.app_sets[set_name] = new_apps
            self._save_sets()
            voice.speak(f"Zestaw {set_name} gotowy.")
            return True
        
        voice.speak("Anulowano tworzenie zestawu.")
        return False