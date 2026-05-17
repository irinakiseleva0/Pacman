import { Award, Heart, LineChart as LineChartIcon, User } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { displayMode, fetchScores, type ScoreEntry } from "@/lib/api";
import { DashboardNav } from "@/pages/Leaderboard";

export default function Profile({ username }: { username: string }) {
  const [scores, setScores] = useState<ScoreEntry[]>([]);
  const [status, setStatus] = useState("Loading profile");

  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        const data = await fetchScores({ username });
        if (!cancelled) {
          setScores(data);
          setStatus("Synced");
        }
      } catch {
        if (!cancelled) {
          setStatus("API unavailable");
        }
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, [username]);

  const chartData = useMemo(
    () =>
      [...scores]
        .reverse()
        .map((score, index) => ({
          label: score.date ? new Date(score.date).toLocaleDateString() : `Run ${index + 1}`,
          score: score.value,
        })),
    [scores],
  );

  const favoriteMode = useMemo(() => {
    const counts = scores.reduce<Record<string, number>>((acc, score) => {
      acc[score.mode] = (acc[score.mode] ?? 0) + 1;
      return acc;
    }, {});
    const top = Object.entries(counts).sort((a, b) => b[1] - a[1])[0]?.[0];
    return top ? displayMode(top) : "No runs yet";
  }, [scores]);

  const bestScore = Math.max(0, ...scores.map((score) => score.value));
  const achievements = [
    { title: "First Sync", unlocked: scores.length > 0 },
    { title: "Score Spike", unlocked: bestScore >= 5000 },
    { title: "Seed Chaser", unlocked: new Set(scores.map((score) => score.seed)).size >= 3 },
  ];

  return (
    <main className="min-h-screen bg-neon-ink px-5 py-8 text-white sm:px-8 lg:px-10">
      <div className="mx-auto max-w-7xl">
        <DashboardNav />
        <section className="mt-8 grid gap-5 lg:grid-cols-[0.7fr_1.3fr]">
          <Card className="border-neon-cyan/25 bg-white/[0.045] p-6">
            <User className="h-8 w-8 text-neon-cyan" />
            <h1 className="mt-5 font-display text-3xl font-black">{username}</h1>
            <p className="mt-2 text-sm text-slate-400">{status}</p>
            <div className="mt-6 grid gap-3">
              <Metric label="Best Score" value={bestScore.toLocaleString()} />
              <Metric label="Runs" value={String(scores.length)} />
              <Metric label="Favorite Mode" value={favoriteMode} />
            </div>
          </Card>

          <Card className="border-white/10 bg-white/[0.045] p-6">
            <div className="flex items-center gap-3">
              <LineChartIcon className="h-5 w-5 text-neon-yellow" />
              <h2 className="font-display text-xl font-bold uppercase">Score History</h2>
            </div>
            <div className="mt-5 h-[320px]">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData}>
                  <CartesianGrid stroke="rgba(255,255,255,0.08)" />
                  <XAxis dataKey="label" stroke="#94a3b8" tick={{ fontSize: 12 }} />
                  <YAxis stroke="#94a3b8" tick={{ fontSize: 12 }} />
                  <Tooltip contentStyle={{ background: "#090a16", border: "1px solid rgba(255,255,255,0.14)" }} />
                  <Line type="monotone" dataKey="score" stroke="#33f6ff" strokeWidth={3} dot={{ r: 3 }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </Card>
        </section>

        <section className="mt-5 grid gap-5 lg:grid-cols-[1fr_1fr]">
          <Card className="border-neon-purple/25 bg-white/[0.045] p-6">
            <Award className="h-7 w-7 text-neon-purple" />
            <h2 className="mt-4 font-display text-xl font-bold uppercase">Achievements</h2>
            <div className="mt-4 flex flex-wrap gap-2">
              {achievements.map((achievement) => (
                <Badge key={achievement.title} variant={achievement.unlocked ? "yellow" : "outline"}>
                  {achievement.title}
                </Badge>
              ))}
            </div>
          </Card>
          <Card className="border-neon-yellow/25 bg-white/[0.045] p-6">
            <Heart className="h-7 w-7 text-neon-yellow" />
            <h2 className="mt-4 font-display text-xl font-bold uppercase">Favorite Mode</h2>
            <p className="mt-4 text-3xl font-black text-white">{favoriteMode}</p>
          </Card>
        </section>
      </div>
    </main>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md border border-white/10 bg-black/20 p-4">
      <p className="text-xs uppercase tracking-[0.18em] text-slate-400">{label}</p>
      <p className="mt-2 font-display text-xl text-white">{value}</p>
    </div>
  );
}
