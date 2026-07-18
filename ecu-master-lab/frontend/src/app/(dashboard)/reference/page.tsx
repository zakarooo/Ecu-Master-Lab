"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import Sidebar from "@/components/layout/Sidebar";
import { api } from "@/lib/api";
import {
  Database,
  Cpu,
  Radio,
  FileCode,
  Map,
  ShieldCheck,
  HardDrive,
  Tag,
  Ruler,
  Car,
} from "lucide-react";

interface RefCard {
  title: string;
  icon: any;
  href: string;
  color: string;
  borderColor: string;
  description: string;
  countKey: string;
}

const refCards: RefCard[] = [
  {
    title: "Fabricants",
    icon: Database,
    href: "/reference/manufacturers",
    color: "text-blue-400",
    borderColor: "border-blue-500/20",
    description: "Fabricants d'ECU et informations",
    countKey: "manufacturers",
  },
  {
    title: "Modèles ECU",
    icon: FileCode,
    href: "/reference/ecu-models",
    color: "text-cyan-400",
    borderColor: "border-cyan-500/20",
    description: "Modèles de calculateurs",
    countKey: "ecuModels",
  },
  {
    title: "Processeurs",
    icon: Cpu,
    href: "/reference/processors",
    color: "text-green-400",
    borderColor: "border-green-500/20",
    description: "Processeurs et architectures",
    countKey: "processors",
  },
  {
    title: "Protocoles",
    icon: Radio,
    href: "/reference",
    color: "text-purple-400",
    borderColor: "border-purple-500/20",
    description: "Protocoles de communication",
    countKey: "protocols",
  },
  {
    title: "Signatures ECU",
    icon: ShieldCheck,
    href: "/reference/signatures",
    color: "text-yellow-400",
    borderColor: "border-yellow-500/20",
    description: "Patterns de signature binaire",
    countKey: "signatures",
  },
  {
    title: "Mémoires",
    icon: HardDrive,
    href: "/reference",
    color: "text-orange-400",
    borderColor: "border-orange-500/20",
    description: "Layouts mémoire des ECU",
    countKey: "memoryLayouts",
  },
  {
    title: "Cartes",
    icon: Map,
    href: "/reference",
    color: "text-pink-400",
    borderColor: "border-pink-500/20",
    description: "Cartes de calibration détectées",
    countKey: "maps",
  },
  {
    title: "Catégories de cartes",
    icon: Tag,
    href: "/reference",
    color: "text-red-400",
    borderColor: "border-red-500/20",
    description: "Catégories et types de cartes",
    countKey: "mapCategories",
  },
  {
    title: "Unités",
    icon: Ruler,
    href: "/reference",
    color: "text-teal-400",
    borderColor: "border-teal-500/20",
    description: "Unités de mesure pour cartes",
    countKey: "mapUnits",
  },
  {
    title: "Marques véhicules",
    icon: Car,
    href: "/reference",
    color: "text-indigo-400",
    borderColor: "border-indigo-500/20",
    description: "Marques et modèles véhicules",
    countKey: "vehicleBrands",
  },
];

export default function ReferencePage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [counts, setCounts] = useState<Record<string, number>>({});

  useEffect(() => {
    if (!localStorage.getItem("token")) {
      router.push("/login");
      return;
    }
    loadCounts();
  }, []);

  const loadCounts = async () => {
    setLoading(true);
    try {
      const results = await Promise.allSettled([
        api.v2.manufacturers.list("skip=0&limit=1"),
        api.v2.ecuModels.list("skip=0&limit=1"),
        api.v2.processors.list("skip=0&limit=1"),
        api.v2.protocols.list("skip=0&limit=1"),
        api.v2.ecuSignatures.list("skip=0&limit=1"),
        api.v2.memoryLayouts.list("skip=0&limit=1"),
        api.v2.maps.list("skip=0&limit=1"),
        api.v2.mapCategories.list("skip=0&limit=1"),
        api.v2.mapUnits.list("skip=0&limit=1"),
        api.v2.vehicleBrands.list("skip=0&limit=1"),
      ]);

      const keys = [
        "manufacturers",
        "ecuModels",
        "processors",
        "protocols",
        "signatures",
        "memoryLayouts",
        "maps",
        "mapCategories",
        "mapUnits",
        "vehicleBrands",
      ];

      const newCounts: Record<string, number> = {};
      results.forEach((result, idx) => {
        if (result.status === "fulfilled" && result.value) {
          newCounts[keys[idx]] = result.value.total || 0;
        } else {
          newCounts[keys[idx]] = 0;
        }
      });
      setCounts(newCounts);
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  };

  return (
    <div className="flex min-h-screen bg-hero-gradient">
      <Sidebar />
      <main className="flex-1 p-8 ml-64">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-3xl font-bold text-white mb-2">
            <span className="gradient-text">Données Référence</span>
          </h1>
          <p className="text-white/50 mb-8">
            Base de données de référence pour l&apos;identification et l&apos;analyse ECU
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {refCards.map((card) => (
              <Link key={card.title} href={card.href}>
                <div className="glass rounded-2xl p-6 card-hover cursor-pointer group">
                  <div className="flex items-start justify-between mb-4">
                    <div
                      className={`w-12 h-12 rounded-xl flex items-center justify-center border ${card.borderColor} bg-white/5`}
                    >
                      <card.icon className={`w-6 h-6 ${card.color}`} />
                    </div>
                    <span className="text-2xl font-bold text-white">
                      {loading ? "-" : (counts[card.countKey] ?? 0)}
                    </span>
                  </div>
                  <h3 className="text-lg font-semibold text-white mb-1 group-hover:text-blue-400 transition-colors">
                    {card.title}
                  </h3>
                  <p className="text-sm text-white/50">{card.description}</p>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}
