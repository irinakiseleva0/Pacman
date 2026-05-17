import { type LucideIcon } from "lucide-react";
import { motion } from "framer-motion";

import { Card } from "@/components/ui/card";
import { cn } from "@/lib/utils";

interface StatCardProps {
  label: string;
  value: string;
  detail: string;
  icon: LucideIcon;
  accent?: "yellow" | "cyan" | "purple";
}

const accents = {
  yellow: "text-neon-yellow shadow-glow-yellow",
  cyan: "text-neon-cyan shadow-glow",
  purple: "text-neon-purple shadow-glow-purple",
};

export function StatCard({
  label,
  value,
  detail,
  icon: Icon,
  accent = "cyan",
}: StatCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 18 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.45 }}
    >
      <Card className="h-full border-white/10 bg-white/[0.045] p-5 backdrop-blur transition duration-300 hover:border-white/20 hover:bg-white/[0.06]">
        <div className="flex items-start justify-between gap-4">
          <div>
            <p className="text-xs uppercase tracking-[0.22em] text-slate-400">
              {label}
            </p>
            <p className="mt-3 font-display text-3xl font-black text-white">
              {value}
            </p>
          </div>
          <div
            className={cn(
              "rounded-md border border-current/30 bg-black/30 p-3",
              accents[accent],
            )}
          >
            <Icon className="h-5 w-5" />
          </div>
        </div>
        <p className="mt-4 text-sm text-slate-300">{detail}</p>
      </Card>
    </motion.div>
  );
}
