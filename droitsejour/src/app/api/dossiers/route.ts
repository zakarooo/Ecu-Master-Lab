import { NextRequest, NextResponse } from "next/server";
import { dossierRepository } from "@/services/storage/repository";

export async function GET() {
  try {
    const dossiers = dossierRepository.getAll();
    return NextResponse.json(dossiers);
  } catch {
    return NextResponse.json({ error: "Erreur lors de la récupération des dossiers" }, { status: 500 });
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    if (!body || typeof body !== "object" || !body.informationsPersonnelles) {
      return NextResponse.json({ error: "Body invalide" }, { status: 400 });
    }
    const dossier = dossierRepository.create(body);
    return NextResponse.json(dossier, { status: 201 });
  } catch {
    return NextResponse.json({ error: "Erreur lors de la création du dossier" }, { status: 500 });
  }
}
