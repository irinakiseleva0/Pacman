import { RefreshCcw, Search, Trophy } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { displayMode, fetchLeaderboard, type ScoreEntry } from "@/lib/api";

const MODES = ["arcade", "endless", "challenge", "time_attack", "dailychallenge"];
const DIFFICULTIES = ["all", "easy", "normal", "hard"];

export default function Leaderboard() {
  const [mode, setMode] = useState("arcade");
  const [difficulty, setDifficulty] = useState("all");
  const [rows, setRows] = useState<ScoreEntry[]>([]);
  const [status, setStatus] = useState("Loading leaderboard");
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        setStatus("Syncing");
        const data = await fetchLeaderboard(mode, 50);
        if (!cancelled) {
          setRows(data);
          setLastUpdated(new Date());
          setStatus("Live");
        }
      } catch {
        if (!cancelled) {
          setStatus("API unavailable");
        }
      }
    }

    load();
    const timer = window.setInterval(load, 30_000);
    return () => {
      cancelled = true;
      window.clearInterval(timer);
    };
  }, [mode]);

  const filteredRows = useMemo(() => {
    if (difficulty === "all") {
      return rows;
    }
    return rows.filter((row) => row.difficulty?.toLowerCase() === difficulty);
  }, [difficulty, rows]);

  return (
    <main className="min-h-screen bg-neon-ink px-5 py-8 text-white sm:px-8 lg:px-10">
      <div className="mx-auto max-w-7xl">
        <DashboardNav />
        <section className="mt-8 flex flex-col justify-between gap-5 border-b border-white/10 pb-6 lg:flex-row lg:items-end">
          <div>
            <Badge variant="cyan">Auto-refresh 30s</Badge>
            <h1 className="mt-4 font-display text-4xl font-black uppercase tracking-normal">
              Leaderboard
            </h1>
            <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-300">
              Top 50 runs from the Django API, filtered by mode and local difficulty tags when present.
            </p>
          </div>
          <div className="flex items-center gap-3 text-sm text-slate-300">
            <RefreshCcw className="h-4 w-4 text-neon-cyan" />
            <span>{status}</span>
            {lastUpdated && <span>{lastUpdated.toLocaleTimeString()}</span>}
          </div>
        </section>

        <section className="mt-6 grid gap-4 lg:grid-cols-[1fr_220px]">
          <Card className="overflow-hidden border-white/10 bg-white/[0.045]">
            <div className="flex flex-wrap items-center gap-3 border-b border-white/10 p-4">
              <Search className="h-4 w-4 text-neon-yellow" />
              {MODES.map((item) => (
                <Button
                  key={item}
                  variant={item === mode ? "default" : "outline"}
                  size="sm"
                  onClick={() => setMode(item)}
                >
                  {displayMode(item)}
                </Button>
              ))}
            </div>
            <div className="overflow-x-auto">
              <table className="w-full min-w-[760px] text-left text-sm">
                <thead className="border-b border-white/10 text-xs uppercase tracking-[0.18em] text-slate-400">
                  <tr>
                    <th className="px-5 py-4">Rank</th>
                    <th className="px-5 py-4">Player</th>
                    <th className="px-5 py-4">Score</th>
                    <th className="px-5 py-4">Mode</th>
                    <th className="px-5 py-4">Seed</th>
                    <th className="px-5 py-4">Date</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredRows.map((row, index) => (
                    <tr key={`${row.id ?? index}-${row.seed}`} className="border-b border-white/5">
                      <td className="px-5 py-4 font-display text-neon-yellow">#{index + 1}</td>
                      <td className="px-5 py-4">
                        <a className="text-neon-cyan hover:underline" href={`/profile/${row.player?.username ?? row.username ?? "unknown"}`}>
                          {row.player?.username ?? row.username ?? "unknown"}
                        </a>
                      </td>
                      <td className="px-5 py-4 font-semibold">{row.value.toLocaleString()}</td>
                      <td className="px-5 py-4">{displayMode(row.mode)}</td>
                      <td className="px-5 py-4 text-slate-300">{row.seed}</td>
                      <td className="px-5 py-4 text-slate-400">
                        {row.date ? new Date(row.date).toLocaleString() : "-"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {filteredRows.length === 0 && (
                <div className="p-8 text-center text-slate-400">No runs found for this filter.</div>
              )}
            </div>
          </Card>
          <Card className="h-fit border-neon-purple/25 bg-white/[0.045] p-5">
            <Trophy className="h-7 w-7 text-neon-purple" />
            <h2 className="mt-4 font-display text-lg font-bold uppercase">Difficulty</h2>
            <div className="mt-4 grid gap-2">
              {DIFFICULTIES.map((item) => (
                <Button
                  key={item}
                  variant={item === difficulty ? "default" : "outline"}
                  onClick={() => setDifficulty(item)}
                >
                  {displayMode(item)}
                </Button>
              ))}
            </div>
          </Card>
        </section>
      </div>
    </main>
  );
}

export function DashboardNav() {
  return (
    <nav className="flex flex-wrap items-center gap-3 text-sm text-slate-300">
      <a className="font-display text-neon-yellow" href="/">Cyberpunk Pac-Man</a>
      <a className="hover:text-neon-cyan" href="/leaderboard">Leaderboard</a>
      <a className="hover:text-neon-cyan" href="/daily">Daily</a>
    </nav>
  );
}
