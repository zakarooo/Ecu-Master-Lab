import Link from "next/link";
import { Button } from "@/components/ui/button";
import { FileQuestion } from "lucide-react";

export default function NotFound() {
  return (
    <div className="container max-w-5xl mx-auto px-4 py-20 text-center">
      <FileQuestion className="h-16 w-16 mx-auto mb-6 text-muted-foreground" />
      <h1 className="text-3xl font-bold mb-4">Page non trouvée</h1>
      <p className="text-muted-foreground mb-8 max-w-md mx-auto">
        La page que vous recherchez n&apos;existe pas ou a été déplacée.
      </p>
      <Link href="/">
        <Button size="lg">
          Retour à l&apos;accueil
        </Button>
      </Link>
    </div>
  );
}
