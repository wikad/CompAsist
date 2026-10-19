import json
import os

import ollama

import config

# Ile ostatnich wiadomości wysyłamy do modelu jako kontekst
MAX_CONTEXT_MESSAGES = 20

class ChatBot:
    def __init__(self, model_name=config.OLLAMA_MODEL):
        self.model_name = model_name
        self.memory_file = str(config.CHAT_HISTORY_FILE)
        self.history = self._load_history()

    def _load_history(self):
        """Metoda wewnętrzna do ładowania pamięci."""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return []
        return []

    def _save_history(self):
        """Metoda wewnętrzna do zapisu pamięci."""
        os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
        with open(self.memory_file, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, ensure_ascii=False, indent=4)

    def get_response(self, user_text):
        """Funkcja, która przyjmuje tekst i zwraca odpowiedź modelu."""
        self.history.append({'role': 'user', 'content': user_text})
        
        try:
            response = ollama.chat(model=self.model_name, messages=self.history[-MAX_CONTEXT_MESSAGES:])
            model_response = response['message']['content']
            
            # Dodaj odpowiedź do historii i zapisz
            self.history.append({'role': 'assistant', 'content': model_response})
            self._save_history()
            
            return model_response
        except Exception as e:
            return f"Błąd komunikacji z Ollama: {e}"

    def uruchom(self):
        """Metoda do interaktywnego czatu w konsoli."""
        print(f"--- Sesja aktywna (Model: {self.model_name}) ---")
        print(f"Wczytano wiadomości: {len(self.history)}")
        
        while True:
            wejscie = input("Ty: ")
            if wejscie.lower() in ['exit', 'quit']:
                break
            
            odpowiedz = self.get_response(wejscie)
            print(f"\nRobot: {odpowiedz}\n")

if __name__ == "__main__":
    # Testowanie klasy bezpośrednio w nlp.py
    bot = ChatBot()
    bot.uruchom()