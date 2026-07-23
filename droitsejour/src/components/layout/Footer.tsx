import { Scale } from "lucide-react";
import { Separator } from "@/components/ui/separator";

export function Footer() {
  return (
    <footer className="border-t bg-muted/30">
      <div className="container px-4 md:px-8 py-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div>
            <div className="flex items-center gap-2 font-bold text-lg mb-2">
              <Scale className="h-5 w-5 text-primary" />
              <span className="text-primary">DroitSéjour</span>
            </div>
            <p className="text-sm text-muted-foreground">
              Plateforme d&apos;aide aux démarches de séjour en France.
              Une assistance informative qui ne remplace pas un conseil juridique professionnel.
            </p>
          </div>
          <div>
            <h3 className="font-semibold mb-2">Ressources</h3>
            <ul className="text-sm text-muted-foreground space-y-1">
              <li><a href="https://www.service-public.fr" target="_blank" rel="noopener noreferrer" className="hover:text-primary transition-colors">Service-Public.fr</a></li>
              <li><a href="https://www.prefectures-regions.gouv.fr" target="_blank" rel="noopener noreferrer" className="hover:text-primary transition-colors">Préfectures de France</a></li>
              <li><a href="https://www.ofii.fr" target="_blank" rel="noopener noreferrer" className="hover:text-primary transition-colors">OFII</a></li>
              <li><a href="https://www.cnda.fr" target="_blank" rel="noopener noreferrer" className="hover:text-primary transition-colors">CNDA</a></li>
            </ul>
          </div>
          <div>
            <h3 className="font-semibold mb-2">Avertissement</h3>
            <p className="text-sm text-muted-foreground">
              Cette application est un outil d&apos;aide informative. Les résultats générés ne constituent pas
              un avis juridique. Consultez toujours un professionnel qualifié.
            </p>
          </div>
        </div>
        <Separator className="my-6" />
        <p className="text-center text-xs text-muted-foreground">
          © {new Date().getFullYear()} DroitSéjour. Tous droits réservés.
          Données stockées localement. Aucune donnée n&apos;est transmise à des tiers.
        </p>
      </div>
    </footer>
  );
}
