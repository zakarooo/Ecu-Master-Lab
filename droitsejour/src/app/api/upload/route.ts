import { NextRequest, NextResponse } from "next/server";
import { uploadRepository } from "@/services/storage/repository";
import { generateId } from "@/lib/utils";
import { Document } from "@/types";

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();
    const file = formData.get("file") as File;
    const dossierId = formData.get("dossierId") as string;

    if (!file || !dossierId) {
      return NextResponse.json({ error: "Fichier et dossierId requis" }, { status: 400 });
    }

    const buffer = Buffer.from(await file.arrayBuffer());
    const savedFilename = uploadRepository.saveFile(buffer, file.name, dossierId);
    const relativePath = `/api/uploads/${dossierId}/${savedFilename}`;

    const doc: Document = {
      id: generateId(),
      nom: file.name,
      type: "autre",
      chemin: relativePath,
      taille: file.size,
      mimetype: file.type,
      dateAjout: new Date().toISOString(),
    };

    return NextResponse.json(doc);
  } catch {
    return NextResponse.json({ error: "Erreur lors de l'upload" }, { status: 500 });
  }
}
