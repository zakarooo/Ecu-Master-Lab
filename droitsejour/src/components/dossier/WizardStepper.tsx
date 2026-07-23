"use client";

import { useState, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  User, FileText, Users, Clock, Upload, StickyNote, Brain, 
  Lightbulb, Mail, CheckSquare, FileDown,
  Save, Check 
} from "lucide-react";
import { Progress } from "@/components/ui/progress";
import { cn, generateId, getTodayISO } from "@/lib/utils";
import { Dossier, WizardStepId, WIZARD_STEPS } from "@/types";
import { toast } from "sonner";

import StepPersonalInfo from "./StepPersonalInfo";
import StepAdministrativeSituation from "./StepAdministrativeSituation";
import StepFamilySituation from "./StepFamilySituation";
import StepHistory from "./StepHistory";
import StepDocuments from "./StepDocuments";
import StepMemo from "./StepMemo";
import StepAnalysis from "./StepAnalysis";
import StepRecommendations from "./StepRecommendations";
import StepLetters from "./StepLetters";
import StepChecklist from "./StepChecklist";
import StepReport from "./StepReport";

const iconMap: Record<string, React.ElementType> = {
  User, FileText, Users, Clock, Upload, StickyNote, Brain,
  Lightbulb, Mail, CheckSquare, FileDown,
};

export default function WizardStepper({ existingDossier }: { existingDossier?: Dossier }) {
  const [currentStep, setCurrentStep] = useState(0);
  const [dossier, setDossier] = useState<Dossier>(
    existingDossier || {
      id: generateId(),
      nom: "Nouveau dossier",
      statut: "brouillon",
      informationsPersonnelles: {} as Dossier["informationsPersonnelles"],
      situationAdministrative: {} as Dossier["situationAdministrative"],
      situationFamiliale: { situation: "celibataire" },
      demarchesPrecedentes: [],
      documents: [],
      memos: [],
      courriers: [],
      checklist: [],
      rapportGenere: false,
      dateCreation: getTodayISO(),
      dateModification: getTodayISO(),
    }
  );
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  const progress = ((currentStep + 1) / WIZARD_STEPS.length) * 100;

  const saveDossier = useCallback(async (data: Partial<Dossier>) => {
    setSaving(true);
    try {
      const updated = { ...dossier, ...data, dateModification: getTodayISO() };
      setDossier(updated);
      
      const hasExistingRecord = existingDossier || saved;
      const url = hasExistingRecord ? `/api/dossiers/${updated.id}` : "/api/dossiers";
      const method = hasExistingRecord ? "PUT" : "POST";
      
      const res = await fetch(url, {
        method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(updated),
      });
      
      if (res.ok) {
        const result = await res.json();
        setDossier(prev => ({ ...prev, ...result }));
        setSaved(true);
        setTimeout(() => setSaved(false), 2000);
      }
    } catch {
      toast.error("Erreur de sauvegarde");
    } finally {
      setSaving(false);
    }
  }, [dossier, existingDossier, saved]);

  const handleUpdate = (data: Partial<Dossier>) => {
    const updated = { ...dossier, ...data };
    setDossier(updated);
  };

  const handleNext = () => {
    if (currentStep < WIZARD_STEPS.length - 1) {
      saveDossier(dossier);
      setCurrentStep(currentStep + 1);
    }
  };

  const handlePrev = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const stepComponents: Record<WizardStepId, React.ReactNode> = {
    personal: <StepPersonalInfo dossier={dossier} onUpdate={handleUpdate} onNext={handleNext} onPrev={handlePrev} />,
    administrative: <StepAdministrativeSituation dossier={dossier} onUpdate={handleUpdate} onNext={handleNext} onPrev={handlePrev} />,
    family: <StepFamilySituation dossier={dossier} onUpdate={handleUpdate} onNext={handleNext} onPrev={handlePrev} />,
    history: <StepHistory dossier={dossier} onUpdate={handleUpdate} onNext={handleNext} onPrev={handlePrev} />,
    documents: <StepDocuments dossier={dossier} onUpdate={handleUpdate} onNext={handleNext} onPrev={handlePrev} />,
    memo: <StepMemo dossier={dossier} onUpdate={handleUpdate} onNext={handleNext} onPrev={handlePrev} />,
    analysis: <StepAnalysis dossier={dossier} onUpdate={handleUpdate} onNext={handleNext} onPrev={handlePrev} />,
    recommendations: <StepRecommendations dossier={dossier} onUpdate={handleUpdate} onNext={handleNext} onPrev={handlePrev} />,
    letters: <StepLetters dossier={dossier} onUpdate={handleUpdate} onNext={handleNext} onPrev={handlePrev} />,
    checklist: <StepChecklist dossier={dossier} onUpdate={handleUpdate} onNext={handleNext} onPrev={handlePrev} />,
    report: <StepReport dossier={dossier} onUpdate={handleUpdate} onNext={handleNext} onPrev={handlePrev} />,
  };

  return (
    <div className="container max-w-5xl mx-auto px-4 py-8">
      {/* Progress header */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <h1 className="text-2xl font-bold">Création du dossier</h1>
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            {saving ? (
              <><Save className="h-4 w-4 animate-pulse" /> Sauvegarde...</>
            ) : saved ? (
              <><Check className="h-4 w-4 text-green-500" /> Sauvegardé</>
            ) : null}
          </div>
        </div>
        
        <Progress value={progress} className="h-2 mb-3" aria-label={`Progression: ${Math.round(progress)}%`} />
        
        {/* Step indicators */}
        <div className="hidden md:flex justify-between overflow-x-auto pb-2">
          {WIZARD_STEPS.map((step, i) => {
            const Icon = iconMap[step.icon] || FileText;
            return (
              <button
                key={step.id}
                onClick={() => setCurrentStep(i)}
                className={cn(
                  "flex flex-col items-center gap-1 px-2 py-1 rounded-lg transition-all text-xs min-w-0",
                  i === currentStep && "text-primary bg-primary/10 font-medium",
                  i < currentStep && "text-green-600 dark:text-green-400",
                  i > currentStep && "text-muted-foreground"
                )}
              >
                <Icon className="h-4 w-4 shrink-0" />
                <span className="truncate max-w-[80px]">{step.label}</span>
              </button>
            );
          })}
        </div>

        {/* Mobile step indicator */}
        <div className="md:hidden flex items-center justify-center gap-2 text-sm">
          <span className="font-medium text-primary">Étape {currentStep + 1}</span>
          <span className="text-muted-foreground">/ {WIZARD_STEPS.length}</span>
          <span className="text-muted-foreground">— {WIZARD_STEPS[currentStep].label}</span>
        </div>
      </div>

      {/* Step content */}
      <AnimatePresence mode="wait">
        <motion.div
          key={currentStep}
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -20 }}
          transition={{ duration: 0.2 }}
        >
          {stepComponents[WIZARD_STEPS[currentStep].id]}
        </motion.div>
      </AnimatePresence>
    </div>
  );
}
