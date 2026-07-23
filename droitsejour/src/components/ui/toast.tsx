"use client";

import { toast as sonnerToast, Toaster as SonnerToaster } from "sonner";

export { SonnerToaster as Toaster };

export function toast(opts: { title?: string; description?: string; variant?: "default" | "destructive" }) {
  if (opts.variant === "destructive") {
    sonnerToast.error(opts.title || opts.description || "Erreur");
  } else {
    sonnerToast.success(opts.title || opts.description || "Succès");
  }
}
