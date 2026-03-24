# Cyberpunk Pac-Man

Arcade maze-chasing reimagined as a neon district survival run.

`Cyberpunk Pac-Man` is a stylized Pac-Man reinterpretation built with Python and raylib. It expands the classic maze loop into a small arcade package with multiple modes, progression, unlockables, challenge boards, and a cinematic cyberpunk UI shell.

## At A Glance

- `4 modes`: Arcade, Endless, Challenge, Time Attack
- `meta progression`: career rank, achievements, run history, unlock tracks
- `cosmetic rewards`: themes, HUD packs, title variants
- `systems depth`: district modifiers, directives, ghost personalities, pressure escalation
- `presentation`: neon menu shell, controller support, capture mode

## Screenshots

Add project media here once screenshots are exported:

```text
docs/
  screenshots/
    menu.png
    gameplay.png
    challenge-board.png
    career.png
  gifs/
    pressure-loop.gif
```

Ready-made media markdown:

See [docs/README-media-template.md](docs/README-media-template.md)

## Overview

This is not meant to be a plain classroom Pac-Man clone.

The project aims to feel like a compact premium arcade game:

- classic route-based Pac-Man rules
- a moody cyberpunk neon presentation
- multiple playable modes
- persistent profile progression
- unlockable rewards and meta goals

The strongest intended identity is:

- `retro rules, modern shell`
- `arcade clarity, cyberpunk atmosphere`
- `small game, strong product framing`

## Key Features

### Gameplay

- classic pellets, power seeds, cherries, teleports, and ghost pressure
- stronger feedback for pickups, ghost-eats, near-miss moments, route chains, and late-board tension
- district traits and run directives that change pacing and reward priorities
- more distinct ghost personalities with path-based navigation

### Modes

- `Arcade`
  - a chapter-style three-district run
- `Endless`
  - survival escalation with tiered pressure
- `Challenge`
  - curated trial-board style runs with unlockable elite trials
- `Time Attack`
  - countdown-driven routing with time banking on board clears

### Progression

- persistent profile saved locally
- career rank and long-term goals
- mode mastery
- challenge rank, credits, streaks, and trophies
- achievements and run history

### Unlockables

- themes
- HUD packs
- title variants
- directive packs
- elite districts
- elite trials

### Presentation

- cyberpunk neon shell UI
- cinematic menu flow
- controller support
- capture mode with `F10` for cleaner screenshots and clips

## Controls

### Keyboard

- `WASD` / Arrow Keys: move
- `Enter` / `Space`: confirm
- `Esc`: back / leave current screen
- `P`: pause
- `F10`: toggle capture mode

### Controller

- D-pad / left stick: move and navigate
- south face button: confirm
- east face button / back: cancel
- start: pause

## Installation

Requirements:

- Python `3.12+` recommended
- `raylib==5.5.0.4`

Install:

```bash
pip install -r requirements.txt
```

Run:

```bash
python main.py
```

## Project Structure

```text
assets/      textures and runtime-loaded art
core/        context, progression, scene base classes, raylib wrapper
data/config/ JSON-backed runtime, difficulty, and layout tuning
data/saves/  generated local profile / score save files
entities/    pacman, ghosts, pellets, cherry, walls, teleports
maps/        map definitions and board loading
scenes/      menu flow, gameplay scene, pause/result, meta screens
ui/          layout, HUD, navigation, controls, theme drawing
utils/       profile, score, audio, visual effects, sprites
main.py      app entry point and scene loop
```

## Save Data

Generated runtime files:

- `data/saves/profile.json`
- `data/saves/scores.json`

These files are local runtime state and are ignored by git.

## Repository Notes

Useful next GitHub-side improvements:

- repository description
- topic tags
- screenshots / GIF previews
- first release
- explicit license

Publishing helper docs:

- [docs/github-publishing-checklist.md](docs/github-publishing-checklist.md)
- [docs/README-media-template.md](docs/README-media-template.md)

## Roadmap

- stronger cyberpunk gameplay presentation
- richer district-specific enemy pressure
- more reward-track visualization
- more map-specific mechanics
- additional elite trials and unlock paths
- trailer/screenshot polish

## Status

Active prototype moving toward a stronger portfolio / release-quality presentation.
