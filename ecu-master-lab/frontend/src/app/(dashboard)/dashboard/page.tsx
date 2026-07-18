"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import Sidebar from "@/components/layout/Sidebar";
import { api } from "@/lib/api";
import { getStatusColor, getStatusLabel } from "@/lib/utils";
import { Plus, FolderOpen, Clock, CheckCircle2, AlertCircle, Loader2, Brain, TrendingUp } from "lucide-react";

export default function DashboardPage() {
  const router = useRouter();
  const [projects, setProjects] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({ total: 0, completed: 0, analyzing: 0, pending: 0 });

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) { router.push("/login"); return; }
    loadProjects();
  }, []);

  const loadProjects = async () => {
    try {
      const data = await api.projects.list();
      setProjects(data);
      setStats({
        total: data.length,
        completed: data.filter((p: any) => p.status === "completed").length,
        analyzing: data.filter((p: any) => ["analyzing", "processing"].includes(p.status)).length,
        pending: data.filter((p: any) => ["pending", "needs_review"].includes(p.status)).length,
      });
    } catch (err) { console.error(err); }
    finally { setLoading(false); }
  };

  return (
    <div className="flex min-h-screen bg-hero-gradient">
      <Sidebar />
      <main className="flex-1 p-8 ml-64">
        <div className="max-w-6xl mx-auto">
          <div className="flex items-center justify-between mb-8">
            <div>
              <h1 className="text-3xl font-bold text-white">Dashboard</h1>
              <p className="text-gray-400 mt-1">Gérez vos projets ECU</p>
            </div>
            <Link href="/projects/new" className="btn-primary flex items-center gap-2">
              <Plus className="w-5 h-5" />
              Nouveau Projet
            </Link>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            {[
              { label: "Total Projets", value: stats.total, icon: FolderOpen, color: "text-blue-400" },
              { label: "Analysés", value: stats.analyzing, icon: Brain, color: "text-purple-400" },
              { label: "Complétés", value: stats.completed, icon: CheckCircle2, color: "text-green-400" },
              { label: "En attente", value: stats.pending, icon: Clock, color: "text-yellow-400" },
            ].map((s, i) => (
              <div key={i} className="glass rounded-2xl p-5">
                <div className="flex items-center justify-between mb-3">
                  <span className="text-sm text-gray-400">{s.label}</span>
                  <s.icon className={`w-5 h-5 ${s.color}`} />
                </div>
                <div className="text-2xl font-bold text-white">{s.value}</div>
              </div>
            ))}
          </div>

          {/* Projects List */}
          <div className="glass rounded-2xl overflow-hidden">
            <div className="px-6 py-4 border-b border-white/5">
              <h2 className="text-lg font-semibold text-white">Projets Récents</h2>
            </div>

            {loading ? (
              <div className="p-12 text-center">
                <Loader2 className="w-8 h-8 text-blue-400 animate-spin mx-auto" />
                <p className="text-gray-400 mt-4">Chargement...</p>
              </div>
            ) : projects.length === 0 ? (
              <div className="p-12 text-center">
                <FolderOpen className="w-12 h-12 text-gray-600 mx-auto mb-4" />
                <p className="text-gray-400 mb-4">Aucun projet pour le moment</p>
                <Link href="/projects/new" className="btn-primary inline-flex items-center gap-2">
                  <Plus className="w-4 h-4" />
                  Créer votre premier projet
                </Link>
              </div>
            ) : (
              <div className="divide-y divide-white/5">
                {projects.map((project) => (
                  <Link key={project.id} href={`/projects/${project.id}`}
                    className="flex items-center justify-between px-6 py-4 hover:bg-white/5 transition-colors cursor-pointer">
                    <div className="flex items-center gap-4">
                      <div className="w-10 h-10 bg-blue-500/10 rounded-xl flex items-center justify-center">
                        <TrendingUp className="w-5 h-5 text-blue-400" />
                      </div>
                      <div>
                        <h3 className="font-medium text-white">{project.name}</h3>
                        <p className="text-sm text-gray-500">
                          {project.vehicle_make} {project.vehicle_model} {project.vehicle_year && `• ${project.vehicle_year}`}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-4">
                      {project.ecu_filename && (
                        <span className="text-xs text-gray-500">{project.ecu_filename}</span>
                      )}
                      <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium border ${getStatusColor(project.status)}`}>
                        {getStatusLabel(project.status)}
                      </span>
                    </div>
                  </Link>
                ))}
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
