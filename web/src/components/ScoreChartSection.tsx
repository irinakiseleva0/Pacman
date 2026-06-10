import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { SectionTitle } from "@/components/SectionTitle";
import { Card } from "@/components/ui/card";
import type { ScorePoint } from "@/data/scores";

export default function ScoreChartSection({
  scoreHistory,
}: {
  scoreHistory: ScorePoint[];
}) {
  return (
    <section className="px-4 py-16 sm:px-8 sm:py-20 lg:px-10">
      <div className="mx-auto max-w-7xl">
        <SectionTitle
          eyebrow="Score telemetry"
          title="Run History Chart"
          description="Recharts powers a responsive score trend panel from the live leaderboard API."
        />
        <Card className="overflow-hidden border-neon-cyan/20 bg-white/[0.045] p-4 shadow-glow sm:p-6">
          <div className="mb-5 flex flex-wrap items-center justify-between gap-3">
            <div>
              <p className="font-display text-sm uppercase tracking-[0.24em] text-neon-cyan">
                Score signal
              </p>
              <p className="mt-2 text-sm text-slate-400">
                Live run history, split from the initial bundle.
              </p>
            </div>
            <div className="flex flex-wrap gap-3 text-xs text-slate-300">
              <span className="inline-flex items-center gap-2">
                <span className="h-2 w-2 rounded-full bg-neon-yellow" />
                Arcade
              </span>
              <span className="inline-flex items-center gap-2">
                <span className="h-2 w-2 rounded-full bg-neon-cyan" />
                Endless
              </span>
              <span className="inline-flex items-center gap-2">
                <span className="h-2 w-2 rounded-full bg-neon-purple" />
                Challenge
              </span>
            </div>
          </div>
          <div className="h-[320px] w-full sm:h-[380px]">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={scoreHistory} margin={{ left: -18, right: 12, top: 12 }}>
                <defs>
                  <linearGradient id="arcade" x1="0" x2="0" y1="0" y2="1">
                    <stop offset="5%" stopColor="#ffe66d" stopOpacity={0.42} />
                    <stop offset="95%" stopColor="#ffe66d" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="endless" x1="0" x2="0" y1="0" y2="1">
                    <stop offset="5%" stopColor="#33f6ff" stopOpacity={0.36} />
                    <stop offset="95%" stopColor="#33f6ff" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="challenge" x1="0" x2="0" y1="0" y2="1">
                    <stop offset="5%" stopColor="#b565ff" stopOpacity={0.36} />
                    <stop offset="95%" stopColor="#b565ff" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid stroke="rgba(255,255,255,0.08)" vertical={false} />
                <XAxis
                  dataKey="run"
                  stroke="#94a3b8"
                  tickLine={false}
                  axisLine={false}
                  tickMargin={10}
                />
                <YAxis
                  stroke="#94a3b8"
                  tickLine={false}
                  axisLine={false}
                  tickFormatter={(value) => `${Number(value) / 1000}k`}
                />
                <Tooltip
                  contentStyle={{
                    background: "#090a14",
                    border: "1px solid rgba(51, 246, 255, 0.3)",
                    borderRadius: "8px",
                    color: "#f8fafc",
                    boxShadow: "0 0 30px rgba(51, 246, 255, 0.18)",
                  }}
                  labelStyle={{ color: "#ffe66d" }}
                />
                <Area
                  type="monotone"
                  dataKey="arcade"
                  stroke="#ffe66d"
                  strokeWidth={3}
                  fill="url(#arcade)"
                />
                <Area
                  type="monotone"
                  dataKey="endless"
                  stroke="#33f6ff"
                  strokeWidth={3}
                  fill="url(#endless)"
                />
                <Area
                  type="monotone"
                  dataKey="challenge"
                  stroke="#b565ff"
                  strokeWidth={3}
                  fill="url(#challenge)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>
    </section>
  );
}
