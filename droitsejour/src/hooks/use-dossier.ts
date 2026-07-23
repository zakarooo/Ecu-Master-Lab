"use client";

import { useState, useEffect, useCallback } from "react";
import { Dossier } from "@/types";

export function useDossier(id?: string) {
  const [dossier, setDossier] = useState<Dossier | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDossier = useCallback(async () => {
    if (!id) {
      setLoading(false);
      return;
    }
    try {
      const res = await fetch(`/api/dossiers/${id}`);
      if (!res.ok) throw new Error("Dossier non trouvé");
      const data = await res.json();
      setDossier(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erreur inconnue");
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect -- standard async data fetch on mount
    fetchDossier();
  }, [fetchDossier]);

  const updateDossier = async (data: Partial<Dossier>) => {
    if (!id) return;
    try {
      const res = await fetch(`/api/dossiers/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
      if (res.ok) {
        const updated = await res.json();
        setDossier(updated);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erreur de mise à jour");
    }
  };

  return { dossier, loading, error, updateDossier, refetch: fetchDossier };
}
