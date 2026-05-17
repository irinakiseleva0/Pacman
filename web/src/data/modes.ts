export interface GameMode {
  name: string;
  tagline: string;
  description: string;
  accent: "yellow" | "cyan" | "purple";
  stats: string[];
}

export const modes: GameMode[] = [
  {
    name: "Arcade",
    tagline: "Classic district clear",
    description:
      "Clear boards, manage lives, chain power seed windows, and push for a clean high score route.",
    accent: "yellow",
    stats: ["3 lives", "Board clears", "Balanced ghosts"],
  },
  {
    name: "Endless",
    tagline: "Pressure keeps climbing",
    description:
      "A survival loop built for marathon routes, risky cherry dives, and run-history bragging rights.",
    accent: "cyan",
    stats: ["Scaling pace", "Run streaks", "Long-form scoring"],
  },
  {
    name: "Challenge",
    tagline: "Precision trials",
    description:
      "Focused objectives stress routing, pickup timing, and nerve when the maze starts fighting back.",
    accent: "purple",
    stats: ["Objective goals", "Mastery badges", "Tight margins"],
  },
  {
    name: "Time Attack",
    tagline: "Fastest clean board wins",
    description:
      "A clock-first mode for players who want crisp corners, optimized paths, and no wasted turns.",
    accent: "cyan",
    stats: ["Countdown", "Speed routes", "Split chasing"],
  },
];
