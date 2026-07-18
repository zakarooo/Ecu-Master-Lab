"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import Navbar from "@/components/layout/Navbar";
import { api } from "@/lib/api";
import { Cpu, Eye, EyeOff, Loader2 } from "lucide-react";

export default function RegisterPage() {
  const router = useRouter();
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [form, setForm] = useState({
    first_name: "", last_name: "", email: "", phone: "", password: "",
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const res = await api.auth.register(form);
      localStorage.setItem("token", res.access_token);
      localStorage.setItem("user", JSON.stringify(res.user));
      router.push("/dashboard");
    } catch (err: any) {
      setError(err.message || "Erreur lors de l'inscription");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-hero-gradient">
      <Navbar />
      <div className="flex items-center justify-center min-h-screen pt-16 px-4">
        <div className="w-full max-w-md">
          <div className="glass rounded-3xl p-8 glow-border animate-slide-up">
            <div className="text-center mb-8">
              <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-cyan-400 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <Cpu className="w-9 h-9 text-white" />
              </div>
              <h1 className="text-2xl font-bold text-white">Créer un compte</h1>
              <p className="text-gray-400 text-sm mt-2">Rejoignez ECU Master Lab</p>
            </div>

            {error && (
              <div className="bg-red-500/10 border border-red-500/30 rounded-xl px-4 py-3 mb-6 text-red-400 text-sm">
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm text-gray-400 mb-1">Prénom</label>
                  <input type="text" className="input-field" value={form.first_name}
                    onChange={(e) => setForm({ ...form, first_name: e.target.value })} required />
                </div>
                <div>
                  <label className="block text-sm text-gray-400 mb-1">Nom</label>
                  <input type="text" className="input-field" value={form.last_name}
                    onChange={(e) => setForm({ ...form, last_name: e.target.value })} required />
                </div>
              </div>

              <div>
                <label className="block text-sm text-gray-400 mb-1">Email</label>
                <input type="email" className="input-field" value={form.email}
                  onChange={(e) => setForm({ ...form, email: e.target.value })} required />
              </div>

              <div>
                <label className="block text-sm text-gray-400 mb-1">Téléphone</label>
                <input type="tel" className="input-field" value={form.phone}
                  onChange={(e) => setForm({ ...form, phone: e.target.value })} />
              </div>

              <div>
                <label className="block text-sm text-gray-400 mb-1">Mot de passe</label>
                <div className="relative">
                  <input type={showPassword ? "text" : "password"} className="input-field pr-12"
                    value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} required />
                  <button type="button" onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-300">
                    {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                  </button>
                </div>
              </div>

              <button type="submit" disabled={loading} className="btn-primary w-full flex items-center justify-center gap-2">
                {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : null}
                {loading ? "Création..." : "Créer mon compte"}
              </button>
            </form>

            <p className="text-center text-gray-500 text-sm mt-6">
              Déjà un compte ?{" "}
              <Link href="/login" className="text-blue-400 hover:text-blue-300">Se connecter</Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
