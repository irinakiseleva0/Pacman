import { Clock, Trophy } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { fetchLeaderboard, type ScoreEntry } from "@/lib/api";
import { DashboardNav } from "@/pages/Leaderboard";

function secondsUntilTomorrow() {
  const now = new Date();
  const tomorrow = new Date(now);
  tomorrow.setHours(24, 0, 0, 0);
  return Math.max(0, Math.floor((tomorrow.getTime() - now.getTime()) / 1000));
}

function formatCountdown(totalSeconds: number) {
  const hours = Math.floor(totalSeconds / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const seconds = totalSeconds % 60;
  return `${hours.toString().padStart(2, "0")}:${minutes.toString().padStart(2, "0")}:${seconds.toString().padStart(2, "0")}`;
}

export default function Daily() {
  const [remaining, setRemaining] = useState(secondsUntilTomorrow());
  const [rows, setRows] = useState<ScoreEntry[]>([]);
  const dailySeed = useMemo(() => {
    const now = new Date();
    return Number(`${now.getFullYear()}${String(now.getMonth() + 1).padStart(2, "0")}${String(now.getDate()).padStart(2, "0")}`);
  }, []);

  useEffect(() => {
    const timer = window.setInterval(() => setRemaining(secondsUntilTomorrow()), 1000);
    return () => window.clearInterval(timer);
  }, []);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        const data = await fetchLeaderboard("dailychallenge", 50);
        if (!cancelled) {
          setRows(data.filter((row) => row.seed === dailySeed));
        }
      } catch {
        if (!cancelled) {
          setRows([]);
        }
      }
    }

    load();
    const timer = window.setInterval(load, 30_000);
    return () => {
      cancelled = true;
      window.clearInterval(timer);
    };
  }, [dailySeed]);

  return (
    <main className="min-h-screen bg-neon-ink px-5 py-8 text-white sm:px-8 lg:px-10">
      <div className="mx-auto max-w-7xl">
        <DashboardNav />
        <section className="mt-8 grid gap-5 lg:grid-cols-[360px_1fr]">
          <Card className="border-neon-yellow/25 bg-white/[0.045] p-6">
            <Clock className="h-8 w-8 text-neon-yellow" />
            <Badge className="mt-5" variant="yellow">Daily Seed {dailySeed}</Badge>
            <h1 className="mt-5 font-display text-4xl font-black uppercase">
              {formatCountdown(remaining)}
            </h1>
            <p className="mt-3 text-sm leading-6 text-slate-300">
              Time until the next shared Daily Challenge map is generated.
            </p>
          </Card>

          <Card className="overflow-hidden border-white/10 bg-white/[0.045]">
            <div className="flex items-center gap-3 border-b border-white/10 p-5">
              <Trophy className="h-5 w-5 text-neon-cyan" />
              <h2 className="font-display text-xl font-bold uppercase">Top Of The Day</h2>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full min-w-[620px] text-left text-sm">
                <thead className="border-b border-white/10 text-xs uppercase tracking-[0.18em] text-slate-400">
                  <tr>
                    <th className="px-5 py-4">Rank</th>
                    <th className="px-5 py-4">Player</th>
                    <th className="px-5 py-4">Score</th>
                    <th className="px-5 py-4">Seed</th>
                  </tr>
                </thead>
                <tbody>
                  {rows.map((row, index) => (
                    <tr key={`${row.id ?? index}-${row.value}`} className="border-b border-white/5">
                      <td className="px-5 py-4 text-neon-yellow">#{index + 1}</td>
                      <td className="px-5 py-4 text-neon-cyan">{row.player?.username ?? row.username ?? "unknown"}</td>
                      <td className="px-5 py-4 font-semibold">{row.value.toLocaleString()}</td>
                      <td className="px-5 py-4 text-slate-300">{row.seed}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {rows.length === 0 && (
                <div className="p-8 text-center text-slate-400">No daily scores submitted yet.</div>
              )}
            </div>
          </Card>
        </section>
      </div>
    </main>
  );
}
