"use client";

import Link from "next/link";
import { useState, useEffect } from "react";
import { Menu, X, Cpu, LogOut, User, LayoutDashboard } from "lucide-react";

export default function Navbar() {
  const [isOpen, setIsOpen] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [userName, setUserName] = useState("");

  useEffect(() => {
    const token = localStorage.getItem("token");
    const user = localStorage.getItem("user");
    if (token && user) {
      setIsLoggedIn(true);
      const parsed = JSON.parse(user);
      setUserName(`${parsed.first_name} ${parsed.last_name}`);
    }
  }, []);

  const logout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    setIsLoggedIn(false);
    window.location.href = "/";
  };

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 glass-strong">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <Link href="/" className="flex items-center gap-2 group">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-cyan-400 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform">
              <Cpu className="w-6 h-6 text-white" />
            </div>
            <span className="text-xl font-bold gradient-text hidden sm:block">ECU Master Lab</span>
          </Link>

          <div className="hidden md:flex items-center gap-8">
            <Link href="/#features" className="text-gray-400 hover:text-white transition-colors text-sm">
              Fonctionnalités
            </Link>
            <Link href="/#security" className="text-gray-400 hover:text-white transition-colors text-sm">
              Sécurité
            </Link>
            <Link href="/#faq" className="text-gray-400 hover:text-white transition-colors text-sm">
              FAQ
            </Link>
            {isLoggedIn ? (
              <div className="flex items-center gap-4">
                <Link href="/dashboard" className="flex items-center gap-2 text-gray-300 hover:text-white transition-colors text-sm">
                  <LayoutDashboard className="w-4 h-4" />
                  Dashboard
                </Link>
                <div className="flex items-center gap-2 text-sm text-gray-400">
                  <User className="w-4 h-4" />
                  {userName}
                </div>
                <button onClick={logout} className="text-gray-400 hover:text-red-400 transition-colors">
                  <LogOut className="w-4 h-4" />
                </button>
              </div>
            ) : (
              <div className="flex items-center gap-4">
                <Link href="/login" className="text-gray-300 hover:text-white transition-colors text-sm">
                  Connexion
                </Link>
                <Link href="/register" className="btn-primary text-sm">
                  Commencer
                </Link>
              </div>
            )}
          </div>

          <button onClick={() => setIsOpen(!isOpen)} className="md:hidden text-gray-400 hover:text-white">
            {isOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>
      </div>

      {isOpen && (
        <div className="md:hidden glass-strong border-t border-white/10">
          <div className="px-4 py-4 space-y-3">
            <Link href="/#features" className="block text-gray-400 hover:text-white py-2" onClick={() => setIsOpen(false)}>
              Fonctionnalités
            </Link>
            <Link href="/#security" className="block text-gray-400 hover:text-white py-2" onClick={() => setIsOpen(false)}>
              Sécurité
            </Link>
            {isLoggedIn ? (
              <>
                <Link href="/dashboard" className="block text-gray-300 hover:text-white py-2" onClick={() => setIsOpen(false)}>
                  Dashboard
                </Link>
                <button onClick={logout} className="block text-red-400 hover:text-red-300 py-2">
                  Déconnexion
                </button>
              </>
            ) : (
              <>
                <Link href="/login" className="block text-gray-300 hover:text-white py-2" onClick={() => setIsOpen(false)}>
                  Connexion
                </Link>
                <Link href="/register" className="block btn-primary text-center" onClick={() => setIsOpen(false)}>
                  Commencer
                </Link>
              </>
            )}
          </div>
        </div>
      )}
    </nav>
  );
}
