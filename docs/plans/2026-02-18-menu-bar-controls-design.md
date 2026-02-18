# Menu Bar Controls Design

Add menu bar buttons for quick playback control without CLI.

## Requirements

- 3 buttons directly in menu bar (no dropdown): play/pause, next, favorite
- Play button toggles icon based on playback state (▶ when paused, ⏸ when playing)
- Favorite button shows filled heart when favorited, outline when not

## Architecture

Add `MenuBarController` class to manage the status item:

```
┌─────────────────────────────────────────────┐
│                  XlgPlayer                  │
│  ┌─────────────────┐  ┌──────────────────┐  │
│  │ MenuBarController│  │  Socket Server   │  │
│  │  - statusItem   │  │  (existing)      │  │
│  │  - playButton   │  │                  │  │
│  │  - nextButton   │  │                  │  │
│  │  - favButton    │  │                  │  │
│  └────────┬────────┘  └────────┬─────────┘  │
│           └────────┬───────────┘            │
│                    ▼                        │
│            handleCommand()                  │
└─────────────────────────────────────────────┘
```

## UI Details

**Icons** (SF Symbols):
- Play: `play.fill` / Pause: `pause.fill`
- Next: `forward.fill`
- Favorite: `heart` (outline) / `heart.fill` (favorited)

**State updates**: 1-second timer polls player state to update icons.

**Styling**: Borderless buttons with template images (adapts to light/dark mode).

## Implementation

**Changes to `main.swift`**:
- Add `MenuBarController` class (~60 lines)
- Initialize after authorization, before `app.run()`
- Add timer for state updates

**Button actions** reuse existing logic:
- Play/pause → `handleCommand(parts: ["toggle"])`
- Next → `handleCommand(parts: ["skip"])`
- Favorite → `handleCommand(parts: ["favorite"])`
