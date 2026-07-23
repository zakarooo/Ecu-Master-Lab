"use client";

import { useState } from "react";
import { Download, FileDown, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Dossier } from "@/types";
import { generateReportPDF, downloadPDF } from "@/services/pdf/pdf-service";

export default function ReportDownloadButton({ dossier }: { dossier: Dossier }) {
  const [generating, setGenerating] = useState(false);

  const handleGenerate = () => {
    setGenerating(true);
    setTimeout(() => {
      try {
        const doc = generateReportPDF(dossier);
        const filename = `rapport-${dossier.informationsPersonnelles?.nom || "dossier"}-${new Date().toISOString().split("T")[0]}.pdf`;
        downloadPDF(doc, filename);
      } catch (error) {
        console.error("PDF generation error:", error);
      } finally {
        setGenerating(false);
      }
    }, 500);
  };

  return (
    <div className="flex flex-col items-center gap-4">
      <FileDown className="h-16 w-16 text-primary/30" />
      <Button onClick={handleGenerate} disabled={generating} size="lg">
        {generating ? (
          <>
            <Loader2 className="mr-2 h-5 w-5 animate-spin" />
            Génération en cours...
          </>
        ) : (
          <>
            <Download className="mr-2 h-5 w-5" />
            Télécharger le rapport PDF
          </>
        )}
      </Button>
      <p className="text-xs text-muted-foreground">
        Le rapport sera téléchargé automatiquement.
      </p>
    </div>
  );
}
