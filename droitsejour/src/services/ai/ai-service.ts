import { Dossier, AnalyseResultat, Courrier, TypeCourrier, ChecklistItem } from "@/types";
import { buildAnalysisPrompt, buildLetterPrompt } from "./prompts";
import { generateId, getTodayISO } from "@/lib/utils";

export type AIProvider = "openai" | "anthropic" | "gemini" | "local";

interface AIConfig {
  provider: AIProvider;
  apiKey?: string;
  baseUrl?: string;
  model?: string;
}

const defaultConfig: AIConfig = {
  provider: "local",
  model: "gpt-4o-mini",
};

function getConfig(): AIConfig {
  return {
    provider: (process.env.AI_PROVIDER as AIProvider) || defaultConfig.provider,
    apiKey: process.env.AI_API_KEY || "",
    baseUrl: process.env.AI_BASE_URL || "",
    model: process.env.AI_MODEL || defaultConfig.model,
  };
}

async function callAI(prompt: string): Promise<string> {
  const config = getConfig();

  if (config.provider === "local" || !config.apiKey) {
    return generateLocalAnalysis(prompt);
  }

  try {
    if (config.provider === "openai") {
      const res = await fetch("https://api.openai.com/v1/chat/completions", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${config.apiKey}`,
        },
        body: JSON.stringify({
          model: config.model || "gpt-4o-mini",
          messages: [{ role: "user", content: prompt }],
          temperature: 0.3,
        }),
      });
      const data = await res.json();
      return data.choices?.[0]?.message?.content || "";
    }

    if (config.provider === "anthropic") {
      const res = await fetch("https://api.anthropic.com/v1/messages", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "x-api-key": config.apiKey,
          "anthropic-version": "2023-06-01",
        },
        body: JSON.stringify({
          model: config.model || "claude-3-haiku-20240307",
          max_tokens: 4096,
          messages: [{ role: "user", content: prompt }],
        }),
      });
      const data = await res.json();
      return data.content?.[0]?.text || "";
    }

    if (config.provider === "gemini") {
      const res = await fetch(
        `https://generativelanguage.googleapis.com/v1beta/models/${config.model || "gemini-1.5-flash"}:generateContent?key=${config.apiKey}`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            contents: [{ parts: [{ text: prompt }] }],
          }),
        }
      );
      const data = await res.json();
      return data.candidates?.[0]?.content?.parts?.[0]?.text || "";
    }
  } catch (error) {
    console.error("AI API error:", error);
    return generateLocalAnalysis(prompt);
  }

  return generateLocalAnalysis(prompt);
}

function generateLocalAnalysis(_prompt: string): string {
  return JSON.stringify({
    resume: "Analyse générée localement. Pour une analyse plus approfondie, configurez une clé API d'un fournisseur IA (OpenAI, Anthropic ou Gemini). Cette analyse est basée sur les informations fournies dans le dossier.",
    chronologie: [
      { date: "À compléter", evenement: "Entrée en France (date à préciser)" },
      { date: "Actuel", evenement: "Situation administrative à analyser" },
    ],
    forces: [
      "Dossier en cours de constitution",
      "Volonté de régulariser sa situation",
      "Préparation des documents nécessaires",
    ],
    faiblesses: [
      "Informations à compléter pour une analyse précise",
      "Documents supplémentaires potentiellement nécessaires",
    ],
    documentsManquants: [
      "Justificatif de domicile récent (moins de 3 mois)",
      "Justificatif d'emploi ou de ressources",
      "Attestation d'assurance maladie",
      "Titre de séjour ou récépissé en cours de validité",
    ],
    argumentsFavorables: [
      "Intégration sociale et professionnelle en France",
      "Respect des obligations légales",
    ],
    pointsPreuves: [
      "Justificatifs de résidence stable",
      "Preuves d'activité professionnelle",
      "Justificatifs familiaux si applicable",
    ],
    risques: [
      "Risque de refus si les justificatifs sont insuffisants",
      "Délais de traitement pouvant varier selon les préfectures",
    ],
    demarchesRecommandees: [
      {
        titre: "Prise de rendez-vous en préfecture",
        description: "Prendre rendez-vous auprès de la préfecture compétente pour déposer votre demande de titre de séjour.",
        priorite: "haute" as const,
        delai: "1 mois",
      },
      {
        titre: "Constitution du dossier",
        description: "Rassembler tous les documents nécessaires selon la checklist fournie.",
        priorite: "haute" as const,
        delai: "2 semaines",
      },
      {
        titre: "Consultation juridique",
        description: "Consulter un avocat ou une association d'aide aux étrangers pour valider votre dossier.",
        priorite: "moyenne" as const,
        delai: "1 mois",
      },
    ],
    ordreActions: [
      "Rassembler les documents d'identité",
      "Obtenir les justificatifs de domicile",
      "Récupérer les justificatifs d'emploi",
      "Prendre rendez-vous en préfecture",
      "Déposer le dossier complet",
      "Suivre l'avancement de la demande",
    ],
    administrationsConcernees: [
      "Préfecture",
      "OFII (Office Français de l'Immigration et de l'Intégration)",
      "CAF (Caisse d'Allocations Familiales)" ,
      "URSSAF",
    ],
  });
}

