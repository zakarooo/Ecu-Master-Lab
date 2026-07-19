"use client";

import { useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import Navbar from "@/components/layout/Navbar";
import { api } from "@/lib/api";
import { Cpu, Eye, EyeOff, Loader2, CheckCircle } from "lucide-react";

export default function ResetPasswordPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const token = searchParams.get("token");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (password !== confirm) {
      setError("Les mots de passe ne correspondent pas");
      return;
    }
    if (!token) {
      setError("Token invalide");
      return;
    }
    setLoading(true);
    setError("");
    try {
      await api.auth.resetPassword(token, password);
      setSuccess(true);
    } catch (err: any) {
      setError(err.message || "Erreur lors de la réinitialisation");
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
              <h1 className="text-2xl font-bold text-white">Nouveau mot de passe</h1>
              <p className="text-gray-400 text-sm mt-2">Choisissez un mot de passe sécurisé</p>
            </div>

            {error && (
              <div className="bg-red-500/10 border border-red-500/30 rounded-xl px-4 py-3 mb-6 text-red-400 text-sm">
                {error}
              </div>
            )}

            {success ? (
              <div className="text-center">
                <CheckCircle className="w-12 h-12 text-green-400 mx-auto mb-4" />
                <p className="text-green-400 text-sm mb-6">
                  Mot de passe réinitialisé avec succès !
                </p>
                <Link href="/login" className="btn-primary inline-block">Se connecter</Link>
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm text-gray-400 mb-1">Nouveau mot de passe</label>
                  <div className="relative">
                    <input type={showPassword ? "text" : "password"} className="input-field pr-12"
                      value={password} onChange={(e) => setPassword(e.target.value)} required minLength={8} />
                    <button type="button" onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-300">
                      {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                    </button>
                  </div>
                  <p className="text-xs text-gray-500 mt-1">Min 8 caractères, 1 majuscule, 1 minuscule, 1 chiffre</p>
                </div>
                <div>
                  <label className="block text-sm text-gray-400 mb-1">Confirmer le mot de passe</label>
                  <input type={showPassword ? "text" : "password"} className="input-field"
                    value={confirm} onChange={(e) => setConfirm(e.target.value)} required />
                </div>
                <button type="submit" disabled={loading} className="btn-primary w-full flex items-center justify-center gap-2">
                  {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : null}
                  {loading ? "Réinitialisation..." : "Réinitialiser le mot de passe"}
                </button>
              </form>
            )}

            <p className="text-center text-gray-500 text-sm mt-6">
              <Link href="/login" className="text-blue-400 hover:text-blue-300">Retour à la connexion</Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
