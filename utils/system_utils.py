import os
import webbrowser
from datetime import datetime
from urllib.parse import quote_plus

import pyautogui
from pycaw.pycaw import AudioUtilities

import config
from .vs_logic import ProjectManager


class SystemController:
    def __init__(self):
        self.project_manager = ProjectManager()

    def _stop_assistant(self, assistant):
        if assistant:
            assistant.stop()
        return "Zamykam się. Do usłyszenia!"

    def open_browser(self, url="https://www.google.com"):
        webbrowser.open(url)
        return "Otwieram przeglądarkę."

    def search_youtube(self, query):
        if query:
            url = f"https://www.youtube.com/results?search_query={quote_plus(query)}"
            webbrowser.open(url)
            return f"Szukam {query} na YouTube."
        webbrowser.open("https://www.youtube.com")
        return "Otwieram YouTube."
    
    def set_chrome_volume(self, increase=True):
        sessions = AudioUtilities.GetAllSessions()
        for session in sessions:
            if session.Process and session.Process.name() == "chrome.exe":
                volume = session.SimpleAudioVolume
                current = volume.GetMasterVolume()
                new_vols = min(1.0, current + 0.1) if increase else max(0.0, current - 0.1)
                volume.SetMasterVolume(new_vols, None)
                return "Zmieniono głośność Chrome."
        return "Nie znaleziono procesów Chrome."

    def search_google(self, query):
        if query:
            url = f"https://www.google.com/search?q={quote_plus(query)}"
            webbrowser.open(url)
            return f"Wyszukuję {query} w Google."
        return "Co mam sprawdzić w Google?"

    def get_time(self):
        return f"Jest godzina {datetime.now().strftime('%H:%M')}."

    def get_date(self):
        return f"Dziś jest {datetime.now().strftime('%d.%m.%Y')}."

    def open_steam(self):
        os.system("start steam://open/main")
        return "Uruchamiam Steam."

    def open_discord(self):
        os.system("start discord://")
        return "Uruchamiam Discord."

    def open_messenger(self):
        chrome_path = r'"C:\Program Files\Google\Chrome\Application\chrome.exe"'
        url = "https://www.messenger.com/"
        os.system(f'start {chrome_path} "{url}"')
        return "Otwieram Messenger."
    
    def _handle_vscode_logic(self, query, assistant_obj, voice):
        pm = self.project_manager # instancja klasy ProjectManager

        # 1. Brak nazwy w komendzie
        if not query:
            voice.speak("Jasne, jaki projekt chcesz otworzyć?")
            query = assistant_obj.listen_for_speech()
            if not query: return "Nie usłyszałam nazwy."

        project_name = query.lower().strip()
        
        # 2. Inteligentne szukanie (Urozmaicenie)
        match = pm.find_best_match(project_name)
        
        if match:
            if match != project_name:
                voice.speak(f"Nie znalazłam projektu {project_name}, ale mam {match}. Czy o ten chodzi?")
                confirm = assistant_obj.listen_for_speech()
                if "tak" not in confirm.lower(): return "Anulowano otwarcie."
            
            return pm.open_in_vs_code(match)

        # 3. Projekt nie istnieje - propozycja stworzenia
        voice.speak(f"Nie masz jeszcze projektu {project_name}. Czy chcesz go stworzyć w folderze głównym?")
        decision = assistant_obj.listen_for_speech()

        if any(word in decision.lower() for word in ["tak", "dawaj", "pewnie", "jasne"]):
            return pm.create_project(project_name)
        
        return "Dobrze, w takim razie nic nie otwieram."

    def _handle_notepad_logic(self, assistant_obj, voice):
        notes_dir = str(config.NOTES_DIR)
        os.makedirs(notes_dir, exist_ok=True) # Tworzy folder jeśli nie istnieje

        # 1. Pytanie o nazwę pliku
        voice.speak("Jak ma się nazywać ten notatnik?")
        file_name = assistant_obj.listen_for_speech()
        
        if not file_name:
            voice.speak("Nie usłyszałam nazwy. Przerywam.")
            return

        full_path = os.path.join(notes_dir, f"{file_name.strip()}.txt")

        # 2. Dyktowanie treści
        voice.speak(f"Tworzę notatnik {file_name}. Słucham treści. Powiedz stop, aby zakończyć.")
        
        with open(full_path, "a", encoding="utf-8") as f:
            while True:
                text = assistant_obj.listen_for_speech()
                if text:
                    text_lower = text.lower().strip()
                    if text_lower in ["stop", "koniec", "zakończ"]:
                        break
                    
                    f.write(text + "\n")
                    f.flush()
                    print(f"📝 Dopisano: {text}")

        voice.speak("Notatka została zapisana.")

    def _read_notepad_logic(self, assistant_obj, voice):
        notes_dir = str(config.NOTES_DIR)
        
        voice.speak("Który notatnik mam przeczytać?")
        file_name = assistant_obj.listen_for_speech()
        
        if not file_name:
            return

        full_path = os.path.join(notes_dir, f"{file_name.strip()}.txt")

        if os.path.exists(full_path):
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()
                if content.strip():
                    voice.speak(f"Oto treść notatnika {file_name}:")
                    voice.speak(content)
                else:
                    voice.speak("Ten notatnik jest pusty.")
        else:
            voice.speak(f"Nie znalazłam notatnika o nazwie {file_name}.")

    def _take_screenshot(self, voice):
        ss_dir = str(config.SCREENSHOTS_DIR)
        
        # Tworzymy folder, jeśli nie istnieje
        if not os.path.exists(ss_dir):
            os.makedirs(ss_dir)
            
        # Generujemy nazwę pliku na podstawie daty i czasu
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_path = os.path.join(ss_dir, f"screenshot_{timestamp}.png")
        
        try:
            # Wykonanie i zapisanie zrzutu ekranu
            screenshot = pyautogui.screenshot()
            screenshot.save(file_path)
            
            print(f"📸 Screenshot zapisany: {file_path}")
            if voice:
                voice.speak("Zrobiłem zrzut ekranu.")
        except Exception as e:
            print(f"❌ Błąd podczas robienia screenshotu: {e}")
            if voice:
                voice.speak("Wystąpił błąd podczas robienia zdjęcia ekranu.")