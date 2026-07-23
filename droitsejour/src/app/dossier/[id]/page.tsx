import type { Metadata } from "next";
import { notFound } from "next/navigation";
import Link from "next/link";
import { ArrowLeft, Calendar, FileText, User } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { formatDate } from "@/lib/utils";
import { dossierRepository } from "@/services/storage/repository";

export async function generateMetadata({ params }: { params: Promise<{ id: string }> }): Promise<Metadata> {
  const { id } = await params;
  const dossier = dossierRepository.getById(id);
  if (!dossier) return { title: "Dossier non trouvé" };
  const prenom = dossier.informationsPersonnelles?.prenom || "";
  const nom = dossier.informationsPersonnelles?.nom || "";
  const name = `${prenom} ${nom}`.trim() || dossier.nom;
  return {
    title: `Dossier — ${name}`,
    description: `Dossier de séjour de ${name}. Statut : ${dossier.statut}.`,
  };
}

export default async function DossierDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const dossier = dossierRepository.getById(id);
  
  if (!dossier) notFound();

  const statutBadge = {
    brouillon: "secondary" as const,
    en_cours: "default" as const,
    analyse: "outline" as const,
    termine: "default" as const,
  };

  return (
    <div className="container max-w-5xl mx-auto px-4 py-8">
      <Link href="/" className="inline-flex items-center text-sm text-muted-foreground hover:text-primary mb-6">
        <ArrowLeft className="mr-2 h-4 w-4" />
        Retour à l&apos;accueil
      </Link>

      <div className="flex items-start justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold mb-2">{dossier.nom}</h1>
          <div className="flex items-center gap-4 text-sm text-muted-foreground">
            <span className="flex items-center gap-1">
              <Calendar className="h-4 w-4" />
              Créé le {formatDate(dossier.dateCreation)}
            </span>
            <Badge variant={statutBadge[dossier.statut]}>
              {dossier.statut}
            </Badge>
          </div>
        </div>
        <Link href={`/dossier/${id}/analyse`}>
          <Button>Voir l&apos;analyse</Button>
        </Link>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm flex items-center gap-2">
              <User className="h-4 w-4" />
              Informations
            </CardTitle>
          </CardHeader>
          <CardContent className="text-sm space-y-1">
            <p><strong>Nom:</strong> {dossier.informationsPersonnelles?.prenom} {dossier.informationsPersonnelles?.nom}</p>
            <p><strong>Nationalité:</strong> {dossier.informationsPersonnelles?.nationalite}</p>
            <p><strong>Situation:</strong> {dossier.situationAdministrative?.statutSejour}</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm flex items-center gap-2">
              <FileText className="h-4 w-4" />
              Documents
            </CardTitle>
          </CardHeader>
          <CardContent className="text-sm">
            <p>{dossier.documents?.length || 0} document(s) joint(s)</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm flex items-center gap-2">
              <FileText className="h-4 w-4" />
              Démarches
            </CardTitle>
          </CardHeader>
          <CardContent className="text-sm">
            <p>{dossier.demarchesPrecedentes?.length || 0} démarche(s) enregistrée(s)</p>
          </CardContent>
        </Card>
      </div>

      <div className="mt-8 flex gap-4">
        <Link href={`/dossier/${id}/analyse`}>
          <Button variant="outline">Analyse IA</Button>
        </Link>
        <Link href={`/dossier/${id}/courriers`}>
          <Button variant="outline">Courriers</Button>
        </Link>
        <Link href={`/dossier/${id}/checklist`}>
          <Button variant="outline">Checklist</Button>
        </Link>
        <Link href={`/dossier/${id}/rapport`}>
          <Button variant="outline">Rapport PDF</Button>
        </Link>
      </div>
    </div>
  );
}
