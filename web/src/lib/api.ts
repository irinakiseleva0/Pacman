export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, "") ?? "";

// When API_BASE_URL is empty, fetch calls become relative (e.g. /api/scores/)
// which will 404 on GitHub Pages — components already handle this with try/catch.

export type Player = {
  id?: number;
  username: string;
  created_at?: string;
};

export type ScoreEntry = {
  id?: number;
  player?: Player;
  username?: string;
  mode: string;
  difficulty?: string;
  value: number;
  seed: number;
  date?: string | null;
};

export async function fetchScores(params: Record<string, string | number | undefined> = {}) {
  const search = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== "") {
      search.set(key, String(value));
    }
  });
  const response = await fetch(`${API_BASE_URL}/api/scores/?${search.toString()}`);
  if (!response.ok) {
    throw new Error(`Scores request failed: ${response.status}`);
  }
  return (await response.json()) as ScoreEntry[];
}

export async function fetchLeaderboard(mode: string, limit = 50) {
  const search = new URLSearchParams();
  if (mode) {
    search.set("mode", mode);
  }
  const response = await fetch(`${API_BASE_URL}/api/leaderboard/?${search.toString()}`);
  if (!response.ok) {
    throw new Error(`Leaderboard request failed: ${response.status}`);
  }
  const rows = (await response.json()) as ScoreEntry[];
  return rows.slice(0, limit);
}

export function displayMode(mode: string) {
  return mode
    .replace(/_/g, " ")
    .replace(/\b\w/g, (char) => char.toUpperCase());
}
