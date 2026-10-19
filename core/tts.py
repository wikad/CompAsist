import os
import torch
import numpy as np
import sounddevice as sd
from TTS.api import TTS

import config

class CoquiTTS:
    def __init__(self, voice_filename=config.VOICE_FILE):
        """
        Klasa zarządzająca generowaniem mowy (klonowaniem) i odtwarzaniem.
        """
        # 1. Próbka głosu do klonowania (folder voices/)
        self.voices_dir = str(config.VOICES_DIR)
        self.speaker_wav = os.path.join(self.voices_dir, voice_filename)
        if not os.path.exists(self.speaker_wav):
            raise FileNotFoundError(
                f"Brak próbki głosu: {self.speaker_wav}. Dodaj plik .wav do folderu voices/ (instrukcja w README)."
            )
        
        # 2. Wybór urządzenia (GPU przyspiesza generowanie o ok. 10x)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"--- Inicjalizacja Coqui TTS na: {self.device} ---")
        
        # 3. Ładowanie modelu XTTS v2 (Wczytuje się raz przy starcie)
        self.model_name = "tts_models/multilingual/multi-dataset/xtts_v2"
        self.tts = TTS(self.model_name).to(self.device)

    def speak(self, text):
        """
        Główna funkcja: bierze tekst, klonuje głos i od razu go odtwarza.
        """
        if not text or text.strip() == "":
            return

        print(f"🔊 Generowanie mowy: {text}")

        try:
            # Generowanie fali dźwiękowej bezpośrednio do pamięci RAM
            # Dzięki temu nie zużywamy dysku i jest szybciej
            wav = self.tts.tts(
                text=text,
                speaker_wav=self.speaker_wav,
                language="pl"
            )

            # Odtwarzanie dźwięku
            # XTTS v2 generuje dźwięk w częstotliwości 24000 Hz
            sd.play(np.array(wav), 24000)
            sd.wait() # Czekamy, aż asystent skończy mówić

        except Exception as e:
            print(f"❌ Błąd w module mowy: {e}")
            
    def _find_voice_file(self, filename):
        base_name = os.path.splitext(filename)[0] # Pozbywa się rozszerzenia, jeśli użytkownik je podał
        for ext in ['.wav', '.ogg']:
            path = os.path.join(self.voices_dir, base_name + ext)
            if os.path.exists(path):
                return path
        return None
    
    def change_voice(self, name_query):
        """
        Publiczna metoda do zmiany głosu. 
        Zwraca True przy sukcesie, False jeśli pliku nie ma.
        """
        new_path = self._find_voice_file(name_query)
        
        if new_path:
            self.speaker_wav = new_path
            print(f"✅ Głos zmieniony na: {os.path.basename(new_path)}")
            return True
        else:
            print(f"❌ Nie znaleziono pliku dla: {name_query} (.wav lub .ogg)")
            return False
        
        
# --- Przykład użycia (możesz to wywołać bezpośrednio py core/tts.py) ---
if __name__ == "__main__":
    # Inicjalizacja
    asystent_glos = CoquiTTS()
    
    # Próba mowy
    asystent_glos.speak("Test modułu mowy zakończony sukcesem. Wszystkie funkcje działają w jednym pliku.")