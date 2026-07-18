"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Sidebar from "@/components/layout/Sidebar";
import { api } from "@/lib/api";
import { Database, ChevronLeft, ChevronRight } from "lucide-react";

export default function ManufacturersPage() {
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
      const res = await api.v2.manufacturers.list(params.toString());
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
            <span className="gradient-text">Fabricants</span>
          </h1>

          <div className="glass rounded-xl p-4 mb-6 flex gap-4">
            <input
              type="text"
              placeholder="Rechercher un fabricant..."
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
              <div className="p-8 text-center text-white/50">Aucun fabricant trouvé</div>
            ) : (
              <table className="w-full text-left">
                <thead>
                  <tr className="border-b border-ecu-border">
                    <th className="px-6 py-3 text-xs font-semibold text-white/50 uppercase tracking-wider">
                      Nom
                    </th>
                    <th className="px-6 py-3 text-xs font-semibold text-white/50 uppercase tracking-wider">
                      Pays
                    </th>
                    <th className="px-6 py-3 text-xs font-semibold text-white/50 uppercase tracking-wider">
                      Site web
                    </th>
                    <th className="px-6 py-3 text-xs font-semibold text-white/50 uppercase tracking-wider">
                      Description
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
                        {item.country || "-"}
                      </td>
                      <td className="px-6 py-4 text-sm text-blue-400">
                        {item.website ? (
                          <a
                            href={item.website}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="hover:underline"
                          >
                            {item.website}
                          </a>
                        ) : (
                          "-"
                        )}
                      </td>
                      <td className="px-6 py-4 text-sm text-white/50 max-w-xs truncate">
                        {item.description || "-"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
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
