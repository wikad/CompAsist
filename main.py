"""
Punkt wejścia asystenta głosowego.

Przepływ: mikrofon -> Vosk (STT) -> dopasowanie komendy -> akcja systemowa
                                    `-> brak komendy -> rozmowa z LLM (Ollama)
          odpowiedź -> Coqui XTTS (TTS) -> głośnik
"""
import config
import core.nlp
import core.stt
import core.tts
import utils.command_handler

EXIT_WORDS = ("wyjdź", "koniec", "do widzenia", "stop")

listener = core.stt.WakeWordDetector(
    model_path=str(config.VOSK_MODEL_PATH),
    wake_word=config.WAKE_WORD,
    device_index=config.MIC_DEVICE_INDEX,
)
command = utils.command_handler.CommandExecutor()
chatbot = core.nlp.ChatBot(model_name=config.OLLAMA_MODEL)
voice = core.tts.CoquiTTS(voice_filename=config.VOICE_FILE)


def run_command(text: str) -> bool:
    """Próbuje wykonać komendę. Zwraca True, jeśli tekst był komendą."""
    cmd, query = command.find_command_and_query(text)
    if not cmd:
        return False
    result = command.execute(cmd, query=query, assistant_obj=listener, voice=voice)
    if isinstance(result, str):
        voice.speak(result)
    return True


def conversation(first_message: str):
    """Tryb rozmowy z LLM, dopóki użytkownik go nie zakończy."""
    print("💬 Tryb rozmowy")
    text = first_message
    while True:
        voice.speak(chatbot.get_response(text))

        text = listener.listen_for_speech()
        if not text or any(word in text.lower() for word in EXIT_WORDS):
            print("👋 Koniec rozmowy")
            return
        # W trakcie rozmowy nadal można wydać komendę
        if run_command(text):
            return


def on_wakeword(text: str):
    """Tekst wypowiedziany po słowie aktywującym."""
    if not run_command(text):
        conversation(text)


def on_speech(text: str):
    """Tekst bez słowa aktywującego: wykonujemy tylko znane komendy."""
    run_command(text)


def main():
    print("🚀 Asystent gotowy. Nasłuchuję...")
    listener.listen_forever(on_wakeword=on_wakeword, on_command=on_speech)


if __name__ == "__main__":
    main()
