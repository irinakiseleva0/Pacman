import {
  CircleDot,
  Github,
  Keyboard,
  LayoutDashboard,
  Play,
  Shield,
  Sparkles,
  Target,
  Trophy,
} from "lucide-react";
import { lazy, Suspense, useEffect, useState } from "react";
import { motion } from "framer-motion";

import { FeatureCard } from "@/components/FeatureCard";
import { NeonButton } from "@/components/NeonButton";
import { SectionTitle } from "@/components/SectionTitle";
import { StatCard } from "@/components/StatCard";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { achievements } from "@/data/achievements";
import { features } from "@/data/features";
import { modes } from "@/data/modes";
import { buildCareerStats, buildScoreHistory } from "@/data/scores";
import { fetchScores } from "@/lib/api";
import { cn } from "@/lib/utils";
import Daily from "@/pages/Daily";
import Leaderboard from "@/pages/Leaderboard";
import Profile from "@/pages/Profile";

const ScoreChartSection = lazy(() => import("@/components/ScoreChartSection"));

const reveal = {
  hidden: { opacity: 0, y: 24 },
  visible: { opacity: 1, y: 0 },
};

const modeAccent = {
  yellow: "border-neon-yellow/30 text-neon-yellow shadow-glow-yellow",
  cyan: "border-neon-cyan/30 text-neon-cyan shadow-glow",
  purple: "border-neon-purple/30 text-neon-purple shadow-glow-purple",
};

const statIcons = [Trophy, Target, Shield, Sparkles];

function HeroPreview() {
  return (
    <motion.div
      className="relative mx-auto aspect-[4/3] w-full max-w-xl overflow-hidden rounded-lg border border-neon-cyan/30 bg-black/75 shadow-[0_0_70px_rgba(51,246,255,0.18)]"
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.75, delay: 0.2 }}
    >
      <div className="absolute inset-0 bg-grid-neon bg-[length:32px_32px] opacity-70" />
      <div className="absolute inset-0 bg-[linear-gradient(135deg,rgba(255,255,255,0.12),transparent_22%,transparent_72%,rgba(181,101,255,0.12))]" />
      <div className="absolute inset-x-8 top-10 h-2 rounded-full bg-neon-cyan/80 shadow-glow" />
      <div className="absolute bottom-10 left-8 right-8 h-2 rounded-full bg-neon-purple/80 shadow-glow-purple" />
      <div className="absolute left-10 top-16 h-2/3 w-2 rounded-full bg-neon-cyan/80 shadow-glow" />
      <div className="absolute right-10 top-16 h-2/3 w-2 rounded-full bg-neon-cyan/80 shadow-glow" />
      <motion.div
        className="absolute left-[42%] top-[42%] h-20 w-20 rounded-full bg-neon-yellow shadow-glow-yellow"
        animate={{ x: [0, 22, 0], rotate: [0, 10, 0] }}
        transition={{ repeat: Infinity, duration: 2.4, ease: "easeInOut" }}
      >
        <div className="absolute right-0 top-1/2 h-0 w-0 -translate-y-1/2 border-y-[18px] border-l-[30px] border-y-transparent border-l-black" />
      </motion.div>
      {["bg-red-400", "bg-neon-cyan", "bg-neon-purple", "bg-orange-300"].map(
        (color, index) => (
          <motion.div
            key={color}
            className={cn(
              "absolute h-8 w-8 rounded-t-full shadow-lg",
              color,
              index % 2 === 0 ? "top-24" : "bottom-24",
            )}
            style={{ left: `${18 + index * 19}%` }}
            animate={{ y: [0, 12, 0] }}
            transition={{ repeat: Infinity, duration: 1.9 + index * 0.2 }}
          />
        ),
      )}
      <div className="absolute inset-x-0 bottom-0 flex items-center justify-between border-t border-white/10 bg-black/70 px-5 py-4 text-xs uppercase tracking-[0.22em] text-slate-300">
        <span>Score 33400</span>
        <span className="text-neon-yellow">Lives 3</span>
      </div>
    </motion.div>
  );
}