export async function analyzeDossier(dossier: Dossier): Promise<AnalyseResultat> {
  const prompt = buildAnalysisPrompt(dossier);
  const response = await callAI(prompt);

  try {
    const cleaned = response.replace(/```json\n?/g, "").replace(/```\n?/g, "").trim();
    const parsed = JSON.parse(cleaned);
    return {
      ...parsed,
      dateAnalyse: getTodayISO(),
    };
  } catch {
    return {
      ...JSON.parse(generateLocalAnalysis("")),
      dateAnalyse: getTodayISO(),
    };
  }
}

export async function generateLetter(dossier: Dossier, type: TypeCourrier): Promise<Courrier> {
  const prompt = buildLetterPrompt(dossier, type);
  const response = await callAI(prompt);

  const typeLabels: Record<TypeCourrier, string> = {
    demande_info: "Demande d'information",
    demande_rendez_vous: "Demande de rendez-vous",
    recours: "Recours administratif",
    relance: "Relance",
    communication_dossier: "Demande de communication de dossier",
    courrier_libre: "Courrier libre",
  };

  return {
    id: generateId(),
    type,
    titre: typeLabels[type],
    contenu: response || generateDefaultLetter(dossier, type),
    destinataire: dossier.situationAdministrative?.prefecture || "Préfecture compétente",
    dateCreation: getTodayISO(),
    personnalise: true,
  };
}

function generateDefaultLetter(dossier: Dossier, type: TypeCourrier): string {
  const info = dossier.informationsPersonnelles;
  const admin = dossier.situationAdministrative;

  const headers = [
    `${info?.prenom} ${info?.nom}`,
    info?.adresse,
    `${info?.codePostal} ${info?.ville}`,
    "",
    `Préfecture de ${admin?.prefecture || "..."}`,
    "",
    `Objet: ${type.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase())}`,
    "",
    "Madame, Monsieur,",
    "",
  ];

  const bodies: Record<TypeCourrier, string[]> = {
    demande_info: [
      `Je me permets de vous écrire afin d'obtenir des renseignements concernant ma situation administrative.`,
      `Titulaire d'un dossier référencé ${admin?.numeroDossier || "N/A"}, je souhaiterais obtenir des informations sur l'état d'avancement de mon dossier et les pièces éventuellement manquantes.`,
      "Je reste à votre disposition pour tout renseignement complémentaire.",
    ],
    demande_rendez_vous: [
      `Je souhaite solliciter un rendez-vous auprès de vos services afin de déposer ma demande de titre de séjour.`,
      `Ma situation administrative nécessite un échange avec vos services. Je me tiens à disposition pour me rendre au rendez-vous à la date qui vous conviendra.`,
    ],
    recours: [
      `Par la présente, je souhaite formuler un recours contre la décision qui m'a été notifiée.`,
      `En effet, je considère que cette décision ne prend pas en compte l'ensemble des éléments de mon dossier. Je me permets de joindre les documents justificatifs à l'appui de ma demande.`,
      "Je vous prie de bien vouloir réexaminer ma situation à la lumière des pièces jointes.",
    ],
    relance: [
      `Je me permets de vous adresser cette lettre afin de solliciter un point d'avancement concernant ma demande en cours.`,
      `N'ayant reçu aucun retour depuis ma dernière démarche en date du ${admin?.dateEntree || "N/A"}, je souhaite connaître l'état d'avancement de mon dossier.`,
    ],
    communication_dossier: [
      `Conformément aux dispositions en vigueur, je vous demande de bien vouloir me communiquer une copie de l'ensemble des documents et notes composant mon dossier administratif.`,
      `Ce droit d'accès est garanti par la législation en vigueur et je vous serais reconnaissant de traiter ma demande dans les meilleurs délais.`,
    ],
    courrier_libre: [
      `Je me permets de vous écrire concernant ma situation administrative.`,
      `Les éléments de mon dossier sont les suivants et je reste à votre disposition pour tout complément d'information.`,
    ],
  };

  return [
    ...headers,
    ...(bodies[type] || bodies.courrier_libre),
    "",
    "Dans l'attente de votre réponse, je vous prie d'agréer, Madame, Monsieur, l'expression de mes salutations distinguées.",
    "",
    `Fait à ${info?.ville || "..."}, le ${new Date().toLocaleDateString("fr-FR")}`,
    "",
    `${info?.prenom} ${info?.nom}`,
    "",
    "PJ: Documents justificatifs",
  ].join("\n");
}

