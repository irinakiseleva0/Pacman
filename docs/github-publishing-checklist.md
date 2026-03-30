# GitHub Publishing Checklist

Use this checklist when you are ready to align the public GitHub repository with the current local project state.

## 1. Push The Real Structure

Make sure the default branch reflects the current cleaned structure:

- `scenes/` is present and used by `main.py`
- `core/raylib_api.py` is the active raylib wrapper
- `data/config/` exists
- no runtime JSON files live in the repository root
- no legacy `src/` directory remains

## 2. Verify GitHub README Rendering

After pushing:

- open the repository home page
- verify the rendered README starts with `Cyberpunk Pac-Man`
- verify the README preview matches the raw README
- verify the project structure block mentions `scenes/` and `data/config/`

## 3. Add Repository Description

Recommended GitHub repository description:

`Cyberpunk Pac-Man is a neon-styled arcade maze-chase game built with Python and raylib, featuring multiple modes, progression, unlockables, and a cinematic UI shell.`

Shorter variant:

`A cyberpunk Pac-Man reinterpretation built with Python and raylib, with multiple modes, progression, unlockables, and a premium neon UI shell.`

Copy-paste version:

See `docs/github-about.txt`

## 4. Add Topics

Recommended topic tags:

- `python`
- `raylib`
- `game-dev`
- `arcade`
- `pacman`
- `cyberpunk`
- `indie-game`
- `gameplay-systems`
- `ui-design`
- `portfolio-project`

## 5. Add Screenshots To README

Create a media structure like this:

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

Recommended screenshot order:

1. Main menu
2. Gameplay
3. Challenge board
4. Career / progression

## 6. Add A README Media Section

Suggested markdown block:

```md
## Screenshots

![Main Menu](docs/screenshots/menu.png)
![Gameplay](docs/screenshots/gameplay.png)
![Challenge Board](docs/screenshots/challenge-board.png)
![Career](docs/screenshots/career.png)
```

## 7. Publish A First Release

Suggested release title:

`v0.1.0 - Cyberpunk Prototype Shell`

Suggested release notes:

```md
## Highlights

- Cyberpunk neon menu and gameplay shell
- Arcade, Endless, Challenge, and Time Attack modes
- Career progression, unlockables, and challenge trophies
- Themes, HUD packs, title variants, and district modifiers
- Journal, achievements, run history, and controller support

## Notes

This is an active prototype focused on arcade systems, presentation, and progression design.
```

Ready-made release draft:

See `docs/release-v0.1.0.md`

## 8. Add A One-Line Hook Everywhere

Use one stable hook sentence across:

- repo description
- README opening
- release notes
- portfolio links

Recommended hook:

`Arcade maze-chasing reimagined as a neon district survival run.`

## 9. Add A Portfolio Summary

Use this when sharing the project:

`Cyberpunk Pac-Man is a stylized arcade systems project built with Python and raylib. It expands the classic Pac-Man loop into a multi-mode neon survival package with progression, unlockables, challenge boards, and a cinematic UI presentation.`

## 10. Final Public Check

Before sharing the repository, verify:

- no runtime save files are committed
- no dead legacy folders remain
- no conflicting import names remain
- README preview matches the current branch
- screenshots load correctly on GitHub
- description and topics are filled in
