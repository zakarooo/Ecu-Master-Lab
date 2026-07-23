export const APP_NAME = "DroitSéjour";
export const APP_DESCRIPTION = "Plateforme d'aide aux démarches de séjour en France";
export const APP_URL = process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000";

export const STORAGE_BASE = "./storage";
export const STORAGE_DIRS = {
  users: `${STORAGE_BASE}/users`,
  cases: `${STORAGE_BASE}/cases`,
  uploads: `${STORAGE_BASE}/uploads`,
  reports: `${STORAGE_BASE}/reports`,
  logs: `${STORAGE_BASE}/logs`,
};

export const ACCEPTED_FILE_TYPES = {
  "application/pdf": [".pdf"],
  "image/jpeg": [".jpg", ".jpeg"],
  "image/png": [".png"],
  "image/webp": [".webp"],
};

export const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB

export const NATIONALITES_FREQUENTES = [
  "Algérienne", "Marocaine", "Tunisienne", "Ivoirienne", "Sénégalaise",
  "Malienne", "Congolaise (RDC)", "Camerounaise", "Guinéenne", "Béninoise",
  "Togolaise", "Burkinabè", "Nigériane", "Ghanéenne", "Chinoise",
  "Indienne", "Pakistanaise", "Bangladaise", "Sri Lankaise", "Turque",
  "Syrienne", "Irakienne", "Afghane", "Somalienne", "Érythréenne",
  "Soudanaise", "Tchadienne", "Centrafricaine", "Congolaise (Brazzaville)",
  "Gabonaise", "Rwandaise", "Autre",
];

export const PREFECTURES_FRANCE = [
  "Paris", "Lyon", "Marseille", "Toulouse", "Nice", "Nantes", "Strasbourg",
  "Montpellier", "Bordeaux", "Lille", "Rennes", "Reims", "Le Havre",
  "Saint-Étienne", "Toulon", "Grenoble", "Dijon", "Angers", "Nîmes",
  "Clermont-Ferrand", "Autre",
];

export const LOG_LEVELS = {
  INFO: "info",
  WARN: "warn",
  ERROR: "error",
  DEBUG: "debug",
} as const;
