export interface ScorePoint {
  run: string;
  arcade: number;
  endless: number;
  challenge: number;
}

export interface CareerStat {
  label: string;
  value: string;
  detail: string;
}

export function buildScoreHistory(scores: import("@/lib/api").ScoreEntry[]): ScorePoint[] {
  const arcadeScores = scores
    .filter((s) => s.mode === "arcade")
    .slice(0, 8)
    .reverse();
  return arcadeScores.map((s, i) => ({
    run: `R-${String(i + 1).padStart(2, "0")}`,
    arcade: s.value,
    endless: 0,
    challenge: 0,
  }));
}

export function buildCareerStats(scores: import("@/lib/api").ScoreEntry[]): CareerStat[] {
  const total = scores.reduce((sum, s) => sum + s.value, 0);
  const best = scores.reduce((max, s) => Math.max(max, s.value), 0);
  const wins = scores.filter((s) => s.value > 0).length;
  const modes = new Set(scores.map((s) => s.mode)).size;
  return [
    {
      label: "Career Score",
      value: total > 1000 ? `${Math.round(total / 1000)}K` : String(total),
      detail: "Total score across all runs.",
    },
    { label: "Best Run", value: String(best), detail: "Highest single-run score." },
    { label: "Runs Logged", value: String(wins), detail: "Total completed runs on the board." },
    {
      label: "Modes Played",
      value: String(modes),
      detail: "Distinct game modes on the leaderboard.",
    },
  ];
}

export const scoreHistory: ScorePoint[] = [];
export const careerStats: CareerStat[] = [];
