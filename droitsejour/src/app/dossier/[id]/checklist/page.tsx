import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { dossierRepository } from "@/services/storage/repository";
import { notFound } from "next/navigation";
import { Card, CardContent } from "@/components/ui/card";
import type { Metadata } from "next";

export async function generateMetadata({ params }: { params: Promise<{ id: string }> }): Promise<Metadata> {
  const { id } = await params;
  const dossier = dossierRepository.getById(id);
  return {
    title: dossier ? `Checklist — ${dossier.informationsPersonnelles?.prenom} ${dossier.informationsPersonnelles?.nom}` : "Checklist non trouvée",
    description: "Liste des pièces justificatives à fournir pour le dossier de séjour.",
  };
}

export default async function ChecklistPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const dossier = dossierRepository.getById(id);
  if (!dossier) notFound();

  const checked = dossier.checklist.filter((c) => c.coche).length;
  const total = dossier.checklist.length;

  return (
    <div className="container max-w-5xl mx-auto px-4 py-8">
      <Link href={`/dossier/${id}`} className="inline-flex items-center text-sm text-muted-foreground hover:text-primary mb-6">
        <ArrowLeft className="mr-2 h-4 w-4" />
        Retour au dossier
      </Link>
      <h1 className="text-3xl font-bold mb-2">Checklist</h1>
      <p className="text-sm text-muted-foreground mb-8">{checked}/{total} éléments complétés</p>
      {dossier.checklist.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center text-muted-foreground">
            Aucune checklist disponible. Lancez l&apos;analyse depuis le wizard.
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-2">
          {dossier.checklist.map((item) => (
            <Card key={item.id} className={item.coche ? "bg-green-50 dark:bg-green-950/20" : ""}>
              <CardContent className="py-3 flex items-center gap-3">
                <span className="text-lg">{item.coche ? "✓" : "☐"}</span>
                <div>
                  <p className={`text-sm font-medium ${item.coche ? "line-through text-muted-foreground" : ""}`}>{item.document}</p>
                  <p className="text-xs text-muted-foreground">{item.description}</p>
                </div>
                {item.obligatoire && <span className="ml-auto text-xs bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400 px-2 py-0.5 rounded">Obligatoire</span>}
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
