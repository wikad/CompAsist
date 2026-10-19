import os
import time

import spotipy
from spotipy.oauth2 import SpotifyOAuth

import config


class SpotifyController:
    """Sterowanie Spotify przez Web API. Dane dostępowe czytane z .env."""

    SCOPE = "user-modify-playback-state user-read-playback-state"

    def __init__(self):
        if not (config.SPOTIFY_CLIENT_ID and config.SPOTIFY_CLIENT_SECRET):
            raise RuntimeError(
                "Brak SPOTIFY_CLIENT_ID / SPOTIFY_CLIENT_SECRET w pliku .env - komendy Spotify są wyłączone."
            )
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=config.SPOTIFY_CLIENT_ID,
            client_secret=config.SPOTIFY_CLIENT_SECRET,
            redirect_uri=config.SPOTIFY_REDIRECT_URI,
            scope=self.SCOPE,
            cache_path=str(config.SPOTIFY_CACHE_PATH),
        ))

    def _get_device(self):
        """Pomocnicza metoda do znajdowania aktywnego urządzenia."""
        devices = self.sp.devices()
        if devices['devices']:
            return devices['devices'][0]['id']
        return None

    # --- 1. FUNKCJA: ODPAL SPOTIFY ---
    def open_spotify(self):
        """Otwiera aplikację Spotify w systemie."""
        try:
            os.system("start spotify")
            time.sleep(3) # Czekamy chwilę na zainicjowanie procesu
            return "Otwieram aplikację Spotify."
        except Exception as e:
            return f"Nie udało się otworzyć Spotify: {e}"

    # --- 2. FUNKCJA: PUŚĆ (NAZWA LUB WZNAWIANIE) ---
    def play_music(self, query=None):
        """Puszcza konkretny utwór lub wznawia odtwarzanie."""
        try:
            device_id = self._get_device()
            
            # Jeśli nie znaleziono urządzenia, spróbuj otworzyć i poczekać
            if not device_id:
                self.open_spotify()
                time.sleep(4)
                device_id = self._get_device()
                if not device_id:
                    return "Otwórz Spotify na komputerze, abym mógł puszczać muzykę."

            if query:
                # Wyszukiwanie utworu
                results = self.sp.search(q=query, limit=1, type='track')
                if results['tracks']['items']:
                    track_uri = results['tracks']['items'][0]['uri']
                    track_name = results['tracks']['items'][0]['name']
                    self.sp.start_playback(device_id=device_id, uris=[track_uri])
                    return f"Odtwarzam: {track_name}"
                return f"Nie znalazłem utworu: {query}"
            else:
                # Wznowienie pauzy
                self.sp.start_playback(device_id=device_id)
                return "Wznawiam odtwarzanie."

        except Exception as e:
            return f"Błąd podczas odtwarzania: {e}"

    # --- 3. FUNKCJA: STOP / PAUZA ---
    def pause_music(self):
        """Zatrzymuje aktualnie odtwarzaną muzykę."""
        try:
            device_id = self._get_device()
            if device_id:
                self.sp.pause_playback(device_id=device_id)
                return "Zatrzymuję muzykę."
            return "Spotify nie jest aktywne."
        except Exception as e:
            # Często rzuca błąd, jeśli muzyka jest już zatrzymana
            return "Muzyka jest już zatrzymana lub wystąpił błąd."
    
    # --- 4. FUNKCJA: GŁOŚNOŚĆ ---
    def set_volume(self, change):
        """Pomocnicza metoda do zmiany głośności o określoną wartość (np. +10 lub -10)."""
        try:
            device_id = self._get_device()
            if not device_id:
                return "Nie znaleziono aktywnego urządzenia Spotify."

            # Pobieramy aktualny stan odtwarzania, aby znać obecną głośność
            current_playback = self.sp.current_playback()
            if current_playback and 'device' in current_playback:
                current_volume = current_playback['device']['volume_percent']
                
                # Obliczamy nową głośność w zakresie 0-100
                new_volume = max(0, min(100, current_volume + change))
                
                self.sp.volume(new_volume, device_id=device_id)
                
                status = "Pogłośniono" if change > 0 else "Ściszono"
                return f"{status} (Aktualnie: {new_volume}%)"
            
            return "Nie udało się pobrać aktualnej głośności."
        except Exception as e:
            return f"Błąd sterowania głośnością: {e}"

    def volume_up(self):
        """Zwiększa głośność o 10%."""
        return self.set_volume(10)

    def volume_down(self):
        """Zmniejsza głośność o 10%."""
        return self.set_volume(-10)