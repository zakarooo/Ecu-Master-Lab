import { Dossier } from "@/types";

export function buildAnalysisPrompt(dossier: Dossier): string {
  const { informationsPersonnelles: info, situationAdministrative: admin, situationFamiliale: family, demarchesPrecedentes: demarches, documents, memos } = dossier;

  return `Tu es un expert en droit des étrangers en France. Analyse le dossier suivant et fournis une analyse structurée.

INFORMATIONS PERSONNELLES:
- Nom: ${info?.prenom} ${info?.nom}
- Date de naissance: ${info?.dateNaissance}
- Lieu de naissance: ${info?.lieuNaissance}
- Nationalité: ${info?.nationalite}
- Situation familiale: ${info?.situationFamiliale}
- Nombre d'enfants: ${info?.nombreEnfants}

SITUATION ADMINISTRATIVE:
- Statut de séjour: ${admin?.statutSejour}
- Type de titre: ${admin?.typeTitre || "Non précisé"}
- Date d'entrée en France: ${admin?.dateEntree || "Non précisé"}
- Date d'expiration: ${admin?.dateExpiration || "Non précisé"}
- Numéro de dossier: ${admin?.numeroDossier || "Non précisé"}
- Préfecture: ${admin?.prefecture || "Non précisé"}
- Motif de séjour: ${admin?.motifSejour || "Non précisé"}
- Emploi actuel: ${admin?.emploiActuel || "Non précisé"}
- Employeur: ${admin?.employeur || "Non précisé"}
- Durée de l'emploi: ${admin?.dureeEmploi || "Non précisé"}
- Ressources mensuelles: ${admin?.ressourcesMensuelles || "Non précisé"} EUR
- Couverture maladie: ${admin?.couvertureMaladie ? "Oui" : "Non"}
- Impôts: ${admin?.impots ? "Oui" : "Non"}

SITUATION FAMILIALE:
- Situation: ${family?.situation}
${family?.conjoint ? `- Conjoint: ${family.conjoint.prenom} ${family.conjoint.nom}, nationalité ${family.conjoint.nationalite}, statut: ${family.conjoint.statutSejour || "inconnu"}` : ""}
${family?.enfants?.length ? `- Enfants: ${family.enfants.map(e => `${e.prenom} ${e.nom} (${e.dateNaissance}, ${e.nationalite})`).join(", ")}` : ""}
- Famille en France: ${family?.familleEnFrance ? "Oui" : "Non"}

HISTORIQUE DES DÉMARCHES:
${demarches?.length ? demarches.map(d => `- ${d.date}: ${d.type} - ${d.description} (Résultat: ${d.resultat}, Admin: ${d.administration})`).join("\n") : "Aucune démarche enregistrée"}

DOCUMENTS FOURNIS:
${documents?.length ? documents.map(d => `- ${d.nom} (${d.type})`).join("\n") : "Aucun document"}

MÉMO:
${memos?.length ? memos.map(m => m.contenu).join("\n") : "Aucun mémo"}

---
Fournis une analyse JSON avec la structure suivante (en français, sans markdown):
{
  "resume": "Résumé complet de la situation",
  "chronologie": [{"date": "...", "evenement": "..."}],
  "forces": ["..."],
  "faiblesses": ["..."],
  "documentsManquants": ["..."],
  "argumentsFavorables": ["..."],
  "pointsPreuves": ["..."],
  "risques": ["..."],
  "demarchesRecommandees": [{"titre": "...", "description": "...", "priorite": "haute|moyenne|basse", "delai": "..."}],
  "ordreActions": ["..."],
  "administrationsConcernees": ["..."]
}`;
}

export function buildLetterPrompt(dossier: Dossier, type: string): string {
  const { informationsPersonnelles: info, situationAdministrative: admin } = dossier;

  return `Tu es un expert en droit des étrangers en France. Rédige un courrier de type "${type}" pour le dossier suivant.

Personne: ${info?.prenom} ${info?.nom}
Nationalité: ${info?.nationalite}
Adresse: ${info?.adresse}, ${info?.codePostal} ${info?.ville}
Statut: ${admin?.statutSejour}
Préfecture: ${admin?.prefecture || "Non précisé"}
Numéro dossier: ${admin?.numeroDossier || "Non précisé"}

Le courrier doit être:
- Formel et respectueux
- Basé uniquement sur les faits du dossier
- Sans garantir aucun résultat
- En accord avec la législation française en vigueur

Fournis le courrier en texte brut, prêt à être copié.`;
}
