"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Sidebar from "@/components/layout/Sidebar";
import { api } from "@/lib/api";
import { Cpu, ChevronLeft, ChevronRight } from "lucide-react";

export default function ProcessorsPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState<any[]>([]);
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(0);
  const [total, setTotal] = useState(0);
  const LIMIT = 20;

  useEffect(() => {
    if (!localStorage.getItem("token")) {
      router.push("/login");
      return;
    }
    loadData();
  }, [page, search]);

  const loadData = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        skip: String(page * LIMIT),
        limit: String(LIMIT),
      });
      if (search) params.set("search", search);
      const res = await api.v2.processors.list(params.toString());
      setData(res.items || []);
      setTotal(res.total || 0);
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
          <h1 className="text-3xl font-bold text-white mb-6">
            <span className="gradient-text">Processeurs</span>
          </h1>

          <div className="glass rounded-xl p-4 mb-6 flex gap-4">
            <input
              type="text"
              placeholder="Rechercher un processeur..."
              value={search}
              onChange={(e) => {
                setSearch(e.target.value);
                setPage(0);
              }}
              className="input-field flex-1"
            />
          </div>

          <div className="glass rounded-xl overflow-hidden">
            {loading ? (
              <div className="p-8 text-center text-white/50">Chargement...</div>
            ) : data.length === 0 ? (
              <div className="p-8 text-center text-white/50">Aucun processeur trouvé</div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left">
                  <thead>
                    <tr className="border-b border-ecu-border">
                      <th className="px-6 py-3 text-xs font-semibold text-white/50 uppercase tracking-wider">
                        Nom
                      </th>
                      <th className="px-6 py-3 text-xs font-semibold text-white/50 uppercase tracking-wider">
                        Famille
                      </th>
                      <th className="px-6 py-3 text-xs font-semibold text-white/50 uppercase tracking-wider">
                        Fabricant
                      </th>
                      <th className="px-6 py-3 text-xs font-semibold text-white/50 uppercase tracking-wider">
                        Architecture
                      </th>
                      <th className="px-6 py-3 text-xs font-semibold text-white/50 uppercase tracking-wider">
                        Word Size
                      </th>
                      <th className="px-6 py-3 text-xs font-semibold text-white/50 uppercase tracking-wider">
                        Endianness
                      </th>
                      <th className="px-6 py-3 text-xs font-semibold text-white/50 uppercase tracking-wider">
                        Clock MHz
                      </th>
                      <th className="px-6 py-3 text-xs font-semibold text-white/50 uppercase tracking-wider">
                        Flash KB
                      </th>
                      <th className="px-6 py-3 text-xs font-semibold text-white/50 uppercase tracking-wider">
                        RAM KB
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.map((item) => (
                      <tr
                        key={item.id}
                        className="border-b border-white/5 hover:bg-white/5"
                      >
                        <td className="px-6 py-4 text-sm text-white font-medium">
                          {item.name}
                        </td>
                        <td className="px-6 py-4 text-sm text-white/70">
                          {item.family || "-"}
                        </td>
                        <td className="px-6 py-4 text-sm text-white/70">
                          {item.manufacturer || "-"}
                        </td>
                        <td className="px-6 py-4 text-sm text-white/70">
                          {item.architecture || "-"}
                        </td>
                        <td className="px-6 py-4 text-sm text-white/70">
                          {item.word_size || item.wordSize || "-"}
                        </td>
                        <td className="px-6 py-4 text-sm text-white/70">
                          {item.endianness || "-"}
                        </td>
                        <td className="px-6 py-4 text-sm text-white/70">
                          {item.clock_mhz || item.clockMhz || "-"}
                        </td>
                        <td className="px-6 py-4 text-sm text-white/70">
                          {item.flash_kb || item.flashKb || "-"}
                        </td>
                        <td className="px-6 py-4 text-sm text-white/70">
                          {item.ram_kb || item.ramKb || "-"}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          <div className="flex justify-between items-center mt-4 text-white/60">
            <span>Total: {total}</span>
            <div className="flex gap-2">
              <button
                onClick={() => setPage((p) => Math.max(0, p - 1))}
                disabled={page === 0}
                className="btn-secondary px-4 py-2 text-sm flex items-center gap-1 disabled:opacity-30"
              >
                <ChevronLeft className="w-4 h-4" />
                Précédent
              </button>
              <span className="px-4 py-2">
                {page + 1} / {Math.ceil(total / LIMIT) || 1}
              </span>
              <button
                onClick={() => setPage((p) => p + 1)}
                disabled={(page + 1) * LIMIT >= total}
                className="btn-secondary px-4 py-2 text-sm flex items-center gap-1 disabled:opacity-30"
              >
                Suivant
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
