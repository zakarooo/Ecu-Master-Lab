"use client";

import { useForm, useFieldArray } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { motion } from "framer-motion";
import { Users, Plus, Trash2 } from "lucide-react";
import { familySituationSchema, type FamilySituationFormData } from "@/features/dossier/dossier-schema";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { NATIONALITES_FREQUENTES } from "@/lib/constants";
import type { Dossier } from "@/types";

interface StepProps {
  dossier: Dossier;
  onUpdate: (data: Partial<Dossier>) => void;
  onNext: () => void;
  onPrev: () => void;
}

export default function StepFamilySituation({ dossier, onUpdate, onNext, onPrev }: StepProps) {
  const {
    register,
    handleSubmit,
    setValue,
    watch,
    control,
    formState: { errors },
  } = useForm<FamilySituationFormData>({
    resolver: zodResolver(familySituationSchema),
    defaultValues: {
      situation: dossier.situationFamiliale?.situation ?? "celibataire",
      conjoint: dossier.situationFamiliale?.conjoint ?? { nom: "", prenom: "", nationalite: "", statutSejour: "" },
      enfants: dossier.situationFamiliale?.enfants ?? [],
      familleEnFrance: dossier.situationFamiliale?.familleEnFrance ?? false,
      membresFamille: dossier.situationFamiliale?.membresFamille ?? "",
    },
  });

  const { fields: enfantFields, append: addEnfant, remove: removeEnfant } = useFieldArray({
    control,
    name: "enfants",
  });

  const situation = watch("situation");
  const familleEnFrance = watch("familleEnFrance");
  const showConjoint = situation === "marie" || situation === "pacse";

  const onSubmit = (data: FamilySituationFormData) => {
    onUpdate({ situationFamiliale: data });
    onNext();
  };

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}>
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Users className="h-5 w-5" />
            Situation familiale
          </CardTitle>
          <CardDescription>
            Décrivez la situation familiale du demandeur et les membres de sa famille.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            <div className="space-y-2">
              <Label>Situation</Label>
              <Select
                value={situation}
                onValueChange={(v) => setValue("situation", v as FamilySituationFormData["situation"], { shouldValidate: true })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Sélectionnez la situation" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="celibataire">Célibataire</SelectItem>
                  <SelectItem value="marie">Marié(e)</SelectItem>
                  <SelectItem value="divorce">Divorcé(e)</SelectItem>
                  <SelectItem value="veuf">Veuf/ve</SelectItem>
                  <SelectItem value="pacse">Pacsé(e)</SelectItem>
                  <SelectItem value="concubin">Concubin(e)</SelectItem>
                </SelectContent>
              </Select>
              {errors.situation && <p className="text-sm text-destructive">{errors.situation.message}</p>}
            </div>

            {showConjoint && (
              <div className="border rounded-lg p-4 space-y-4">
                <h3 className="text-sm font-semibold">Informations sur le conjoint</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="conjoint.nom">Nom du conjoint</Label>
                    <Input id="conjoint.nom" {...register("conjoint.nom")} placeholder="Nom" />
                    {errors.conjoint?.nom && <p className="text-sm text-destructive">{errors.conjoint.nom.message}</p>}
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="conjoint.prenom">Prénom du conjoint</Label>
                    <Input id="conjoint.prenom" {...register("conjoint.prenom")} placeholder="Prénom" />
                    {errors.conjoint?.prenom && <p className="text-sm text-destructive">{errors.conjoint.prenom.message}</p>}
                  </div>
                  <div className="space-y-2">
                    <Label>Nationalité du conjoint</Label>
                    <Select
                      value={watch("conjoint.nationalite") || undefined}
                      onValueChange={(v) => setValue("conjoint.nationalite", v, { shouldValidate: true })}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Sélectionnez" />
                      </SelectTrigger>
                      <SelectContent>
                        {NATIONALITES_FREQUENTES.map((n) => (
                          <SelectItem key={n} value={n}>{n}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    {errors.conjoint?.nationalite && <p className="text-sm text-destructive">{errors.conjoint.nationalite.message}</p>}
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="conjoint.statutSejour">Statut de séjour du conjoint</Label>
                    <Input id="conjoint.statutSejour" {...register("conjoint.statutSejour")} placeholder="Ex: Régulier" />
                  </div>
                </div>
              </div>
            )}

            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-semibold">Enfants</h3>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => addEnfant({ nom: "", prenom: "", dateNaissance: "", nationalite: "" })}
                >
                  <Plus className="h-4 w-4 mr-1" />
                  Ajouter un enfant
                </Button>
              </div>
              {enfantFields.map((field, index) => (
                <div key={field.id} className="border rounded-lg p-4 space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-medium text-muted-foreground">Enfant {index + 1}</span>
                    <Button type="button" variant="ghost" size="sm" onClick={() => removeEnfant(index)}>
                      <Trash2 className="h-4 w-4 text-destructive" />
                    </Button>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    <div className="space-y-2">
                      <Label htmlFor={`enfants.${index}.nom`}>Nom</Label>
                      <Input id={`enfants.${index}.nom`} {...register(`enfants.${index}.nom`)} placeholder="Nom" />
                      {errors.enfants?.[index]?.nom && <p className="text-sm text-destructive">{errors.enfants[index]?.nom?.message}</p>}
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor={`enfants.${index}.prenom`}>Prénom</Label>
                      <Input id={`enfants.${index}.prenom`} {...register(`enfants.${index}.prenom`)} placeholder="Prénom" />
                      {errors.enfants?.[index]?.prenom && <p className="text-sm text-destructive">{errors.enfants[index]?.prenom?.message}</p>}
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor={`enfants.${index}.dateNaissance`}>Date de naissance</Label>
                      <Input id={`enfants.${index}.dateNaissance`} type="date" {...register(`enfants.${index}.dateNaissance`)} />
                      {errors.enfants?.[index]?.dateNaissance && <p className="text-sm text-destructive">{errors.enfants[index]?.dateNaissance?.message}</p>}
                    </div>
                    <div className="space-y-2">
                      <Label>Nationalité</Label>
                      <Select
                        value={watch(`enfants.${index}.nationalite`) || undefined}
                        onValueChange={(v) => setValue(`enfants.${index}.nationalite`, v, { shouldValidate: true })}
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Sélectionnez" />
                        </SelectTrigger>
                        <SelectContent>
                          {NATIONALITES_FREQUENTES.map((n) => (
                            <SelectItem key={n} value={n}>{n}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                      {errors.enfants?.[index]?.nationalite && <p className="text-sm text-destructive">{errors.enfants[index]?.nationalite?.message}</p>}
                    </div>
                  </div>
                </div>
              ))}
              {enfantFields.length === 0 && (
                <p className="text-sm text-muted-foreground">Aucun enfant déclaré.</p>
              )}
            </div>

            <div className="border-t pt-4 space-y-3">
              <div className="flex items-center gap-2">
                <Checkbox
                  id="familleEnFrance"
                  checked={familleEnFrance}
                  onCheckedChange={(v) => setValue("familleEnFrance", Boolean(v))}
                />
                <Label htmlFor="familleEnFrance">Des membres de la famille en France</Label>
              </div>
              <div className="space-y-2">
                <Label htmlFor="membresFamille">Membres de la famille en France</Label>
                <Textarea
                  id="membresFamille"
                  {...register("membresFamille")}
                  placeholder="Décrivez les membres de la famille déjà en France..."
                  rows={3}
                />
              </div>
            </div>

            <div className="flex justify-between">
              <Button type="button" variant="outline" onClick={onPrev}>
                Précédent
              </Button>
              <Button type="submit">Suivant</Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </motion.div>
  );
}
