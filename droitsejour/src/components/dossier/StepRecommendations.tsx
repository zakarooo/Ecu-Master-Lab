"use client";

import { motion } from "framer-motion";
import { Lightbulb, ListOrdered, Building2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import type { Dossier } from "@/types";

interface StepProps {
  dossier: Dossier;
  onUpdate: (data: Partial<Dossier>) => void;
  onNext: () => void;
  onPrev: () => void;
}

const PRIORITY_CONFIG = {
  haute: { label: "Haute", className: "bg-red-100 text-red-800 border-red-200" },
  moyenne: { label: "Moyenne", className: "bg-yellow-100 text-yellow-800 border-yellow-200" },
  basse: { label: "Basse", className: "bg-green-100 text-green-800 border-green-200" },
};

export default function StepRecommendations({ dossier, onNext, onPrev }: StepProps) {
  const analyse = dossier.analyse;

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}>
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Lightbulb className="h-5 w-5" />
            Recommandations
          </CardTitle>
          <CardDescription>
            Découvrez les démarches recommandées et l&apos;ordre d&apos;actions à suivre.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {!analyse ? (
            <p className="text-sm text-muted-foreground text-center py-8">
              Lancez l&apos;analyse à l&apos;étape précédente pour obtenir des recommandations.
            </p>
          ) : (
            <>
              {analyse.demarchesRecommandees.length > 0 && (
                <div className="space-y-3">
                  <h3 className="font-semibold flex items-center gap-2">
                    <Lightbulb className="h-4 w-4" />
                    Démarches recommandées
                  </h3>
                  {analyse.demarchesRecommandees.map((d, i) => {
                    const priority = PRIORITY_CONFIG[d.priorite];
                    return (
                      <div key={i} className="border rounded-lg p-4 space-y-2">
                        <div className="flex items-start justify-between">
                          <h4 className="text-sm font-semibold">{d.titre}</h4>
                          <Badge className={cn("shrink-0", priority.className)}>
                            {priority.label}
                          </Badge>
                        </div>
                        <p className="text-sm text-muted-foreground">{d.description}</p>
                        {d.delai && (
                          <p className="text-xs text-muted-foreground">
                            Délai recommandé : {d.delai}
                          </p>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}

              {analyse.ordreActions.length > 0 && (
                <div className="space-y-3">
                  <h3 className="font-semibold flex items-center gap-2">
                    <ListOrdered className="h-4 w-4" />
                    Ordre des actions
                  </h3>
                  <ol className="space-y-2">
                    {analyse.ordreActions.map((action, i) => (
                      <li key={i} className="flex items-start gap-3 text-sm">
                        <span className="flex items-center justify-center h-6 w-6 rounded-full bg-primary text-primary-foreground text-xs font-bold shrink-0">
                          {i + 1}
                        </span>
                        <span className="pt-0.5">{action}</span>
                      </li>
                    ))}
                  </ol>
                </div>
              )}

              {analyse.administrationsConcernees.length > 0 && (
                <div className="space-y-3">
                  <h3 className="font-semibold flex items-center gap-2">
                    <Building2 className="h-4 w-4" />
                    Administrations concernées
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {analyse.administrationsConcernees.map((admin, i) => (
                      <Badge key={i} variant="secondary">
                        {admin}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}
            </>
          )}

          <div className="flex justify-between pt-4">
            <Button type="button" variant="outline" onClick={onPrev}>
              Précédent
            </Button>
            <Button type="button" onClick={onNext}>
              Suivant
            </Button>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}
