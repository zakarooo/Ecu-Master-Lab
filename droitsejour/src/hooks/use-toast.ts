"use client";

import { toast as sonnerToast } from "sonner";

export function useToast() {
  return {
    toast: (opts: { title?: string; description?: string; variant?: "default" | "destructive" }) => {
      if (opts.variant === "destructive") {
        sonnerToast.error(opts.title || opts.description || "Erreur");
      } else {
        sonnerToast(opts.title || opts.description || "");
      }
    },
  };
}
