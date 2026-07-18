"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Sidebar from "@/components/layout/Sidebar";
import { api } from "@/lib/api";
import {
  Upload,
  Play,
  FileCode,
  ScanLine,
  BarChart3,
  CheckCircle,
  Clock,
  AlertCircle,
} from "lucide-react";

export default function AnalysisPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [files, setFiles] = useState<any[]>([]);
  const [analyses, setAnalyses] = useState<any[]>([]);
  const [stats, setStats] = useState({ totalFiles: 0, totalAnalyses: 0, avgConfidence: 0 });

  useEffect(() => {
    if (!localStorage.getItem("token")) {
      router.push("/login");
      return;
    }
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [filesRes, analysesRes] = await Promise.all([
        api.v2.ecuFiles.list("skip=0&limit=10"),
        api.v2.analyses.list("skip=0&limit=10"),
      ]);
      setFiles(filesRes.items || []);
      setAnalyses(analysesRes.items || []);

      const totalFiles = filesRes.total || 0;
      const totalAnalyses = analysesRes.total || 0;
      const items = analysesRes.items || [];
      const avgConfidence =
        items.length > 0
          ? items.reduce((sum: number, a: any) => sum + (a.confidence || 0), 0) / items.length
          : 0;
      setStats({ totalFiles, totalAnalyses, avgConfidence: Math.round(avgConfidence * 100) });
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "completed":
        return (
          <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-green-500/10 text-green-400 border border-green-500/20">
            <CheckCircle className="w-3 h-3" />
            Terminé
          </span>
        );
      case "running":
        return (
          <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-blue-500/10 text-blue-400 border border-blue-500/20">
            <Clock className="w-3 h-3" />
            En cours
          </span>
        );
      case "failed":
        return (
          <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-red-500/10 text-red-400 border border-red-500/20">
            <AlertCircle className="w-3 h-3" />
            Échoué
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-yellow-500/10 text-yellow-400 border border-yellow-500/20">
            <Clock className="w-3 h-3" />
            {status}
          </span>
        );
    }
  };

  const runAnalysis = async (fileId: number) => {
    try {
      await api.v2.analyses.run(fileId);
      loadData();
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="flex min-h-screen bg-hero-gradient">
      <Sidebar />
      <main className="flex-1 p-8 ml-64">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-3xl font-bold text-white mb-6">
            <span className="gradient-text">Analyse ECU</span>
          </h1>

          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div className="glass rounded-xl p-6 card-hover">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-blue-500/10 rounded-xl flex items-center justify-center border border-blue-500/20">
                  <FileCode className="w-6 h-6 text-blue-400" />
                </div>
                <div>
                  <div className="text-2xl font-bold text-white">{stats.totalFiles}</div>
                  <div className="text-sm text-white/50">Fichiers ECU</div>
                </div>
              </div>
            </div>
            <div className="glass rounded-xl p-6 card-hover">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-cyan-500/10 rounded-xl flex items-center justify-center border border-cyan-500/20">
                  <ScanLine className="w-6 h-6 text-cyan-400" />
                </div>
                <div>
                  <div className="text-2xl font-bold text-white">{stats.totalAnalyses}</div>
                  <div className="text-sm text-white/50">Analyses réalisées</div>
                </div>
              </div>
            </div>
            <div className="glass rounded-xl p-6 card-hover">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-green-500/10 rounded-xl flex items-center justify-center border border-green-500/20">
                  <BarChart3 className="w-6 h-6 text-green-400" />
                </div>
                <div>
                  <div className="text-2xl font-bold text-white">{stats.avgConfidence}%</div>
                  <div className="text-sm text-white/50">Confiance moyenne</div>
                </div>
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="flex gap-4 mb-8">
            <button
              onClick={() => router.push("/analysis/upload")}
              className="btn-primary flex items-center gap-2"
            >
              <Upload className="w-5 h-5" />
              Upload nouveau fichier
            </button>
          </div>

          {/* Recent Analyses */}
          <div className="glass rounded-xl overflow-hidden">
            <div className="px-6 py-4 border-b border-white/5">
              <h2 className="text-lg font-semibold text-white">Analyses récentes</h2>
            </div>
            {loading ? (
              <div className="p-8 text-center text-white/50">Chargement...</div>
            ) : analyses.length === 0 ? (
              <div className="p-8 text-center text-white/50">
                Aucune analyse. Uploadez un fichier pour commencer.
              </div>
            ) : (
              <table className="w-full text-left">
                <thead>
                  <tr className="border-b border-ecu-border">
                    <th className="px-6 py-3 text-xs font-semibold text-white/50 uppercase tracking-wider">
                      Fichier
                    </th>
                    <th className="px-6 py-3 text-xs font-semibold text-white/50 uppercase tracking-wider">
                      Statut
                    </th>
                    <th className="px-6 py-3 text-xs font-semibold text-white/50 uppercase tracking-wider">
                      Confiance
                    </th>
                    <th className="px-6 py-3 text-xs font-semibold text-white/50 uppercase tracking-wider">
                      ECU détecté
                    </th>
                    <th className="px-6 py-3 text-xs font-semibold text-white/50 uppercase tracking-wider">
                      Date
                    </th>
                    <th className="px-6 py-3 text-xs font-semibold text-white/50 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {analyses.map((analysis) => (
                    <tr
                      key={analysis.id}
                      className="border-b border-white/5 hover:bg-white/5 cursor-pointer"
                      onClick={() => router.push(`/analysis/${analysis.id}`)}
                    >
                      <td className="px-6 py-4 text-sm text-white">
                        {analysis.filename || analysis.ecu_file?.filename || "-"}
                      </td>
                      <td className="px-6 py-4">{getStatusBadge(analysis.status)}</td>
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-2">
                          <div className="w-16 h-2 bg-white/10 rounded-full overflow-hidden">
                            <div
                              className="h-full bg-gradient-to-r from-blue-500 to-cyan-400 rounded-full"
                              style={{ width: `${(analysis.confidence || 0) * 100}%` }}
                            />
                          </div>
                          <span className="text-sm text-white/60">
                            {Math.round((analysis.confidence || 0) * 100)}%
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-4 text-sm text-white/70">
                        {analysis.detected_ecu_model || "-"}
                      </td>
                      <td className="px-6 py-4 text-sm text-white/50">
                        {analysis.created_at
                          ? new Date(analysis.created_at).toLocaleDateString("fr-FR")
                          : "-"}
                      </td>
                      <td className="px-6 py-4">
                        {analysis.status === "pending" && (
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              runAnalysis(analysis.ecu_file_id || analysis.id);
                            }}
                            className="btn-secondary px-3 py-1 text-xs flex items-center gap-1"
                          >
                            <Play className="w-3 h-3" />
                            Lancer
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>

          {/* Recent Files */}
          <div className="glass rounded-xl overflow-hidden mt-8">
            <div className="px-6 py-4 border-b border-white/5">
              <h2 className="text-lg font-semibold text-white">Fichiers récents</h2>
            </div>
            {loading ? (
              <div className="p-8 text-center text-white/50">Chargement...</div>
            ) : files.length === 0 ? (
              <div className="p-8 text-center text-white/50">Aucun fichier uploadé.</div>
            ) : (
              <table className="w-full text-left">
                <thead>
                  <tr className="border-b border-ecu-border">
                    <th className="px-6 py-3 text-xs font-semibold text-white/50 uppercase tracking-wider">
                      Nom
                    </th>
                    <th className="px-6 py-3 text-xs font-semibold text-white/50 uppercase tracking-wider">
                      Taille
                    </th>
                    <th className="px-6 py-3 text-xs font-semibold text-white/50 uppercase tracking-wider">
                      SHA256
                    </th>
                    <th className="px-6 py-3 text-xs font-semibold text-white/50 uppercase tracking-wider">
                      Date
                    </th>
                    <th className="px-6 py-3 text-xs font-semibold text-white/50 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {files.map((file) => (
                    <tr key={file.id} className="border-b border-white/5 hover:bg-white/5">
                      <td className="px-6 py-4 text-sm text-white">{file.filename}</td>
                      <td className="px-6 py-4 text-sm text-white/60">
                        {file.file_size
                          ? `${(file.file_size / 1024).toFixed(1)} KB`
                          : "-"}
                      </td>
                      <td className="px-6 py-4 text-sm text-white/40 font-mono">
                        {file.sha256 ? `${file.sha256.substring(0, 16)}...` : "-"}
                      </td>
                      <td className="px-6 py-4 text-sm text-white/50">
                        {file.created_at
                          ? new Date(file.created_at).toLocaleDateString("fr-FR")
                          : "-"}
                      </td>
                      <td className="px-6 py-4">
                        <button
                          onClick={() => runAnalysis(file.id)}
                          className="btn-secondary px-3 py-1 text-xs flex items-center gap-1"
                        >
                          <Play className="w-3 h-3" />
                          Analyser
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
