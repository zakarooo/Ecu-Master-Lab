"use client";

import { useState, useEffect } from "react";
import { useRouter, useParams } from "next/navigation";
import Sidebar from "@/components/layout/Sidebar";
import { api } from "@/lib/api";
import {
  ArrowLeft,
  FileCode,
  CheckCircle,
  AlertCircle,
  Clock,
  Cpu,
  Radio,
  Zap,
  Layers,
  Map,
  ShieldCheck,
} from "lucide-react";

type Tab = "overview" | "hypotheses" | "scores" | "maps" | "segments" | "checksums";

const tabs: { key: Tab; label: string; icon: any }[] = [
  { key: "overview", label: "Overview", icon: Layers },
  { key: "hypotheses", label: "Hypothèses", icon: AlertCircle },
  { key: "scores", label: "Scores", icon: Zap },
  { key: "maps", label: "Cartes", icon: Map },
  { key: "segments", label: "Segments", icon: FileCode },
  { key: "checksums", label: "Checksums", icon: ShieldCheck },
];

export default function AnalysisDetailPage() {
  const router = useRouter();
  const params = useParams();
  const id = Number(params.id);
  const [loading, setLoading] = useState(true);
  const [analysis, setAnalysis] = useState<any>(null);
  const [activeTab, setActiveTab] = useState<Tab>("overview");

  useEffect(() => {
    if (!localStorage.getItem("token")) {
      router.push("/login");
      return;
    }
    if (id) loadAnalysis();
  }, [id]);

  const loadAnalysis = async () => {
    setLoading(true);
    try {
      const res = await api.v2.analyses.get(id);
      setAnalysis(res);
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "completed":
        return (
          <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium bg-green-500/10 text-green-400 border border-green-500/20">
            <CheckCircle className="w-3 h-3" />
            Terminé
          </span>
        );
      case "running":
        return (
          <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium bg-blue-500/10 text-blue-400 border border-blue-500/20">
            <Clock className="w-3 h-3" />
            En cours
          </span>
        );
      case "failed":
        return (
          <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium bg-red-500/10 text-red-400 border border-red-500/20">
            <AlertCircle className="w-3 h-3" />
            Échoué
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium bg-yellow-500/10 text-yellow-400 border border-yellow-500/20">
            <Clock className="w-3 h-3" />
            {status}
          </span>
        );
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return "from-green-500 to-emerald-400";
    if (confidence >= 0.5) return "from-blue-500 to-cyan-400";
    if (confidence >= 0.3) return "from-yellow-500 to-orange-400";
    return "from-red-500 to-pink-400";
  };

  if (loading) {
    return (
      <div className="flex min-h-screen bg-hero-gradient">
        <Sidebar />
        <main className="flex-1 p-8 ml-64">
          <div className="max-w-7xl mx-auto">
            <div className="text-center text-white/50 py-20">Chargement de l&apos;analyse...</div>
          </div>
        </main>
      </div>
    );
  }

  if (!analysis) {
    return (
      <div className="flex min-h-screen bg-hero-gradient">
        <Sidebar />
        <main className="flex-1 p-8 ml-64">
          <div className="max-w-7xl mx-auto">
            <div className="text-center text-white/50 py-20">Analyse introuvable.</div>
          </div>
        </main>
      </div>
    );
  }

  const confidence = analysis.confidence || 0;
  const hypotheses = analysis.hypotheses || [];
  const scores = analysis.scores || [];
  const maps = analysis.maps || analysis.detected_maps || [];
  const segments = analysis.segments || [];
  const checksums = analysis.checksums || [];

  return (
    <div className="flex min-h-screen bg-hero-gradient">
      <Sidebar />
      <main className="flex-1 p-8 ml-64">
        <div className="max-w-7xl mx-auto">
          {/* Back button */}
          <button
            onClick={() => router.push("/analysis")}
            className="flex items-center gap-2 text-white/50 hover:text-white mb-6 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            Retour aux analyses
          </button>

          {/* Header */}
          <div className="glass rounded-2xl p-6 mb-8">
            <div className="flex items-start justify-between">
              <div className="space-y-3">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 bg-blue-500/10 rounded-xl flex items-center justify-center border border-blue-500/20">
                    <FileCode className="w-6 h-6 text-blue-400" />
                  </div>
                  <div>
                    <h1 className="text-2xl font-bold text-white">
                      {analysis.filename || analysis.ecu_file?.filename || `Analyse #${analysis.id}`}
                    </h1>
                    <p className="text-sm text-white/50">
                      {analysis.created_at
                        ? new Date(analysis.created_at).toLocaleString("fr-FR")
                        : ""}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  {getStatusBadge(analysis.status)}
                  {analysis.detected_ecu_model && (
                    <span className="text-sm text-white/60">
                      ECU: <span className="text-white">{analysis.detected_ecu_model}</span>
                    </span>
                  )}
                </div>
              </div>

              {/* Confidence Gauge */}
              <div className="text-center">
                <div className="relative w-24 h-24">
                  <svg className="w-24 h-24 -rotate-90" viewBox="0 0 100 100">
                    <circle
                      cx="50"
                      cy="50"
                      r="42"
                      fill="none"
                      stroke="rgba(255,255,255,0.05)"
                      strokeWidth="8"
                    />
                    <circle
                      cx="50"
                      cy="50"
                      r="42"
                      fill="none"
                      stroke="url(#confGradient)"
                      strokeWidth="8"
                      strokeDasharray={`${confidence * 264} 264`}
                      strokeLinecap="round"
                    />
                    <defs>
                      <linearGradient id="confGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                        <stop offset="0%" stopColor="#3B82F6" />
                        <stop offset="100%" stopColor="#22D3EE" />
                      </linearGradient>
                    </defs>
                  </svg>
                  <div className="absolute inset-0 flex items-center justify-center">
                    <span className="text-xl font-bold text-white">
                      {Math.round(confidence * 100)}%
                    </span>
                  </div>
                </div>
                <p className="text-xs text-white/50 mt-2">Confiance</p>
              </div>
            </div>
          </div>

          {/* Tabs */}
          <div className="flex gap-1 mb-6 p-1 glass rounded-xl overflow-x-auto">
            {tabs.map((tab) => (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key)}
                className={`flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium transition-all whitespace-nowrap ${
                  activeTab === tab.key
                    ? "bg-blue-500/15 text-blue-400 border border-blue-500/20"
                    : "text-white/50 hover:text-white hover:bg-white/5"
                }`}
              >
                <tab.icon className="w-4 h-4" />
                {tab.label}
              </button>
            ))}
          </div>

          {/* Tab Content */}
          <div className="glass rounded-2xl p-6">
            {activeTab === "overview" && (
              <div className="space-y-6">
                <h2 className="text-lg font-semibold text-white mb-4">Informations détectées</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  <InfoCard
                    icon={<Cpu className="w-5 h-5 text-blue-400" />}
                    label="Fabricant"
                    value={analysis.detected_manufacturer || "-"}
                  />
                  <InfoCard
                    icon={<FileCode className="w-5 h-5 text-cyan-400" />}
                    label="Modèle ECU"
                    value={analysis.detected_ecu_model || "-"}
                  />
                  <InfoCard
                    icon={<Cpu className="w-5 h-5 text-green-400" />}
                    label="Processeur"
                    value={analysis.detected_processor || "-"}
                  />
                  <InfoCard
                    icon={<Radio className="w-5 h-5 text-purple-400" />}
                    label="Protocole"
                    value={analysis.detected_protocol || "-"}
                  />
                  <InfoCard
                    icon={<Layers className="w-5 h-5 text-orange-400" />}
                    label="Version HW"
                    value={analysis.hardware_version || "-"}
                  />
                  <InfoCard
                    icon={<Layers className="w-5 h-5 text-yellow-400" />}
                    label="Version SW"
                    value={analysis.software_version || "-"}
                  />
                  <InfoCard
                    icon={<Zap className="w-5 h-5 text-red-400" />}
                    label="Marque véhicule"
                    value={analysis.vehicle_brand || "-"}
                  />
                  <InfoCard
                    icon={<Zap className="w-5 h-5 text-pink-400" />}
                    label="Moteur"
                    value={analysis.engine_type || "-"}
                  />
                </div>
              </div>
            )}

            {activeTab === "hypotheses" && (
              <div className="space-y-4">
                <h2 className="text-lg font-semibold text-white mb-4">Hypothèses de identification</h2>
                {hypotheses.length === 0 ? (
                  <p className="text-white/50 text-center py-8">Aucune hypothèse disponible.</p>
                ) : (
                  <div className="space-y-3">
                    {hypotheses.map((hyp: any, idx: number) => (
                      <div
                        key={idx}
                        className="bg-white/5 rounded-xl p-4 border border-white/5"
                      >
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center gap-3">
                            <span className="w-6 h-6 bg-blue-500/20 rounded-full flex items-center justify-center text-xs font-bold text-blue-400">
                              {idx + 1}
                            </span>
                            <span className="text-white font-medium">
                              {hyp.ecu_model || hyp.name || `Hypothèse ${idx + 1}`}
                            </span>
                          </div>
                          <span className="text-sm text-blue-400 font-semibold">
                            {Math.round((hyp.probability || hyp.confidence || 0) * 100)}%
                          </span>
                        </div>
                        <div className="w-full h-2 bg-white/5 rounded-full overflow-hidden mb-2">
                          <div
                            className="h-full bg-gradient-to-r from-blue-500 to-cyan-400 rounded-full"
                            style={{
                              width: `${(hyp.probability || hyp.confidence || 0) * 100}%`,
                            }}
                          />
                        </div>
                        {hyp.evidence && hyp.evidence.length > 0 && (
                          <ul className="mt-2 space-y-1">
                            {hyp.evidence.map((ev: string, i: number) => (
                              <li key={i} className="text-xs text-white/40 flex items-start gap-2">
                                <span className="text-blue-400 mt-0.5">•</span>
                                {ev}
                              </li>
                            ))}
                          </ul>
                        )}
                        {hyp.manufacturer && (
                          <p className="text-xs text-white/40 mt-2">
                            Fabricant: {hyp.manufacturer}
                          </p>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {activeTab === "scores" && (
              <div className="space-y-4">
                <h2 className="text-lg font-semibold text-white mb-4">Scores d&apos;analyse</h2>
                {scores.length === 0 ? (
                  <p className="text-white/50 text-center py-8">Aucun score disponible.</p>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="w-full text-left">
                      <thead>
                        <tr className="border-b border-ecu-border">
                          <th className="px-4 py-3 text-xs font-semibold text-white/50 uppercase tracking-wider">
                            Facteur
                          </th>
                          <th className="px-4 py-3 text-xs font-semibold text-white/50 uppercase tracking-wider">
                            Score brut
                          </th>
                          <th className="px-4 py-3 text-xs font-semibold text-white/50 uppercase tracking-wider">
                            Poids
                          </th>
                          <th className="px-4 py-3 text-xs font-semibold text-white/50 uppercase tracking-wider">
                            Score pondéré
                          </th>
                          <th className="px-4 py-3 text-xs font-semibold text-white/50 uppercase tracking-wider">
                            Explication
                          </th>
                        </tr>
                      </thead>
                      <tbody>
                        {scores.map((score: any, idx: number) => (
                          <tr key={idx} className="border-b border-white/5 hover:bg-white/5">
                            <td className="px-4 py-3 text-sm text-white font-medium">
                              {score.factor_name || score.name || "-"}
                            </td>
                            <td className="px-4 py-3 text-sm text-white/70">
                              {(score.raw_score || score.score || 0).toFixed(3)}
                            </td>
                            <td className="px-4 py-3 text-sm text-white/70">
                              {(score.weight || 0).toFixed(3)}
                            </td>
                            <td className="px-4 py-3 text-sm text-blue-400 font-medium">
                              {(score.weighted_score || 0).toFixed(3)}
                            </td>
                            <td className="px-4 py-3 text-sm text-white/50 max-w-xs">
                              {score.explanation || "-"}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            )}

            {activeTab === "maps" && (
              <div className="space-y-4">
                <h2 className="text-lg font-semibold text-white mb-4">Cartes détectées</h2>
                {maps.length === 0 ? (
                  <p className="text-white/50 text-center py-8">Aucune carte détectée.</p>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {maps.map((m: any, idx: number) => (
                      <div
                        key={idx}
                        className="bg-white/5 rounded-xl p-4 border border-white/5 card-hover"
                      >
                        <div className="flex items-center gap-3 mb-3">
                          <div className="w-10 h-10 bg-purple-500/10 rounded-lg flex items-center justify-center border border-purple-500/20">
                            <Map className="w-5 h-5 text-purple-400" />
                          </div>
                          <div>
                            <p className="text-sm text-white font-medium">
                              {m.name || `Carte ${idx + 1}`}
                            </p>
                            <p className="text-xs text-white/40">
                              Offset: 0x{(m.offset || 0).toString(16).toUpperCase().padStart(8, "0")}
                            </p>
                          </div>
                        </div>
                        <div className="space-y-2 text-xs">
                          <div className="flex justify-between">
                            <span className="text-white/50">Taille</span>
                            <span className="text-white/70">
                              {m.size || 0} bytes
                              {m.rows && m.columns
                                ? ` (${m.rows}×${m.columns})`
                                : ""}
                            </span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-white/50">Dimensions</span>
                            <span className="text-white/70">
                              {m.rows || "?"} × {m.columns || "?"}
                            </span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-white/50">Confiance</span>
                            <span className="text-blue-400">
                              {Math.round((m.confidence || 0) * 100)}%
                            </span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {activeTab === "segments" && (
              <div className="space-y-4">
                <h2 className="text-lg font-semibold text-white mb-4">Segments mémoire</h2>
                {segments.length === 0 ? (
                  <p className="text-white/50 text-center py-8">Aucun segment disponible.</p>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="w-full text-left">
                      <thead>
                        <tr className="border-b border-ecu-border">
                          <th className="px-4 py-3 text-xs font-semibold text-white/50 uppercase tracking-wider">
                            Type
                          </th>
                          <th className="px-4 py-3 text-xs font-semibold text-white/50 uppercase tracking-wider">
                            Début
                          </th>
                          <th className="px-4 py-3 text-xs font-semibold text-white/50 uppercase tracking-wider">
                            Fin
                          </th>
                          <th className="px-4 py-3 text-xs font-semibold text-white/50 uppercase tracking-wider">
                            Taille
                          </th>
                          <th className="px-4 py-3 text-xs font-semibold text-white/50 uppercase tracking-wider">
                            Entropie
                          </th>
                          <th className="px-4 py-3 text-xs font-semibold text-white/50 uppercase tracking-wider">
                            Validité
                          </th>
                        </tr>
                      </thead>
                      <tbody>
                        {segments.map((seg: any, idx: number) => (
                          <tr key={idx} className="border-b border-white/5 hover:bg-white/5">
                            <td className="px-4 py-3 text-sm text-white font-medium">
                              {seg.type || seg.segment_type || "-"}
                            </td>
                            <td className="px-4 py-3 text-sm text-white/70 font-mono">
                              0x{(seg.start_offset || seg.start || 0).toString(16).toUpperCase().padStart(8, "0")}
                            </td>
                            <td className="px-4 py-3 text-sm text-white/70 font-mono">
                              0x{(seg.end_offset || seg.end || 0).toString(16).toUpperCase().padStart(8, "0")}
                            </td>
                            <td className="px-4 py-3 text-sm text-white/70">
                              {seg.size || 0} bytes
                            </td>
                            <td className="px-4 py-3 text-sm text-white/70">
                              {(seg.entropy || 0).toFixed(4)}
                            </td>
                            <td className="px-4 py-3">
                              {seg.is_valid !== undefined || seg.valid !== undefined ? (
                                seg.is_valid || seg.valid ? (
                                  <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-green-500/10 text-green-400 border border-green-500/20">
                                    <CheckCircle className="w-3 h-3" />
                                    Valide
                                  </span>
                                ) : (
                                  <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-red-500/10 text-red-400 border border-red-500/20">
                                    <AlertCircle className="w-3 h-3" />
                                    Invalide
                                  </span>
                                )
                              ) : (
                                <span className="text-white/30">-</span>
                              )}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            )}

            {activeTab === "checksums" && (
              <div className="space-y-4">
                <h2 className="text-lg font-semibold text-white mb-4">Checksums</h2>
                {checksums.length === 0 ? (
                  <p className="text-white/50 text-center py-8">Aucun checksum disponible.</p>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="w-full text-left">
                      <thead>
                        <tr className="border-b border-ecu-border">
                          <th className="px-4 py-3 text-xs font-semibold text-white/50 uppercase tracking-wider">
                            Algorithme
                          </th>
                          <th className="px-4 py-3 text-xs font-semibold text-white/50 uppercase tracking-wider">
                            Offset
                          </th>
                          <th className="px-4 py-3 text-xs font-semibold text-white/50 uppercase tracking-wider">
                            Valeur stockée
                          </th>
                          <th className="px-4 py-3 text-xs font-semibold text-white/50 uppercase tracking-wider">
                            Valeur calculée
                          </th>
                          <th className="px-4 py-3 text-xs font-semibold text-white/50 uppercase tracking-wider">
                            Statut
                          </th>
                        </tr>
                      </thead>
                      <tbody>
                        {checksums.map((cs: any, idx: number) => (
                          <tr key={idx} className="border-b border-white/5 hover:bg-white/5">
                            <td className="px-4 py-3 text-sm text-white font-medium">
                              {cs.algorithm || cs.type || "-"}
                            </td>
                            <td className="px-4 py-3 text-sm text-white/70 font-mono">
                              0x{(cs.offset || 0).toString(16).toUpperCase().padStart(8, "0")}
                            </td>
                            <td className="px-4 py-3 text-sm text-white/70 font-mono">
                              {cs.stored_value !== undefined
                                ? `0x${cs.stored_value.toString(16).toUpperCase()}`
                                : cs.stored || "-"}
                            </td>
                            <td className="px-4 py-3 text-sm text-white/70 font-mono">
                              {cs.computed_value !== undefined
                                ? `0x${cs.computed_value.toString(16).toUpperCase()}`
                                : cs.computed || "-"}
                            </td>
                            <td className="px-4 py-3">
                              {cs.is_valid !== undefined || cs.valid !== undefined ? (
                                cs.is_valid || cs.valid ? (
                                  <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-green-500/10 text-green-400 border border-green-500/20">
                                    <CheckCircle className="w-3 h-3" />
                                    Valide
                                  </span>
                                ) : (
                                  <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-red-500/10 text-red-400 border border-red-500/20">
                                    <AlertCircle className="w-3 h-3" />
                                    Invalide
                                  </span>
                                )
                              ) : (
                                <span className="text-white/30">-</span>
                              )}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

function InfoCard({ icon, label, value }: { icon: React.ReactNode; label: string; value: string }) {
  return (
    <div className="bg-white/5 rounded-xl p-4 border border-white/5">
      <div className="flex items-center gap-3">
        {icon}
        <div>
          <p className="text-xs text-white/50">{label}</p>
          <p className="text-sm text-white font-medium">{value}</p>
        </div>
      </div>
    </div>
  );
}
