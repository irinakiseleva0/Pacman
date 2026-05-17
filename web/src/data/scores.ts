export interface ScorePoint {
  run: string;
  arcade: number;
  endless: number;
  challenge: number;
}

export const scoreHistory: ScorePoint[] = [
  { run: "R-01", arcade: 12800, endless: 14200, challenge: 9200 },
  { run: "R-02", arcade: 16400, endless: 17100, challenge: 11400 },
  { run: "R-03", arcade: 15250, endless: 19800, challenge: 12800 },
  { run: "R-04", arcade: 21100, endless: 22500, challenge: 14600 },
  { run: "R-05", arcade: 23600, endless: 24800, challenge: 17200 },
  { run: "R-06", arcade: 25900, endless: 28100, challenge: 19300 },
  { run: "R-07", arcade: 30200, endless: 31800, challenge: 22600 },
  { run: "R-08", arcade: 33400, endless: 35600, challenge: 24800 },
];

export const careerStats = [
  {
    label: "Career Score",
    value: "742K",
    detail: "Mock profile total across local runs.",
  },
  {
    label: "District Rank",
    value: "17",
    detail: "Progression level toward neon legend status.",
  },
  {
    label: "Boards Cleared",
    value: "128",
    detail: "Completed mazes across Arcade and Challenge.",
  },
  {
    label: "Best Streak",
    value: "11",
    detail: "Consecutive clean clears without a loss.",
  },
];
