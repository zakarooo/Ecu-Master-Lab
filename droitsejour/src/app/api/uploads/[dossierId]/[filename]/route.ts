import { NextRequest, NextResponse } from "next/server";
import { uploadRepository } from "@/services/storage/repository";
import fs from "fs";
import path from "path";

export async function GET(
  _request: NextRequest,
  { params }: { params: Promise<{ dossierId: string; filename: string }> }
) {
  const { dossierId, filename } = await params;
  try {
    const filePath = uploadRepository.getFilePath(dossierId, filename);
    if (!filePath) {
      return NextResponse.json({ error: "Fichier non trouvé" }, { status: 404 });
    }

    const buffer = fs.readFileSync(filePath);
    const ext = path.extname(filename).toLowerCase();
    const mimeTypes: Record<string, string> = {
      ".pdf": "application/pdf",
      ".jpg": "image/jpeg",
      ".jpeg": "image/jpeg",
      ".png": "image/png",
      ".webp": "image/webp",
    };
    const contentType = mimeTypes[ext] || "application/octet-stream";

    return new NextResponse(buffer, {
      headers: {
        "Content-Type": contentType,
        "Content-Disposition": `inline; filename="${filename}"`,
      },
    });
  } catch {
    return NextResponse.json({ error: "Erreur serveur" }, { status: 500 });
  }
}
