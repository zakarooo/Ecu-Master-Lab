import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { dossierRepository } from "@/services/storage/repository";
import { notFound } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { Metadata } from "next";

export async function generateMetadata({ params }: { params: Promise<{ id: string }> }): Promise<Metadata> {
  const { id } = await params;
  const dossier = dossierRepository.getById(id);
  return {
    title: dossier ? `Courriers — ${dossier.informationsPersonnelles?.prenom} ${dossier.informationsPersonnelles?.nom}` : "Courriers non trouvés",
    description: "Courriers administratifs générés pour le dossier de séjour.",
  };
}

export default async function CourriersPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const dossier = dossierRepository.getById(id);
  if (!dossier) notFound();

  return (
    <div className="container max-w-5xl mx-auto px-4 py-8">
      <Link href={`/dossier/${id}`} className="inline-flex items-center text-sm text-muted-foreground hover:text-primary mb-6">
        <ArrowLeft className="mr-2 h-4 w-4" />
        Retour au dossier
      </Link>
      <h1 className="text-3xl font-bold mb-8">Courriers</h1>
      {dossier.courriers.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center text-muted-foreground">
            Aucun courrier généré. Lancez l&apos;analyse depuis le wizard pour générer des courriers.
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-6">
          {dossier.courriers.map((c) => (
            <Card key={c.id}>
              <CardHeader>
                <CardTitle className="text-lg">{c.titre}</CardTitle>
                <p className="text-sm text-muted-foreground">Destinataire: {c.destinataire}</p>
              </CardHeader>
              <CardContent>
                <pre className="text-sm whitespace-pre-wrap font-sans leading-relaxed bg-muted/30 p-4 rounded-lg">
                  {c.contenu}
                </pre>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
