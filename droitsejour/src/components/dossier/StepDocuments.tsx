"use client";

import { useState, useRef, useCallback } from "react";
import { motion } from "framer-motion";
import { Upload, FileText, Trash2, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { ACCEPTED_FILE_TYPES, MAX_FILE_SIZE } from "@/lib/constants";
import { cn, generateId, formatFileSize, getTodayISO } from "@/lib/utils";
import type { Dossier, Document } from "@/types";

interface StepProps {
  dossier: Dossier;
  onUpdate: (data: Partial<Dossier>) => void;
  onNext: () => void;
  onPrev: () => void;
}

export default function StepDocuments({ dossier, onUpdate, onNext, onPrev }: StepProps) {
  const [documents, setDocuments] = useState<Document[]>(dossier.documents ?? []);
  const [isDragging, setIsDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const acceptedExtensions = Object.values(ACCEPTED_FILE_TYPES).flat().join(", ");
  const acceptedMimeTypes = Object.keys(ACCEPTED_FILE_TYPES);

  const validateFile = (file: File): string | null => {
    if (!acceptedMimeTypes.includes(file.type)) {
      return `Type de fichier non accepté : ${file.type}`;
    }
    if (file.size > MAX_FILE_SIZE) {
      return `Fichier trop volumineux : ${formatFileSize(file.size)} (max ${formatFileSize(MAX_FILE_SIZE)})`;
    }
    return null;
  };

  const processFiles = useCallback(async (files: FileList | File[]) => {
    setError(null);
    const fileArray = Array.from(files);

    for (const file of fileArray) {
      const validationError = validateFile(file);
      if (validationError) {
        setError(validationError);
        return;
      }
    }

    setUploading(true);
    const newDocuments: Document[] = [];

    for (const file of fileArray) {
      try {
        const formData = new FormData();
        formData.append("file", file);
        formData.append("dossierId", dossier.id);

        const response = await fetch("/api/upload", {
          method: "POST",
          body: formData,
        });

        if (!response.ok) throw new Error("Erreur lors de l'upload");

        const result = await response.json();

        const doc: Document = {
          id: result.id ?? generateId(),
          nom: file.name,
          type: "autre",
          chemin: result.chemin ?? `/uploads/${dossier.id}/${file.name}`,
          taille: file.size,
          mimetype: file.type,
          dateAjout: getTodayISO(),
        };
        newDocuments.push(doc);
      } catch {
        setError(`Erreur lors de l'upload de ${file.name}`);
      }
    }

    setDocuments((prev) => [...prev, ...newDocuments]);
    setUploading(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files.length > 0) {
      processFiles(e.dataTransfer.files);
    }
  }, [processFiles]);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      processFiles(e.target.files);
    }
  };

  const handleRemove = (id: string) => {
    setDocuments((prev) => prev.filter((d) => d.id !== id));
  };

  const handleSave = () => {
    onUpdate({ documents });
    onNext();
  };

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}>
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Upload className="h-5 w-5" />
            Documents
          </CardTitle>
          <CardDescription>
            Téléversez les documents pertinents pour le dossier (PDF, JPG, PNG, WebP, max 10 Mo).
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onClick={() => fileInputRef.current?.click()}
            className={cn(
              "border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors",
              isDragging ? "border-primary bg-primary/5" : "border-muted-foreground/25 hover:border-muted-foreground/50"
            )}
          >
            <Upload className="h-8 w-8 mx-auto mb-2 text-muted-foreground" />
            <p className="text-sm text-muted-foreground">
              Glissez-déposez vos fichiers ici ou cliquez pour sélectionner
            </p>
            <p className="text-xs text-muted-foreground mt-1">
              Types acceptés : {acceptedExtensions}
            </p>
            <input
              ref={fileInputRef}
              type="file"
              multiple
              accept={acceptedExtensions}
              onChange={handleFileSelect}
              className="hidden"
            />
          </div>

          {uploading && (
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <div className="h-4 w-4 animate-spin rounded-full border-2 border-primary border-t-transparent" />
              Téléversement en cours...
            </div>
          )}

          {error && (
            <div className="flex items-center gap-2 text-sm text-destructive">
              <AlertCircle className="h-4 w-4" />
              {error}
            </div>
          )}

          {documents.length > 0 && (
            <div className="space-y-2">
              {documents.map((doc) => (
                <div key={doc.id} className="flex items-center justify-between border rounded-lg p-3">
                  <div className="flex items-center gap-3">
                    <FileText className="h-5 w-5 text-muted-foreground" />
                    <div>
                      <p className="text-sm font-medium">{doc.nom}</p>
                      <p className="text-xs text-muted-foreground">
                        {formatFileSize(doc.taille)} - {doc.mimetype}
                      </p>
                    </div>
                  </div>
                  <Button variant="ghost" size="icon" onClick={() => handleRemove(doc.id)} aria-label="Supprimer le document">
                    <Trash2 className="h-4 w-4 text-destructive" />
                  </Button>
                </div>
              ))}
            </div>
          )}

          <div className="flex justify-between pt-4">
            <Button type="button" variant="outline" onClick={onPrev}>
              Précédent
            </Button>
            <Button type="button" onClick={handleSave}>
              Suivant
            </Button>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}
