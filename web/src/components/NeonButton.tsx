import {
  cloneElement,
  isValidElement,
  type ComponentPropsWithoutRef,
  type ReactElement,
  type ReactNode,
} from "react";
import { motion } from "framer-motion";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

type NeonButtonProps = ComponentPropsWithoutRef<typeof Button> & {
  glow?: "yellow" | "cyan" | "purple";
};

const glowStyles = {
  yellow:
    "border-neon-yellow/60 bg-neon-yellow text-black shadow-glow-yellow hover:bg-neon-yellow/90",
  cyan: "border-neon-cyan/60 bg-neon-cyan text-black shadow-glow hover:bg-neon-cyan/90",
  purple:
    "border-neon-purple/70 bg-neon-purple text-white shadow-glow-purple hover:bg-neon-purple/90",
};

export function NeonButton({
  className,
  glow = "yellow",
  children,
  ...props
}: NeonButtonProps) {
  const buttonClassName = cn(
    "group relative min-h-11 overflow-hidden border font-display uppercase tracking-[0.18em] focus-visible:ring-offset-2 focus-visible:ring-offset-neon-ink",
    glowStyles[glow],
    className,
  );

  if (props.asChild && isValidElement(children)) {
    const child = children as ReactElement<{ children?: ReactNode }>;

    return (
      <motion.div whileHover={{ y: -2, scale: 1.02 }} whileTap={{ scale: 0.98 }}>
        <Button className={buttonClassName} {...props}>
          {cloneElement(child, undefined, (
            <>
              <span className="absolute inset-0 -translate-x-full bg-white/25 transition-transform duration-500 group-hover:translate-x-full" />
              <span className="relative z-10 flex items-center gap-2">{child.props.children}</span>
            </>
          ))}
        </Button>
      </motion.div>
    );
  }

  return (
    <motion.div whileHover={{ y: -2, scale: 1.02 }} whileTap={{ scale: 0.98 }}>
      <Button
        className={buttonClassName}
        {...props}
      >
        <span className="absolute inset-0 -translate-x-full bg-white/25 transition-transform duration-500 group-hover:translate-x-full" />
        <span className="relative z-10 flex items-center gap-2">{children}</span>
      </Button>
    </motion.div>
  );
}
