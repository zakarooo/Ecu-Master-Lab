"use client";

interface JsonLdProps {
  data: Record<string, unknown>;
}

export default function JsonLd({ data }: JsonLdProps) {
  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(data) }}
    />
  );
}

export function OrganizationJsonLd() {
  return (
    <JsonLd
      data={{
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        name: "DroitSéjour",
        applicationCategory: "LegalTech",
        operatingSystem: "Web",
        description:
          "Plateforme professionnelle d'aide aux démarches de séjour, régularisation et obtention de documents administratifs en France.",
        url: process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000",
        offers: {
          "@type": "Offer",
          price: "0",
          priceCurrency: "EUR",
        },
      }}
    />
  );
}

export function FAQJsonLd() {
  return (
    <JsonLd
      data={{
        "@context": "https://schema.org",
        "@type": "FAQPage",
        mainEntity: [
          {
            "@type": "Question",
            name: "Qu'est-ce que DroitSéjour ?",
            acceptedAnswer: {
              "@type": "Answer",
              text: "DroitSéjour est une plateforme d'aide aux démarches de séjour en France. Elle fournit une analyse IA personnalisée, génère des courriers administratifs et établit des rapports PDF professionnels.",
            },
          },
          {
            "@type": "Question",
            name: "DroitSéjour remplace-t-il un avocat ?",
            acceptedAnswer: {
              "@type": "Answer",
              text: "Non. DroitSéjour est un outil d'aide informative. Les analyses et courriers générés ne constituent pas un avis juridique et ne remplacent pas les conseils d'un avocat spécialisé en droit des étrangers.",
            },
          },
          {
            "@type": "Question",
            name: "Mes données sont-elles sécurisées ?",
            acceptedAnswer: {
              "@type": "Answer",
              text: "Oui. Toutes les données sont stockées localement sur nos serveurs. Aucune donnée n'est transmise à des tiers. La confidentialité est notre priorité.",
            },
          },
        ],
      }}
    />
  );
}
