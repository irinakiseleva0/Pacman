import {
  Crown,
  Flame,
  Gem,
  Medal,
  ShieldCheck,
  Zap,
  type LucideIcon,
} from "lucide-react";

export interface Achievement {
  title: string;
  description: string;
  progress: number;
  icon: LucideIcon;
  tier: "bronze" | "silver" | "gold";
}

export const achievements: Achievement[] = [
  {
    title: "Neon Appetite",
    description: "Eat 10,000 pellets across career runs.",
    progress: 88,
    icon: Flame,
    tier: "gold",
  },
  {
    title: "Ghost Circuit",
    description: "Defeat 150 ghosts during rage windows.",
    progress: 64,
    icon: Zap,
    tier: "silver",
  },
  {
    title: "Maze Cartographer",
    description: "Clear every available map profile.",
    progress: 72,
    icon: Gem,
    tier: "silver",
  },
  {
    title: "Hard Mode Runner",
    description: "Win 12 Hard difficulty games.",
    progress: 41,
    icon: ShieldCheck,
    tier: "bronze",
  },
  {
    title: "Cherry Hunter",
    description: "Collect 250 cherries before timeout.",
    progress: 93,
    icon: Medal,
    tier: "gold",
  },
  {
    title: "District Legend",
    description: "Reach the terminal career rank.",
    progress: 57,
    icon: Crown,
    tier: "silver",
  },
];
