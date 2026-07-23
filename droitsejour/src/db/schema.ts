import { sqliteTable, text, integer } from "drizzle-orm/sqlite-core";

export const dossiers = sqliteTable("dossiers", {
  id: text("id").primaryKey(),
  nom: text("nom").notNull().default("Nouveau dossier"),
  statut: text("statut").notNull().default("brouillon"),
  typeDossier: text("type_dossier").notNull().default("particulier"),
  rapportGenere: integer("rapport_genere", { mode: "boolean" }).notNull().default(false),
  dateCreation: text("date_creation").notNull(),
  dateModification: text("date_modification").notNull(),
});

export const personalInfo = sqliteTable("personal_info", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  dossierId: text("dossier_id").notNull().references(() => dossiers.id, { onDelete: "cascade" }),
  nom: text("nom").notNull().default(""),
  prenom: text("prenom").notNull().default(""),
  dateNaissance: text("date_naissance").default(""),
  lieuNaissance: text("lieu_naissance").default(""),
  nationalite: text("nationalite").default(""),
  adresse: text("adresse").default(""),
  codePostal: text("code_postal").default(""),
  ville: text("ville").default(""),
  telephone: text("telephone").default(""),
  email: text("email").default(""),
  situationFamiliale: text("situation_familiale").default("celibataire"),
  nombreEnfants: integer("nombre_enfants").default(0),
  passeportNumero: text("passeport_numero"),
  passeportDelivrance: text("passeport_delivrance"),
  passeportExpiration: text("passeport_expiration"),
});

export const situationAdmin = sqliteTable("situation_admin", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  dossierId: text("dossier_id").notNull().references(() => dossiers.id, { onDelete: "cascade" }),
  statutSejour: text("statut_sejour").default("inconnu"),
  typeTitre: text("type_titre"),
  dateEntree: text("date_entree"),
  dateExpiration: text("date_expiration"),
  numeroDossier: text("numero_dossier"),
  administration: text("administration"),
  prefecture: text("prefecture"),
  motifSejour: text("motif_sejour"),
  emploiActuel: text("emploi_actuel"),
  employeur: text("employeur"),
  dureeEmploi: text("duree_emploi"),
  ressourcesMensuelles: integer("ressources_mensuelles"),
  couvertureMaladie: integer("couverture_maladie", { mode: "boolean" }).default(false),
  impots: integer("impots", { mode: "boolean" }).default(false),
});

export const situationFamille = sqliteTable("situation_famille", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  dossierId: text("dossier_id").notNull().references(() => dossiers.id, { onDelete: "cascade" }),
  situation: text("situation").default("celibataire"),
  conjointJson: text("conjoint_json"),
  enfantsJson: text("enfants_json"),
  familleEnFrance: integer("famille_en_france", { mode: "boolean" }).default(false),
  membresFamille: text("membres_famille"),
});

export const documents = sqliteTable("documents", {
  id: text("id").primaryKey(),
  dossierId: text("dossier_id").notNull().references(() => dossiers.id, { onDelete: "cascade" }),
  nom: text("nom").notNull(),
  type: text("type").notNull().default("autre"),
  chemin: text("chemin").notNull(),
  taille: integer("taille").notNull(),
  mimetype: text("mimetype").notNull(),
  dateAjout: text("date_ajout").notNull(),
  ocrText: text("ocr_text"),
});

export const demarches = sqliteTable("demarches", {
  id: text("id").primaryKey(),
  dossierId: text("dossier_id").notNull().references(() => dossiers.id, { onDelete: "cascade" }),
  date: text("date").notNull(),
  type: text("type").notNull(),
  description: text("description").notNull(),
  resultat: text("resultat").notNull(),
  administration: text("administration").notNull(),
  documentsFournis: text("documents_fournis"),
});

export const memos = sqliteTable("memos", {
  id: text("id").primaryKey(),
  dossierId: text("dossier_id").notNull().references(() => dossiers.id, { onDelete: "cascade" }),
  contenu: text("contenu").notNull(),
  dateCreation: text("date_creation").notNull(),
  dateModification: text("date_modification").notNull(),
});

export const analyses = sqliteTable("analyses", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  dossierId: text("dossier_id").notNull().references(() => dossiers.id, { onDelete: "cascade" }),
  contenu: text("contenu").notNull(),
  provider: text("provider"),
  dateAnalyse: text("date_analyse").notNull(),
});

export const courriers = sqliteTable("courriers", {
  id: text("id").primaryKey(),
  dossierId: text("dossier_id").notNull().references(() => dossiers.id, { onDelete: "cascade" }),
  type: text("type").notNull(),
  titre: text("titre").notNull(),
  contenu: text("contenu").notNull(),
  destinataire: text("destinataire").notNull().default(""),
  dateCreation: text("date_creation").notNull(),
  personnalise: integer("personnalise", { mode: "boolean" }).notNull().default(false),
});

export const checklistItems = sqliteTable("checklist_items", {
  id: text("id").primaryKey(),
  dossierId: text("dossier_id").notNull().references(() => dossiers.id, { onDelete: "cascade" }),
  document: text("document").notNull(),
  description: text("description").notNull().default(""),
  obligatoire: integer("obligatoire", { mode: "boolean" }).notNull().default(false),
  coche: integer("coche", { mode: "boolean" }).notNull().default(false),
  categorie: text("categorie").notNull().default(""),
});

export const users = sqliteTable("users", {
  id: text("id").primaryKey(),
  nom: text("nom").notNull(),
  prenom: text("prenom").notNull(),
  email: text("email").notNull().unique(),
  dateCreation: text("date_creation").notNull(),
});
