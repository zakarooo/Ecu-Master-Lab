"use client";

import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import Sidebar from "@/components/layout/Sidebar";
import { api } from "@/lib/api";
import { getStatusColor, getStatusLabel } from "@/lib/utils";
import {
  Users, FolderOpen, CheckCircle2, Clock, AlertCircle,
  BarChart3, Shield, Loader2, Activity, Trash2, ArrowRightLeft,
  ChevronLeft, ChevronRight, UserMinus
} from "lucide-react";

export default function AdminPage() {
  const router = useRouter();
  const [stats, setStats] = useState<any>(null);
  const [users, setUsers] = useState<any[]>([]);
  const [usersTotal, setUsersTotal] = useState(0);
  const [projects, setProjects] = useState<any[]>([]);
  const [projectsTotal, setProjectsTotal] = useState(0);
  const [logs, setLogs] = useState<any[]>([]);
  const [logsTotal, setLogsTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("overview");
  const [transferProjectId, setTransferProjectId] = useState<number | null>(null);
  const [transferUserId, setTransferUserId] = useState("");
  const [usersPage, setUsersPage] = useState(0);
  const [projectsPage, setProjectsPage] = useState(0);
  const [logsPage, setLogsPage] = useState(0);
  const PAGE_SIZE = 15;

  useEffect(() => {
    if (!localStorage.getItem("token")) { router.push("/login"); return; }
    loadAdminData();
  }, []);

  const loadAdminData = async () => {
    try {
      const s = await api.admin.stats();
      setStats(s);
      const u = await api.admin.users(`skip=0&limit=${PAGE_SIZE}`);
      setUsers(u.items); setUsersTotal(u.total);
      const p = await api.admin.projects(`skip=0&limit=${PAGE_SIZE}`);
      setProjects(p.items); setProjectsTotal(p.total);
      const l = await api.admin.auditLogs(`skip=0&limit=${PAGE_SIZE}`);
      setLogs(l.items); setLogsTotal(l.total);
    } catch (err: any) {
      if (err.message?.includes("403") || err.message?.includes("administrateur")) {
        alert("Accès réservé aux administrateurs");
        router.push("/dashboard");
      }
    } finally { setLoading(false); }
  };

  const loadUsers = useCallback(async (page: number) => {
    setUsersPage(page);
    const r = await api.admin.users(`skip=${page * PAGE_SIZE}&limit=${PAGE_SIZE}`);
    setUsers(r.items); setUsersTotal(r.total);
  }, []);

  const loadProjects = useCallback(async (page: number) => {
    setProjectsPage(page);
    const r = await api.admin.projects(`skip=${page * PAGE_SIZE}&limit=${PAGE_SIZE}`);
    setProjects(r.items); setProjectsTotal(r.total);
  }, []);

  const loadLogs = useCallback(async (page: number) => {
    setLogsPage(page);
    const r = await api.admin.auditLogs(`skip=${page * PAGE_SIZE}&limit=${PAGE_SIZE}`);
    setLogs(r.items); setLogsTotal(r.total);
  }, []);

  const handleDeleteProject = async (id: number) => {
    if (!confirm("Supprimer ce projet et tous ses fichiers ? Cette action est irréversible.")) return;
    try {
      await api.admin.deleteProject(id);
      loadProjects(projectsPage);
      loadAdminData();
    } catch (err: any) { alert(err.message); }
  };

  const handleDeleteUser = async (id: number, email: string) => {
    if (!confirm(`Supprimer l'utilisateur ${email} ? Cette action est irréversible.`)) return;
    try {
      await api.admin.deleteUser(id);
      loadUsers(0);
      loadAdminData();
    } catch (err: any) { alert(err.message); }
  };

  const handleTransfer = async (id: number) => {
    if (!transferUserId.trim()) { alert("Saisissez l'ID utilisateur cible"); return; }
    try {
      await api.admin.transferProject(id, { target_user_id: parseInt(transferUserId) });
      setTransferProjectId(null);
      setTransferUserId("");
      loadProjects(projectsPage);
    } catch (err: any) { alert(err.message); }
  };

  const Pagination = ({ page, total, onLoad }: { page: number; total: number; onLoad: (p: number) => void }) => {
    const totalPages = Math.ceil(total / PAGE_SIZE);
    if (totalPages <= 1) return null;
    return (
      <div className="flex items-center justify-between px-6 py-3 border-t border-white/5">
        <span className="text-xs text-gray-500">{total} résultat(s)</span>
        <div className="flex items-center gap-2">
          <button onClick={() => onLoad(page - 1)} disabled={page === 0}
            className="p-1 text-gray-500 hover:text-white disabled:opacity-30"><ChevronLeft className="w-4 h-4" /></button>
          <span className="text-xs text-gray-400">{page + 1}/{totalPages}</span>
          <button onClick={() => onLoad(page + 1)} disabled={page >= totalPages - 1}
            className="p-1 text-gray-500 hover:text-white disabled:opacity-30"><ChevronRight className="w-4 h-4" /></button>
        </div>
      </div>
    );
  };

  if (loading) return (
    <div className="flex min-h-screen bg-hero-gradient items-center justify-center">
      <Loader2 className="w-8 h-8 text-blue-400 animate-spin" />
    </div>
  );

  const tabs = [
    { id: "overview", label: "Vue d'ensemble", icon: BarChart3 },
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

          {activeTab === "users" && (
            <div className="glass rounded-2xl overflow-hidden animate-fade-in">
              <div className="px-6 py-4 border-b border-white/5">
                <h2 className="text-lg font-semibold text-white">Utilisateurs ({usersTotal})</h2>
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
                      <button onClick={() => handleDeleteUser(user.id, user.email)}
                        className="p-1.5 text-gray-500 hover:text-red-400 transition-colors" title="Supprimer">
                        <UserMinus className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
              <Pagination page={usersPage} total={usersTotal} onLoad={loadUsers} />
            </div>
          )}

          {activeTab === "projects" && (
            <div className="glass rounded-2xl overflow-hidden animate-fade-in">
              <div className="px-6 py-4 border-b border-white/5">
                <h2 className="text-lg font-semibold text-white">Projets ({projectsTotal})</h2>
              </div>
              <div className="divide-y divide-white/5">
                {projects.map((p) => (
                  <div key={p.id} className="flex items-center justify-between px-6 py-4">
                    <div className="flex-1 min-w-0">
                      <p className="text-white font-medium">{p.name}</p>
                      <p className="text-sm text-gray-500">{p.vehicle_make} {p.vehicle_model} • {p.ecu_filename || "Pas de fichier"} • User #{p.user_id || "?"}</p>
                    </div>
                    <div className="flex items-center gap-3 ml-4">
                      <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium border ${getStatusColor(p.status)}`}>
                        {getStatusLabel(p.status)}
                      </span>

                      {transferProjectId === p.id ? (
                        <div className="flex items-center gap-2">
                          <input type="number" className="input-field w-24 text-xs py-1" placeholder="User ID"
                            value={transferUserId} onChange={(e) => setTransferUserId(e.target.value)} />
                          <button onClick={() => handleTransfer(p.id)} className="text-xs text-blue-400 hover:text-blue-300">OK</button>
                          <button onClick={() => { setTransferProjectId(null); setTransferUserId(""); }} className="text-xs text-gray-500">Annuler</button>
                        </div>
                      ) : (
                        <button onClick={() => setTransferProjectId(p.id)}
                          className="p-1.5 text-gray-500 hover:text-blue-400 transition-colors" title="Transférer">
                          <ArrowRightLeft className="w-4 h-4" />
                        </button>
                      )}

                      <button onClick={() => handleDeleteProject(p.id)}
                        className="p-1.5 text-gray-500 hover:text-red-400 transition-colors" title="Supprimer">
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
              <Pagination page={projectsPage} total={projectsTotal} onLoad={loadProjects} />
            </div>
          )}

          {activeTab === "logs" && (
            <div className="glass rounded-2xl overflow-hidden animate-fade-in">
              <div className="px-6 py-4 border-b border-white/5">
                <h2 className="text-lg font-semibold text-white">Journal d&apos;Audit ({logsTotal})</h2>
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
              <Pagination page={logsPage} total={logsTotal} onLoad={loadLogs} />
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
