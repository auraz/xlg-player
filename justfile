default:
    @just --list

test:
    uv run pytest -v

lint:
    uv run ruff check xlg_player

fmt:
    uv run ruff format xlg_player

run *ARGS:
    uv run xlg-player {{ARGS}}

build-player:
    cd swift-player && swift build -c release
    mkdir -p swift-player/XlgPlayer.app/Contents/MacOS
    cp swift-player/Info.plist swift-player/XlgPlayer.app/Contents/
    cp swift-player/.build/release/xlg-player swift-player/XlgPlayer.app/Contents/MacOS/
    find swift-player/XlgPlayer.app -exec xattr -c {} \; 2>/dev/null || true
    codesign --force --sign - swift-player/XlgPlayer.app

install-player:
    cp -r swift-player/XlgPlayer.app ~/Applications/
    ln -sf ~/Applications/XlgPlayer.app/Contents/MacOS/xlg-player ~/.local/bin/xlg-player-swift

build-streamdeck:
    cd streamdeck-plugin && npm install && npm run build

install-streamdeck:
    ln -sf "$(pwd)/streamdeck-plugin/com.xlg.player.sdPlugin" ~/Library/Application\ Support/com.elgato.StreamDeck/Plugins/
