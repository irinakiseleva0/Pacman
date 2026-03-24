# Cyberpunk Pac-Man

A cyberpunk-flavored Pac-Man project built with Python and raylib.

This repository is no longer just a basic Pac-Man clone. It includes multiple game modes, progression systems, unlockable cosmetic layers, challenge boards, a career profile, controller support, and a custom neon UI shell designed around a cinematic cyberpunk mood.

## Hook

Arcade maze-chasing reimagined as a neon district survival run.

## Elevator Pitch

`Cyberpunk Pac-Man` is a stylish maze-chase project that treats Pac-Man like a compact arcade campaign instead of a single classic board. You route through neon-lit districts, survive escalating ghost pressure, clear curated challenge boards, unlock visual packs, and build a persistent profile across multiple modes.

The goal is not just to recreate Pac-Man mechanics, but to package them like a small premium arcade product with progression, identity, and a stronger presentation layer.

## Fantasy

You are not just clearing dots in a timeless abstract maze. You are pushing through hostile city sectors, syncing route lines, breaking ghost pressure, and surviving district control systems under neon signal light.

The intended feeling is:

- `retro rules, modern shell`
- `arcade clarity, cyberpunk atmosphere`
- `score routing with pressure escalation`
- `small game, strong identity`

## Why It Should Feel Different In 10 Seconds

- a cyberpunk neon shell instead of a plain retro UI
- campaign-like chapter flow in `Arcade`
- survival escalation in `Endless`
- curated trial-board presentation in `Challenge`
- visible profile progression, unlocks, and reward tracks
- district identity, themed modifiers, and ghost pressure states

## What Makes This Version Different

- `Arcade`, `Endless`, `Challenge`, and `Time Attack` modes
- district-specific modifiers and elite late-run pressure
- distinct ghost personalities and district-based behavior bias
- progression systems: career rank, mode mastery, challenge rank, trophies
- unlockable themes, HUD packs, title variants, directive packs, elite districts, elite trials
- challenge board, achievements, run history, journal/codex, and career screens
- controller support and capture mode for cleaner screenshots/trailer shots
- custom cyberpunk UI direction instead of default retro menu screens

## Current Feature Set

### Core Gameplay

- classic maze-chase loop with pellets, power seeds, cherries, teleports, and ghosts
- stronger live feedback for pellet pickup, ghost defeat, route chains, near-miss tension, and pressure spikes
- mode-specific pacing and board directives
- chapter-style Arcade flow
- survival-tier Endless escalation
- curated trial-board style Challenge mode
- Time Attack countdown flow with board-clear time banking

### Meta / Product Layer

- persistent profile saved in `data/saves/profile.json`
- persistent score data in `data/saves/scores.json`
- career overview and long-term goals
- achievements screen
- run history screen
- themes screen
- challenge unlocks and trophies
- journal/codex for districts, ghost types, and trial entries

### Presentation

- cyberpunk neon shell UI
- cinematic menu flow
- presentation/capture mode toggle with `F10`
- controller navigation across gameplay and shell screens

## Steam-Style Positioning

If this were presented as a store-facing prototype, the strongest pitch would be:

> A neon-drenched arcade chase game where classic Pac-Man routing meets survival pressure, curated challenge boards, and long-term progression.

This project is currently strongest when framed as:

- a `portfolio-quality arcade systems project`
- a `stylized Pac-Man reinterpretation`
- a `small premium arcade package`, not a pure clone

## Installation

### Requirements

- Python `3.12+` recommended
- `raylib` Python package

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the game:

```bash
python main.py
```

## Controls

### Keyboard

- `WASD` / Arrow Keys: move
- `Enter` / `Space`: confirm in menus
- `Esc`: back / leave current screen
- `P`: pause
- `F10`: toggle capture mode

### Controller

- D-pad / left stick: move and navigate
- south face button: confirm
- east face button / back: cancel
- start: pause

## Media Plan

The repository is now structurally closer to a product, but to really sell the game publicly it still needs media:

- `3-5 gameplay screenshots`
- `1 menu screenshot`
- `1 challenge/career screenshot`
- `1 short GIF` showing pressure escalation, ghost-eat feedback, and a clean board clear
- `1 short trailer-style clip` built from capture mode

Recommended future README media block:

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

A ready-to-use GitHub publishing checklist and media template live in:

- `docs/github-publishing-checklist.md`
- `docs/README-media-template.md`

## Screens and Modes

### Main Screens

- `Menu`
- `Modes`
- `Challenge Board`
- `Career`
- `Achievements`
- `Run History`
- `Themes`
- `Options`
- `Journal`
- `Pause`
- `Result`

### Modes

- `Arcade`
  - campaign-like three-district run
- `Endless`
  - survival escalation with tiered pressure
- `Challenge`
  - curated trial board with unlockable elite slots
- `Time Attack`
  - countdown-based score routing mode

## Project Structure

```text
assets/      textures and runtime-loaded art
core/        game context, scene base classes, progression logic
data/config/ JSON-backed runtime, difficulty, and layout tuning
entities/    pacman, ghosts, pellets, cherry, walls, teleports
maps/        map definitions and board loading
scenes/      menu flow, gameplay scene, pause/result, meta screens
ui/          layout, HUD, navigation, controls, theme drawing
utils/       profile, score, audio, visual effects, sprites
main.py      app entry point and scene loop
```

## Structure Notes

The repository was cleaned so scene files no longer sprawl across the root. The main interactive screens now live under `scenes/`, while shared logic remains in `core/`, `entities/`, `ui/`, and `utils/`.
The project also uses a local wrapper around `raylib` at `core/raylib_api.py`, so the dependency boundary is explicit and does not conflict with the external package name.
Important tuning values now live in `data/config/` instead of only inside Python files, so runtime balance, layout sizing, and difficulty presets are easier to iterate on without touching gameplay code.

## Dependencies

See [requirements.txt](./requirements.txt).

Current runtime dependency:

- `raylib==5.5.0.4`

## Save Data

Generated local files:

- `data/saves/profile.json`
- `data/saves/scores.json`

These are part of the local runtime state and will change as you play.
The project now uses JSON-backed runtime save files consistently. Older text-file score storage was removed to avoid parallel save formats and repository confusion.

## Repository Notes

This project would benefit even more from the following GitHub-side metadata:

- repository description
- topic tags like `python`, `raylib`, `pacman`, `game-dev`, `arcade`, `cyberpunk`
- release builds or tagged milestones
- gameplay screenshots / GIF previews in the README
- an explicit license

I did not invent a license file automatically here, because that is a legal/project decision and should be chosen intentionally.

## Roadmap

- more map-specific mechanics
- stronger cyberpunk gameplay presentation
- richer district-specific enemy pressure
- more reward-track visualization
- additional elite trials and unlock paths
- more trailer/screenshot polish

## Status

Active prototype moving toward a stronger portfolio / release-quality presentation.
