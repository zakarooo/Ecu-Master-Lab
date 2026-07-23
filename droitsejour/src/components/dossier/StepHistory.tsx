"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Clock, Plus, Trash2, Edit2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { generateId } from "@/lib/utils";
import type { Dossier, DemarchePrecedente } from "@/types";

interface StepProps {
  dossier: Dossier;
  onUpdate: (data: Partial<Dossier>) => void;
  onNext: () => void;
  onPrev: () => void;
}

interface DemarcheForm {
  date: string;
  type: string;
  description: string;
  resultat: string;
  administration: string;
  documentsFournis: string;
}

const EMPTY_FORM: DemarcheForm = {
  date: "",
  type: "",
  description: "",
  resultat: "",
  administration: "",
  documentsFournis: "",
};

export default function StepHistory({ dossier, onUpdate, onNext, onPrev }: StepProps) {
  const [demarches, setDemarches] = useState<DemarchePrecedente[]>(dossier.demarchesPrecedentes ?? []);
  const [form, setForm] = useState<DemarcheForm>(EMPTY_FORM);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);

  const [formError, setFormError] = useState<string | null>(null);

  const handleChange = (field: keyof DemarcheForm, value: string) => {
    setForm((prev) => ({ ...prev, [field]: value }));
    setFormError(null);
  };

  const validateForm = (): boolean => {
    if (!form.date) { setFormError("La date est requise"); return false; }
    if (!form.type.trim()) { setFormError("Le type de démarche est requis"); return false; }
    if (!form.description.trim()) { setFormError("La description est requise"); return false; }
    if (!form.resultat.trim()) { setFormError("Le résultat est requis"); return false; }
    if (!form.administration.trim()) { setFormError("L'administration est requise"); return false; }
    return true;
  };

  const handleAdd = () => {
    if (!validateForm()) return;
    if (editingId) {
      setDemarches((prev) =>
        prev.map((d) =>
          d.id === editingId
            ? {
                ...d,
                ...form,
                documentsFournis: form.documentsFournis.split(",").map((s) => s.trim()).filter(Boolean),
              }
            : d
        )
      );
    } else {
      const newDemarche: DemarchePrecedente = {
        id: generateId(),
        ...form,
        documentsFournis: form.documentsFournis.split(",").map((s) => s.trim()).filter(Boolean),
      };
      setDemarches((prev) => [...prev, newDemarche]);
    }
    setForm(EMPTY_FORM);
    setEditingId(null);
    setShowForm(false);
  };

  const handleEdit = (d: DemarchePrecedente) => {
    setForm({
      date: d.date,
      type: d.type,
      description: d.description,
      resultat: d.resultat,
      administration: d.administration,
      documentsFournis: d.documentsFournis.join(", "),
    });
    setEditingId(d.id);
    setShowForm(true);
  };

  const handleRemove = (id: string) => {
    setDemarches((prev) => prev.filter((d) => d.id !== id));
  };

  const handleSave = () => {
    onUpdate({ demarchesPrecedentes: demarches });
    onNext();
  };

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}>
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Clock className="h-5 w-5" />
            Historique des démarches
          </CardTitle>
          <CardDescription>
            Listez toutes les démarches administratives déjà effectuées et leurs résultats.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {demarches.length > 0 && (
            <div className="space-y-3">
              {demarches.map((d) => (
                <div key={d.id} className="border rounded-lg p-4 space-y-2">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-semibold">{d.type}</span>
                        <span className="text-xs text-muted-foreground">{d.date}</span>
                      </div>
                      <p className="text-sm text-muted-foreground mt-1">{d.description}</p>
                      <p className="text-sm mt-1">
                        <span className="font-medium">Résultat :</span> {d.resultat}
                      </p>
                      <p className="text-sm text-muted-foreground">
                        <span className="font-medium">Administration :</span> {d.administration}
                      </p>
                      {d.documentsFournis.length > 0 && (
                        <p className="text-xs text-muted-foreground mt-1">
                          Documents : {d.documentsFournis.join(", ")}
                        </p>
                      )}
                    </div>
                    <div className="flex gap-1">
                      <Button variant="ghost" size="icon" onClick={() => handleEdit(d)} aria-label="Modifier la démarche">
                        <Edit2 className="h-4 w-4" />
                      </Button>
                      <Button variant="ghost" size="icon" onClick={() => handleRemove(d.id)} aria-label="Supprimer la démarche">
                        <Trash2 className="h-4 w-4 text-destructive" />
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {!showForm && (
            <Button
              type="button"
              variant="outline"
              onClick={() => { setForm(EMPTY_FORM); setEditingId(null); setShowForm(true); }}
            >
              <Plus className="h-4 w-4 mr-1" />
              Ajouter une démarche
            </Button>
          )}

          {showForm && (
            <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: "auto" }} className="border rounded-lg p-4 space-y-3">
              <h3 className="text-sm font-semibold">
                {editingId ? "Modifier la démarche" : "Nouvelle démarche"}
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div className="space-y-2">
                  <Label>Date</Label>
                  <Input type="date" value={form.date} onChange={(e) => handleChange("date", e.target.value)} />
                </div>
                <div className="space-y-2">
                  <Label>Type</Label>
                  <Input value={form.type} onChange={(e) => handleChange("type", e.target.value)} placeholder="Ex: Demande de titre de séjour" />
                </div>
                <div className="space-y-2">
                  <Label>Administration</Label>
                  <Input value={form.administration} onChange={(e) => handleChange("administration", e.target.value)} placeholder="Ex: Préfecture de Paris" />
                </div>
                <div className="space-y-2">
                  <Label>Résultat</Label>
                  <Input value={form.resultat} onChange={(e) => handleChange("resultat", e.target.value)} placeholder="Ex: Accepté, Refusé..." />
                </div>
              </div>
              <div className="space-y-2">
                <Label>Description</Label>
                <Textarea value={form.description} onChange={(e) => handleChange("description", e.target.value)} placeholder="Décrivez la démarche effectuée..." rows={2} />
              </div>
              <div className="space-y-2">
                <Label>Documents fournis (séparés par des virgules)</Label>
                <Input value={form.documentsFournis} onChange={(e) => handleChange("documentsFournis", e.target.value)} placeholder="Ex: Passeport, Justificatif de domicile" />
              </div>
              <div className="flex gap-2">
                <Button type="button" onClick={handleAdd}>
                  {editingId ? "Enregistrer" : "Ajouter"}
                </Button>
                <Button type="button" variant="ghost" onClick={() => { setShowForm(false); setEditingId(null); setForm(EMPTY_FORM); setFormError(null); }}>
                  Annuler
                </Button>
              </div>
              {formError && <p className="text-sm text-destructive">{formError}</p>}
            </motion.div>
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
