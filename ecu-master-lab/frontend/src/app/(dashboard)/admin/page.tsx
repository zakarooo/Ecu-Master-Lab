"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Sidebar from "@/components/layout/Sidebar";
import { api } from "@/lib/api";
import { getStatusColor, getStatusLabel } from "@/lib/utils";
import {
  Users, FolderOpen, CheckCircle2, Clock, AlertCircle,
  BarChart3, Shield, Loader2, Activity
} from "lucide-react";

export default function AdminPage() {
  const router = useRouter();
  const [stats, setStats] = useState<any>(null);
  const [users, setUsers] = useState<any[]>([]);
  const [projects, setProjects] = useState<any[]>([]);
  const [logs, setLogs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("overview");

  useEffect(() => {
    if (!localStorage.getItem("token")) { router.push("/login"); return; }
    loadAdminData();
  }, []);

  const loadAdminData = async () => {
    try {
      const [s, u, p, l] = await Promise.all([
        api.admin.stats(), api.admin.users(), api.admin.projects(), api.admin.auditLogs(),
      ]);
      setStats(s); setUsers(u); setProjects(p); setLogs(l);
    } catch (err: any) {
      if (err.message?.includes("403") || err.message?.includes("administrateur")) {
        alert("Accès réservé aux administrateurs");
        router.push("/dashboard");
      }
    } finally { setLoading(false); }
  };

  if (loading) return (
    <div className="flex min-h-screen bg-hero-gradient items-center justify-center">
      <Loader2 className="w-8 h-8 text-blue-400 animate-spin" />
    </div>
  );

  const tabs = [
    { id: "overview", label: "Vue d&apos;ensemble", icon: BarChart3 },
    { id: "users", label: "Utilisateurs", icon: Users },
    { id: "projects", label: "Projets", icon: FolderOpen },
    { id: "logs", label: "Journal", icon: Activity },
  ];

  return (
    <div className="flex min-h-screen bg-hero-gradient">
      <Sidebar />
      <main className="flex-1 p-8 ml-64">
        <div className="max-w-6xl mx-auto">
          <div className="flex items-center gap-3 mb-8">
            <Shield className="w-8 h-8 text-blue-400" />
            <div>
              <h1 className="text-3xl font-bold text-white">Administration</h1>
              <p className="text-gray-400 mt-1">Gestion de la plateforme ECU Master Lab</p>
            </div>
          </div>

          {/* Tabs */}
          <div className="flex gap-2 mb-8">
            {tabs.map((tab) => (
              <button key={tab.id} onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm transition-all ${
                  activeTab === tab.id
                    ? "bg-blue-500/10 text-blue-400 border border-blue-500/20"
                    : "text-gray-400 hover:text-white hover:bg-white/5"
                }`}>
                <tab.icon className="w-4 h-4" />
                {tab.label}
              </button>
            ))}
          </div>

          {/* Overview */}
          {activeTab === "overview" && stats && (
            <div className="space-y-6 animate-fade-in">
              <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4">
                {[
                  { label: "Utilisateurs", value: stats.total_users, icon: Users, color: "text-blue-400" },
                  { label: "Projets", value: stats.total_projects, icon: FolderOpen, color: "text-cyan-400" },
                  { label: "En attente", value: stats.pending_projects, icon: Clock, color: "text-yellow-400" },
                  { label: "En cours", value: stats.analyzing_projects, icon: AlertCircle, color: "text-purple-400" },
                  { label: "Complétés", value: stats.completed_projects, icon: CheckCircle2, color: "text-green-400" },
                  { label: "Échoués", value: stats.failed_projects, icon: AlertCircle, color: "text-red-400" },
                ].map((s, i) => (
                  <div key={i} className="glass rounded-2xl p-5">
                    <div className="flex items-center justify-between mb-3">
                      <span className="text-xs text-gray-500">{s.label}</span>
                      <s.icon className={`w-4 h-4 ${s.color}`} />
                    </div>
                    <div className="text-2xl font-bold text-white">{s.value}</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Users */}
          {activeTab === "users" && (
            <div className="glass rounded-2xl overflow-hidden animate-fade-in">
              <div className="px-6 py-4 border-b border-white/5">
                <h2 className="text-lg font-semibold text-white">Utilisateurs ({users.length})</h2>
              </div>
              <div className="divide-y divide-white/5">
                {users.map((user) => (
                  <div key={user.id} className="flex items-center justify-between px-6 py-4">
                    <div>
                      <p className="text-white font-medium">{user.first_name} {user.last_name}</p>
                      <p className="text-sm text-gray-500">{user.email}</p>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                        user.role === "admin" ? "bg-red-500/10 text-red-400 border border-red-500/20"
                          : user.role === "expert" ? "bg-purple-500/10 text-purple-400 border border-purple-500/20"
                            : "bg-blue-500/10 text-blue-400 border border-blue-500/20"
                      }`}>{user.role}</span>
                      <span className={`w-2 h-2 rounded-full ${user.is_active ? "bg-green-400" : "bg-gray-500"}`} />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Projects */}
          {activeTab === "projects" && (
            <div className="glass rounded-2xl overflow-hidden animate-fade-in">
              <div className="px-6 py-4 border-b border-white/5">
                <h2 className="text-lg font-semibold text-white">Projets ({projects.length})</h2>
              </div>
              <div className="divide-y divide-white/5">
                {projects.map((p) => (
                  <div key={p.id} className="flex items-center justify-between px-6 py-4">
                    <div>
                      <p className="text-white font-medium">{p.name}</p>
                      <p className="text-sm text-gray-500">{p.vehicle_make} {p.vehicle_model} • {p.ecu_filename || "Pas de fichier"}</p>
                    </div>
                    <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium border ${getStatusColor(p.status)}`}>
                      {getStatusLabel(p.status)}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Audit Logs */}
          {activeTab === "logs" && (
            <div className="glass rounded-2xl overflow-hidden animate-fade-in">
              <div className="px-6 py-4 border-b border-white/5">
                <h2 className="text-lg font-semibold text-white">Journal d&apos;Audit ({logs.length})</h2>
              </div>
              <div className="divide-y divide-white/5 max-h-[600px] overflow-y-auto">
                {logs.map((log) => (
                  <div key={log.id} className="px-6 py-3 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <Activity className="w-4 h-4 text-gray-500" />
                      <div>
                        <p className="text-sm text-white">{log.action}</p>
                        <p className="text-xs text-gray-500">User #{log.user_id} • {log.resource_type} #{log.resource_id}</p>
                      </div>
                    </div>
                    <span className="text-xs text-gray-600">{new Date(log.created_at).toLocaleString("fr-FR")}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
