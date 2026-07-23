"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { CheckSquare, Check, Square } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { Progress } from "@/components/ui/progress";
import { cn } from "@/lib/utils";
import type { Dossier, ChecklistItem } from "@/types";

interface StepProps {
  dossier: Dossier;
  onUpdate: (data: Partial<Dossier>) => void;
  onNext: () => void;
  onPrev: () => void;
}

function buildDefaultChecklist(dossier: Dossier): ChecklistItem[] {
  if (dossier.checklist && dossier.checklist.length > 0) return dossier.checklist;
  const analyse = dossier.analyse;
  const items: ChecklistItem[] = [];

  items.push(
    { id: "c1", document: "Passeport en cours de validité", description: "Passeport du demandeur valide", obligatoire: true, coche: false, categorie: "Documents d'identité" },
    { id: "c2", document: "Justificatif de domicile", description: "Facture ou attestation d'hébergement", obligatoire: true, coche: false, categorie: "Documents d'identité" },
    { id: "c3", document: "Photographies d'identité", description: "Photos au format officiel", obligatoire: true, coche: false, categorie: "Documents d'identité" },
    { id: "c4", document: "Justificatif de situation familiale", description: "Livret de famille ou acte de mariage", obligatoire: false, coche: false, categorie: "Situation familiale" },
    { id: "c5", document: "Justificatif d'emploi", description: "Contrat de travail ou attestation employeur", obligatoire: false, coche: false, categorie: "Situation professionnelle" },
    { id: "c6", document: "Justificatif de ressources", description: "Bulletins de salaire ou avis d'imposition", obligatoire: false, coche: false, categorie: "Situation professionnelle" },
    { id: "c7", document: "Couverture maladie", description: "Atestation de sécurité sociale ou mutuelle", obligatoire: false, coche: false, categorie: "Santé" },
  );

  if (analyse?.documentsManquants) {
    analyse.documentsManquants.forEach((doc, i) => {
      items.push({
        id: `am${i}`,
        document: doc,
        description: `Document manquant identifié par l'analyse IA`,
        obligatoire: false,
        coche: false,
        categorie: "Documents manquants",
      });
    });
  }

  return items;
}

export default function StepChecklist({ dossier, onUpdate, onNext, onPrev }: StepProps) {
  const [items, setItems] = useState<ChecklistItem[]>(buildDefaultChecklist(dossier));

  const toggleItem = (id: string) => {
    setItems((prev) => prev.map((item) => (item.id === id ? { ...item, coche: !item.coche } : item)));
  };

  const totalItems = items.length;
  const checkedItems = items.filter((i) => i.coche).length;
  const progress = totalItems > 0 ? Math.round((checkedItems / totalItems) * 100) : 0;

  const categories = Array.from(new Set(items.map((i) => i.categorie)));

  const handleSave = () => {
    onUpdate({ checklist: items });
    onNext();
  };

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}>
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <CheckSquare className="h-5 w-5" />
            Checklist
          </CardTitle>
          <CardDescription>
            Suivez l&apos;avancement de la constitution du dossier.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted-foreground">{checkedItems} / {totalItems} éléments cochés</span>
              <span className="font-medium">{progress}%</span>
            </div>
            <Progress value={progress} />
          </div>

          {categories.map((cat) => (
            <div key={cat} className="space-y-2">
              <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide">{cat}</h3>
              <div className="space-y-1">
                {items.filter((i) => i.categorie === cat).map((item) => (
                  <div
                    key={item.id}
                    className={cn(
                      "flex items-center gap-3 p-3 rounded-lg border transition-colors",
                      item.coche ? "bg-primary/5 border-primary/20" : "hover:bg-muted/50"
                    )}
                  >
                    <Checkbox
                      id={item.id}
                      checked={item.coche}
                      onCheckedChange={() => toggleItem(item.id)}
                    />
                    <div className="flex-1">
                      <label
                        htmlFor={item.id}
                        className={cn(
                          "text-sm font-medium cursor-pointer",
                          item.coche && "line-through text-muted-foreground"
                        )}
                      >
                        {item.document}
                        {item.obligatoire && (
                          <span className="ml-1 text-destructive text-xs">*</span>
                        )}
                      </label>
                      <p className="text-xs text-muted-foreground">{item.description}</p>
                    </div>
                    {item.coche && <Check className="h-4 w-4 text-primary" />}
                    {!item.coche && <Square className="h-4 w-4 text-muted-foreground/30" />}
                  </div>
                ))}
              </div>
            </div>
          ))}

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
