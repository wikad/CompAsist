"""
core/stt.py - Ciągłe nasłuchiwanie z sygnalizacją słowa kluczowego
"""
import json
import queue
import numpy as np
import sounddevice as sd
import vosk
from typing import Optional, Callable


class WakeWordDetector:
    """Nasłuchuje ciągle i sygnalizuje wykrycie słowa kluczowego"""
    
    def __init__(self, model_path: str = "models/vosk-model-small-pl-0.22", 
                 wake_word: str = "asystent", device_index: Optional[int] = None):
        """
        Args:
            model_path: Ścieżka do modelu Vosk
            wake_word: Słowo kluczowe (może być kilka oddzielonych |)
            device_index: Indeks mikrofonu (None = domyślny)
        """
        self.device_index = device_index
        self.wake_word = wake_word.lower()
        self.sample_rate = 16000
        self.audio_queue = queue.Queue()
        self.is_listening = False
        
        print(f"Ładowanie modelu Vosk: {model_path}")
        try:
            self.model = vosk.Model(model_path)
            print(f"Model załadowany | Słowo kluczowe: '{wake_word}'")
        except Exception as e:
            raise RuntimeError(f"Błąd ładowania modelu: {e}")
    
    def _audio_callback(self, indata, frames, time, status):
        """Przechwytuje dźwięk z mikrofonu"""
        self.audio_queue.put(bytes(indata))
    
    def _extract_clean_text(self, text_with_wakeword: str) -> str:
        """Wyodrębnia czysty tekst po słowie kluczowym"""
        text_lower = text_with_wakeword.lower()
        
        # Sprawdź wszystkie warianty słowa kluczowego
        wake_variants = self.wake_word.split('|')
        
        for wake in wake_variants:
            if wake in text_lower:
                # Znajdź pozycję słowa kluczowego
                pos = text_lower.find(wake)
                # Zwróć tekst PO słowie kluczowym
                clean = text_with_wakeword[pos + len(wake):].strip()
                return clean
        
        return ""  # Nie znaleziono słowa kluczowego
    
    def listen_forever(self, 
                      on_wakeword: Optional[Callable[[str], None]] = None,
                      on_command: Optional[Callable[[str], None]] = None):
        """
        Nieskończona pętla nasłuchująca
        
        Args:
            on_wakeword: Wywoływane przy wykryciu słowa kluczowego
            on_command: Opcjonalnie - wywoływane z tekstem po słowie kluczowym
        """
        print(f"\n🔊 NASŁUCHIWANIE ROZPOCZĘTE")
        print(f"   Słowo aktywujące: '{self.wake_word}'")
        print(f"   Naciśnij Ctrl+C aby zatrzymać\n")
        
        self.is_listening = True
        recognizer = vosk.KaldiRecognizer(self.model, self.sample_rate)
        
        try:
            with sd.RawInputStream(
                samplerate=self.sample_rate,
                blocksize=8000,
                dtype='int16',
                channels=1,
                callback=self._audio_callback,
                device=self.device_index
            ):
                while self.is_listening:
                    try:
                        # Pobierz dane audio
                        data = self.audio_queue.get(timeout=0.5)
                        
                        # Przetwórz przez Vosk
                        if recognizer.AcceptWaveform(data):
                            result = json.loads(recognizer.Result())
                            full_text = result.get("text", "").strip()
                            
                            if full_text:
                                print(f"📝 Rozpoznano: '{full_text}'")
                                
                                # Sprawdź czy jest słowo kluczowe
                                if any(wake in full_text.lower() 
                                      for wake in self.wake_word.split('|')):
                                    
                                    print(f"✅ WYKRYTO SŁOWO KLUCZOWE!")

                                    # Jeśli podano callback komend, wyodrębnij czysty tekst
                                    if on_wakeword:
                                        clean_text = self._extract_clean_text(full_text)
                                        if clean_text:
                                            on_wakeword(clean_text)
                                elif on_command:
                                    on_command(full_text)
                    except queue.Empty:
                        continue  # Brak danych - kontynuuj nasłuchiwanie
                        
        except KeyboardInterrupt:
            print("\n🛑 Zatrzymano przez użytkownika")
        except Exception as e:
            print(f"❌ Błąd: {e}")
        finally:
            self.is_listening = False
   
    def listen_for_speech(self) -> str:
        """Słucha mikrofonu do momentu rozpoznania pełnej frazy i zwraca tekst."""
        recognizer = vosk.KaldiRecognizer(self.model, self.sample_rate)
        
        # Czyścimy kolejkę, żeby nie przetwarzać starych dźwięków
        with self.audio_queue.mutex:
            self.audio_queue.queue.clear()

        print("🎤 Nasłuchiwanie odpowiedzi...")
        
        while True:
            try:
                # Pobierz dane audio z kolejki (audio_callback cały czas działa w tle)
                data = self.audio_queue.get(timeout=2.0)
                
                if recognizer.AcceptWaveform(data):
                    result = json.loads(recognizer.Result())
                    tekst = result.get("text", "").strip()
                    if tekst:
                        print(f"📝 Rozpoznano w czacie: '{tekst}'")
                        return tekst
                else:
                    # Opcjonalnie można sprawdzać PartialResult dla lepszego UX
                    pass
            except queue.Empty:
                print("... cisza ...")
                return ""
    def stop(self):
        """Zatrzymuje nasłuchiwanie"""
        self.is_listening = False
        print("⏹️  Zatrzymano nasłuchiwanie")


# Szybki test: python -m core.stt
if __name__ == "__main__":
    import config

    detector = WakeWordDetector(str(config.VOSK_MODEL_PATH), config.WAKE_WORD, config.MIC_DEVICE_INDEX)
    detector.listen_forever(
        on_wakeword=lambda text: print(f"   🗣️  Komenda: '{text}'"),
        on_command=lambda text: None,
    )
