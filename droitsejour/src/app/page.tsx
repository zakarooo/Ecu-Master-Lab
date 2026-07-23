import Link from "next/link";
import { Scale, Shield, FileText, Brain, Mail, Download, CheckCircle, ArrowRight, AlertTriangle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { FAQJsonLd } from "@/components/shared/JsonLd";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "DroitSéjour — Simplifiez vos démarches de séjour en France",
  description:
    "Accompagnement personnalisé pour les personnes rencontrant des difficultés dans leurs démarches de séjour, régularisation ou obtention de documents administratifs en France.",
};

const features = [
  { icon: FileText, title: "Création de dossier", description: "Guidage étape par étape pour constituer un dossier complet et clair." },
  { icon: Brain, title: "Analyse IA", description: "Analyse automatisée de votre situation avec identification des forces et risques." },
  { icon: Mail, title: "Courriers automatiques", description: "Génération de courriers administratifs personnalisés et adaptés à votre cas." },
  { icon: CheckCircle, title: "Checklist complète", description: "Liste des pièces justificatives obligatoires et recommandées." },
  { icon: Download, title: "Rapport PDF", description: "Téléchargement d'un rapport professionnel récapitulatif de votre dossier." },
  { icon: Shield, title: "Confidentialité", description: "Toutes vos données restent stockées localement. Aucune fuite possible." },
];

const steps = [
  "Créez votre dossier en quelques minutes",
  "Complétez vos informations personnelles",
  "Décrivez votre situation administrative",
  "Téléversez vos documents",
  "Recevez une analyse personnalisée",
  "Téléchargez votre rapport et courriers",
];

export default function HomePage() {
  return (
    <div className="flex flex-col">
      <FAQJsonLd />
      {/* Hero */}
      <section className="relative overflow-hidden bg-gradient-to-br from-primary/5 via-background to-primary/10 py-20 md:py-32">
        <div className="container px-4 md:px-8 relative z-10">
          <div className="max-w-3xl mx-auto text-center">
            <div className="inline-flex items-center gap-2 rounded-full bg-primary/10 px-4 py-1.5 text-sm text-primary mb-6">
              <Scale className="h-4 w-4" />
              Plateforme d&apos;aide juridique
            </div>
            <h1 className="text-4xl md:text-6xl font-bold tracking-tight mb-6">
              Simplifiez vos démarches de{" "}
              <span className="text-primary">séjour en France</span>
            </h1>
            <p className="text-lg md:text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
              Accompagnement personnalisé pour les personnes rencontrant des difficultés
              dans leurs démarches de séjour, régularisation ou obtention de documents administratifs.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href="/dossier/new">
                <Button size="lg" className="text-base px-8">
                  Créer mon dossier
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Button>
              </Link>
              <Button variant="outline" size="lg" className="text-base px-8">
                En savoir plus
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Disclaimer */}
      <section className="bg-amber-50 dark:bg-amber-950/30 border-y">
        <div className="container px-4 md:px-8 py-4">
          <div className="flex items-start gap-3 max-w-4xl mx-auto">
            <AlertTriangle className="h-5 w-5 text-amber-600 dark:text-amber-400 mt-0.5 shrink-0" />
            <p className="text-sm text-amber-800 dark:text-amber-200">
              <strong>Avertissement :</strong> DroitSéjour est un outil d&apos;aide informative.
              Les analyses, courriers et recommandations générés ne constituent pas un avis juridique
              et ne remplacent pas les conseils d&apos;un avocat ou d&apos;un professionnel qualifié en droit des étrangers.
            </p>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-16 md:py-24">
        <div className="container px-4 md:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">Fonctionnalités principales</h2>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              Tout ce dont vous avez besoin pour structurer et compléter votre dossier de séjour.
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
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
        </div>
      </section>

      {/* Steps */}
      <section className="py-16 md:py-24 bg-muted/30">
        <div className="container px-4 md:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">Comment ça marche ?</h2>
            <p className="text-muted-foreground">Un parcours simple en 6 étapes.</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-4xl mx-auto">
            {steps.map((step, i) => (
              <div key={i} className="flex items-start gap-4">
                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary text-primary-foreground font-bold text-sm">
                  {i + 1}
                </div>
                <p className="text-sm pt-1">{step}</p>
              </div>
            ))}
          </div>
          <div className="text-center mt-12">
            <Link href="/dossier/new">
              <Button size="lg" className="text-base px-8">
                Commencer maintenant
                <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
