"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { motion } from "framer-motion";
import { FileText } from "lucide-react";
import { administrativeSituationSchema, type AdministrativeSituationFormData } from "@/features/dossier/dossier-schema";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { PREFECTURES_FRANCE } from "@/lib/constants";
import type { Dossier } from "@/types";

interface StepProps {
  dossier: Dossier;
  onUpdate: (data: Partial<Dossier>) => void;
  onNext: () => void;
  onPrev: () => void;
}

export default function StepAdministrativeSituation({ dossier, onUpdate, onNext, onPrev }: StepProps) {
  const {
    register,
    handleSubmit,
    setValue,
    watch,
    formState: { errors },
  } = useForm<AdministrativeSituationFormData>({
    resolver: zodResolver(administrativeSituationSchema),
    defaultValues: {
      statutSejour: dossier.situationAdministrative?.statutSejour ?? "inconnu",
      typeTitre: dossier.situationAdministrative?.typeTitre ?? "",
      dateEntree: dossier.situationAdministrative?.dateEntree ?? "",
      dateExpiration: dossier.situationAdministrative?.dateExpiration ?? "",
      numeroDossier: dossier.situationAdministrative?.numeroDossier ?? "",
      administration: dossier.situationAdministrative?.administration ?? "",
      prefecture: dossier.situationAdministrative?.prefecture ?? "",
      motifSejour: dossier.situationAdministrative?.motifSejour ?? "",
      emploiActuel: dossier.situationAdministrative?.emploiActuel ?? "",
      employeur: dossier.situationAdministrative?.employeur ?? "",
      dureeEmploi: dossier.situationAdministrative?.dureeEmploi ?? "",
      ressourcesMensuelles: dossier.situationAdministrative?.ressourcesMensuelles ?? undefined,
      couvertureMaladie: dossier.situationAdministrative?.couvertureMaladie ?? false,
      impots: dossier.situationAdministrative?.impots ?? false,
    },
  });

  const statutSejour = watch("statutSejour");
  const couvertureMaladie = watch("couvertureMaladie");
  const impots = watch("impots");

  const onSubmit = (data: AdministrativeSituationFormData) => {
    onUpdate({ situationAdministrative: data });
    onNext();
  };

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}>
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            Situation administrative
          </CardTitle>
          <CardDescription>
            Décrivez la situation administrative actuelle du demandeur en France.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Statut de séjour</Label>
                <Select
                  value={statutSejour}
                  onValueChange={(v) => setValue("statutSejour", v as AdministrativeSituationFormData["statutSejour"], { shouldValidate: true })}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Sélectionnez le statut" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="regulier">Régulier</SelectItem>
                    <SelectItem value="irregulier">Irrégulier</SelectItem>
                    <SelectItem value="en_cours">En cours</SelectItem>
                    <SelectItem value="refuse">Refusé</SelectItem>
                    <SelectItem value="expire">Expiré</SelectItem>
                    <SelectItem value="inconnu">Inconnu</SelectItem>
                  </SelectContent>
                </Select>
                {errors.statutSejour && <p className="text-sm text-destructive">{errors.statutSejour.message}</p>}
              </div>
              <div className="space-y-2">
                <Label htmlFor="typeTitre">Type de titre</Label>
                <Input id="typeTitre" {...register("typeTitre")} placeholder="Ex: Carte de séjour temporaire" />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="dateEntree">Date d&apos;entrée en France</Label>
                <Input id="dateEntree" type="date" {...register("dateEntree")} />
              </div>
              <div className="space-y-2">
                <Label htmlFor="dateExpiration">Date d&apos;expiration</Label>
                <Input id="dateExpiration" type="date" {...register("dateExpiration")} />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="numeroDossier">Numéro de dossier</Label>
                <Input id="numeroDossier" {...register("numeroDossier")} placeholder="Numéro de dossier" />
              </div>
              <div className="space-y-2">
                <Label htmlFor="administration">Administration</Label>
                <Input id="administration" {...register("administration")} placeholder="Nom de l'administration" />
              </div>
            </div>

            <div className="space-y-2">
              <Label>Préfecture</Label>
              <Select
                value={watch("prefecture") || undefined}
                onValueChange={(v) => setValue("prefecture", v, { shouldValidate: true })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Sélectionnez une préfecture" />
                </SelectTrigger>
                <SelectContent>
                  {PREFECTURES_FRANCE.map((p) => (
                    <SelectItem key={p} value={p}>{p}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="motifSejour">Motif du séjour</Label>
              <Input id="motifSejour" {...register("motifSejour")} placeholder="Ex: Regroupement familial, travail..." />
            </div>

            <div className="border-t pt-4">
              <h3 className="text-sm font-semibold mb-3">Emploi et ressources</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="emploiActuel">Emploi actuel</Label>
                  <Input id="emploiActuel" {...register("emploiActuel")} placeholder="Ex: Salarié, auto-entrepreneur..." />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="employeur">Employeur</Label>
                  <Input id="employeur" {...register("employeur")} placeholder="Nom de l'employeur" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="dureeEmploi">Durée de l&apos;emploi</Label>
                  <Input id="dureeEmploi" {...register("dureeEmploi")} placeholder="Ex: 2 ans" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="ressourcesMensuelles">Ressources mensuelles (€)</Label>
                  <Input id="ressourcesMensuelles" type="number" {...register("ressourcesMensuelles", { valueAsNumber: true })} placeholder="Montant en euros" />
                </div>
              </div>
            </div>

            <div className="border-t pt-4 space-y-3">
              <h3 className="text-sm font-semibold">Divers</h3>
              <div className="flex items-center gap-2">
                <Checkbox
                  id="couvertureMaladie"
                  checked={couvertureMaladie}
                  onCheckedChange={(v) => setValue("couvertureMaladie", Boolean(v))}
                />
                <Label htmlFor="couvertureMaladie">Couverture maladie</Label>
              </div>
              <div className="flex items-center gap-2">
                <Checkbox
                  id="impots"
                  checked={impots}
                  onCheckedChange={(v) => setValue("impots", Boolean(v))}
                />
                <Label htmlFor="impots">Impôts déclarés</Label>
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
