"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Brain, Loader2, CheckCircle2, AlertTriangle, FileQuestion, ThumbsUp, ShieldAlert } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import type { Dossier, AnalyseResultat } from "@/types";

interface StepProps {
  dossier: Dossier;
  onUpdate: (data: Partial<Dossier>) => void;
  onNext: () => void;
  onPrev: () => void;
}

export default function StepAnalysis({ dossier, onUpdate, onNext, onPrev }: StepProps) {
  const [analyse, setAnalyse] = useState<AnalyseResultat | undefined>(dossier.analyse);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleAnalyze = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`/api/dossiers/${dossier.id}/analyse`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      });
      if (!response.ok) throw new Error("Erreur lors de l'analyse");
      const result: AnalyseResultat = await response.json();
      setAnalyse(result);
      onUpdate({ analyse: result });
    } catch {
      setError("Une erreur est survenue lors de l'analyse. Veuillez réessayer.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}>
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Brain className="h-5 w-5" />
            Analyse IA
          </CardTitle>
          <CardDescription>
            Lancez l&apos;analyse automatique du dossier pour obtenir un diagnostic personnalisé.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {!analyse && !loading && (
            <div className="text-center py-8">
              <Brain className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
              <p className="text-muted-foreground mb-4">
                Cliquez sur le bouton ci-dessous pour lancer l&apos;analyse du dossier.
              </p>
              <Button onClick={handleAnalyze}>
                <Brain className="h-4 w-4 mr-2" />
                Lancer l&apos;analyse
              </Button>
            </div>
          )}

          {loading && (
            <div className="text-center py-8">
              <motion.div animate={{ rotate: 360 }} transition={{ duration: 2, repeat: Infinity, ease: "linear" }}>
                <Loader2 className="h-12 w-12 mx-auto text-primary" />
              </motion.div>
              <p className="text-muted-foreground mt-4">Analyse en cours...</p>
            </div>
          )}

          {error && (
            <div className="text-center py-8">
              <AlertTriangle className="h-12 w-12 mx-auto text-destructive mb-4" />
              <p className="text-destructive mb-4">{error}</p>
              <Button onClick={handleAnalyze} variant="outline">
                Réessayer
              </Button>
            </div>
          )}

          {analyse && (
            <div className="space-y-6">
              <div className="space-y-2">
                <h3 className="flex items-center gap-2 font-semibold">
                  <CheckCircle2 className="h-4 w-4 text-primary" />
                  Résumé
                </h3>
                <p className="text-sm text-muted-foreground">{analyse.resume}</p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <h3 className="flex items-center gap-2 font-semibold text-green-700">
                    <ThumbsUp className="h-4 w-4" />
                    Forces
                  </h3>
                  <ul className="space-y-1">
                    {analyse.forces.map((f, i) => (
                      <li key={i} className="text-sm text-green-600 flex items-start gap-2">
                        <span className="text-green-500 mt-0.5">+</span>
                        {f}
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="space-y-2">
                  <h3 className="flex items-center gap-2 font-semibold text-red-700">
                    <AlertTriangle className="h-4 w-4" />
                    Faiblesses
                  </h3>
                  <ul className="space-y-1">
                    {analyse.faiblesses.map((f, i) => (
                      <li key={i} className="text-sm text-red-600 flex items-start gap-2">
                        <span className="text-red-500 mt-0.5">-</span>
                        {f}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>

              <div className="space-y-2">
                <h3 className="flex items-center gap-2 font-semibold">
                  <FileQuestion className="h-4 w-4 text-amber-600" />
                  Documents manquants
                </h3>
                <ul className="space-y-1">
                  {analyse.documentsManquants.map((d, i) => (
                    <li key={i} className="text-sm text-amber-600 flex items-start gap-2">
                      <span className="mt-0.5">•</span>
                      {d}
                    </li>
                  ))}
                </ul>
              </div>

              <div className="space-y-2">
                <h3 className="flex items-center gap-2 font-semibold text-green-700">
                  <ThumbsUp className="h-4 w-4" />
                  Arguments favorables
                </h3>
                <ul className="space-y-1">
                  {analyse.argumentsFavorables.map((a, i) => (
                    <li key={i} className="text-sm text-green-600 flex items-start gap-2">
                      <span className="mt-0.5">•</span>
                      {a}
                    </li>
                  ))}
                </ul>
              </div>

              <div className="space-y-2">
                <h3 className="flex items-center gap-2 font-semibold text-red-700">
                  <ShieldAlert className="h-4 w-4" />
                  Risques
                </h3>
                <ul className="space-y-1">
                  {analyse.risques.map((r, i) => (
                    <li key={i} className="text-sm text-red-600 flex items-start gap-2">
                      <span className="mt-0.5">!</span>
                      {r}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          )}

          <div className="flex justify-between pt-4">
            <Button type="button" variant="outline" onClick={onPrev}>
              Précédent
            </Button>
            <Button type="button" onClick={onNext} disabled={loading}>
              Suivant
            </Button>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}
