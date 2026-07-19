"use client";

import { useState, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import Navbar from "@/components/layout/Navbar";
import { api } from "@/lib/api";
import { Cpu, CheckCircle, XCircle, Loader2 } from "lucide-react";

export default function VerifyEmailPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const token = searchParams.get("token");
  const [status, setStatus] = useState<"loading" | "success" | "error">("loading");
  const [message, setMessage] = useState("");

  useEffect(() => {
    if (!token) {
      setStatus("error");
      setMessage("Lien de vérification invalide");
      return;
    }
    api.auth.verifyEmail(token)
      .then(() => {
        setStatus("success");
        setMessage("Email vérifié avec succès ! Vous pouvez maintenant vous connecter.");
      })
      .catch((err: any) => {
        setStatus("error");
        setMessage(err.message || "Token de vérification invalide ou expiré");
      });
  }, [token]);

  return (
    <div className="min-h-screen bg-hero-gradient">
      <Navbar />
      <div className="flex items-center justify-center min-h-screen pt-16 px-4">
        <div className="w-full max-w-md">
          <div className="glass rounded-3xl p-8 glow-border animate-slide-up text-center">
            <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-cyan-400 rounded-2xl flex items-center justify-center mx-auto mb-4">
              <Cpu className="w-9 h-9 text-white" />
            </div>
            <h1 className="text-2xl font-bold text-white mb-4">Vérification d&apos;email</h1>
            {status === "loading" && (
              <div className="flex items-center justify-center gap-2 text-gray-400">
                <Loader2 className="w-5 h-5 animate-spin" />
                Vérification en cours...
              </div>
            )}
            {status === "success" && (
              <>
                <CheckCircle className="w-12 h-12 text-green-400 mx-auto mb-4" />
                <p className="text-green-400 text-sm mb-6">{message}</p>
                <Link href="/login" className="btn-primary inline-block">Se connecter</Link>
              </>
            )}
            {status === "error" && (
              <>
                <XCircle className="w-12 h-12 text-red-400 mx-auto mb-4" />
                <p className="text-red-400 text-sm mb-6">{message}</p>
                <Link href="/login" className="btn-secondary inline-block">Retour à la connexion</Link>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
