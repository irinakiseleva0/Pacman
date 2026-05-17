import { type LucideIcon } from "lucide-react";
import { motion } from "framer-motion";

import { Card } from "@/components/ui/card";

interface FeatureCardProps {
  title: string;
  description: string;
  icon: LucideIcon;
  signal: string;
}

export function FeatureCard({
  title,
  description,
  icon: Icon,
  signal,
}: FeatureCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.5 }}
      whileHover={{ y: -5 }}
    >
      <Card className="group relative h-full overflow-hidden border-white/10 bg-white/[0.04] p-6 backdrop-blur transition duration-300 hover:border-neon-cyan/50 hover:bg-neon-cyan/[0.045] hover:shadow-glow">
        <div className="pointer-events-none absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-neon-cyan/60 to-transparent opacity-0 transition group-hover:opacity-100" />
        <div className="flex items-center justify-between gap-4">
          <div className="rounded-md border border-neon-cyan/25 bg-neon-cyan/10 p-3 text-neon-cyan">
            <Icon className="h-5 w-5" />
          </div>
          <span className="font-display text-xs uppercase tracking-[0.22em] text-neon-yellow">
            {signal}
          </span>
        </div>
        <h3 className="mt-6 font-display text-xl font-bold text-white">{title}</h3>
        <p className="mt-3 leading-7 text-slate-300">{description}</p>
      </Card>
    </motion.div>
  );
}
