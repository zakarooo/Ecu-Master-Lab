export type StatutSejour = "regulier" | "irregulier" | "en_cours" | "refuse" | "expire" | "inconnu";
export type TypeDocument = "passeport" | "titre_sejour" | "carte_sejour" | "carte_resident" | "recipisse" | "demande_recepisse" | "certificat" | "justificatif_domicile" | "justificatif_emploi" | "justificatif_ressources" | "attestation" | "autre";
export type SituationFamiliale = "celibataire" | "marie" | "divorce" | "veuf" | "pacse" | "concubin";
export type Nationalite = string;
export type TypeCourrier = "demande_info" | "demande_rendez_vous" | "recours" | "relance" | "communication_dossier" | "courrier_libre";
export type StatutDossier = "brouillon" | "en_cours" | "analyse" | "termine";
export type TypeDossier = "particulier" | "entreprise";

export interface InformationsPersonnelles {
  nom: string;
  prenom: string;
  dateNaissance: string;
  lieuNaissance: string;
  nationalite: string;
  adresse: string;
  codePostal: string;
  ville: string;
  telephone: string;
  email: string;
  situationFamiliale: SituationFamiliale;
  nombreEnfants: number;
  passeportNumero?: string;
  passeportDelivrance?: string;
  passeportExpiration?: string;
}

export interface SituationAdministrative {
  statutSejour: StatutSejour;
  typeTitre?: string;
  dateEntree?: string;
  dateExpiration?: string;
  numeroDossier?: string;
  administration?: string;
  prefecture?: string;
  motifSejour?: string;
  emploiActuel?: string;
  employeur?: string;
  dureeEmploi?: string;
  ressourcesMensuelles?: number;
  couvertureMaladie?: boolean;
  impots?: boolean;
}

export interface SituationFamilialeInfo {
  situation: SituationFamiliale;
  conjoint?: {
    nom: string;
    prenom: string;
    nationalite: string;
    statutSejour?: string;
  };
  enfants?: Array<{
    nom: string;
    prenom: string;
    dateNaissance: string;
    nationalite: string;
  }>;
  familleEnFrance?: boolean;
  membresFamille?: string;
}

export interface DemarchePrecedente {
  id: string;
  date: string;
  type: string;
  description: string;
  resultat: string;
  administration: string;
  documentsFournis: string[];
}

export interface Document {
  id: string;
  nom: string;
  type: TypeDocument;
  chemin: string;
  taille: number;
  mimetype: string;
  dateAjout: string;
  ocrText?: string;
}

export interface Memo {
  id: string;
  contenu: string;
  dateCreation: string;
  dateModification: string;
}

export interface AnalyseResultat {
  resume: string;
  chronologie: Array<{ date: string; evenement: string }>;
  forces: string[];
  faiblesses: string[];
  documentsManquants: string[];
  argumentsFavorables: string[];
  pointsPreuves: string[];
  risques: string[];
  demarchesRecommandees: Array<{
    titre: string;
    description: string;
    priorite: "haute" | "moyenne" | "basse";
    delai?: string;
  }>;
  ordreActions: string[];
  administrationsConcernees: string[];
  dateAnalyse: string;
}

export interface Courrier {
  id: string;
  type: TypeCourrier;
  titre: string;
  contenu: string;
  destinataire: string;
  dateCreation: string;
  personnalise: boolean;
}

export interface ChecklistItem {
  id: string;
  document: string;
  description: string;
  obligatoire: boolean;
  coche: boolean;
  categorie: string;
}

export interface RapportPDF {
  dateGeneration: string;
  contenu: string;
}

export interface Dossier {
  id: string;
  nom: string;
  statut: StatutDossier;
  typeDossier?: TypeDossier;
  informationsPersonnelles: InformationsPersonnelles;
  situationAdministrative: SituationAdministrative;
  situationFamiliale: SituationFamilialeInfo;
  demarchesPrecedentes: DemarchePrecedente[];
  documents: Document[];
  memos: Memo[];
  analyse?: AnalyseResultat;
  courriers: Courrier[];
  checklist: ChecklistItem[];
  rapportGenere: boolean;
  dateCreation: string;
  dateModification: string;
}

export interface User {
  id: string;
  nom: string;
  prenom: string;
  email: string;
  dateCreation: string;
}

export const WIZARD_STEPS = [
  { id: "personal", label: "Informations personnelles", icon: "User" },
  { id: "administrative", label: "Situation administrative", icon: "FileText" },
  { id: "family", label: "Situation familiale", icon: "Users" },
  { id: "history", label: "Historique des démarches", icon: "Clock" },
  { id: "documents", label: "Documents", icon: "Upload" },
  { id: "memo", label: "Mémo", icon: "StickyNote" },
  { id: "analysis", label: "Analyse IA", icon: "Brain" },
  { id: "recommendations", label: "Recommandations", icon: "Lightbulb" },
  { id: "letters", label: "Courriers", icon: "Mail" },
  { id: "checklist", label: "Checklist", icon: "CheckSquare" },
  { id: "report", label: "Rapport PDF", icon: "FileDown" },
] as const;

export type WizardStepId = typeof WIZARD_STEPS[number]["id"];
