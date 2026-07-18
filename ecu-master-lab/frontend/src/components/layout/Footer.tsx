import { Cpu } from "lucide-react";

export default function Footer() {
  return (
    <footer className="border-t border-white/5 bg-black/30">
      <div className="max-w-7xl mx-auto px-4 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div>
            <div className="flex items-center gap-2 mb-4">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-cyan-400 rounded-lg flex items-center justify-center">
                <Cpu className="w-5 h-5 text-white" />
              </div>
              <span className="font-bold gradient-text">ECU Master Lab</span>
            </div>
            <p className="text-gray-500 text-sm">
              Plateforme SaaS professionnelle de calibration ECU propulsée par l&apos;intelligence artificielle.
            </p>
          </div>
          <div>
            <h3 className="font-semibold text-white mb-3 text-sm">Plateforme</h3>
            <ul className="space-y-2 text-sm text-gray-500">
              <li><a href="/#features" className="hover:text-blue-400 transition-colors">Fonctionnalités</a></li>
              <li><a href="/#security" className="hover:text-blue-400 transition-colors">Sécurité</a></li>
              <li><a href="/#faq" className="hover:text-blue-400 transition-colors">FAQ</a></li>
            </ul>
          </div>
          <div>
            <h3 className="font-semibold text-white mb-3 text-sm">Support</h3>
            <ul className="space-y-2 text-sm text-gray-500">
              <li><span className="hover:text-blue-400 transition-colors cursor-pointer">Documentation</span></li>
              <li><span className="hover:text-blue-400 transition-colors cursor-pointer">Contact</span></li>
              <li><span className="hover:text-blue-400 transition-colors cursor-pointer">Status</span></li>
            </ul>
          </div>
          <div>
            <h3 className="font-semibold text-white mb-3 text-sm">Légal</h3>
            <ul className="space-y-2 text-sm text-gray-500">
              <li><span className="hover:text-blue-400 transition-colors cursor-pointer">CGU</span></li>
              <li><span className="hover:text-blue-400 transition-colors cursor-pointer">Confidentialité</span></li>
              <li><span className="hover:text-blue-400 transition-colors cursor-pointer">Mentions légales</span></li>
            </ul>
          </div>
        </div>
        <div className="border-t border-white/5 mt-8 pt-8 text-center text-gray-600 text-xs">
          &copy; 2026 ECU Master Lab. Tous droits réservés.
        </div>
      </div>
    </footer>
  );
}
