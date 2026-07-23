import { z } from "zod";

export const personalInfoSchema = z.object({
  nom: z.string().min(2, "Le nom doit contenir au moins 2 caractères"),
  prenom: z.string().min(2, "Le prénom doit contenir au moins 2 caractères"),
  dateNaissance: z.string().min(1, "La date de naissance est requise"),
  lieuNaissance: z.string().min(2, "Le lieu de naissance est requis"),
  nationalite: z.string().min(2, "La nationalité est requise"),
  adresse: z.string().min(5, "L'adresse est requise"),
  codePostal: z.string().regex(/^\d{5}$/, "Code postal invalide"),
  ville: z.string().min(2, "La ville est requise"),
  telephone: z.string().min(10, "Numéro de téléphone invalide"),
  email: z.string().email("Email invalide"),
  situationFamiliale: z.enum(["celibataire", "marie", "divorce", "veuf", "pacse", "concubin"]),
  nombreEnfants: z.number().min(0).max(20),
  passeportNumero: z.string().optional(),
  passeportDelivrance: z.string().optional(),
  passeportExpiration: z.string().optional(),
});

export const administrativeSituationSchema = z.object({
  statutSejour: z.enum(["regulier", "irregulier", "en_cours", "refuse", "expire", "inconnu"]),
  typeTitre: z.string().optional(),
  dateEntree: z.string().optional(),
  dateExpiration: z.string().optional(),
  numeroDossier: z.string().optional(),
  administration: z.string().optional(),
  prefecture: z.string().optional(),
  motifSejour: z.string().optional(),
  emploiActuel: z.string().optional(),
  employeur: z.string().optional(),
  dureeEmploi: z.string().optional(),
  ressourcesMensuelles: z.number().optional(),
  couvertureMaladie: z.boolean().optional(),
  impots: z.boolean().optional(),
});

export const familySituationSchema = z.object({
  situation: z.enum(["celibataire", "marie", "divorce", "veuf", "pacse", "concubin"]),
  conjoint: z.object({
    nom: z.string().min(1),
    prenom: z.string().min(1),
    nationalite: z.string().min(1),
    statutSejour: z.string().optional(),
  }).optional(),
  enfants: z.array(z.object({
    nom: z.string().min(1),
    prenom: z.string().min(1),
    dateNaissance: z.string().min(1),
    nationalite: z.string().min(1),
  })).optional(),
  familleEnFrance: z.boolean().optional(),
  membresFamille: z.string().optional(),
});

export const demarcheSchema = z.object({
  date: z.string().min(1, "La date est requise"),
  type: z.string().min(1, "Le type est requis"),
  description: z.string().min(5, "La description est requise"),
  resultat: z.string().min(1, "Le résultat est requis"),
  administration: z.string().min(1, "L'administration est requise"),
  documentsFournis: z.array(z.string()).optional(),
});

export const memoSchema = z.object({
  contenu: z.string().min(1, "Le mémo ne peut pas être vide"),
});

export type PersonalInfoFormData = z.infer<typeof personalInfoSchema>;
export type AdministrativeSituationFormData = z.infer<typeof administrativeSituationSchema>;
export type FamilySituationFormData = z.infer<typeof familySituationSchema>;
export type DemarcheFormData = z.infer<typeof demarcheSchema>;
export type MemoFormData = z.infer<typeof memoSchema>;