function HeroSection() {
  return (
    <section className="relative overflow-hidden px-4 pb-16 pt-8 sm:px-8 sm:pb-20 lg:px-10 lg:pt-10">
      <div className="mx-auto grid max-w-7xl items-center gap-12 lg:grid-cols-[1.05fr_0.95fr]">
        <motion.div
          initial="hidden"
          animate="visible"
          variants={reveal}
          transition={{ duration: 0.65 }}
        >
          <Badge variant="yellow" className="mb-6">
            Python raylib arcade showcase
          </Badge>
          <h1 className="max-w-4xl font-display text-4xl font-black uppercase leading-tight text-white sm:text-6xl lg:text-7xl">
            Cyberpunk Pac-Man
          </h1>
          <p className="mt-6 max-w-2xl text-base leading-8 text-slate-300 sm:text-lg">
            A neon portfolio frontend for a Python raylib Pac-Man game, built to
            show off its modes, career systems, controls, and arcade polish
            without touching the original game logic.
          </p>
          <div className="mt-8 flex flex-col gap-3 sm:flex-row">
            <NeonButton glow="yellow" asChild>
              <a href="https://github.com/" target="_blank" rel="noreferrer">
                <Github className="h-4 w-4" />
                GitHub
              </a>
            </NeonButton>
            <NeonButton glow="cyan" asChild>
              <a href="play">
                <Play className="h-4 w-4" />
                Play Web Build
              </a>
            </NeonButton>
            <NeonButton glow="purple" asChild>
              <a href="daily">
                <Trophy className="h-4 w-4" />
                Daily
              </a>
            </NeonButton>
          </div>
          <div className="mt-10 grid max-w-xl grid-cols-1 gap-3 min-[420px]:grid-cols-3">
            {["Arcade", "Endless", "Challenge"].map((item) => (
              <div
                key={item}
                className="rounded-lg border border-white/10 bg-white/[0.045] px-4 py-3 text-center font-display text-xs uppercase tracking-[0.18em] text-slate-300 shadow-[inset_0_1px_0_rgba(255,255,255,0.08)]"
              >
                {item}
              </div>
            ))}
          </div>
        </motion.div>
        <HeroPreview />
      </div>
    </section>
  );
}

function BrowserGameSection() {
  return (
    <section className="px-5 py-20 sm:px-8 lg:px-10">
      <div className="mx-auto max-w-7xl">
        <SectionTitle
          eyebrow="WebAssembly port"
          title="Browser Build Embedded In The Showcase"
          description="The React shell now reserves a playable slot for the Pygbag-generated WebAssembly export, served from the Vite public game folder."
        />
        <div className="overflow-hidden rounded-lg border border-neon-cyan/25 bg-black shadow-[0_0_80px_rgba(51,246,255,0.16)]">
          <iframe
            className="block aspect-[16/10] w-full bg-black"
            src="game/index.html"
            title="Cyberpunk Pac-Man browser build"
          />
        </div>
        <div className="mt-5 flex flex-wrap gap-3">
          <NeonButton glow="cyan" asChild>
            <a href="play">
              <Play className="h-4 w-4" />
              Open Player
            </a>
          </NeonButton>
          <NeonButton glow="yellow" asChild>
            <a href="leaderboard">
              <LayoutDashboard className="h-4 w-4" />
              Leaderboard
            </a>
          </NeonButton>
        </div>
      </div>
    </section>
  );
}

function GamePreviewSection() {
  const previews = [
    {
      title: "Gameplay capture",
      subtitle: "Live raylib screen",
      image: "qa_screen.png",
      tone: "cyan",
    },
    {
      title: "Menu terminal",
      subtitle: "Mode select shell",
      image: null,
      tone: "yellow",
    },
    {
      title: "Career screen",
      subtitle: "Profile progression",
      image: null,
      tone: "purple",
    },
    {
      title: "Achievements",
      subtitle: "Unlock grid",
      image: null,
      tone: "cyan",
    },
  ];

  return (
    <section className="px-5 py-20 sm:px-8 lg:px-10">
      <div className="mx-auto max-w-7xl">
        <SectionTitle
          eyebrow="Preview deck"
          title="Screenshots Ready For The README"
          description="The web showcase uses styled placeholders now, with clear slots for gameplay captures, menu states, and future release media."
        />
        <div className="grid gap-5 sm:grid-cols-2 xl:grid-cols-4">
          {previews.map((preview, index) => (
            <ScreenshotCard key={preview.title} preview={preview} index={index} />
          ))}
        </div>
      </div>
    </section>
  );
}

