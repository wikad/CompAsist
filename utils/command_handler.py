import json

import config
from . import audio_utils
from . import sets_utils
from . import steam_controller
from . import system_utils


class _SpotifyDisabled:
    """Zastępuje SpotifyController, gdy brak danych dostępowych w .env."""

    def __getattr__(self, _name):
        return lambda *args, **kwargs: "Spotify nie jest skonfigurowane. Uzupełnij plik .env."


class CommandExecutor:
    def __init__(self, json_path=config.COMMANDS_FILE):
        self.json_path = json_path
        self.commands = self._load_commands()
        self.system = system_utils.SystemController()
        self.app_manager = sets_utils.AppSetManager()
        self.steam = steam_controller.SteamLauncher()
        try:
            self.spotify = audio_utils.SpotifyController()
        except Exception as e:
            print(f"⚠️  {e}")
            self.spotify = _SpotifyDisabled()

    # === ŁADOWANIE I ZAPIS PLIKÓW ===
    def _load_commands(self):
        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Błąd ładowania commands.json: {e}")
            return {}
    
    # === WYSZUKIWANIE KOMEND ===
    def find_command_and_query(self, user_text):
        user_text_lower = user_text.lower().strip()
        for cmd_name, triggers in self.commands.items():
            for trigger in triggers:
                trigger_lower = trigger.lower()
                if user_text_lower.startswith(trigger_lower):
                    query = user_text_lower.replace(trigger_lower, "", 1).strip()
                    return cmd_name, query
        return None, None
    
    # === WYKONYWANIE KOMEND ===
    def execute(self, command_name, query=None, assistant_obj=None, voice=None):
        actions = {
            # Spotify
            "volume_up": lambda: self.spotify.volume_up(),
            "volume_down": lambda: self.spotify.volume_down(),
            "play_music": lambda: self.spotify.play_music(query),
            "open_spotify": lambda: self.spotify.open_spotify(),
            "stop_music": lambda: self.spotify.pause_music(),
            
            "volume_up_chrome": lambda: self.system.set_chrome_volume(increase=True),
            "volume_down_chrome": lambda: self.system.set_chrome_volume(increase=False),
            "search_yt": lambda: self.system.search_youtube(query),
            "google": lambda: self.system.search_google(query),
            "open_browser": self.system.open_browser,

            "take_screenshot": lambda: self.system._take_screenshot(voice),
            "time": self.system.get_time,
            "date": self.system.get_date,
            "open_steam": self.system.open_steam,
            "open_discord": self.system.open_discord,
            "open_messenger": self.system.open_messenger,
                        
            "app_set": lambda: self.app_manager.run_set(query, assistant_obj, voice),
            
            "create_note": lambda: self.system._handle_notepad_logic(assistant_obj, voice),
            "read_note": lambda: self.system._read_notepad_logic(assistant_obj, voice),

            # Specyficzne logiki asystenta (zostają tutaj, bo wymagają voice/assistant_obj)
            "open_vscode": lambda: self.system._handle_vscode_logic(query, assistant_obj, voice),
            "END": lambda: self.system._stop_assistant(assistant_obj),
            "wielkie_dzieki": lambda: voice.speak("Nie ma za co!"),
            "change_voice": lambda: self._handle_voice_change_logic(query, voice),
            "launch_game": lambda: self.steam._handle_game_logic(query, voice),
            "close_game": lambda: self.steam._handle_close_game(voice),
        }
        
        if command_name in actions:
            action = actions[command_name]
            return action() if callable(action) else action
        return f"Nieznana komenda: {command_name}"


    def _handle_voice_change_logic(self, query, voice_obj):
        if not query:
            voice_obj.speak("Nie podałeś nazwy głosu.")
            return

        # Czyścimy tekst (np. " Marek " -> "marek")
        voice_name = query.strip().lower()

        success = voice_obj.change_voice(voice_name)
        
        if success:
            voice_obj.speak(f"Głos został zmieniony na {voice_name}")
        else:
            voice_obj.speak(f"Niestety nie mam w bazie głosu o nazwie {voice_name}")