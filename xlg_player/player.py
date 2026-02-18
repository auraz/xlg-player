"""Player control via Unix socket communication."""

import os
import re
import socket
import subprocess
from pathlib import Path

from applemusicpy import AppleMusic

from xlg_player.config import get_config

PLAYER_SOCKET = "/tmp/xlg-player.sock"


def send_to_player(command: str) -> str:
    """Send command to running player via Unix socket, return response."""
    try:
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.settimeout(2.0)
        sock.connect(PLAYER_SOCKET)
        sock.sendall(command.encode())
        response = sock.recv(1024).decode().strip()
        sock.close()
        return response
    except (socket.error, OSError):
        return ""


def kill_existing_players() -> None:
    """Kill any existing xlg-player processes."""
    subprocess.run(["pkill", "-f", "xlg-player"], stderr=subprocess.DEVNULL)


def pause() -> str:
    """Pause playback."""
    return "Paused" if send_to_player("pause") == "OK" else "Player not running"


def resume() -> str:
    """Resume playback."""
    return "Resumed" if send_to_player("resume") == "OK" else "Player not running"


def toggle() -> str:
    """Toggle play/pause."""
    return "Toggled" if send_to_player("toggle") == "OK" else "Player not running"


def skip() -> str:
    """Skip to next track."""
    return "Skipped" if send_to_player("skip") == "OK" else "Player not running"


def previous() -> str:
    """Go to previous track."""
    return "Previous" if send_to_player("previous") == "OK" else "Player not running"


def volume(level: str) -> str:
    """Set or adjust volume (0-100, +10, -10)."""
    return f"Volume: {level}" if send_to_player(f"volume {level}") == "OK" else "Player not running"


def status() -> str:
    """Get player status as JSON."""
    response = send_to_player("status")
    return response if response else '{"error":"Player not running"}'


def favorite() -> str:
    """Toggle favorite on current track."""
    return "Favorited" if send_to_player("favorite") == "OK" else "Player not running"


def play(query: str) -> str:
    """Play music via Apple Music catalog using native MusicKit player."""
    key_id = get_config("APPLE_MUSIC_KEY_ID")
    team_id = get_config("APPLE_MUSIC_TEAM_ID")
    key_path = get_config("APPLE_MUSIC_KEY_PATH")
    private_key = get_config("APPLE_MUSIC_PRIVATE_KEY")

    if key_path and not private_key:
        with open(os.path.expanduser(key_path)) as f:
            private_key = f.read()

    if key_id and team_id and private_key:
        am = AppleMusic(secret_key=private_key, key_id=key_id, team_id=team_id)
        player_app = Path.home() / "Applications" / "XlgPlayer.app" / "Contents" / "MacOS" / "xlg-player"
        is_playlist = "playlist" in query.lower()

        if is_playlist:
            search_query = re.sub(r"\bplaylist\b", "", query, flags=re.IGNORECASE).strip()
            results = am.search(search_query, types=["playlists"], limit=1)
            playlists = results.get("results", {}).get("playlists", {}).get("data", [])
            if not playlists:
                raise RuntimeError(f"No playlists found for: {query}")
            playlist = playlists[0]
            playlist_id = playlist["id"]
            playlist_name = playlist["attributes"]["name"]
            if player_app.exists():
                if send_to_player(f"--playlist {playlist_id}") == "OK":
                    return f"Playing playlist: {playlist_name}"
                kill_existing_players()
                subprocess.Popen([str(player_app), "--playlist", playlist_id], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return f"Playing playlist: {playlist_name}"
            subprocess.run(["open", f"music://music.apple.com/us/playlist/{playlist_id}"])
            return f"Opening playlist: {playlist_name}"

        results = am.search(query, types=["songs"], limit=1)
        songs = results.get("results", {}).get("songs", {}).get("data", [])
        if not songs:
            raise RuntimeError(f"No songs found for: {query}")
        song = songs[0]
        song_id = song["id"]
        song_name = song["attributes"]["name"]
        if player_app.exists():
            if send_to_player(song_id) == "OK":
                return f"Playing: {song_name}"
            kill_existing_players()
            subprocess.Popen([str(player_app), song_id], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return f"Playing: {song_name}"
        subprocess.run(["open", f"music://music.apple.com/us/song/{song_id}"])
        return f"Opening: {song_name} (click to play)"

    script = f'''
    tell application "Music"
        set searchResults to search library playlist 1 for "{query}"
        if (count of searchResults) > 0 then
            play item 1 of searchResults
            return "playing:" & name of item 1 of searchResults
        else
            return "not found"
        end if
    end tell
    '''
    result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Apple Music error: {result.stderr}")
    output = result.stdout.strip()
    if output.startswith("playing:"):
        return f"Playing: {output[8:]}"
    from urllib.parse import quote
    subprocess.run(["open", f"music://music.apple.com/search?term={quote(query)}"])
    return f"Searching Apple Music for: {query}"
