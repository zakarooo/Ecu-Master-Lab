import { NextRequest, NextResponse } from "next/server";
import { dossierRepository } from "@/services/storage/repository";

export async function GET(_request: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  try {
    const dossier = dossierRepository.getById(id);
    if (!dossier) return NextResponse.json({ error: "Dossier non trouvé" }, { status: 404 });
    return NextResponse.json(dossier);
  } catch {
    return NextResponse.json({ error: "Erreur serveur" }, { status: 500 });
  }
}

export async function PUT(request: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  try {
    const existing = dossierRepository.getById(id);
    if (!existing) return NextResponse.json({ error: "Dossier non trouvé" }, { status: 404 });
    const body = await request.json();
    const updated = dossierRepository.save({ ...existing, ...body, id });
    return NextResponse.json(updated);
  } catch {
    return NextResponse.json({ error: "Erreur serveur" }, { status: 500 });
  }
}

export async function DELETE(_request: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  try {
    const deleted = dossierRepository.delete(id);
    if (!deleted) return NextResponse.json({ error: "Dossier non trouvé" }, { status: 404 });
    return NextResponse.json({ success: true });
  } catch {
    return NextResponse.json({ error: "Erreur serveur" }, { status: 500 });
  }
}
