"use client";

import { useState, useEffect, useCallback } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import Sidebar from "@/components/layout/Sidebar";
import { api } from "@/lib/api";
import { ArrowLeft, Loader2, Search } from "lucide-react";

interface Column {
  key: string;
  label: string;
  render?: (val: any) => React.ReactNode;
}

const TYPE_CONFIG: Record<string, { title: string; apiMethod: (q?: string) => Promise<any>; columns: Column[] }> = {
  protocols: {
    title: "Protocoles",
    apiMethod: (q) => api.v2.protocols.list(q ? `search=${encodeURIComponent(q)}&skip=0&limit=50` : "skip=0&limit=50"),
    columns: [
      { key: "name", label: "Nom" },
      { key: "description", label: "Description" },
      { key: "requires_bootloader", label: "Bootloader", render: (v: boolean) => v ? "Oui" : "Non" },
      { key: "typical_tools", label: "Outils" },
    ],
  },
  memoryLayouts: {
    title: "Mémoires",
    apiMethod: (q) => api.v2.memoryLayouts.list(q ? `search=${encodeURIComponent(q)}&skip=0&limit=50` : "skip=0&limit=50"),
    columns: [
      { key: "ecu_model_id", label: "Modèle ECU" },
      { key: "total_size_bytes", label: "Taille", render: (v: number) => v ? `${(v / 1024).toFixed(0)} KB` : "-" },
      { key: "endianness", label: "Endianness" },
      { key: "notes", label: "Notes" },
    ],
  },
  maps: {
    title: "Cartes",
    apiMethod: (q) => api.v2.maps.list(q ? `search=${encodeURIComponent(q)}&skip=0&limit=50` : "skip=0&limit=50"),
    columns: [
      { key: "name", label: "Nom" },
      { key: "address_hex", label: "Adresse" },
      { key: "rows", label: "Lignes" },
      { key: "cols", label: "Colonnes" },
      { key: "data_type", label: "Type" },
    ],
  },
  mapCategories: {
    title: "Catégories de cartes",
    apiMethod: (q) => api.v2.mapCategories.list(q ? `search=${encodeURIComponent(q)}&skip=0&limit=50` : "skip=0&limit=50"),
    columns: [
      { key: "name", label: "Nom" },
      { key: "description", label: "Description" },
      { key: "sort_order", label: "Ordre" },
    ],
  },
  mapUnits: {
    title: "Unités",
    apiMethod: (q) => api.v2.mapUnits.list(q ? `search=${encodeURIComponent(q)}&skip=0&limit=50` : "skip=0&limit=50"),
    columns: [
      { key: "symbol", label: "Symbole" },
      { key: "name", label: "Nom" },
      { key: "unit_type", label: "Type" },
    ],
  },
  vehicleBrands: {
    title: "Marques véhicules",
    apiMethod: (q) => api.v2.vehicleBrands.list(q ? `search=${encodeURIComponent(q)}&skip=0&limit=50` : "skip=0&limit=50"),
    columns: [
      { key: "name", label: "Nom" },
      { key: "country", label: "Pays" },
      { key: "logo_url", label: "Logo", render: (v: string) => v ? <img src={v} alt="" className="w-6 h-6 rounded" /> : "-" },
    ],
  },
};

export default function ReferenceTypePage() {
  const params = useParams();
  const router = useRouter();
  const type = params.type as string;
  const config = TYPE_CONFIG[type];

  const [items, setItems] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");

  useEffect(() => {
    if (!localStorage.getItem("token")) { router.push("/login"); return; }
    if (!config) { router.push("/reference"); return; }
    loadData();
  }, [type]);

  const loadData = useCallback(async (q?: string) => {
    if (!config) return;
    setLoading(true);
    try {
      const res = await config.apiMethod(q);
      setItems(res.items || []);
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  }, [config]);

  useEffect(() => {
    const t = setTimeout(() => loadData(search || undefined), 300);
    return () => clearTimeout(t);
  }, [search]);

  if (!config) return null;

  return (
    <div className="flex min-h-screen bg-hero-gradient">
      <Sidebar />
      <main className="flex-1 p-8 ml-64">
        <div className="max-w-7xl mx-auto">
          <Link href="/reference" className="inline-flex items-center gap-2 text-gray-400 hover:text-white mb-6 text-sm">
            <ArrowLeft className="w-4 h-4" /> Retour
          </Link>
          <h1 className="text-3xl font-bold text-white mb-2">
            <span className="gradient-text">{config.title}</span>
          </h1>

          <div className="relative mb-6 mt-6">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
            <input type="text" className="input-field pl-10 w-full max-w-md" placeholder="Rechercher..."
              value={search} onChange={(e) => setSearch(e.target.value)} />
          </div>

          {loading ? (
            <div className="flex items-center gap-2 text-gray-400 mt-12">
              <Loader2 className="w-5 h-5 animate-spin" /> Chargement...
            </div>
          ) : items.length === 0 ? (
            <p className="text-gray-500 mt-12">Aucun élément trouvé</p>
          ) : (
            <div className="glass rounded-2xl overflow-hidden">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-white/10">
                    {config.columns.map((col) => (
                      <th key={col.key} className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase">{col.label}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {items.map((item, i) => (
                    <tr key={item.id || i} className="border-b border-white/5 hover:bg-white/5">
                      {config.columns.map((col) => (
                        <td key={col.key} className="px-4 py-3 text-white">
                          {col.render ? col.render(item[col.key]) : (item[col.key] ?? "-")}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
