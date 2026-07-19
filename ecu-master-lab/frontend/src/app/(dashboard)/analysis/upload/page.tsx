"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { Loader2 } from "lucide-react";

export default function UploadPage() {
  const router = useRouter();

  useEffect(() => {
    router.replace("/projects/new");
  }, [router]);

  return (
    <div className="flex min-h-screen bg-hero-gradient items-center justify-center">
      <div className="text-center">
        <Loader2 className="w-8 h-8 text-blue-400 animate-spin mx-auto mb-4" />
        <p className="text-gray-400">Redirection vers Nouveau Projet...</p>
      </div>
    </div>
  );
}
