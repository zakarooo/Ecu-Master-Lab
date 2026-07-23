import type { Metadata } from "next";
import { Inter } from "next/font/google";
import Script from "next/script";
import "./globals.css";
import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";
import { Toaster } from "sonner";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });

const BASE_URL = process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000";

const organizationJsonLd = {
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  name: "DroitSéjour",
  applicationCategory: "LegalTech",
  operatingSystem: "Web",
  description:
    "Plateforme professionnelle d'aide aux démarches de séjour, régularisation et obtention de documents administratifs en France.",
  url: BASE_URL,
  offers: {
    "@type": "Offer",
    price: "0",
    priceCurrency: "EUR",
  },
};

export const metadata: Metadata = {
  metadataBase: new URL(BASE_URL),
  title: {
    default: "DroitSéjour - Aide aux démarches de séjour en France",
    template: "%s | DroitSéjour",
  },
  description: "Plateforme professionnelle d'aide aux démarches de séjour, régularisation et obtention de documents administratifs en France. Analyse IA, courriers, et rapports.",
  keywords: ["séjour France", "titre de séjour", "préfecture", "régularisation", "démarches administratives", "immigration", "LegalTech", "droit des étrangers", "autorisation de travail"],
  authors: [{ name: "DroitSéjour" }],
  openGraph: {
    type: "website",
    locale: "fr_FR",
    siteName: "DroitSéjour",
    title: "DroitSéjour - Aide aux démarches de séjour en France",
    description: "Plateforme d'aide aux démarches de séjour avec analyse IA, courriers automatiques et rapports professionnels.",
    url: BASE_URL,
  },
  twitter: {
    card: "summary_large_image",
    title: "DroitSéjour",
    description: "Aide aux démarches de séjour en France",
  },
  robots: {
    index: true,
    follow: true,
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="fr" suppressHydrationWarning>
      <head>
        <Script
          id="organization-jsonld"
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(organizationJsonLd) }}
        />
      </head>
      <body className={`${inter.variable} font-sans antialiased min-h-screen flex flex-col`}>
        <Header />
        <main className="flex-1">{children}</main>
        <Footer />
        <Toaster />
      </body>
    </html>
  );
}
