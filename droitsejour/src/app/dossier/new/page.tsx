import type { Metadata } from "next";
import WizardStepper from "@/components/dossier/WizardStepper";

export const metadata: Metadata = {
  title: "Créer un dossier",
  description: "Créez votre dossier de séjour en France étape par étape.",
};

export default function NewDossierPage() {
  return (
    <div className="min-h-screen">
      <WizardStepper />
    </div>
  );
}
