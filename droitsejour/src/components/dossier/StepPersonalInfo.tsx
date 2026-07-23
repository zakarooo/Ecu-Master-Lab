"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { motion } from "framer-motion";
import { User, CreditCard } from "lucide-react";
import { personalInfoSchema, type PersonalInfoFormData } from "@/features/dossier/dossier-schema";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { NATIONALITES_FREQUENTES } from "@/lib/constants";
import type { Dossier } from "@/types";
import { useEffect } from "react";

interface StepProps {
  dossier: Dossier;
  onUpdate: (data: Partial<Dossier>) => void;
  onNext: () => void;
  onPrev: () => void;
}

export default function StepPersonalInfo({ dossier, onUpdate, onNext }: StepProps) {
  const {
    register,
    handleSubmit,
    setValue,
    watch,
    formState: { errors },
  } = useForm<PersonalInfoFormData>({
    resolver: zodResolver(personalInfoSchema),
    defaultValues: {
      nom: dossier.informationsPersonnelles?.nom ?? "",
      prenom: dossier.informationsPersonnelles?.prenom ?? "",
      dateNaissance: dossier.informationsPersonnelles?.dateNaissance ?? "",
      lieuNaissance: dossier.informationsPersonnelles?.lieuNaissance ?? "",
      nationalite: dossier.informationsPersonnelles?.nationalite ?? "",
      adresse: dossier.informationsPersonnelles?.adresse ?? "",
      codePostal: dossier.informationsPersonnelles?.codePostal ?? "",
      ville: dossier.informationsPersonnelles?.ville ?? "",
      telephone: dossier.informationsPersonnelles?.telephone ?? "",
      email: dossier.informationsPersonnelles?.email ?? "",
      situationFamiliale: dossier.informationsPersonnelles?.situationFamiliale ?? "celibataire",
      nombreEnfants: dossier.informationsPersonnelles?.nombreEnfants ?? 0,
      passeportNumero: dossier.informationsPersonnelles?.passeportNumero ?? "",
      passeportDelivrance: dossier.informationsPersonnelles?.passeportDelivrance ?? "",
      passeportExpiration: dossier.informationsPersonnelles?.passeportExpiration ?? "",
    },
  });

  const situationFamiliale = watch("situationFamiliale");

  useEffect(() => {
    setValue("situationFamiliale", situationFamiliale);
  }, [situationFamiliale, setValue]);

  const onSubmit = (data: PersonalInfoFormData) => {
    onUpdate({ informationsPersonnelles: data });
    onNext();
  };

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}>
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <User className="h-5 w-5" />
            Informations personnelles
          </CardTitle>
          <CardDescription>
            Renseignez les informations personnelles du demandeur.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="nom">Nom</Label>
                <Input id="nom" {...register("nom")} placeholder="Nom de famille" />
                {errors.nom && <p className="text-sm text-destructive">{errors.nom.message}</p>}
              </div>
              <div className="space-y-2">
                <Label htmlFor="prenom">Prénom</Label>
                <Input id="prenom" {...register("prenom")} placeholder="Prénom" />
                {errors.prenom && <p className="text-sm text-destructive">{errors.prenom.message}</p>}
              </div>
              <div className="space-y-2">
                <Label htmlFor="dateNaissance">Date de naissance</Label>
                <Input id="dateNaissance" type="date" {...register("dateNaissance")} />
                {errors.dateNaissance && <p className="text-sm text-destructive">{errors.dateNaissance.message}</p>}
              </div>
              <div className="space-y-2">
                <Label htmlFor="lieuNaissance">Lieu de naissance</Label>
                <Input id="lieuNaissance" {...register("lieuNaissance")} placeholder="Ville, pays" />
                {errors.lieuNaissance && <p className="text-sm text-destructive">{errors.lieuNaissance.message}</p>}
              </div>
              <div className="space-y-2">
                <Label>Nationalité</Label>
                <Select
                  value={watch("nationalite")}
                  onValueChange={(v) => setValue("nationalite", v, { shouldValidate: true })}
                >
                  <SelectTrigger aria-label="Nationalité">
                    <SelectValue placeholder="Sélectionnez une nationalité" />
                  </SelectTrigger>
                  <SelectContent>
                    {NATIONALITES_FREQUENTES.map((n) => (
                      <SelectItem key={n} value={n}>{n}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {errors.nationalite && <p className="text-sm text-destructive">{errors.nationalite.message}</p>}
              </div>
              <div className="space-y-2">
                <Label htmlFor="telephone">Téléphone</Label>
                <Input id="telephone" {...register("telephone")} placeholder="06 12 34 56 78" />
                {errors.telephone && <p className="text-sm text-destructive">{errors.telephone.message}</p>}
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="adresse">Adresse</Label>
              <Input id="adresse" {...register("adresse")} placeholder="Adresse complète" />
              {errors.adresse && <p className="text-sm text-destructive">{errors.adresse.message}</p>}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="codePostal">Code postal</Label>
                <Input id="codePostal" {...register("codePostal")} placeholder="75001" />
                {errors.codePostal && <p className="text-sm text-destructive">{errors.codePostal.message}</p>}
              </div>
              <div className="space-y-2">
                <Label htmlFor="ville">Ville</Label>
                <Input id="ville" {...register("ville")} placeholder="Paris" />
                {errors.ville && <p className="text-sm text-destructive">{errors.ville.message}</p>}
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input id="email" type="email" {...register("email")} placeholder="email@exemple.fr" />
              {errors.email && <p className="text-sm text-destructive">{errors.email.message}</p>}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Situation familiale</Label>
                <Select
                  value={situationFamiliale}
                  onValueChange={(v) => setValue("situationFamiliale", v as PersonalInfoFormData["situationFamiliale"], { shouldValidate: true })}
                >
                  <SelectTrigger aria-label="Situation familiale">
                    <SelectValue placeholder="Sélectionnez" />
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
                {errors.situationFamiliale && <p className="text-sm text-destructive">{errors.situationFamiliale.message}</p>}
              </div>
              <div className="space-y-2">
                <Label htmlFor="nombreEnfants">Nombre d&apos;enfants</Label>
                <Input
                  id="nombreEnfants"
                  type="number"
                  min={0}
                  max={20}
                  {...register("nombreEnfants", { valueAsNumber: true })}
                />
                {errors.nombreEnfants && <p className="text-sm text-destructive">{errors.nombreEnfants.message}</p>}
              </div>
            </div>

            <div className="border-t pt-4">
              <h2 className="flex items-center gap-2 text-sm font-semibold mb-3">
                <CreditCard className="h-4 w-4" />
                Passeport
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="passeportNumero">Numéro</Label>
                  <Input id="passeportNumero" {...register("passeportNumero")} placeholder="Numéro de passeport" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="passeportDelivrance">Date de délivrance</Label>
                  <Input id="passeportDelivrance" type="date" {...register("passeportDelivrance")} />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="passeportExpiration">Date d&apos;expiration</Label>
                  <Input id="passeportExpiration" type="date" {...register("passeportExpiration")} />
                </div>
              </div>
            </div>

            <div className="flex justify-end">
              <Button type="submit">Suivant</Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </motion.div>
  );
}
