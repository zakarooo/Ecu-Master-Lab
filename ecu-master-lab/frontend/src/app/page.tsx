"use client";

import Link from "next/link";
import Navbar from "@/components/layout/Navbar";
import Footer from "@/components/layout/Footer";
import {
  Cpu, Shield, Zap, Brain, FileCheck, Cloud, ArrowRight,
  CheckCircle2, Lock, Clock, Star, Upload, BarChart3, Users
} from "lucide-react";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-hero-gradient">
      <Navbar />

      {/* Hero */}
      <section className="relative min-h-screen flex items-center justify-center overflow-hidden pt-16">
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl animate-float" />
          <div className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-cyan-500/10 rounded-full blur-3xl animate-float" style={{ animationDelay: "2s" }} />
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-blue-500/5 rounded-full blur-3xl" />
        </div>

        <div className="relative z-10 max-w-5xl mx-auto px-4 text-center">
          <div className="inline-flex items-center gap-2 glass rounded-full px-4 py-2 mb-8 animate-fade-in">
            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
            <span className="text-sm text-gray-400">Agent IA opérationnel</span>
          </div>

          <h1 className="text-5xl md:text-7xl font-bold mb-6 animate-slide-up">
            <span className="text-white">Calibration ECU</span>
            <br />
            <span className="gradient-text">Propulsée par l&apos;IA</span>
          </h1>

          <p className="text-lg md:text-xl text-gray-400 max-w-2xl mx-auto mb-10 animate-slide-up" style={{ animationDelay: "0.1s" }}>
            Déposez votre fichier ECU, sélectionnez vos modifications, et laissez notre Agent IA
            analyser et traiter automatiquement votre calibration.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 animate-slide-up" style={{ animationDelay: "0.2s" }}>
            <Link href="/register" className="btn-primary text-lg flex items-center gap-2">
              Commencer maintenant
              <ArrowRight className="w-5 h-5" />
            </Link>
            <Link href="/#features" className="btn-secondary text-lg">
              En savoir plus
            </Link>
          </div>

          <div className="mt-16 grid grid-cols-3 gap-8 max-w-lg mx-auto animate-fade-in" style={{ animationDelay: "0.4s" }}>
            <div>
              <div className="text-2xl font-bold text-white">10K+</div>
              <div className="text-xs text-gray-500">Fichiers traités</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-white">98%</div>
              <div className="text-xs text-gray-500">Précision IA</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-white">45s</div>
              <div className="text-xs text-gray-500">Temps moyen</div>
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="py-24 relative">
        <div className="max-w-7xl mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
              Fonctionnalités <span className="gradient-text">Avancées</span>
            </h2>
            <p className="text-gray-400 max-w-2xl mx-auto">
              Une suite complète d&apos;outils pour la calibration ECU, alimentée par intelligence artificielle.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              { icon: Brain, title: "Agent IA ECU", desc: "Analyse automatique du binaire ECU avec détection du type, compatibilité et risques." },
              { icon: Upload, title: "Upload Intelligent", desc: "Glisser-déposer avec validation automatique des formats BIN, ORI, HEX, FRF, MPC, BDM." },
              { icon: Shield, title: "Sécurité Renforcée", desc: "Sauvegarde automatique, versionnage, chiffrement des fichiers et sauvegardes chiffrées." },
              { icon: Zap, title: "Traitement Rapide", desc: "Calcul des checksums, modification automatique et génération du fichier en secondes." },
              { icon: FileCheck, title: "Rapport d&apos;Analyse", desc: "Rapport détaillé avec type ECU, zones cartographiques, checksums et indice de confiance." },
              { icon: BarChart3, title: "Dashboard Complet", desc: "Suivi en temps réel de tous vos projets avec historique et notifications WebSocket." },
            ].map((feature, i) => (
              <div key={i} className="glass rounded-2xl p-6 card-hover group">
                <div className="w-12 h-12 bg-blue-500/10 rounded-xl flex items-center justify-center mb-4 group-hover:bg-blue-500/20 transition-colors">
                  <feature.icon className="w-6 h-6 text-blue-400" />
                </div>
                <h3 className="text-lg font-semibold text-white mb-2">{feature.title}</h3>
                <p className="text-gray-400 text-sm">{feature.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How it works */}
      <section className="py-24 relative">
        <div className="max-w-5xl mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
              Comment ça <span className="gradient-text">fonctionne</span>
            </h2>
          </div>

          <div className="space-y-8">
            {[
              { step: "01", title: "Créez votre compte", desc: "Inscrivez-vous en quelques secondes pour accéder à la plateforme." },
              { step: "02", title: "Déposez votre fichier ECU", desc: "Uploadez votre fichier binaire via notre interface drag & drop sécurisée." },
              { step: "03", title: "L&apos;Agent IA analyse automatiquement", desc: "Détection du type ECU, checksum, compatibilité et zones cartographiques." },
              { step: "04", title: "Sélectionnez vos modifications", desc: "Choisissez parmi nos options : Stage 1-3, DPF OFF, EGR, AdBlue, et plus." },
              { step: "05", title: "Téléchargez le fichier modifié", desc: "Récupérez votre fichier calibré avec le rapport d&apos;analyse complet." },
            ].map((item, i) => (
              <div key={i} className="flex items-start gap-6 glass rounded-2xl p-6 card-hover">
                <div className="w-14 h-14 bg-gradient-to-br from-blue-500 to-cyan-400 rounded-xl flex items-center justify-center flex-shrink-0">
                  <span className="text-white font-bold text-lg">{item.step}</span>
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-white mb-1">{item.title}</h3>
                  <p className="text-gray-400 text-sm">{item.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Supported Tools */}
      <section className="py-24 relative">
        <div className="max-w-5xl mx-auto px-4 text-center">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
            Outils <span className="gradient-text">Compatibles</span>
          </h2>
          <p className="text-gray-400 mb-12">Supportés par tous les outils de lecture ECU du marché</p>
          <div className="flex flex-wrap justify-center gap-4">
            {["Autotuner", "Flex", "KESS", "KTAG", "CMD Flash", "PCM Flash", "BitBox", "Magic Motorsport", "FoxFlash", "Dimsport"].map((tool) => (
              <div key={tool} className="glass rounded-xl px-5 py-3 text-sm text-gray-300 hover:text-white hover:border-blue-500/30 transition-all cursor-default">
                {tool}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Security */}
      <section id="security" className="py-24 relative">
        <div className="max-w-5xl mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
              Sécurité <span className="gradient-text">Maximale</span>
            </h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[
              { icon: Lock, title: "Chiffrement", desc: "Tous les fichiers sont chiffrés en transit et au repos avec AES-256." },
              { icon: Cloud, title: "Sauvegardes", desc: "Versionnage automatique avec sauvegarde toutes les 5 minutes." },
              { icon: Shield, title: "Original préservé", desc: "Copie originale toujours conservée. Aucune modification sans votre accord." },
            ].map((item, i) => (
              <div key={i} className="glass rounded-2xl p-6 text-center card-hover">
                <div className="w-14 h-14 bg-blue-500/10 rounded-xl flex items-center justify-center mx-auto mb-4">
                  <item.icon className="w-7 h-7 text-blue-400" />
                </div>
                <h3 className="text-lg font-semibold text-white mb-2">{item.title}</h3>
                <p className="text-gray-400 text-sm">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* FAQ */}
      <section id="faq" className="py-24 relative">
        <div className="max-w-3xl mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
              Questions <span className="gradient-text">Fréquentes</span>
            </h2>
          </div>

          <div className="space-y-4">
            {[
              { q: "Quels formats de fichiers sont supportés ?", a: "BIN, ORI, HEX, FRF, MPC, BDM et ZIP. Nos outils d'analyse supportent tous les formats courants du marché." },
              { q: "L'Agent IA peut-elle remplacer un préparateur ?", a: "L'Agent IA traite automatiquement les modifications standards (Stage 1, DPF OFF, etc.). Pour des modifications complexes, le fichier est transmis à un expert humain." },
              { q: "Mon fichier original est-il en sécurité ?", a: "Oui, nous conservons toujours une copie originale intacte. Vous pouvez à tout moment revenir à la version originale." },
              { q: "Combien de temps prend le traitement ?", a: "L'analyse IA prend environ 45 secondes. Le traitement complet varie selon les modifications sélectionnées." },
              { q: "Quels outils de lecture sont compatibles ?", a: "Tous les outils majeurs : Autotuner, Flex, KESS, KTAG, CMD Flash, PCM Flash, BitBox, FoxFlash, Dimsport, et plus." },
            ].map((item, i) => (
              <div key={i} className="glass rounded-xl p-5">
                <h3 className="font-semibold text-white mb-2">{item.q}</h3>
                <p className="text-gray-400 text-sm">{item.a}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-24 relative">
        <div className="max-w-3xl mx-auto px-4 text-center">
          <div className="glass rounded-3xl p-12 glow-border">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
              Prêt à commencer ?
            </h2>
            <p className="text-gray-400 mb-8 max-w-xl mx-auto">
              Rejoignez les préparateurs automobiles qui font confiance à ECU Master Lab pour leurs calibrations.
            </p>
            <Link href="/register" className="btn-primary text-lg inline-flex items-center gap-2">
              Créer mon compte gratuit
              <ArrowRight className="w-5 h-5" />
            </Link>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
}
