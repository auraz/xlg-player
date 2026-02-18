# Menu Bar Controls Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add 3 menu bar buttons (play/pause, next, favorite) with dynamic icons based on playback state.

**Architecture:** Add `MenuBarController` class to `main.swift` that creates an NSStatusItem with NSStackView containing 3 buttons. A 1-second timer updates button icons based on player state.

**Tech Stack:** Swift 6, AppKit (NSStatusItem, NSStackView, NSButton), SF Symbols

---

### Task 1: Add MenuBarController class skeleton

**Files:**
- Modify: `swift-player/Sources/xlg-player/main.swift:245` (add at end)

**Step 1: Add MenuBarController class with status item setup**

Add this class at the end of `main.swift`, before the closing brace of the file:

```swift
@MainActor
class MenuBarController {
    private var statusItem: NSStatusItem!
    private var playButton: NSButton!
    private var nextButton: NSButton!
    private var favButton: NSButton!
    private var updateTimer: Timer?

    init() {
        setupStatusItem()
        startUpdateTimer()
    }

    private func setupStatusItem() {
        statusItem = NSStatusBar.system.statusItem(withLength: NSStatusItem.variableLength)

        let stackView = NSStackView()
        stackView.orientation = .horizontal
        stackView.spacing = 4

        playButton = makeButton(symbol: "play.fill", action: #selector(togglePlay))
        nextButton = makeButton(symbol: "forward.fill", action: #selector(skipNext))
        favButton = makeButton(symbol: "heart", action: #selector(toggleFavorite))

        stackView.addArrangedSubview(playButton)
        stackView.addArrangedSubview(nextButton)
        stackView.addArrangedSubview(favButton)

        statusItem.button?.addSubview(stackView)
        stackView.translatesAutoresizingMaskIntoConstraints = false
        NSLayoutConstraint.activate([
            stackView.leadingAnchor.constraint(equalTo: statusItem.button!.leadingAnchor, constant: 4),
            stackView.trailingAnchor.constraint(equalTo: statusItem.button!.trailingAnchor, constant: -4),
            stackView.centerYAnchor.constraint(equalTo: statusItem.button!.centerYAnchor)
        ])
    }

    private func makeButton(symbol: String, action: Selector) -> NSButton {
        let button = NSButton()
        button.image = NSImage(systemSymbolName: symbol, accessibilityDescription: nil)
        button.image?.isTemplate = true
        button.bezelStyle = .inline
        button.isBordered = false
        button.target = self
        button.action = action
        button.widthAnchor.constraint(equalToConstant: 24).isActive = true
        return button
    }

    private func startUpdateTimer() {
        updateTimer = Timer.scheduledTimer(withTimeInterval: 1.0, repeats: true) { [weak self] _ in
            Task { @MainActor in self?.updateButtonStates() }
        }
    }

    private func updateButtonStates() {
        let isPlaying = XlgPlayer.player.state.playbackStatus == .playing
        playButton.image = NSImage(systemSymbolName: isPlaying ? "pause.fill" : "play.fill", accessibilityDescription: nil)
        playButton.image?.isTemplate = true

        let isFavorited = checkFavorited()
        favButton.image = NSImage(systemSymbolName: isFavorited ? "heart.fill" : "heart", accessibilityDescription: nil)
        favButton.image?.isTemplate = true
    }

    private func checkFavorited() -> Bool {
        guard let script = NSAppleScript(source: "tell application \"Music\" to return favorited of current track") else { return false }
        var error: NSDictionary?
        let result = script.executeAndReturnError(&error)
        return error == nil && result.booleanValue
    }

    @objc private func togglePlay() {
        Task { _ = await XlgPlayer.handleCommand(parts: ["toggle"]) }
    }

    @objc private func skipNext() {
        Task { _ = await XlgPlayer.handleCommand(parts: ["skip"]) }
    }

    @objc private func toggleFavorite() {
        Task { _ = await XlgPlayer.handleCommand(parts: ["favorite"]) }
    }
}
```

**Step 2: Build to verify syntax**

Run: `cd swift-player && swift build 2>&1 | head -20`
Expected: Build should succeed or show only unrelated warnings

**Step 3: Commit**

```bash
git add swift-player/Sources/xlg-player/main.swift
git commit -m "feat(swift): add MenuBarController class skeleton"
```

---

### Task 2: Initialize MenuBarController in main()

**Files:**
- Modify: `swift-player/Sources/xlg-player/main.swift:30-42` (main Task block)

**Step 1: Add property to hold MenuBarController**

Add this line after `nonisolated(unsafe) static var player` (around line 12):

```swift
@MainActor static var menuBar: MenuBarController?
```

**Step 2: Initialize MenuBarController after authorization**

In the `main()` function, inside the Task block (around line 38), add this line after `await playContent(...)` and before `startSocketServer()`:

```swift
menuBar = MenuBarController()
```

The Task block should now look like:

```swift
Task { @MainActor in
    var status = MusicAuthorization.currentStatus
    if status != .authorized { status = await MusicAuthorization.request() }
    guard status == .authorized else {
        print("Not authorized")
        app.terminate(nil)
        return
    }
    await playContent(isPlaylist: isPlaylist, ids: ids)
    menuBar = MenuBarController()
    startSocketServer()
}
```

**Step 3: Build and run to verify**

Run: `cd swift-player && swift build -c release`
Expected: Build succeeds

**Step 4: Commit**

```bash
git add swift-player/Sources/xlg-player/main.swift
git commit -m "feat(swift): initialize menu bar on startup"
```

---

### Task 3: Test menu bar manually

**Files:**
- None (manual testing)

**Step 1: Build the player**

Run: `just build-player`
Expected: Build succeeds, app is signed

**Step 2: Install and run**

Run: `just install-player && ~/Applications/XlgPlayer.app/Contents/MacOS/xlg-player 1234567890`
(Use a dummy song ID - it will fail to play but the menu bar should appear)

Expected: 3 buttons appear in menu bar (▶ ⏭ ♡)

**Step 3: Test button clicks**

- Click play button → should toggle (may show error in console if no track)
- Click next button → should attempt skip
- Click favorite button → should toggle favorite

**Step 4: Update README**

Add to README.md in the Architecture section:

```markdown
The Swift player also provides menu bar controls (▶ ⏭ ❤) for quick access.
```

**Step 5: Commit**

```bash
git add README.md
git commit -m "docs: mention menu bar controls in README"
```

---

### Task 4: Update design doc with completion status

**Files:**
- Modify: `docs/plans/2026-02-18-menu-bar-controls-design.md`

**Step 1: Add completion note**

Add at the end of the design doc:

```markdown

## Status

Implemented 2026-02-18. See `swift-player/Sources/xlg-player/main.swift`.
```

**Step 2: Commit**

```bash
git add docs/plans/2026-02-18-menu-bar-controls-design.md
git commit -m "docs: mark menu bar controls as implemented"
```
