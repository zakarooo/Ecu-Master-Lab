import { NextRequest, NextResponse } from "next/server";
import { analyzeDossier } from "@/services/ai/ai-service";
import { dossierRepository } from "@/services/storage/repository";

export async function POST(_request: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  try {
    const dossier = dossierRepository.getById(id);
    if (!dossier) return NextResponse.json({ error: "Dossier non trouvé" }, { status: 404 });

    const analyse = await analyzeDossier(dossier);
    dossier.analyse = analyse;
    dossier.statut = "analyse";
    dossierRepository.save(dossier);

    return NextResponse.json(analyse);
  } catch {
    return NextResponse.json({ error: "Erreur lors de l'analyse" }, { status: 500 });
  }
}