function ScreenshotCard({
  preview,
  index,
}: {
  preview: { title: string; subtitle: string; image: string | null; tone: string };
  index: number;
}) {
  const [imageFailed, setImageFailed] = useState(false);
  const showImage = preview.image && !imageFailed;

  return (
    <motion.div
      className="group overflow-hidden rounded-lg border border-white/10 bg-white/[0.045] shadow-[0_20px_80px_rgba(0,0,0,0.28)] transition duration-300 hover:-translate-y-1 hover:border-neon-cyan/50 hover:shadow-glow"
      initial={{ opacity: 0, y: 24 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.45, delay: index * 0.08 }}
    >
      <div className="relative aspect-video bg-black">
        {showImage ? (
          <img
            src={preview.image ?? undefined}
            alt={`${preview.title} preview`}
            className="h-full w-full object-cover transition duration-500 group-hover:scale-[1.04]"
            onError={() => setImageFailed(true)}
          />
        ) : (
          <ScreenshotPlaceholder tone={preview.tone} index={index} />
        )}
        <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-white/5" />
      </div>
      <div className="flex items-center justify-between gap-3 border-t border-white/10 px-5 py-4">
        <div className="min-w-0">
          <span className="block truncate font-display text-sm uppercase tracking-[0.18em] text-white">
            {preview.title}
          </span>
          <span className="mt-1 block text-xs text-slate-400">{preview.subtitle}</span>
        </div>
        <Badge variant={showImage ? "cyan" : "purple"}>
          {showImage ? "Live" : "Mock"}
        </Badge>
      </div>
    </motion.div>
  );
}

function ScreenshotPlaceholder({ tone, index }: { tone: string; index: number }) {
  const accent =
    tone === "yellow"
      ? "bg-neon-yellow text-neon-yellow shadow-glow-yellow"
      : tone === "purple"
        ? "bg-neon-purple text-neon-purple shadow-glow-purple"
        : "bg-neon-cyan text-neon-cyan shadow-glow";

  return (
    <>
      <div className="absolute inset-0 bg-grid-neon bg-[length:22px_22px] opacity-55" />
      <div className="absolute inset-5 rounded-md border border-current/25 text-neon-cyan" />
      <div className={cn("absolute left-7 top-7 h-2 w-24 rounded-full", accent)} />
      <div className="absolute left-7 right-7 top-14 grid grid-cols-5 gap-2">
        {Array.from({ length: 15 }).map((_, dotIndex) => (
          <div
            key={dotIndex}
            className={cn(
              "h-2 rounded-full bg-white/12",
              (dotIndex + index) % 4 === 0 && "bg-neon-yellow/80 shadow-glow-yellow",
            )}
          />
        ))}
      </div>
      <div className="absolute bottom-8 left-7 flex items-end gap-2">
        <CircleDot className="h-10 w-10 text-neon-yellow drop-shadow-[0_0_14px_rgba(255,230,109,0.6)]" />
        <LayoutDashboard className={cn("h-8 w-8", accent.replace("bg-", "text-"))} />
      </div>
      <div className="absolute bottom-8 right-7 h-10 w-10 rounded-t-full bg-neon-purple shadow-glow-purple" />
    </>
  );
}

function FeaturesSection() {
  return (
    <section className="px-4 py-16 sm:px-8 sm:py-20 lg:px-10">
      <div className="mx-auto max-w-7xl">
        <SectionTitle
          eyebrow="Feature matrix"
          title="Classic Maze Logic, Modern Arcade Shell"
          description="The showcase highlights the actual Python project structure: raylib gameplay, progression data, mode selection, and cyberpunk UI direction."
        />
        <div className="grid gap-5 md:grid-cols-2 lg:grid-cols-3">
          {features.map((feature) => (
            <FeatureCard key={feature.title} {...feature} />
          ))}
        </div>
      </div>
    </section>
  );
}

