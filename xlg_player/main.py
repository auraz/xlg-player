"""XLG Player CLI - Apple Music command line player."""

import sys

from xlg_player import player


def print_usage() -> None:
    """Print usage information."""
    print("""xlg-player - Apple Music CLI player

Usage:
    xlg-player play "song name"     Search and play a song
    xlg-player play "playlist X"    Play a playlist (include "playlist" in query)
    xlg-player pause                Pause playback
    xlg-player resume               Resume playback
    xlg-player toggle               Toggle play/pause
    xlg-player skip                 Skip to next track
    xlg-player previous             Go to previous track
    xlg-player volume 50            Set volume to 50%
    xlg-player volume +10           Increase volume by 10%
    xlg-player volume -10           Decrease volume by 10%
    xlg-player status               Get JSON status
    xlg-player favorite             Toggle favorite on current track
    xlg-player auth                 Authorize with Apple Music""")


def main() -> int:
    """Main entry point."""
    args = sys.argv[1:]
    if not args:
        print_usage()
        return 0

    cmd = args[0].lower()

    try:
        if cmd == "play":
            if len(args) < 2:
                print("Usage: xlg-player play <query>")
                return 1
            print(player.play(" ".join(args[1:])))
        elif cmd == "pause":
            print(player.pause())
        elif cmd == "resume":
            print(player.resume())
        elif cmd == "toggle":
            print(player.toggle())
        elif cmd == "skip":
            print(player.skip())
        elif cmd in ("previous", "prev"):
            print(player.previous())
        elif cmd == "volume":
            if len(args) < 2:
                print("Usage: xlg-player volume <level>")
                return 1
            print(player.volume(args[1]))
        elif cmd == "status":
            print(player.status())
        elif cmd in ("favorite", "love"):
            print(player.favorite())
        elif cmd == "auth":
            from xlg_player.auth import run_auth_server
            run_auth_server()
        elif cmd in ("help", "-h", "--help"):
            print_usage()
        else:
            print(f"Unknown command: {cmd}")
            print_usage()
            return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