export function generateChecklist(dossier: Dossier): ChecklistItem[] {
  const base: ChecklistItem[] = [
    { id: generateId(), document: "Passeport en cours de validité", description: "Passeport ou document de voyage en cours de validité", obligatoire: true, coche: false, categorie: "Identité" },
    { id: generateId(), document: "Justificatif de domicile", description: "Facture EDF, téléphone, ou attestation d'hébergement de moins de 3 mois", obligatoire: true, coche: false, categorie: "Domicile" },
    { id: generateId(), document: "Photos d'identité", description: "3 photos d'identité récentes aux normes officielles", obligatoire: true, coche: false, categorie: "Identité" },
    { id: generateId(), document: "Justificatif d'emploi", description: "Contrat de travail, attestation employeur, ou bulletin de salaire", obligatoire: true, coche: false, categorie: "Emploi" },
    { id: generateId(), document: "Justificatif de ressources", description: "3 derniers bulletins de salaire ou justificatif de revenus", obligatoire: true, coche: false, categorie: "Finances" },
    { id: generateId(), document: "Attestation d'assurance maladie", description: "Carte vitale ou attestation de droits à la sécurité sociale", obligatoire: false, coche: false, categorie: "Santé" },
    { id: generateId(), document: "Titre de séjour précédent", description: "Copie du titre de séjour ou récépissé précédent si applicable", obligatoire: false, coche: false, categorie: "Séjour" },
    { id: generateId(), document: "Certificat de naissance", description: "Extrait de naissance avec traduction si nécessaire", obligatoire: false, coche: false, categorie: "État civil" },
    { id: generateId(), document: "Justificatif d'impôts", description: "Avis d'imposition ou attestation fiscale", obligatoire: false, coche: false, categorie: "Finances" },
    { id: generateId(), document: "Attestation de non-condamnation", description: "Bulletin n°3 du casier judiciaire du pays d'origine", obligatoire: false, coche: false, categorie: "Juridique" },
  ];

  const items = [...base];

  if (dossier.situationFamiliale?.situation === "marie" || dossier.situationFamiliale?.situation === "pacse") {
    items.push(
      { id: generateId(), document: "Livret de famille", description: "Livret de famille ou acte de mariage", obligatoire: true, coche: false, categorie: "Famille" },
      { id: generateId(), document: "Titre de séjour du conjoint", description: "Copie du titre de séjour du conjoint", obligatoire: true, coche: false, categorie: "Famille" }
    );
  }

  if (dossier.situationFamiliale?.enfants?.length) {
    items.push(
      { id: generateId(), document: "Justificatif de scolarité des enfants", description: "Attestation d'inscription scolaire", obligatoire: false, coche: false, categorie: "Famille" }
    );
  }

  return items;
}
