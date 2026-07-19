"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Sidebar from "@/components/layout/Sidebar";
import { api } from "@/lib/api";
import { User, Lock, Save, Loader2, CheckCircle } from "lucide-react";

export default function ProfilePage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [user, setUser] = useState<any>(null);
  const [profile, setProfile] = useState({ first_name: "", last_name: "", email: "", phone: "" });
  const [passwords, setPasswords] = useState({ current_password: "", new_password: "", confirm_password: "" });
  const [profileMsg, setProfileMsg] = useState("");
  const [passwordMsg, setPasswordMsg] = useState("");
  const [profileError, setProfileError] = useState("");
  const [passwordError, setPasswordError] = useState("");

  useEffect(() => {
    if (!localStorage.getItem("token")) { router.push("/login"); return; }
    loadProfile();
  }, []);

  const loadProfile = async () => {
    try {
      const u = await api.auth.me();
      setUser(u);
      setProfile({
        first_name: u.first_name || "",
        last_name: u.last_name || "",
        email: u.email || "",
        phone: u.phone || "",
      });
    } catch (e: any) {
      console.error(e);
    }
    setLoading(false);
  };

  const handleProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setProfileMsg(""); setProfileError("");
    try {
      const res = await api.auth.updateProfile(profile);
      setUser(res);
      localStorage.setItem("user", JSON.stringify(res));
      setProfileMsg("Profil mis à jour");
    } catch (err: any) {
      setProfileError(err.message);
    }
    setSaving(false);
  };

  const handlePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setPasswordMsg(""); setPasswordError("");
    if (passwords.new_password !== passwords.confirm_password) {
      setPasswordError("Les mots de passe ne correspondent pas");
      return;
    }
    setSaving(true);
    try {
      await api.auth.changePassword({
        current_password: passwords.current_password,
        new_password: passwords.new_password,
      });
      setPasswordMsg("Mot de passe modifié");
      setPasswords({ current_password: "", new_password: "", confirm_password: "" });
    } catch (err: any) {
      setPasswordError(err.message);
    }
    setSaving(false);
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
        <div className="max-w-2xl mx-auto">
          <div className="flex items-center gap-3 mb-8">
            <User className="w-8 h-8 text-blue-400" />
            <div>
              <h1 className="text-3xl font-bold text-white">Mon Profil</h1>
              <p className="text-gray-400 mt-1">Gérez vos informations personnelles</p>
            </div>
          </div>

          {/* Profile Form */}
          <form onSubmit={handleProfile} className="glass rounded-2xl p-6 mb-6">
            <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
              <User className="w-5 h-5 text-blue-400" /> Informations personnelles
            </h2>
            <div className="grid grid-cols-2 gap-4 mb-4">
              <div>
                <label className="block text-xs text-gray-400 mb-1">Prénom</label>
                <input className="input-field w-full" value={profile.first_name}
                  onChange={(e) => setProfile({ ...profile, first_name: e.target.value })} />
              </div>
              <div>
                <label className="block text-xs text-gray-400 mb-1">Nom</label>
                <input className="input-field w-full" value={profile.last_name}
                  onChange={(e) => setProfile({ ...profile, last_name: e.target.value })} />
              </div>
            </div>
            <div className="mb-4">
              <label className="block text-xs text-gray-400 mb-1">Email</label>
              <input type="email" className="input-field w-full" value={profile.email}
                onChange={(e) => setProfile({ ...profile, email: e.target.value })} />
            </div>
            <div className="mb-4">
              <label className="block text-xs text-gray-400 mb-1">Téléphone</label>
              <input className="input-field w-full" value={profile.phone}
                onChange={(e) => setProfile({ ...profile, phone: e.target.value })} />
            </div>
            {profileMsg && <p className="text-green-400 text-sm mb-3 flex items-center gap-1"><CheckCircle className="w-4 h-4" />{profileMsg}</p>}
            {profileError && <p className="text-red-400 text-sm mb-3">{profileError}</p>}
            <button type="submit" disabled={saving}
              className="btn-primary flex items-center gap-2">
              {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
              Enregistrer
            </button>
          </form>

          {/* Password Form */}
          <form onSubmit={handlePassword} className="glass rounded-2xl p-6">
            <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
              <Lock className="w-5 h-5 text-yellow-400" /> Changer le mot de passe
            </h2>
            <div className="mb-4">
              <label className="block text-xs text-gray-400 mb-1">Mot de passe actuel</label>
              <input type="password" className="input-field w-full" value={passwords.current_password}
                onChange={(e) => setPasswords({ ...passwords, current_password: e.target.value })} />
            </div>
            <div className="mb-4">
              <label className="block text-xs text-gray-400 mb-1">Nouveau mot de passe</label>
              <input type="password" className="input-field w-full" value={passwords.new_password}
                onChange={(e) => setPasswords({ ...passwords, new_password: e.target.value })} />
            </div>
            <div className="mb-4">
              <label className="block text-xs text-gray-400 mb-1">Confirmer</label>
              <input type="password" className="input-field w-full" value={passwords.confirm_password}
                onChange={(e) => setPasswords({ ...passwords, confirm_password: e.target.value })} />
            </div>
            {passwordMsg && <p className="text-green-400 text-sm mb-3 flex items-center gap-1"><CheckCircle className="w-4 h-4" />{passwordMsg}</p>}
            {passwordError && <p className="text-red-400 text-sm mb-3">{passwordError}</p>}
            <button type="submit" disabled={saving}
              className="btn-primary flex items-center gap-2">
              {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Lock className="w-4 h-4" />}
              Modifier le mot de passe
            </button>
          </form>

          {/* Account Info */}
          {user && (
            <div className="glass rounded-2xl p-6 mt-6">
              <h2 className="text-lg font-semibold text-white mb-4">Informations du compte</h2>
              <div className="space-y-2 text-sm">
                <p className="text-gray-400">Rôle: <span className="text-white font-medium">{user.role}</span></p>
                <p className="text-gray-400">Email vérifié: <span className={user.is_email_verified ? "text-green-400" : "text-yellow-400"}>
                  {user.is_email_verified ? "Oui" : "Non"}
                </span></p>
                <p className="text-gray-400">Membre depuis: <span className="text-white">
                  {new Date(user.created_at).toLocaleDateString("fr-FR")}
                </span></p>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
