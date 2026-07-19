"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Sidebar from "@/components/layout/Sidebar";
import { api } from "@/lib/api";
import {
  ShieldCheck, CheckCircle2, XCircle, Clock, AlertTriangle,
  Loader2, Brain, ChevronDown, ChevronUp, FileCode,
} from "lucide-react";

export default function ExpertPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [projects, setProjects] = useState<any[]>([]);
  const [expandedId, setExpandedId] = useState<number | null>(null);
  const [rejectReason, setRejectReason] = useState("");
  const [actingId, setActingId] = useState<number | null>(null);

  useEffect(() => {
    if (!localStorage.getItem("token")) { router.push("/login"); return; }
    loadPending();
  }, []);

  const loadPending = async () => {
    try {
      const data = await api.expert.pendingReview();
      setProjects(data);
    } catch (err: any) {
      if (err.message?.includes("403")) {
        alert("Accès réservé aux experts");
        router.push("/dashboard");
      }
    } finally { setLoading(false); }
  };

  const handleApprove = async (id: number) => {
    setActingId(id);
    try {
      await api.expert.approve(id);
      setProjects((prev) => prev.filter((p) => p.id !== id));
    } catch (err: any) { alert(err.message); }
    finally { setActingId(null); }
  };

  const handleReject = async (id: number) => {
    if (!rejectReason.trim()) { alert("Veuillez saisir un motif"); return; }
    setActingId(id);
    try {
      await api.expert.reject(id, { reason: rejectReason });
      setProjects((prev) => prev.filter((p) => p.id !== id));
      setRejectReason("");
      setExpandedId(null);
    } catch (err: any) { alert(err.message); }
    finally { setActingId(null); }
  };

  if (loading) return (
    <div className="flex min-h-screen bg-hero-gradient items-center justify-center">
      <Loader2 className="w-8 h-8 text-blue-400 animate-spin" />
    </div>
  );

  return (
    <div className="flex min-h-screen bg-hero-gradient">
      <Sidebar />
      <main className="flex-1 p-8 ml-64">
        <div className="max-w-5xl mx-auto">
          <div className="flex items-center gap-3 mb-8">
            <ShieldCheck className="w-8 h-8 text-orange-400" />
            <div>
              <h1 className="text-3xl font-bold text-white">Revues Expert</h1>
              <p className="text-gray-400 mt-1">Projets nécessitant une validation avant traitement</p>
            </div>
          </div>

          {projects.length === 0 ? (
            <div className="glass rounded-2xl p-12 text-center">
              <CheckCircle2 className="w-12 h-12 text-green-400 mx-auto mb-4" />
              <p className="text-gray-400 text-lg">Aucun projet en attente de revue</p>
            </div>
          ) : (
            <div className="space-y-4">
              {projects.map((project) => {
                let analysis: any = {};
                try { analysis = JSON.parse(project.ai_analysis_json || "{}"); } catch {}
                const isExpanded = expandedId === project.id;

                return (
                  <div key={project.id} className="glass rounded-2xl overflow-hidden">
                    <div
                      className="flex items-center justify-between px-6 py-4 cursor-pointer hover:bg-white/5 transition-colors"
                      onClick={() => setExpandedId(isExpanded ? null : project.id)}
                    >
                      <div className="flex items-center gap-4">
                        <div className="w-10 h-10 bg-orange-500/10 rounded-xl flex items-center justify-center">
                          <AlertTriangle className="w-5 h-5 text-orange-400" />
                        </div>
                        <div>
                          <h3 className="font-medium text-white">{project.name}</h3>
                          <p className="text-sm text-gray-500">
                            {project.vehicle_make} {project.vehicle_model} {project.vehicle_year && `• ${project.vehicle_year}`}
                            {project.ecu_filename && ` — ${project.ecu_filename}`}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        {project.ai_confidence != null && (
                          <span className="text-sm text-blue-400">
                            Confiance: {Math.round(project.ai_confidence * 100)}%
                          </span>
                        )}
                        {isExpanded ? <ChevronUp className="w-4 h-4 text-gray-500" /> : <ChevronDown className="w-4 h-4 text-gray-500" />}
                      </div>
                    </div>

                    {isExpanded && (
                      <div className="px-6 pb-6 border-t border-white/5 pt-4 animate-fade-in">
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
                          <div className="bg-white/5 rounded-xl p-3">
                            <div className="text-xs text-gray-500 mb-1">ECU</div>
                            <div className="text-sm font-medium text-white">{analysis.ecu_type || project.ai_detected_ecu || "-"}</div>
                          </div>
                          <div className="bg-white/5 rounded-xl p-3">
                            <div className="text-xs text-gray-500 mb-1">Hardware</div>
                            <div className="text-sm font-medium text-white">{analysis.hw_version || "-"}</div>
                          </div>
                          <div className="bg-white/5 rounded-xl p-3">
                            <div className="text-xs text-gray-500 mb-1">Software</div>
                            <div className="text-sm font-medium text-white">{analysis.sw_version || "-"}</div>
                          </div>
                          <div className="bg-white/5 rounded-xl p-3">
                            <div className="text-xs text-gray-500 mb-1">Checksum</div>
                            <div className={`text-sm font-medium ${analysis.checksum_valid ? "text-green-400" : "text-red-400"}`}>
                              {analysis.checksum_valid ? "Valide" : "Invalide"}
                            </div>
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

                        {analysis.recommendation && (
                          <div className="bg-blue-500/5 border border-blue-500/20 rounded-xl p-4 mb-4">
                            <p className="text-sm text-blue-400">{analysis.recommendation}</p>
                          </div>
                        )}

                        <div className="flex items-center gap-3 mt-4">
                          <button
                            onClick={() => handleApprove(project.id)}
                            disabled={actingId === project.id}
                            className="btn-primary flex items-center gap-2"
                          >
                            {actingId === project.id ? <Loader2 className="w-4 h-4 animate-spin" /> : <CheckCircle2 className="w-4 h-4" />}
                            Approuver
                          </button>

                          <div className="flex items-center gap-2 flex-1">
                            <input
                              type="text"
                              className="input-field flex-1"
                              placeholder="Motif du rejet..."
                              value={rejectReason}
                              onChange={(e) => setRejectReason(e.target.value)}
                            />
                            <button
                              onClick={() => handleReject(project.id)}
                              disabled={actingId === project.id || !rejectReason.trim()}
                              className="btn-secondary flex items-center gap-2 text-red-400 border-red-500/30 hover:bg-red-500/10"
                            >
                              {actingId === project.id ? <Loader2 className="w-4 h-4 animate-spin" /> : <XCircle className="w-4 h-4" />}
                              Rejeter
                            </button>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
