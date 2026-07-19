"use client";

import { useState, useEffect, useCallback } from "react";
import { useParams, useRouter } from "next/navigation";
import Sidebar from "@/components/layout/Sidebar";
import { api } from "@/lib/api";
import { getStatusColor, getStatusLabel } from "@/lib/utils";
import {
  Upload, Brain, FileCheck, CheckCircle2, Download, Loader2,
  AlertTriangle, Clock, Zap, Shield, ChevronDown, ChevronUp, Wrench,
  Layers, BarChart3, Map, Cpu, Hash, FileSearch
} from "lucide-react";

const ALL_MODS = [
  { category: "Performance", items: ["Stage 1", "Stage 2", "Stage 3"] },
  { category: "Économie", items: ["Eco Tune"] },
  { category: "Fonctions", items: ["EGR OFF", "DPF/FAP OFF", "AdBlue OFF", "Start/Stop OFF", "Vmax", "Pop & Bang", "Hardcut", "Launch Control", "DTC OFF", "Immo OFF", "Flaps OFF", "Lambda OFF", "NOx OFF", "MAF OFF", "TVA OFF"] },
];

export default function ProjectDetailPage() {
  const params = useParams();
  const router = useRouter();
  const projectId = Number(params.id);

  const [project, setProject] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [analysis, setAnalysis] = useState<any>(null);
  const [v2Analysis, setV2Analysis] = useState<any>(null);
  const [analysisTab, setAnalysisTab] = useState<"summary" | "hypotheses" | "scores" | "maps" | "segments" | "checksums">("summary");
  const [selectedMods, setSelectedMods] = useState<string[]>([]);
  const [clientNotes, setClientNotes] = useState("");
  const [dragActive, setDragActive] = useState(false);
  const [showAnalysis, setShowAnalysis] = useState(false);

  useEffect(() => {
    if (!localStorage.getItem("token")) { router.push("/login"); return; }
    loadProject();
  }, [projectId]);

  const loadProject = async () => {
    try {
      const data = await api.projects.get(projectId);
      setProject(data);
      if (data.ai_analysis_json) setAnalysis(JSON.parse(data.ai_analysis_json));
      if (data.modifications) setSelectedMods(JSON.parse(data.modifications));

      try {
        const v2 = await api.projects.analysis(projectId);
        if (v2.analysis) setV2Analysis(v2);
      } catch {}
    } catch (err) { console.error(err); }
    finally { setLoading(false); }
  };

  const handleUpload = async (file: File) => {
    setUploading(true);
    try {
      const res = await api.projects.upload(projectId, file);
      setAnalysis(res.analysis);
      setProject((p: any) => ({ ...p, status: res.status, ai_analysis_json: JSON.stringify(res.analysis) }));
    } catch (err: any) { alert(err.message); }
    finally { setUploading(false); }
  };

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(false);
    if (e.dataTransfer.files?.[0]) handleUpload(e.dataTransfer.files[0]);
  }, []);

  const toggleMod = (mod: string) => {
    setSelectedMods((prev) => prev.includes(mod) ? prev.filter((m) => m !== mod) : [...prev, mod]);
  };

  const submitMods = async () => {
    try {
      await api.projects.setModifications(projectId, { modifications: selectedMods, client_notes: clientNotes });
      setProject((p: any) => ({ ...p, status: "processing", modifications: JSON.stringify(selectedMods) }));
    } catch (err: any) { alert(err.message); }
  };

  const processProject = async () => {
    setProcessing(true);
    try {
      await api.projects.process(projectId);
      await loadProject();
    } catch (err: any) { alert(err.message); }
    finally { setProcessing(false); }
  };

  if (loading) return (
    <div className="flex min-h-screen bg-hero-gradient items-center justify-center">
      <Loader2 className="w-8 h-8 text-blue-400 animate-spin" />
    </div>
  );

  if (!project) return (
    <div className="flex min-h-screen bg-hero-gradient items-center justify-center">
      <p className="text-gray-400">Projet non trouvé</p>
    </div>
  );

  const compatibleMods = (analysis?.compatible_modifications || []).map((m: string) => m.toLowerCase());

  return (
    <div className="flex min-h-screen bg-hero-gradient">
      <Sidebar />
      <main className="flex-1 p-8 ml-64">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="flex items-center justify-between mb-8">
            <div>
              <h1 className="text-3xl font-bold text-white">{project.name}</h1>
              <p className="text-gray-400 mt-1">
                {project.vehicle_make} {project.vehicle_model} {project.vehicle_year && `• ${project.vehicle_year}`}
              </p>
            </div>
            <span className={`inline-flex items-center px-4 py-2 rounded-full text-sm font-medium border ${getStatusColor(project.status)}`}>
              {getStatusLabel(project.status)}
            </span>
          </div>

          {/* Upload Zone */}
          {["pending", "needs_review"].includes(project.status) && !project.ecu_filename && (
            <div
              className={`glass rounded-2xl p-12 text-center border-2 border-dashed transition-all cursor-pointer ${
                dragActive ? "border-blue-500 bg-blue-500/5" : "border-white/10 hover:border-white/20"
              }`}
              onDragOver={(e) => { e.preventDefault(); setDragActive(true); }}
              onDragLeave={() => setDragActive(false)}
              onDrop={handleDrop}
              onClick={() => document.getElementById("file-input")?.click()}
            >
              <input id="file-input" type="file" className="hidden"
                accept=".bin,.ori,.hex,.frf,.mpc,.bdm,.zip"
                onChange={(e) => e.target.files?.[0] && handleUpload(e.target.files[0])} />
              {uploading ? (
                <div>
                  <Loader2 className="w-12 h-12 text-blue-400 animate-spin mx-auto mb-4" />
                  <p className="text-white font-medium">Upload et analyse en cours...</p>
                  <p className="text-gray-500 text-sm mt-2">L&apos;Agent IA analyse votre fichier</p>
                </div>
              ) : (
                <div>
                  <Upload className="w-12 h-12 text-gray-500 mx-auto mb-4" />
                  <p className="text-white font-medium mb-2">Glissez votre fichier ECU ici</p>
                  <p className="text-gray-500 text-sm">ou cliquez pour sélectionner</p>
                  <p className="text-gray-600 text-xs mt-4">BIN, ORI, HEX, FRF, MPC, BDM, ZIP — Max 50MB</p>
                </div>
              )}
            </div>
          )}

          {/* File Info */}
          {project.ecu_filename && (
            <div className="glass rounded-2xl p-6 mb-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <FileCheck className="w-5 h-5 text-green-400" />
                  <div>
                    <p className="text-white font-medium">{project.ecu_filename}</p>
                    <p className="text-xs text-gray-500">{project.ecu_file_hash?.substring(0, 16)}...</p>
                  </div>
                </div>
                {analysis && (
                  <button onClick={() => setShowAnalysis(!showAnalysis)} className="btn-secondary text-sm flex items-center gap-2">
                    <Brain className="w-4 h-4" />
                    Rapport IA
                    {showAnalysis ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                  </button>
                )}
              </div>
            </div>
          )}

          {/* AI Analysis Report — Tabs */}
          {showAnalysis && analysis && (
            <div className="glass rounded-2xl p-6 mb-6 glow-border animate-slide-up">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <Brain className="w-5 h-5 text-blue-400" />
                Rapport ECU AI ENGINE
              </h3>

              {/* Tab Navigation */}
              <div className="flex flex-wrap gap-1 mb-6 bg-white/5 rounded-xl p-1">
                {([
                  { id: "summary" as const, label: "Résumé", icon: FileSearch },
                  ...(v2Analysis?.hypotheses?.length ? [{ id: "hypotheses" as const, label: "Hypothèses", icon: Layers }] : []),
                  ...(v2Analysis?.scores?.length ? [{ id: "scores" as const, label: "Scores", icon: BarChart3 }] : []),
                  ...(v2Analysis?.maps?.length ? [{ id: "maps" as const, label: "Cartes", icon: Map }] : []),
                  ...(v2Analysis?.segments?.length ? [{ id: "segments" as const, label: "Segments", icon: Cpu }] : []),
                  ...(v2Analysis?.checksums?.length ? [{ id: "checksums" as const, label: "Checksums", icon: Hash }] : []),
                ]).map(tab => (
                  <button key={tab.id} onClick={() => setAnalysisTab(tab.id)}
                    className={`flex items-center gap-1.5 px-3 py-2 rounded-lg text-xs font-medium transition-all ${
                      analysisTab === tab.id ? "bg-blue-500/20 text-blue-400" : "text-gray-400 hover:text-white hover:bg-white/5"
                    }`}>
                    <tab.icon className="w-3.5 h-3.5" />
                    {tab.label}
                  </button>
                ))}
              </div>

              {/* Tab: Summary */}
              {analysisTab === "summary" && (
                <>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                    {[
                      { label: "ECU", value: analysis.ecu_type },
                      { label: "Hardware", value: analysis.hw_version },
                      { label: "Software", value: analysis.sw_version },
                      { label: "Checksum", value: analysis.checksum_valid ? "Valide ✓" : "Invalide ✗", color: analysis.checksum_valid ? "text-green-400" : "text-red-400" },
                    ].map((item, i) => (
                      <div key={i} className="bg-white/5 rounded-xl p-3">
                        <div className="text-xs text-gray-500 mb-1">{item.label}</div>
                        <div className={`text-sm font-medium ${item.color || "text-white"}`}>{item.value}</div>
                      </div>
                    ))}
                  </div>
                  <div className="grid grid-cols-3 gap-4 mb-6">
                    <div className="bg-white/5 rounded-xl p-4 text-center">
                      <div className="text-2xl font-bold gradient-text">{analysis.confidence}%</div>
                      <div className="text-xs text-gray-500">Confiance</div>
                    </div>
                    <div className="bg-white/5 rounded-xl p-4 text-center">
                      <div className="text-2xl font-bold text-white">{analysis.estimated_time_seconds}s</div>
                      <div className="text-xs text-gray-500">Temps estimé</div>
                    </div>
                    <div className="bg-white/5 rounded-xl p-4 text-center">
                      <div className="text-2xl font-bold text-white">{analysis.map_regions?.length || 0}</div>
                      <div className="text-xs text-gray-500">Zones carto</div>
                    </div>
                  </div>
                  {analysis.risks?.length > 0 && (
                    <div className="bg-yellow-500/5 border border-yellow-500/20 rounded-xl p-4 mb-4">
                      <div className="flex items-center gap-2 mb-2">
                        <AlertTriangle className="w-4 h-4 text-yellow-400" />
                        <span className="text-sm font-medium text-yellow-400">Risques détectés</span>
                      </div>
                      {analysis.risks.map((risk: string, i: number) => (
                        <p key={i} className="text-xs text-yellow-400/70 ml-6">{risk}</p>
                      ))}
                    </div>
                  )}
                  <div className="bg-blue-500/5 border border-blue-500/20 rounded-xl p-4">
                    <p className="text-sm text-blue-400">{analysis.recommendation}</p>
                  </div>
                </>
              )}

              {/* Tab: Hypotheses */}
              {analysisTab === "hypotheses" && v2Analysis?.hypotheses && (
                <div className="space-y-3">
                  {v2Analysis.hypotheses.map((h: any, i: number) => (
                    <div key={i} className="bg-white/5 rounded-xl p-4 border border-white/5">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-xs font-mono text-blue-400 bg-blue-500/10 px-2 py-0.5 rounded">#{h.rank}</span>
                        <span className="text-xs text-gray-500">Score: {(h.confidence_score * 100).toFixed(1)}%</span>
                      </div>
                      <p className="text-sm text-white font-medium">{h.hypothesis_type}</p>
                      <p className="text-xs text-gray-400 mt-1">{h.description}</p>
                      {h.supporting_evidence && <p className="text-xs text-gray-500 mt-2 italic">{h.supporting_evidence}</p>}
                    </div>
                  ))}
                </div>
              )}

              {/* Tab: Scores */}
              {analysisTab === "scores" && v2Analysis?.scores && (
                <div className="space-y-3">
                  {v2Analysis.scores.map((s: any, i: number) => (
                    <div key={i} className="bg-white/5 rounded-xl p-4 flex items-center justify-between border border-white/5">
                      <div>
                        <p className="text-sm text-white font-medium">{s.metric_name}</p>
                        <p className="text-xs text-gray-500">{s.description}</p>
                      </div>
                      <div className="text-right">
                        <div className={`text-lg font-bold ${s.normalized_score >= 0.7 ? "text-green-400" : s.normalized_score >= 0.4 ? "text-yellow-400" : "text-red-400"}`}>
                          {(s.normalized_score * 100).toFixed(0)}
                        </div>
                        <div className="text-[10px] text-gray-500">{s.category}</div>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* Tab: Maps */}
              {analysisTab === "maps" && v2Analysis?.maps && (
                <div className="space-y-3">
                  {v2Analysis.maps.map((m: any, i: number) => (
                    <div key={i} className="bg-white/5 rounded-xl p-4 border border-white/5">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm text-white font-medium">{m.map_name}</span>
                        <span className="text-xs text-gray-500">{m.map_type}</span>
                      </div>
                      <div className="grid grid-cols-2 gap-2 text-xs">
                        <div className="text-gray-400">Offset: <span className="text-white font-mono">{m.offset_hex}</span></div>
                        <div className="text-gray-400">Taille: <span className="text-white">{m.size_bytes} octets</span></div>
                        <div className="text-gray-400">Axes: <span className="text-white">{m.x_axis_count}×{m.y_axis_count}</span></div>
                        <div className="text-gray-400">Confiance: <span className="text-blue-400">{(m.confidence * 100).toFixed(0)}%</span></div>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* Tab: Segments */}
              {analysisTab === "segments" && v2Analysis?.segments && (
                <div className="space-y-3">
                  {v2Analysis.segments.map((s: any, i: number) => (
                    <div key={i} className="bg-white/5 rounded-xl p-4 border border-white/5">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm text-white font-medium">{s.segment_type}</span>
                        <span className="text-xs text-gray-500">{s.data_type}</span>
                      </div>
                      <div className="grid grid-cols-3 gap-2 text-xs">
                        <div className="text-gray-400">Offset: <span className="text-white font-mono">{s.offset_hex}</span></div>
                        <div className="text-gray-400">Taille: <span className="text-white">{s.size_bytes} octets</span></div>
                        <div className="text-gray-400">Contenu: <span className="text-white">{s.content_type}</span></div>
                      </div>
                      {s.description && <p className="text-xs text-gray-500 mt-2">{s.description}</p>}
                    </div>
                  ))}
                </div>
              )}

              {/* Tab: Checksums */}
              {analysisTab === "checksums" && v2Analysis?.checksums && (
                <div className="space-y-3">
                  {v2Analysis.checksums.map((c: any, i: number) => (
                    <div key={i} className="bg-white/5 rounded-xl p-4 border border-white/5">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm text-white font-medium">{c.algorithm}</span>
                        <span className={`text-xs px-2 py-0.5 rounded ${c.is_valid ? "bg-green-500/10 text-green-400" : "bg-red-500/10 text-red-400"}`}>
                          {c.is_valid ? "Valide ✓" : "Invalide ✗"}
                        </span>
                      </div>
                      <div className="grid grid-cols-2 gap-2 text-xs">
                        <div className="text-gray-400">Offset: <span className="text-white font-mono">{c.offset_hex}</span></div>
                        <div className="text-gray-400">Zone: <span className="text-white">{c.range_description}</span></div>
                      </div>
                      <div className="mt-2 text-[11px] font-mono text-gray-500 break-all">
                        Calculé: {c.calculated_value}
                      </div>
                      {c.stored_value && (
                        <div className="text-[11px] font-mono text-gray-500 break-all">
                          Stocké: {c.stored_value}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Modifications Selection */}
          {["analyzed", "needs_review"].includes(project.status) && (
            <div className="glass rounded-2xl p-6 mb-6">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <Wrench className="w-5 h-5 text-blue-400" />
                Sélection des Modifications
              </h3>

              {ALL_MODS.map((group) => (
                <div key={group.category} className="mb-6">
                  <h4 className="text-sm font-medium text-gray-400 mb-3 uppercase tracking-wider">{group.category}</h4>
                  <div className="flex flex-wrap gap-2">
                    {group.items.map((mod) => {
                      const modLower = mod.toLowerCase().replace(/ /g, "");
                      const isCompatible = compatibleMods.some((cm: string) => cm.replace(/ /g, "").includes(modLower.replace("off", "")) || modLower.includes(cm.replace(/ /g, "").replace("off", "")));
                      const isSelected = selectedMods.includes(mod);
                      return (
                        <button key={mod} onClick={() => isCompatible && toggleMod(mod)}
                          disabled={!isCompatible}
                          className={`px-4 py-2 rounded-xl text-sm font-medium border transition-all ${
                            isSelected
                              ? "bg-blue-500/20 border-blue-500/50 text-blue-400"
                              : isCompatible
                                ? "bg-white/5 border-white/10 text-gray-400 hover:border-blue-500/30 hover:text-white"
                                : "bg-white/2 border-white/5 text-gray-600 cursor-not-allowed line-through"
                          }`}>
                          {mod}
                          {!isCompatible && " ✗"}
                        </button>
                      );
                    })}
                  </div>
                </div>
              ))}

              <div className="mt-6">
                <label className="block text-sm text-gray-400 mb-2">Notes / Instructions</label>
                <textarea className="input-field min-h-[100px] resize-y" placeholder="Décrivez vos besoins spécifiques..."
                  value={clientNotes} onChange={(e) => setClientNotes(e.target.value)} />
              </div>

              <div className="mt-6 flex justify-end">
                <button onClick={submitMods} disabled={selectedMods.length === 0}
                  className="btn-primary flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed">
                  <CheckCircle2 className="w-4 h-4" />
                  Confirmer ({selectedMods.length} modif.{selectedMods.length > 1 ? "s" : ""})
                </button>
              </div>
            </div>
          )}

          {/* Processing */}
          {project.status === "processing" && (
            <div className="glass rounded-2xl p-8 text-center glow-border">
              <Zap className="w-12 h-12 text-blue-400 mx-auto mb-4 animate-pulse" />
              <h3 className="text-xl font-semibold text-white mb-2">Traitement en cours</h3>
              <p className="text-gray-400 mb-6">L&apos;Agent IA applique vos modifications...</p>
              <button onClick={processProject} disabled={processing} className="btn-primary flex items-center gap-2 mx-auto">
                {processing ? <Loader2 className="w-4 h-4 animate-spin" /> : <Zap className="w-4 h-4" />}
                {processing ? "Traitement..." : "Lancer le traitement"}
              </button>
            </div>
          )}

          {/* Needs Review */}
          {project.status === "needs_review" && (
            <div className="glass rounded-2xl p-8 text-center border border-orange-500/30">
              <AlertTriangle className="w-16 h-16 text-orange-400 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-white mb-2">Revue Expert Requise</h3>
              <p className="text-gray-400 mb-2">L&apos;Agent IA a détecté des risques sur ce fichier.</p>
              <p className="text-orange-400 text-sm mb-6">Le traitement automatique est bloqué. Un expert doit valider avant de continuer.</p>
              <div className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-orange-500/10 border border-orange-500/20 text-orange-400 text-sm">
                <Clock className="w-4 h-4" />
                En attente d&apos;un expert
              </div>
            </div>
          )}

          {/* Completed */}
          {project.status === "completed" && (
            <div className="glass rounded-2xl p-8 text-center glow-border">
              <CheckCircle2 className="w-16 h-16 text-green-400 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-white mb-2">Traitement Terminé</h3>
              <p className="text-gray-400 mb-2">Votre fichier ECU modifié est prêt</p>
              {project.result_checksum && (
                <p className="text-xs text-gray-500 mb-6">SHA-256: {project.result_checksum.substring(0, 32)}...</p>
              )}
              <div className="flex items-center justify-center gap-4">
                <button onClick={async () => {
                  const token = localStorage.getItem("token");
                  const res = await fetch(`/api/projects/${projectId}/download-original`, {
                    headers: { Authorization: `Bearer ${token}` },
                  });
                  if (!res.ok) { alert("Erreur de téléchargement de l'original"); return; }
                  const blob = await res.blob();
                  const url = URL.createObjectURL(blob);
                  const a = document.createElement("a");
                  a.href = url;
                  a.download = project.ecu_filename ? `original_${project.ecu_filename}` : "ecu_original.bin";
                  a.click();
                  URL.revokeObjectURL(url);
                }} className="btn-secondary inline-flex items-center gap-2 cursor-pointer">
                  <Download className="w-5 h-5" />
                  Télécharger l&apos;original
                </button>
                <button onClick={async () => {
                  const token = localStorage.getItem("token");
                  const res = await fetch(`/api/projects/${projectId}/download`, {
                    headers: { Authorization: `Bearer ${token}` },
                  });
                  if (!res.ok) { alert("Erreur de téléchargement"); return; }
                  const blob = await res.blob();
                  const url = URL.createObjectURL(blob);
                  const a = document.createElement("a");
                  a.href = url;
                  a.download = project.ecu_filename ? `modified_${project.ecu_filename}` : "ecu_modified.bin";
                  a.click();
                  URL.revokeObjectURL(url);
                }} className="btn-primary inline-flex items-center gap-2 cursor-pointer">
                  <Download className="w-5 h-5" />
                  Télécharger le fichier modifié
                </button>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
