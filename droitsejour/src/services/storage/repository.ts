import fs from "fs";
import path from "path";
import { Dossier, User } from "@/types";
import { generateId, getTodayISO } from "@/lib/utils";

const STORAGE_BASE = path.join(process.cwd(), "storage");

function ensureDir(dirPath: string): void {
  if (!fs.existsSync(dirPath)) {
    fs.mkdirSync(dirPath, { recursive: true });
  }
}

function readJSON<T>(filePath: string): T | null {
  try {
    if (!fs.existsSync(filePath)) return null;
    const data = fs.readFileSync(filePath, "utf-8");
    return JSON.parse(data) as T;
  } catch {
    return null;
  }
}

function writeJSON<T>(filePath: string, data: T): void {
  ensureDir(path.dirname(filePath));
  fs.writeFileSync(filePath, JSON.stringify(data, null, 2), "utf-8");
}

function listFiles(dirPath: string, extension: string = ".json"): string[] {
  ensureDir(dirPath);
  return fs.readdirSync(dirPath)
    .filter((f) => f.endsWith(extension))
    .map((f) => path.join(dirPath, f));
}

// === Dossier Repository ===
export const dossierRepository = {
  getAll(): Dossier[] {
    const dir = path.join(STORAGE_BASE, "cases");
    const files = listFiles(dir);
    return files
      .map((f) => readJSON<Dossier>(f))
      .filter((d): d is Dossier => d !== null)
      .sort((a, b) => new Date(b.dateModification).getTime() - new Date(a.dateModification).getTime());
  },

  getById(id: string): Dossier | null {
    const filePath = path.join(STORAGE_BASE, "cases", `${id}.json`);
    return readJSON<Dossier>(filePath);
  },

  save(dossier: Dossier): Dossier {
    const updated = { ...dossier, dateModification: getTodayISO() };
    const filePath = path.join(STORAGE_BASE, "cases", `${updated.id}.json`);
    writeJSON(filePath, updated);
    return updated;
  },

  create(data: Partial<Dossier>): Dossier {
    const id = generateId();
    const now = getTodayISO();
    const dossier: Dossier = {
      id,
      nom: data.nom || "Nouveau dossier",
      statut: data.statut || "brouillon",
      informationsPersonnelles: data.informationsPersonnelles || ({} as Dossier["informationsPersonnelles"]),
      situationAdministrative: data.situationAdministrative || ({} as Dossier["situationAdministrative"]),
      situationFamiliale: data.situationFamiliale || { situation: "celibataire" },
      demarchesPrecedentes: data.demarchesPrecedentes || [],
      documents: data.documents || [],
      memos: data.memos || [],
      courriers: data.courriers || [],
      checklist: data.checklist || [],
      rapportGenere: data.rapportGenere || false,
      dateCreation: data.dateCreation || now,
      dateModification: now,
    };
    return this.save(dossier);
  },

  delete(id: string): boolean {
    const filePath = path.join(STORAGE_BASE, "cases", `${id}.json`);
    if (fs.existsSync(filePath)) {
      fs.unlinkSync(filePath);
      return true;
    }
    return false;
  },

  search(query: string): Dossier[] {
    const all = this.getAll();
    const q = query.toLowerCase();
    return all.filter(
      (d) =>
        d.nom.toLowerCase().includes(q) ||
        d.informationsPersonnelles?.prenom?.toLowerCase().includes(q) ||
        d.informationsPersonnelles?.nom?.toLowerCase().includes(q)
    );
  },
};

// === User Repository ===
export const userRepository = {
  getAll(): User[] {
    const dir = path.join(STORAGE_BASE, "users");
    const files = listFiles(dir);
    return files
      .map((f) => readJSON<User>(f))
      .filter((u): u is User => u !== null);
  },

  getById(id: string): User | null {
    const filePath = path.join(STORAGE_BASE, "users", `${id}.json`);
    return readJSON<User>(filePath);
  },

  save(user: User): User {
    const filePath = path.join(STORAGE_BASE, "users", `${user.id}.json`);
    writeJSON(filePath, user);
    return user;
  },

  create(data: Omit<User, "id" | "dateCreation">): User {
    const user: User = {
      id: generateId(),
      dateCreation: getTodayISO(),
      ...data,
    };
    return this.save(user);
  },
};

// === Upload Repository ===
export const uploadRepository = {
  saveFile(buffer: Buffer, filename: string, dossierId: string): string {
    const uploadDir = path.join(STORAGE_BASE, "uploads", dossierId);
    ensureDir(uploadDir);
    const uniqueName = `${generateId()}_${filename}`;
    const filePath = path.join(uploadDir, uniqueName);
    fs.writeFileSync(filePath, buffer);
    return uniqueName;
  },

  getFilePath(dossierId: string, filename: string): string | null {
    const filePath = path.join(STORAGE_BASE, "uploads", dossierId, filename);
    return fs.existsSync(filePath) ? filePath : null;
  },

  deleteFile(filePath: string): boolean {
    if (fs.existsSync(filePath)) {
      fs.unlinkSync(filePath);
      return true;
    }
    return false;
  },
};

// === Log Repository ===
export const logRepository = {
  log(level: string, message: string, data?: unknown): void {
    const logDir = path.join(STORAGE_BASE, "logs");
    ensureDir(logDir);
    const date = new Date().toISOString().split("T")[0];
    const logFile = path.join(logDir, `${date}.json`);
    const logs = readJSON<Array<{ timestamp: string; level: string; message: string; data?: unknown }>>(logFile) || [];
    logs.push({ timestamp: getTodayISO(), level, message, data });
    writeJSON(logFile, logs);
  },

  info(message: string, data?: unknown) {
    this.log("info", message, data);
  },
  warn(message: string, data?: unknown) {
    this.log("warn", message, data);
  },
  error(message: string, data?: unknown) {
    this.log("error", message, data);
  },
};
