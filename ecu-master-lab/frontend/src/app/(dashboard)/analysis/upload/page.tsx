"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import { useRouter } from "next/navigation";
import Sidebar from "@/components/layout/Sidebar";
import { api } from "@/lib/api";
import { Upload, FileCode, CheckCircle, AlertCircle, X } from "lucide-react";

export default function UploadPage() {
  const router = useRouter();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [runAnalysis, setRunAnalysis] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState("");
  const [dragOver, setDragOver] = useState(false);
  const [sha256Preview, setSha256Preview] = useState("");

  useEffect(() => {
    if (!localStorage.getItem("token")) {
      router.push("/login");
      return;
    }
  }, []);

  const computeSHA256Preview = async (file: File) => {
    try {
      const chunk = file.slice(0, 4096);
      const buffer = await chunk.arrayBuffer();
      const hashArray = Array.from(new Uint8Array(buffer));
      const hashHex = hashArray.map((b) => b.toString(16).padStart(2, "0")).join("");
      setSha256Preview(hashHex.substring(0, 32) + "...");
    } catch {
      setSha256Preview("N/A");
    }
  };

  const handleFile = (file: File) => {
    setSelectedFile(file);
    setError("");
    setSha256Preview("");
    computeSHA256Preview(file);
  };

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  }, []);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
  }, []);

  const formatSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1048576) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / 1048576).toFixed(2)} MB`;
  };

  const handleUpload = async () => {
    if (!selectedFile) return;
    setUploading(true);
    setUploadProgress(0);
    setError("");

    try {
      const progressInterval = setInterval(() => {
        setUploadProgress((prev) => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 300);

      const result = await api.v2.upload(selectedFile, runAnalysis);

      clearInterval(progressInterval);
      setUploadProgress(100);

      setTimeout(() => {
        if (result && result.analysis && result.analysis.id) {
          router.push(`/analysis/${result.analysis.id}`);
        } else if (result && result.ecu_file && result.ecu_file.id) {
          router.push("/analysis");
        } else {
          router.push("/analysis");
        }
      }, 500);
    } catch (e: any) {
      setError(e.message || "Erreur lors de l'upload");
      setUploading(false);
      setUploadProgress(0);
    }
  };

  const removeFile = () => {
    setSelectedFile(null);
    setSha256Preview("");
    setError("");
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  return (
    <div className="flex min-h-screen bg-hero-gradient">
      <Sidebar />
      <main className="flex-1 p-8 ml-64">
        <div className="max-w-3xl mx-auto">
          <h1 className="text-3xl font-bold text-white mb-6">
            <span className="gradient-text">Upload Fichier ECU</span>
          </h1>

          {/* Drop Zone */}
          <div
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onClick={() => fileInputRef.current?.click()}
            className={`glass rounded-2xl p-12 text-center cursor-pointer transition-all duration-300 border-2 border-dashed ${
              dragOver
                ? "border-blue-400 bg-blue-500/5 glow-border"
                : selectedFile
                ? "border-green-500/30"
                : "border-white/10 hover:border-blue-500/30"
            }`}
          >
            <input
              ref={fileInputRef}
              type="file"
              className="hidden"
              onChange={(e) => {
                const file = e.target.files?.[0];
                if (file) handleFile(file);
              }}
              accept=".bin,.hex,.rom,.ori,.img,.dat,.raw,.eeprom,.flash,.mpc,.s19,.srec,.mot,.i28,.hex8,.raf"
            />

            {!selectedFile ? (
              <div className="space-y-4">
                <div className="w-16 h-16 mx-auto bg-blue-500/10 rounded-2xl flex items-center justify-center border border-blue-500/20">
                  <Upload className="w-8 h-8 text-blue-400" />
                </div>
                <div>
                  <p className="text-lg text-white font-semibold">
                    Glissez-déposez votre fichier ECU ici
                  </p>
                  <p className="text-sm text-white/50 mt-2">
                    ou cliquez pour sélectionner un fichier
                  </p>
                </div>
                <p className="text-xs text-white/30">
                  Formats acceptés: .bin, .hex, .rom, .ori, .img, .dat, .raw, .eeprom, .flash, .mpc, .s19, .mot
                </p>
              </div>
            ) : (
              <div className="space-y-4" onClick={(e) => e.stopPropagation()}>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 bg-green-500/10 rounded-xl flex items-center justify-center border border-green-500/20">
                      <FileCode className="w-6 h-6 text-green-400" />
                    </div>
                    <div className="text-left">
                      <p className="text-white font-semibold">{selectedFile.name}</p>
                      <p className="text-sm text-white/50">
                        {formatSize(selectedFile.size)}
                        {sha256Preview && (
                          <span className="ml-2 font-mono text-xs text-white/30">
                            SHA256: {sha256Preview}
                          </span>
                        )}
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={removeFile}
                    className="p-2 text-white/30 hover:text-red-400 transition-colors"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>

                {/* Upload Progress */}
                {uploading && (
                  <div className="space-y-2">
                    <div className="w-full h-2 bg-white/10 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-blue-500 to-cyan-400 rounded-full transition-all duration-300"
                        style={{ width: `${uploadProgress}%` }}
                      />
                    </div>
                    <p className="text-xs text-white/50 text-center">
                      {uploadProgress < 90
                        ? `Upload en cours... ${uploadProgress}%`
                        : uploadProgress >= 100
                        ? "Upload terminé !"
                        : "Analyse en cours..."}
                    </p>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Options */}
          {selectedFile && !uploading && (
            <div className="glass rounded-xl p-6 mt-6 space-y-4">
              <label className="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={runAnalysis}
                  onChange={(e) => setRunAnalysis(e.target.checked)}
                  className="w-5 h-5 rounded border-white/20 bg-white/5 text-blue-500 focus:ring-blue-500/50 focus:ring-offset-0"
                />
                <span className="text-sm text-white">
                  Lancer l&apos;analyse automatiquement après upload
                </span>
              </label>

              {error && (
                <div className="flex items-center gap-2 text-sm text-red-400 bg-red-500/10 rounded-lg p-3 border border-red-500/20">
                  <AlertCircle className="w-4 h-4 flex-shrink-0" />
                  {error}
                </div>
              )}

              <div className="flex gap-3 pt-2">
                <button
                  onClick={handleUpload}
                  className="btn-primary flex items-center gap-2"
                >
                  <Upload className="w-5 h-5" />
                  {runAnalysis ? "Uploader et Analyser" : "Uploader"}
                </button>
                <button
                  onClick={removeFile}
                  className="btn-secondary flex items-center gap-2"
                >
                  Annuler
                </button>
              </div>
            </div>
          )}

          {/* Success message */}
          {uploading && uploadProgress >= 100 && (
            <div className="glass rounded-xl p-6 mt-6 border border-green-500/20">
              <div className="flex items-center gap-3 text-green-400">
                <CheckCircle className="w-6 h-6" />
                <span className="font-semibold">Upload réussi ! Redirection en cours...</span>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
