"use client";

import { useState } from "react";
import Link from "next/link";
import Navbar from "@/components/layout/Navbar";
import { api } from "@/lib/api";
import { Cpu, Mail, Loader2, CheckCircle } from "lucide-react";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [sent, setSent] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      await api.auth.forgotPassword(email);
      setSent(true);
    } catch (err: any) {
      setError(err.message || "Erreur lors de l'envoi");
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
              <h1 className="text-2xl font-bold text-white">Mot de passe oublié</h1>
              <p className="text-gray-400 text-sm mt-2">Nous vous enverrons un lien de réinitialisation</p>
            </div>

            {error && (
              <div className="bg-red-500/10 border border-red-500/30 rounded-xl px-4 py-3 mb-6 text-red-400 text-sm">
                {error}
              </div>
            )}

            {sent ? (
              <div className="text-center">
                <CheckCircle className="w-12 h-12 text-green-400 mx-auto mb-4" />
                <p className="text-green-400 text-sm mb-6">
                  Si cet email existe, un lien de réinitialisation a été envoyé.
                </p>
                <Link href="/login" className="btn-primary inline-block">Retour à la connexion</Link>
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm text-gray-400 mb-1">Email</label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                    <input type="email" className="input-field pl-10" value={email}
                      onChange={(e) => setEmail(e.target.value)} required placeholder="votre@email.com" />
                  </div>
                </div>
                <button type="submit" disabled={loading} className="btn-primary w-full flex items-center justify-center gap-2">
                  {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : null}
                  {loading ? "Envoi..." : "Envoyer le lien"}
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
