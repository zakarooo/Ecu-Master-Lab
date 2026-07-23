"use client";

import { useEffect } from "react";
import { Button } from "@/components/ui/button";
import { AlertTriangle } from "lucide-react";

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error("Erreur application:", error);
  }, [error]);

  return (
    <div className="container max-w-5xl mx-auto px-4 py-20 text-center">
      <AlertTriangle className="h-16 w-16 mx-auto mb-6 text-destructive" />
      <h1 className="text-3xl font-bold mb-4">Une erreur est survenue</h1>
      <p className="text-muted-foreground mb-8 max-w-md mx-auto">
        {error.message || "Une erreur inattendue s'est produite. Veuillez réessayer."}
      </p>
      <Button size="lg" onClick={reset}>
        Réessayer
      </Button>
    </div>
  );
}
