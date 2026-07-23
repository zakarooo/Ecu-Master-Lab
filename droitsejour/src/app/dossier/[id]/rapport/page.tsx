import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { dossierRepository } from "@/services/storage/repository";
import { notFound } from "next/navigation";
import { Card, CardContent } from "@/components/ui/card";
import ReportDownloadButton from "@/components/pdf/ReportDownloadButton";
import type { Metadata } from "next";

export async function generateMetadata({ params }: { params: Promise<{ id: string }> }): Promise<Metadata> {
  const { id } = await params;
  const dossier = dossierRepository.getById(id);
  return {
    title: dossier ? `Rapport PDF — ${dossier.informationsPersonnelles?.prenom} ${dossier.informationsPersonnelles?.nom}` : "Rapport non trouvé",
    description: "Téléchargez le rapport PDF récapitulatif du dossier de séjour.",
  };
}

export default async function RapportPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const dossier = dossierRepository.getById(id);
  if (!dossier) notFound();

  return (
    <div className="container max-w-5xl mx-auto px-4 py-8">
      <Link href={`/dossier/${id}`} className="inline-flex items-center text-sm text-muted-foreground hover:text-primary mb-6">
        <ArrowLeft className="mr-2 h-4 w-4" />
        Retour au dossier
      </Link>
      <h1 className="text-3xl font-bold mb-8">Rapport PDF</h1>
      <Card>
        <CardContent className="py-12 text-center">
          <p className="text-muted-foreground mb-6">
            Générez et téléchargez un rapport PDF professionnel récapitulatif de votre dossier.
          </p>
          <ReportDownloadButton dossier={JSON.parse(JSON.stringify(dossier))} />
        </CardContent>
      </Card>
    </div>
  );
}
