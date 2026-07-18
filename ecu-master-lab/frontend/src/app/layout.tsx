import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ECU Master Lab - Plateforme de Calibration ECU",
  description: "Plateforme SaaS professionnelle de modification ECU avec Agent IA",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="fr">
      <body className="antialiased">{children}</body>
    </html>
  );
}
