import json
import os
import webbrowser

import config


class SteamLauncher:
    """Uruchamia i zamyka gry Steam. Lista gier: data/games.json"""

    def __init__(self, games_path=config.GAMES_FILE):
        # Nazwa mówiona -> (ID gry w Steam, nazwa procesu .exe)
        self.games = {}
        if os.path.exists(games_path):
            with open(games_path, "r", encoding="utf-8") as f:
                self.games = {name: (g["steam_id"], g["process"]) for name, g in json.load(f).items()}

    def launch(self, game_name):
        game_name = game_name.lower().strip()
        target = self.games.get(game_name)
        if not target: return False
        
        steam_id = target[0] # Pobieramy ID
        webbrowser.open(f"steam://run/{steam_id}")
        return True

    def close_all_games(self):
        """Próbuje zamknąć wszystkie zdefiniowane gry"""
        any_closed = False
        
        # Pobieramy unikalne nazwy procesów .exe z bazy
        process_names = set(data[1] for data in self.games.values())
        
        for exe in process_names:
            # /F - wymuszenie, /IM - nazwa obrazu, /T - procesy potomne
            # Przekierowujemy wyjście do NULL, żeby nie śmiecić w konsoli
            exit_code = os.system(f"taskkill /F /IM {exe} /T >nul 2>&1")
            if exit_code == 0:
                any_closed = True
        
        return any_closed

    def _handle_game_logic(self, query, voice):
        if not query:
            voice.speak("Jaką grę chcesz włączyć?")
            return

        success = self.launch(query)
        if success:
            voice.speak(f"Odpalam {query}. Powodzenia!")
        else:
            voice.speak(f"Nie mam na liście gry o nazwie {query}.")
    
    def _handle_close_game(self, voice):
        voice.speak("Zamykam gry.")
        success = self.close_all_games()
        
        if success:
            voice.speak("Gry zostały zamknięte.")
        else:
            # Jeśli nic nie znalazł, po prostu nic nie mówi lub mówi, że czysto
            print("Nie znaleziono aktywnych procesów gier do zamknięcia.")