import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function getStatusColor(status: string) {
  const colors: Record<string, string> = {
    pending: "text-yellow-400 bg-yellow-400/10 border-yellow-400/30",
    analyzing: "text-blue-400 bg-blue-400/10 border-blue-400/30",
    analyzed: "text-emerald-400 bg-emerald-400/10 border-emerald-400/30",
    processing: "text-purple-400 bg-purple-400/10 border-purple-400/30",
    completed: "text-green-400 bg-green-400/10 border-green-400/30",
    failed: "text-red-400 bg-red-400/10 border-red-400/30",
    needs_review: "text-orange-400 bg-orange-400/10 border-orange-400/30",
  };
  return colors[status] || "text-gray-400 bg-gray-400/10";
}

export function getStatusLabel(status: string) {
  const labels: Record<string, string> = {
    pending: "En attente",
    analyzing: "Analyse IA",
    analyzed: "Analysé",
    processing: "En cours",
    completed: "Modifié",
    failed: "Échoué",
    needs_review: "Revue requise",
  };
  return labels[status] || status;
}
