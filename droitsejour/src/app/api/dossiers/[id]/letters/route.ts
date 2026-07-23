import { NextRequest, NextResponse } from "next/server";
import { generateLetter } from "@/services/ai/ai-service";
import { dossierRepository } from "@/services/storage/repository";
import { TypeCourrier } from "@/types";

export async function POST(request: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  try {
    const { type } = await request.json() as { type: TypeCourrier };
    const dossier = dossierRepository.getById(id);
    if (!dossier) return NextResponse.json({ error: "Dossier non trouvé" }, { status: 404 });

    const courrier = await generateLetter(dossier, type);
    dossier.courriers.push(courrier);
    dossierRepository.save(dossier);

    return NextResponse.json(courrier);
  } catch {
    return NextResponse.json({ error: "Erreur lors de la génération" }, { status: 500 });
  }
}
