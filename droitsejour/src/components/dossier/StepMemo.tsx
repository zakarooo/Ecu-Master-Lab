"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { StickyNote, Plus, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { generateId, getTodayISO, formatDate } from "@/lib/utils";
import type { Dossier, Memo } from "@/types";

interface StepProps {
  dossier: Dossier;
  onUpdate: (data: Partial<Dossier>) => void;
  onNext: () => void;
  onPrev: () => void;
}

export default function StepMemo({ dossier, onUpdate, onNext, onPrev }: StepProps) {
  const [memos, setMemos] = useState<Memo[]>(dossier.memos ?? []);
  const [contenu, setContenu] = useState("");
  const [error, setError] = useState<string | null>(null);

  const handleAdd = () => {
    if (!contenu.trim()) return;
    if (contenu.trim().length < 10) {
      setError("Le mémo doit contenir au moins 10 caractères");
      return;
    }
    setError(null);
    const now = getTodayISO();
    const memo: Memo = {
      id: generateId(),
      contenu: contenu.trim(),
      dateCreation: now,
      dateModification: now,
    };
    setMemos((prev) => [...prev, memo]);
    setContenu("");
  };

  const handleRemove = (id: string) => {
    setMemos((prev) => prev.filter((m) => m.id !== id));
  };

  const handleSave = () => {
    onUpdate({ memos });
    onNext();
  };

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}>
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <StickyNote className="h-5 w-5" />
            Mémo
          </CardTitle>
          <CardDescription>
            Ajoutez des notes personnelles ou des observations importantes pour le dossier.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Textarea
              value={contenu}
              onChange={(e) => setContenu(e.target.value)}
              placeholder="Écrivez votre mémo ici..."
              rows={4}
            />
            <Button type="button" onClick={handleAdd} disabled={!contenu.trim()}>
              <Plus className="h-4 w-4 mr-1" />
              Ajouter le mémo
            </Button>
            {error && <p className="text-sm text-destructive">{error}</p>}
          </div>

          {memos.length > 0 && (
            <div className="space-y-3">
              {memos.map((memo) => (
                <div key={memo.id} className="border rounded-lg p-3 space-y-1">
                  <div className="flex items-start justify-between">
                    <p className="text-sm whitespace-pre-wrap flex-1">{memo.contenu}</p>
                    <Button variant="ghost" size="icon" onClick={() => handleRemove(memo.id)} aria-label="Supprimer le mémo">
                      <Trash2 className="h-4 w-4 text-destructive" />
                    </Button>
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Créé le {formatDate(memo.dateCreation)}
                  </p>
                </div>
              ))}
            </div>
          )}

          {memos.length === 0 && (
            <p className="text-sm text-muted-foreground text-center py-4">
              Aucun mémo pour le moment.
            </p>
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
