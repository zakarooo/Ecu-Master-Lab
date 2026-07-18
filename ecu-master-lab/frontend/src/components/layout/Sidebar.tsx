"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Cpu,
  LayoutDashboard,
  FolderPlus,
  Shield,
  LogOut,
  ScanLine,
  Upload,
  Database,
  Brain,
} from "lucide-react";
import { cn } from "@/lib/utils";

interface NavItem {
  href: string;
  label: string;
  icon: any;
}

interface NavSection {
  title: string;
  items: NavItem[];
}

const sections: NavSection[] = [
  {
    title: "Navigation",
    items: [
      { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
      { href: "/projects/new", label: "Nouveau Projet", icon: FolderPlus },
      { href: "/admin", label: "Administration", icon: Shield },
    ],
  },
  {
    title: "Analyse",
    items: [
      { href: "/analysis", label: "Analyse ECU", icon: ScanLine },
      { href: "/analysis/upload", label: "Upload Fichier", icon: Upload },
    ],
  },
  {
    title: "Référence",
    items: [
      { href: "/reference", label: "Données Référence", icon: Database },
    ],
  },
  {
    title: "Intelligence",
    items: [
      { href: "/intelligence", label: "ECU Intelligence", icon: Brain },
    ],
  },
];

export default function Sidebar() {
  const pathname = usePathname();

  const logout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    window.location.href = "/";
  };

  return (
    <aside className="fixed left-0 top-0 h-full w-64 glass-strong border-r border-white/5 flex flex-col z-40">
      <div className="p-6 border-b border-white/5">
        <Link href="/dashboard" className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-cyan-400 rounded-xl flex items-center justify-center">
            <Cpu className="w-6 h-6 text-white" />
          </div>
          <div>
            <span className="font-bold text-white text-sm">ECU Master Lab</span>
            <div className="text-xs text-gray-500">v2.0.0</div>
          </div>
        </Link>
      </div>

      <nav className="flex-1 p-4 space-y-6 overflow-y-auto">
        {sections.map((section) => (
          <div key={section.title}>
            <div className="px-4 mb-2 text-[10px] font-semibold uppercase tracking-widest text-white/30">
              {section.title}
            </div>
            <div className="space-y-1">
              {section.items.map((link) => (
                <Link
                  key={link.href}
                  href={link.href}
                  className={cn(
                    "flex items-center gap-3 px-4 py-3 rounded-xl text-sm transition-all",
                    pathname === link.href || (link.href !== "/dashboard" && pathname.startsWith(link.href))
                      ? "bg-blue-500/10 text-blue-400 border border-blue-500/20"
                      : "text-gray-400 hover:text-white hover:bg-white/5"
                  )}
                >
                  <link.icon className="w-5 h-5" />
                  {link.label}
                </Link>
              ))}
            </div>
          </div>
        ))}
      </nav>

      <div className="p-4 border-t border-white/5">
        <button
          onClick={logout}
          className="flex items-center gap-3 px-4 py-3 rounded-xl text-sm text-gray-400 hover:text-red-400 hover:bg-red-500/5 transition-all w-full"
        >
          <LogOut className="w-5 h-5" />
          Déconnexion
        </button>
      </div>
    </aside>
  );
}
