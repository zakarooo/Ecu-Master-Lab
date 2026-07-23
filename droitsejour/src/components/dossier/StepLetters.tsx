"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Mail, Loader2, RefreshCw, FileText } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { getTodayISO } from "@/lib/utils";
import type { Dossier, Courrier, TypeCourrier } from "@/types";

interface StepProps {
  dossier: Dossier;
  onUpdate: (data: Partial<Dossier>) => void;
  onNext: () => void;
  onPrev: () => void;
}

const LETTER_TYPES: Array<{ type: TypeCourrier; title: string; description: string }> = [
  { type: "demande_info", title: "Demande d'information", description: "Demander des informations sur l'état d'un dossier" },
  { type: "demande_rendez_vous", title: "Demande de rendez-vous", description: "Prendre rendez-vous avec une administration" },
  { type: "recours", title: "Recours", description: "Contester une décision administrative" },
  { type: "relance", title: "Relance", description: "Relancer une demande en attente" },
  { type: "communication_dossier", title: "Communication de dossier", description: "Demander l'accès à son dossier administratif" },
  { type: "courrier_libre", title: "Courrier libre", description: "Rédiger un courrier personnalisé" },
];

export default function StepLetters({ dossier, onUpdate, onNext, onPrev }: StepProps) {
  const [courriers, setCourriers] = useState<Courrier[]>(dossier.courriers ?? []);
  const [generatingType, setGeneratingType] = useState<TypeCourrier | null>(null);
  const [selectedCourrier, setSelectedCourrier] = useState<Courrier | null>(null);

  const handleGenerate = async (type: TypeCourrier) => {
    setGeneratingType(type);
    try {
      const response = await fetch(`/api/dossiers/${dossier.id}/letters`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ type }),
      });

      if (!response.ok) throw new Error("Erreur lors de la génération");

      const result = await response.json();
      const courrier: Courrier = {
        id: result.id ?? crypto.randomUUID(),
        type,
        titre: result.titre ?? LETTER_TYPES.find((l) => l.type === type)?.title ?? "",
        contenu: result.contenu ?? "",
        destinataire: result.destinataire ?? "",
        dateCreation: getTodayISO(),
        personnalise: false,
      };

      setCourriers((prev) => [...prev, courrier]);
      setSelectedCourrier(courrier);
    } catch {
      // silently fail
    } finally {
      setGeneratingType(null);
    }
  };

  const handleRegenerate = async (courrier: Courrier) => {
    setGeneratingType(courrier.type);
    try {
      const response = await fetch(`/api/dossiers/${dossier.id}/letters`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ type: courrier.type }),
      });

      if (!response.ok) throw new Error("Erreur lors de la régénération");

      const result = await response.json();
      const updated: Courrier = {
        ...courrier,
        contenu: result.contenu ?? courrier.contenu,
        dateCreation: getTodayISO(),
      };

      setCourriers((prev) => prev.map((c) => (c.id === courrier.id ? updated : c)));
      setSelectedCourrier(updated);
    } catch {
      // silently fail
    } finally {
      setGeneratingType(null);
    }
  };

  const handleSave = () => {
    onUpdate({ courriers });
    onNext();
  };

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}>
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Mail className="h-5 w-5" />
            Courriers
          </CardTitle>
          <CardDescription>
            Générez des courriers administratifs à partir des informations du dossier.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {LETTER_TYPES.map((lt) => (
              <Card
                key={lt.type}
                className="cursor-pointer hover:border-primary transition-colors"
                onClick={() => handleGenerate(lt.type)}
              >
                <CardContent className="p-4 space-y-2">
                  <div className="flex items-center justify-between">
                    <h4 className="text-sm font-semibold">{lt.title}</h4>
                    {generatingType === lt.type && (
                      <Loader2 className="h-4 w-4 animate-spin text-primary" />
                    )}
                  </div>
                  <p className="text-xs text-muted-foreground">{lt.description}</p>
                </CardContent>
              </Card>
            ))}
          </div>

          {courriers.length > 0 && (
            <div className="space-y-3">
              <h3 className="font-semibold text-sm">Courriers générés</h3>
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
                <div className="space-y-2">
                  {courriers.map((c) => (
                    <div
                      key={c.id}
                      onClick={() => setSelectedCourrier(c)}
                      className={`border rounded-lg p-3 cursor-pointer transition-colors ${
                        selectedCourrier?.id === c.id ? "border-primary bg-primary/5" : "hover:border-muted-foreground/50"
                      }`}
                    >
                      <div className="flex items-center gap-2">
                        <FileText className="h-4 w-4 text-muted-foreground" />
                        <span className="text-sm font-medium">{c.titre}</span>
                      </div>
                    </div>
                  ))}
                </div>

                <div className="lg:col-span-2">
                  {selectedCourrier && (
                    <div className="border rounded-lg p-4 space-y-3">
                      <div className="flex items-center justify-between">
                        <h4 className="font-semibold text-sm">{selectedCourrier.titre}</h4>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleRegenerate(selectedCourrier)}
                          disabled={generatingType !== null}
                        >
                          <RefreshCw className="h-4 w-4 mr-1" />
                          Régénérer
                        </Button>
                      </div>
                      <ScrollArea className="h-64">
                        <div className="text-sm whitespace-pre-wrap">{selectedCourrier.contenu}</div>
                      </ScrollArea>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          <div className="flex justify-between pt-4">
            <Button type="button" variant="outline" onClick={onPrev}>
              Précédent
            </Button>
            <Button type="button" onClick={handleSave}>
              Suivant
            </Button>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}
