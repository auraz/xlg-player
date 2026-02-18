# XLG Player

Apple Music CLI player with MusicKit integration.

## Install

```bash
uv tool install xlg-player
```

## Usage

```bash
xlg-player play "Beatles Yesterday"     # Play song
xlg-player play "80s rock playlist"     # Play playlist
xlg-player pause                        # Pause playback
xlg-player resume                       # Resume playback
xlg-player toggle                       # Toggle play/pause
xlg-player skip                         # Next track
xlg-player previous                     # Previous track
xlg-player volume 50                    # Set volume
xlg-player volume +10                   # Volume up
xlg-player status                       # JSON status
xlg-player favorite                     # Toggle favorite
```

## Setup

1. Get credentials from [Apple Developer Portal](https://developer.apple.com/account/resources/authkeys/list):
   - Keys -> + -> Enable MusicKit -> Download `.p8` file
   - Note your Key ID and Team ID

2. Create config file:

```bash
mkdir -p ~/.config/xlg
mv ~/Downloads/AuthKey_*.p8 ~/.config/xlg/AuthKey.p8
cat > ~/.config/xlg/config << 'EOF'
APPLE_MUSIC_KEY_ID=your-key-id
APPLE_MUSIC_TEAM_ID=your-team-id
APPLE_MUSIC_KEY_PATH=~/.config/xlg/AuthKey.p8
EOF
```

3. Build native player (macOS 14+):

```bash
just build-player
just install-player
```

On first run, grant MusicKit authorization when prompted.

## Stream Deck Plugin

Control playback from Elgato Stream Deck.

```bash
just build-streamdeck
just install-streamdeck
```

Restart Stream Deck app, find "XLG Controls" category.

| Button | Action |
|--------|--------|
| Play/Pause | Toggle playback |
| Next | Skip to next |
| Previous | Previous track |
| Volume Up | +10% volume |
| Volume Down | -10% volume |
| Favorite | Love current track |

## Architecture

```
xlg-player CLI (Python)
       |
       v
Unix Socket /tmp/xlg-player.sock
       |
       v
XLG Player (Swift/MusicKit)
       |
       v
Apple Music
```

## Development

```bash
just test    # Run tests
just lint    # Check code
just fmt     # Format code
```
