import {
  Activity,
  BadgeCheck,
  Gamepad2,
  Gauge,
  RadioTower,
  Sparkles,
  type LucideIcon,
} from "lucide-react";

export interface Feature {
  title: string;
  description: string;
  icon: LucideIcon;
  signal: string;
}

export const features: Feature[] = [
  {
    title: "Raylib Arcade Core",
    description:
      "Python gameplay loop with classic pellet routing, collision pressure, power seeds, cherries, and responsive scene transitions.",
    icon: Activity,
    signal: "60 FPS",
  },
  {
    title: "Cyberpunk UI Shell",
    description:
      "Neon menus, scanline panels, animated HUD states, capture mode, and polished end-of-run feedback around the playable client.",
    icon: Sparkles,
    signal: "Glow",
  },
  {
    title: "Persistent Career",
    description:
      "Local profile data tracks rank, achievements, mastery, unlocks, high scores, and run history for long-term progression.",
    icon: BadgeCheck,
    signal: "Save",
  },
  {
    title: "Difficulty Tuning",
    description:
      "Easy, Normal, and Hard presets adjust lives, rage time, ghost release cadence, scoring, and chase pressure.",
    icon: Gauge,
    signal: "Tune",
  },
  {
    title: "Controller Ready",
    description:
      "Keyboard and gamepad input keep arcade navigation fluid from menu selection to frantic maze escapes.",
    icon: Gamepad2,
    signal: "Pad",
  },
  {
    title: "Expandable Systems",
    description:
      "Config-driven layouts, modes, and content mechanics make the project ready for new boards and progression layers.",
    icon: RadioTower,
    signal: "Modular",
  },
];
