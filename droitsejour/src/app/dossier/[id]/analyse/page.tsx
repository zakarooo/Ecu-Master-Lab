import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { dossierRepository } from "@/services/storage/repository";
import { notFound } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { formatDate } from "@/lib/utils";
import type { Metadata } from "next";

export async function generateMetadata({ params }: { params: Promise<{ id: string }> }): Promise<Metadata> {
  const { id } = await params;
  const dossier = dossierRepository.getById(id);
  return {
    title: dossier ? `Analyse — ${dossier.informationsPersonnelles?.prenom} ${dossier.informationsPersonnelles?.nom}` : "Analyse non trouvée",
    description: "Résultat de l'analyse IA du dossier de séjour.",
  };
}

export default async function AnalysePage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const dossier = dossierRepository.getById(id);
  if (!dossier || !dossier.analyse) notFound();
  const a = dossier.analyse;

  return (
    <div className="container max-w-5xl mx-auto px-4 py-8">
      <Link href={`/dossier/${id}`} className="inline-flex items-center text-sm text-muted-foreground hover:text-primary mb-6">
        <ArrowLeft className="mr-2 h-4 w-4" />
        Retour au dossier
      </Link>

      <h1 className="text-3xl font-bold mb-2">Analyse du dossier</h1>
      <p className="text-sm text-muted-foreground mb-8">Analyse effectuée le {formatDate(a.dateAnalyse)}</p>

      <div className="space-y-6">
        <Card>
          <CardHeader><CardTitle>Résumé</CardTitle></CardHeader>
          <CardContent><p className="text-sm leading-relaxed">{a.resume}</p></CardContent>
        </Card>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card className="border-green-200 dark:border-green-800">
            <CardHeader><CardTitle className="text-green-700 dark:text-green-400">Forces</CardTitle></CardHeader>
            <CardContent>
              <ul className="space-y-2">{a.forces.map((f, i) => <li key={i} className="text-sm flex items-start gap-2"><span className="text-green-500 mt-1">✓</span>{f}</li>)}</ul>
            </CardContent>
          </Card>
          <Card className="border-red-200 dark:border-red-800">
            <CardHeader><CardTitle className="text-red-700 dark:text-red-400">Faiblesses</CardTitle></CardHeader>
            <CardContent>
              <ul className="space-y-2">{a.faiblesses.map((f, i) => <li key={i} className="text-sm flex items-start gap-2"><span className="text-red-500 mt-1">✗</span>{f}</li>)}</ul>
            </CardContent>
          </Card>
        </div>

        {a.documentsManquants.length > 0 && (
          <Card className="border-amber-200 dark:border-amber-800">
            <CardHeader><CardTitle className="text-amber-700 dark:text-amber-400">Documents manquants</CardTitle></CardHeader>
            <CardContent>
              <ul className="space-y-1">{a.documentsManquants.map((d, i) => <li key={i} className="text-sm">• {d}</li>)}</ul>
            </CardContent>
          </Card>
        )}

        {a.risques.length > 0 && (
          <Card className="border-orange-200 dark:border-orange-800">
            <CardHeader><CardTitle className="text-orange-700 dark:text-orange-400">Risques</CardTitle></CardHeader>
            <CardContent>
              <ul className="space-y-1">{a.risques.map((r, i) => <li key={i} className="text-sm">⚠ {r}</li>)}</ul>
            </CardContent>
          </Card>
        )}

        {a.demarchesRecommandees.length > 0 && (
          <Card>
            <CardHeader><CardTitle>Démarches recommandées</CardTitle></CardHeader>
            <CardContent>
              <div className="space-y-4">
                {a.demarchesRecommandees.map((d, i) => (
                  <div key={i} className="border-l-4 border-primary pl-4">
                    <div className="flex items-center gap-2 mb-1">
                      <h4 className="font-medium text-sm">{d.titre}</h4>
                      <Badge variant={d.priorite === "haute" ? "destructive" : d.priorite === "moyenne" ? "secondary" : "outline"}>
                        {d.priorite}
                      </Badge>
                    </div>
                    <p className="text-sm text-muted-foreground">{d.description}</p>
                    {d.delai && <p className="text-xs text-muted-foreground mt-1">Délai: {d.delai}</p>}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
