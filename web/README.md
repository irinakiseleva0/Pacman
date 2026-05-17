# Cyberpunk Pac-Man Web Frontend

Polished Vite + React + TypeScript showcase site for the Python/raylib Pac-Man game.

This frontend is intentionally isolated in `/web`. It does not rewrite, import, or modify the Python game logic.

## Stack

- Vite
- React
- TypeScript
- Tailwind CSS
- Framer Motion
- shadcn/ui-style primitives
- lucide-react
- Recharts

## Commands

Install dependencies:

```powershell
npm install
```

Run the local dev server:

```powershell
npm run dev
```

Create a production build:

```powershell
npm run build
```

Preview the production build locally:

```powershell
npm run preview
```

## Structure

```text
src/components/       reusable UI and neon showcase components
src/components/ui/    shadcn-compatible primitives
src/data/             mock features, modes, achievements, and scores
src/lib/              shared utilities
public/               static preview assets
```

## Preview Images

The app uses `public/qa_screen.png`, copied from the project root, as the first real gameplay preview. Other preview frames use styled fallback placeholders so the page still looks polished when more screenshots are not available yet.
