"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { FileDown, Loader2, Download, Eye } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import type { Dossier } from "@/types";

interface StepProps {
  dossier: Dossier;
  onUpdate: (data: Partial<Dossier>) => void;
  onNext: () => void;
  onPrev: () => void;
}

export default function StepReport({ dossier, onUpdate, onPrev }: StepProps) {
  const [generating, setGenerating] = useState(false);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [generated, setGenerated] = useState(dossier.rapportGenere ?? false);

  const handleGenerate = async () => {
    setGenerating(true);
    try {
      const { jsPDF } = await import("jspdf");
      const doc = new jsPDF();

      const pageWidth = doc.internal.pageSize.getWidth();
      let y = 20;

      doc.setFontSize(18);
      doc.text("Rapport Dossier Administratif", pageWidth / 2, y, { align: "center" });
      y += 10;

      doc.setFontSize(10);
      doc.setTextColor(128);
      doc.text(`Dossier: ${dossier.nom}`, pageWidth / 2, y, { align: "center" });
      y += 6;
      doc.text(`Date: ${new Date().toLocaleDateString("fr-FR")}`, pageWidth / 2, y, { align: "center" });
      y += 12;

      doc.setTextColor(0);

      const addSection = (title: string, content: string | string[]) => {
        if (y > 260) { doc.addPage(); y = 20; }
        doc.setFontSize(13);
        doc.setFont("helvetica", "bold");
        doc.text(title, 15, y);
        y += 7;
        doc.setFontSize(10);
        doc.setFont("helvetica", "normal");
        if (Array.isArray(content)) {
          content.forEach((item) => {
            if (y > 275) { doc.addPage(); y = 20; }
            doc.text(`• ${item}`, 20, y);
            y += 5;
          });
        } else {
          const lines = doc.splitTextToSize(content, pageWidth - 30);
          lines.forEach((line: string) => {
            if (y > 275) { doc.addPage(); y = 20; }
            doc.text(line, 20, y);
            y += 5;
          });
        }
        y += 5;
      };

      const ip = dossier.informationsPersonnelles;
      if (ip) {
        addSection("Informations personnelles", [
          `Nom: ${ip.prenom} ${ip.nom}`,
          `Né(e) le ${ip.dateNaissance} à ${ip.lieuNaissance}`,
          `Nationalité: ${ip.nationalite}`,
          `Adresse: ${ip.adresse}, ${ip.codePostal} ${ip.ville}`,
          `Tél: ${ip.telephone} | Email: ${ip.email}`,
          `Situation familiale: ${ip.situationFamiliale}`,
        ]);
      }

      const sa = dossier.situationAdministrative;
      if (sa) {
        addSection("Situation administrative", [
          `Statut de séjour: ${sa.statutSejour}`,
          sa.typeTitre ? `Type de titre: ${sa.typeTitre}` : "",
          sa.prefecture ? `Préfecture: ${sa.prefecture}` : "",
          sa.motifSejour ? `Motif: ${sa.motifSejour}` : "",
          sa.dateExpiration ? `Expiration: ${sa.dateExpiration}` : "",
        ].filter(Boolean));
      }

      if (dossier.analyse) {
        addSection("Résumé de l'analyse", dossier.analyse.resume);
        addSection("Forces", dossier.analyse.forces);
        addSection("Faiblesses", dossier.analyse.faiblesses);
        addSection("Documents manquants", dossier.analyse.documentsManquants);
        addSection("Arguments favorables", dossier.analyse.argumentsFavorables);
        addSection("Risques", dossier.analyse.risques);
      }

      if (dossier.analyse?.demarchesRecommandees) {
        const demarches = dossier.analyse.demarchesRecommandees.map(
          (d, i) => `[${d.priorite.toUpperCase()}] ${i + 1}. ${d.titre}: ${d.description}`
        );
        addSection("Démarches recommandées", demarches);
      }

      if (dossier.memos && dossier.memos.length > 0) {
        const memosContent = dossier.memos.map((m) => m.contenu);
        addSection("Mémos", memosContent);
      }

      const blob = doc.output("blob");
      const url = URL.createObjectURL(blob);
      setPreviewUrl(url);
      setGenerated(true);
      onUpdate({ rapportGenere: true });
    } catch {
      // silently fail
    } finally {
      setGenerating(false);
    }
  };

  const handleDownload = () => {
    if (!previewUrl) return;
    const a = document.createElement("a");
    a.href = previewUrl;
    a.download = `rapport-${dossier.nom || "dossier"}.pdf`;
    a.click();
  };

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}>
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileDown className="h-5 w-5" />
            Rapport PDF
          </CardTitle>
          <CardDescription>
            Générez un rapport complet du dossier au format PDF.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="text-center py-4 space-y-4">
            {!generated && !previewUrl && (
              <div className="space-y-3">
                <FileDown className="h-12 w-12 mx-auto text-muted-foreground" />
                <p className="text-sm text-muted-foreground">
                  Générez un rapport PDF synthétisant toutes les informations du dossier.
                </p>
                <Button onClick={handleGenerate} disabled={generating}>
                  {generating ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Génération en cours...
                    </>
                  ) : (
                    <>
                      <FileDown className="h-4 w-4 mr-2" />
                      Générer le rapport PDF
                    </>
                  )}
                </Button>
              </div>
            )}

            {generated && (
              <div className="space-y-3">
                <p className="text-sm text-green-700">Le rapport a été généré avec succès.</p>
                <div className="flex gap-2 justify-center">
                  <Button variant="outline" onClick={() => { setGenerated(false); setPreviewUrl(null); }}>
                    <FileDown className="h-4 w-4 mr-2" />
                    Régénérer
                  </Button>
                  <Button onClick={handleDownload} disabled={!previewUrl}>
                    <Download className="h-4 w-4 mr-2" />
                    Télécharger
                  </Button>
                </div>
              </div>
            )}
          </div>

          {previewUrl && (
            <div className="border rounded-lg overflow-hidden">
              <div className="flex items-center gap-2 bg-muted/50 px-4 py-2 border-b">
                <Eye className="h-4 w-4" />
                <span className="text-sm font-medium">Aperçu</span>
              </div>
              <iframe
                src={previewUrl}
                className="w-full h-[500px]"
                title="Aperçu du rapport PDF"
              />
            </div>
          )}

          <div className="flex justify-between pt-4">
            <Button type="button" variant="outline" onClick={onPrev}>
              Précédent
            </Button>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}
