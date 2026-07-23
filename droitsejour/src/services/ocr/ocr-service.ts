export interface OCRResult {
  text: string;
  confidence: number;
  language: string;
}

export async function extractTextFromImage(buffer: Buffer, mimetype: string): Promise<OCRResult> {
  console.log(`OCR processing prepared for ${mimetype}. Full OCR coming in V2.`);
  return {
    text: "[OCR] Extraction de texte non encore active. Fonctionnalité prévue pour la version 2.",
    confidence: 0,
    language: "fr",
  };
}

export async function extractTextFromPDF(_buffer: Buffer): Promise<OCRResult> {
  console.log("PDF text extraction prepared. Full extraction coming in V2.");
  return {
    text: "[PDF] Extraction de texte non encore active. Fonctionnalité prévue pour la version 2.",
    confidence: 0,
    language: "fr",
  };
}
