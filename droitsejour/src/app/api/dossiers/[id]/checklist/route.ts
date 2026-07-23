import { NextRequest, NextResponse } from "next/server";
import { generateChecklist } from "@/services/ai/ai-service";
import { dossierRepository } from "@/services/storage/repository";

export async function POST(_request: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  try {
    const dossier = dossierRepository.getById(id);
    if (!dossier) return NextResponse.json({ error: "Dossier non trouvé" }, { status: 404 });

    const checklist = generateChecklist(dossier);
    dossier.checklist = checklist;
    dossierRepository.save(dossier);

    return NextResponse.json(checklist);
  } catch {
    return NextResponse.json({ error: "Erreur lors de la génération de la checklist" }, { status: 500 });
  }
}
