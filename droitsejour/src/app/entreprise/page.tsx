import Link from "next/link";
import { ArrowLeft, Building2, Users, FileCheck, ArrowRight, AlertTriangle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Espace Entreprise — DroitSéjour",
  description:
    "Gérez les demandes de séjour de vos salariés étrangers. Autorisation de travail, régularisation, et suivi des dossiers.",
};

const features = [
  {
    icon: FileCheck,
    title: "Autorisation de travail",
    description: "Générez les pièces nécessaires pour les demandes d'autorisation de travail (CERFA, promesse d'embauche).",
  },
  {
    icon: Users,
    title: "Régularisation salarié",
    description: "Accompagnez vos salariés dans leur démarche de régularisation de situation administrative.",
  },
  {
    icon: Building2,
    title: "Suivi multi-dossiers",
    description: "Gérez plusieurs dossiers salariés depuis un seul espace centralisé.",
  },
];

export default function EntreprisePage() {
  return (
    <div className="container max-w-5xl mx-auto px-4 py-8">
      <Link href="/" className="inline-flex items-center text-sm text-muted-foreground hover:text-primary mb-6">
        <ArrowLeft className="mr-2 h-4 w-4" />
        Retour à l&apos;accueil
      </Link>

      <div className="mb-12">
        <div className="inline-flex items-center gap-2 rounded-full bg-primary/10 px-4 py-1.5 text-sm text-primary mb-6">
          <Building2 className="h-4 w-4" />
          Espace Entreprise
        </div>
        <h1 className="text-3xl md:text-4xl font-bold mb-4">
          Gérez les séjours de vos{" "}
          <span className="text-primary">salariés étrangers</span>
        </h1>
        <p className="text-lg text-muted-foreground max-w-2xl">
          Outil dédié aux DRH et services RH pour faciliter les démarches de séjour
          et d&apos;autorisation de travail de vos collaborateurs étrangers.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
        {features.map((f, i) => (
          <Card key={i} className="hover:shadow-md transition-shadow">
            <CardContent className="p-6">
              <f.icon className="h-10 w-10 text-primary mb-4" />
              <h3 className="font-semibold text-lg mb-2">{f.title}</h3>
              <p className="text-sm text-muted-foreground">{f.description}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      <Card className="border-primary/20">
        <CardHeader>
          <CardTitle>Commencer un dossier salarié</CardTitle>
          <CardDescription>
            Créez un nouveau dossier pour un salarié étranger. Le wizard vous guidera
            à travers les étapes nécessaires.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Link href="/dossier/new">
            <Button size="lg" className="text-base px-8">
              Créer un dossier salarié
              <ArrowRight className="ml-2 h-5 w-5" />
            </Button>
          </Link>
        </CardContent>
      </Card>

      <div className="mt-12 bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-800 rounded-lg p-6">
        <div className="flex items-start gap-3">
          <AlertTriangle className="h-5 w-5 text-amber-600 dark:text-amber-400 mt-0.5 shrink-0" />
          <div>
            <h3 className="font-semibold text-amber-800 dark:text-amber-200 mb-1">
              Avertissement
            </h3>
            <p className="text-sm text-amber-700 dark:text-amber-300">
              Cet outil est un assistant informatif. Les documents générés ne remplacent pas
              les conseils d&apos;un avocat spécialisé en droit des étrangers. Vérifiez toujours
              les informations avec votre service juridique.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