function ModesSection() {
  return (
    <section className="px-5 py-20 sm:px-8 lg:px-10">
      <div className="mx-auto max-w-7xl">
        <SectionTitle
          eyebrow="Game modes"
          title="Four Ways To Enter The Maze"
          description="Mocked copy mirrors the game modes already described by the project while leaving implementation untouched."
        />
        <div className="grid gap-5 lg:grid-cols-4">
          {modes.map((mode, index) => (
            <motion.div
              key={mode.name}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.45, delay: index * 0.06 }}
            >
              <Card
                className={cn(
                  "h-full border bg-white/[0.045] p-6 backdrop-blur",
                  modeAccent[mode.accent],
                )}
              >
                <p className="font-display text-xs uppercase tracking-[0.22em] text-slate-400">
                  {mode.tagline}
                </p>
                <h3 className="mt-4 font-display text-2xl font-black text-white">
                  {mode.name}
                </h3>
                <p className="mt-4 min-h-28 leading-7 text-slate-300">
                  {mode.description}
                </p>
                <div className="mt-5 flex flex-wrap gap-2">
                  {mode.stats.map((stat) => (
                    <Badge key={stat} variant="outline">
                      {stat}
                    </Badge>
                  ))}
                </div>
              </Card>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}

function DashboardSection({
  careerStats,
}: {
  careerStats: ReturnType<typeof buildCareerStats>;
}) {
  return (
    <section className="px-5 py-20 sm:px-8 lg:px-10">
      <div className="mx-auto max-w-7xl">
        <SectionTitle
          eyebrow="Career dashboard"
          title="Achievements And Progress At A Glance"
          description="Mock profile data gives the site a portfolio-ready product feel while staying decoupled from local save files."
        />
        <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
          {careerStats.map((stat, index) => (
            <StatCard
              key={stat.label}
              {...stat}
              icon={statIcons[index]}
              accent={index % 3 === 0 ? "yellow" : index % 3 === 1 ? "cyan" : "purple"}
            />
          ))}
        </div>
        <div className="mt-8 grid gap-5 md:grid-cols-2 lg:grid-cols-3">
          {achievements.map((achievement, index) => {
            const Icon = achievement.icon;
            return (
              <motion.div
                key={achievement.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.45, delay: index * 0.04 }}
              >
              <Card className="h-full border-white/10 bg-white/[0.04] p-5 transition duration-300 hover:border-neon-yellow/40 hover:shadow-glow-yellow">
                  <div className="flex items-start gap-4">
                    <div className="rounded-md border border-neon-yellow/25 bg-neon-yellow/10 p-3 text-neon-yellow">
                      <Icon className="h-5 w-5" />
                    </div>
                    <div className="min-w-0 flex-1">
                      <div className="flex flex-wrap items-center justify-between gap-2">
                        <h3 className="font-display text-base font-bold text-white">
                          {achievement.title}
                        </h3>
                        <Badge variant="purple">{achievement.tier}</Badge>
                      </div>
                      <p className="mt-2 text-sm leading-6 text-slate-300">
                        {achievement.description}
                      </p>
                      <Progress
                        className="mt-4"
                        value={achievement.progress}
                        indicatorClassName="bg-gradient-to-r from-neon-cyan via-neon-purple to-neon-yellow"
                      />
                    </div>
                  </div>
                </Card>
              </motion.div>
            );
          })}
        </div>
      </div>
    </section>
  );
}

function ControlsSection() {
  const controls = [
    ["Move", "WASD or Arrow Keys"],
    ["Confirm", "Enter or Space"],
    ["Back", "Esc"],
    ["Pause", "P"],
    ["Capture", "F10"],
    ["Controller", "D-pad, face buttons, Start"],
  ];

  return (
    <section id="download" className="px-5 py-20 sm:px-8 lg:px-10">
      <div className="mx-auto max-w-7xl">
        <SectionTitle
          eyebrow="Controls"
          title="Built For Keyboard And Controller"
          description="The frontend documents the actual control surface, plus a download callout for packaging future game builds."
        />
        <div className="grid gap-6 lg:grid-cols-[0.85fr_1.15fr]">
          <Card className="border-neon-yellow/25 bg-white/[0.045] p-6 shadow-glow-yellow">
            <Keyboard className="h-8 w-8 text-neon-yellow" />
            <h3 className="mt-5 font-display text-2xl font-black text-white">
              Arcade-ready inputs
            </h3>
            <p className="mt-4 leading-7 text-slate-300">
              The Python client remains the playable game. This web app is a
              polished showcase layer for releases, README media, and future
              profile dashboards.
            </p>
            <div className="mt-6">
              <NeonButton glow="purple" asChild>
                <a href="../README.md">
                  <Play className="h-4 w-4" />
                  Run Instructions
                </a>
              </NeonButton>
            </div>
          </Card>
          <div className="grid gap-3 sm:grid-cols-2">
            {controls.map(([label, value]) => (
              <div
                key={label}
                className="flex min-h-20 items-center justify-between gap-4 rounded-lg border border-white/10 bg-white/[0.04] px-5 py-4 transition duration-300 hover:border-neon-cyan/40 hover:bg-neon-cyan/[0.06]"
              >
                <span className="font-display text-sm uppercase tracking-[0.18em] text-slate-400">
                  {label}
                </span>
                <span className="text-right text-sm font-semibold text-white">{value}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}

function PlayPage() {
  return (
    <main className="min-h-screen bg-neon-ink px-4 py-6 text-foreground sm:px-8 lg:px-10">
      <div className="fixed inset-0 -z-10 bg-radial-signal" />
      <div className="fixed inset-0 -z-10 bg-grid-neon bg-[length:54px_54px] opacity-25" />
      <div className="mx-auto flex max-w-7xl flex-col gap-5">
        <div className="rounded-lg border border-neon-cyan/25 bg-black/80 p-4 shadow-glow">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <a
                className="rounded-sm font-display text-xs uppercase tracking-[0.18em] text-neon-cyan transition hover:text-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-neon-cyan"
                href="/"
              >
                Cyberpunk Pac-Man
              </a>
              <p className="mt-2 text-sm text-slate-300">
                Browser build runs from the generated Pygbag package.
              </p>
            </div>
            <div className="flex flex-wrap gap-3">
              <NeonButton glow="cyan" asChild>
                <a href="game/index.html">
                  <Play className="h-4 w-4" />
                  Direct Build
                </a>
              </NeonButton>
              <NeonButton glow="yellow" asChild>
                <a href="leaderboard">
                  <LayoutDashboard className="h-4 w-4" />
                  Leaderboard
                </a>
              </NeonButton>
              <NeonButton glow="purple" asChild>
                <a href="daily">
                  <Trophy className="h-4 w-4" />
                  Daily
                </a>
              </NeonButton>
            </div>
          </div>
        </div>
        <div className="overflow-hidden rounded-lg border border-neon-cyan/30 bg-black shadow-glow">
          <iframe
            className="block h-[calc(100vh-196px)] min-h-[520px] w-full bg-black"
            src="game/index.html"
            title="Cyberpunk Pac-Man browser build"
          />
        </div>
      </div>
    </main>
  );
}

function Footer() {
  return (
    <footer className="border-t border-white/10 px-5 py-10 sm:px-8 lg:px-10">
      <div className="mx-auto flex max-w-7xl flex-col gap-4 text-sm text-slate-400 sm:flex-row sm:items-center sm:justify-between">
        <p>Cyberpunk Pac-Man showcase frontend. Python game logic untouched.</p>
        <div className="flex gap-4">
          <a className="rounded-sm transition hover:text-neon-yellow focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-neon-yellow" href="#top">
            Top
          </a>
          <a className="rounded-sm transition hover:text-neon-cyan focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-neon-cyan" href="https://github.com/">
            GitHub
          </a>
          <a className="rounded-sm transition hover:text-neon-yellow focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-neon-yellow" href="leaderboard">
            Leaderboard
          </a>
          <a className="rounded-sm transition hover:text-neon-purple focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-neon-purple" href="../README.md">
            Game README
          </a>
        </div>
      </div>
    </footer>
  );
}

export default function App() {
  const [careerStats, setCareerStats] = useState([] as ReturnType<typeof buildCareerStats>);
  const [scoreHistory, setScoreHistory] = useState([] as ReturnType<typeof buildScoreHistory>);

  useEffect(() => {
    fetchScores({})
      .then((scores) => {
        setCareerStats(buildCareerStats(scores));
        setScoreHistory(buildScoreHistory(scores));
      })
      .catch(() => {});
  }, []);

  const rawPath = window.location.pathname;
  // Strip the Vite base prefix so routing works on GitHub Pages
  const base = import.meta.env.BASE_URL.replace(/\/$/, "");
  const path = base ? rawPath.replace(base, "") || "/" : rawPath;
  if (path === "/leaderboard") {
    return <Leaderboard />;
  }
  if (path === "/daily") {
    return <Daily />;
  }
  if (path === "/play") {
    return <PlayPage />;
  }
  if (path.startsWith("/profile/")) {
    const username = decodeURIComponent(path.replace("/profile/", "").split("/")[0] || "unknown");
    return <Profile username={username} />;
  }

  return (
    <main id="top" className="min-h-screen overflow-hidden bg-neon-ink text-foreground">
      <div className="fixed inset-0 -z-10 bg-radial-signal" />
      <div className="fixed inset-0 -z-10 bg-grid-neon bg-[length:54px_54px] opacity-30" />
      <HeroSection />
      <BrowserGameSection />
      <GamePreviewSection />
      <FeaturesSection />
      <ModesSection />
      <DashboardSection careerStats={careerStats} />
      <Suspense fallback={<ChartSkeleton />}>
        <ScoreChartSection scoreHistory={scoreHistory} />
      </Suspense>
      <ControlsSection />
      <Footer />
    </main>
  );
}

function ChartSkeleton() {
  return (
    <section className="px-4 py-16 sm:px-8 sm:py-20 lg:px-10">
      <div className="mx-auto max-w-7xl">
        <Card className="h-[420px] animate-pulse border-neon-cyan/20 bg-white/[0.04] p-6 shadow-glow">
          <div className="h-4 w-44 rounded-full bg-neon-cyan/20" />
          <div className="mt-8 h-[300px] rounded-lg border border-white/10 bg-grid-neon bg-[length:30px_30px] opacity-60" />
        </Card>
      </div>
    </section>
  );
}
