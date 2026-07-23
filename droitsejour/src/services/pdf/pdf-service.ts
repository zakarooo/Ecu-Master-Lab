import jsPDF from "jspdf";
import { Dossier } from "@/types";
import { formatDate } from "@/lib/utils";

function addHeader(doc: jsPDF, title: string): void {
  doc.setFontSize(10);
  doc.setTextColor(100, 100, 100);
  doc.text("DroitSéjour - Aide aux démarches de séjour", 15, 10);
  doc.text(`Généré le ${formatDate(new Date())}`, 195, 10, { align: "right" });
  doc.setDrawColor(0, 51, 153);
  doc.setLineWidth(0.5);
  doc.line(15, 14, 195, 14);
  doc.setFontSize(16);
  doc.setTextColor(0, 51, 153);
  doc.text(title, 105, 25, { align: "center" });
}

function addSectionTitle(doc: jsPDF, title: string, y: number): number {
  doc.setFontSize(13);
  doc.setTextColor(0, 51, 153);
  doc.text(title, 15, y);
  doc.setDrawColor(0, 51, 153);
  doc.setLineWidth(0.3);
  doc.line(15, y + 2, 195, y + 2);
  return y + 8;
}

function addText(doc: jsPDF, text: string, x: number, y: number, maxWidth: number = 170): number {
  doc.setFontSize(10);
  doc.setTextColor(40, 40, 40);
  const lines = doc.splitTextToSize(text, maxWidth);
  doc.text(lines, x, y);
  return y + lines.length * 5;
}

function addBulletList(doc: jsPDF, items: string[], x: number, y: number): number {
  doc.setFontSize(10);
  doc.setTextColor(40, 40, 40);
  items.forEach((item) => {
    if (y > 270) {
      doc.addPage();
      y = 20;
    }
    doc.text(`• ${item}`, x, y);
    const lines = doc.splitTextToSize(item, 160);
    y += lines.length * 5;
  });
  return y;
}

export function generateReportPDF(dossier: Dossier): jsPDF {
  const doc = new jsPDF();
  const info = dossier.informationsPersonnelles;
  const admin = dossier.situationAdministrative;
  const analyse = dossier.analyse;

  // === PAGE DE COUVERTURE ===
  doc.setFillColor(0, 51, 153);
  doc.rect(0, 0, 210, 297, "F");

  doc.setTextColor(255, 255, 255);
  doc.setFontSize(32);
  doc.text("RAPPORT D'ANALYSE", 105, 80, { align: "center" });
  doc.setFontSize(24);
  doc.text("DE SÉJOUR", 105, 95, { align: "center" });

  doc.setFontSize(14);
  doc.text("DroitSéjour - Plateforme d'aide aux démarches", 105, 115, { align: "center" });

  doc.setDrawColor(255, 255, 255);
  doc.setLineWidth(0.5);
  doc.line(60, 125, 150, 125);

  doc.setFontSize(12);
  doc.text(`${info?.prenom || ""} ${info?.nom || ""}`, 105, 140, { align: "center" });
  doc.text(`Nationalité: ${info?.nationalite || "N/A"}`, 105, 150, { align: "center" });
  doc.text(`Dossier: ${admin?.numeroDossier || "N/A"}`, 105, 160, { align: "center" });

  doc.setFontSize(10);
  doc.text(`Date de génération: ${formatDate(new Date())}`, 105, 200, { align: "center" });

  doc.setFontSize(8);
  doc.setTextColor(200, 200, 200);
  doc.text(
    "Ce rapport est généré à titre informatif. Il ne constitue pas un avis juridique.",
    105,
    240,
    { align: "center" }
  );
  doc.text(
    "Il est recommandé de consulter un avocat ou un professionnel qualifié.",
    105,
    248,
    { align: "center" }
  );

  // === PAGE RÉSUMÉ ===
  doc.addPage();
  addHeader(doc, "Résumé du dossier");
  let y = 35;

  y = addSectionTitle(doc, "Informations personnelles", y);
  y = addText(doc, `Nom: ${info?.prenom} ${info?.nom}`, 15, y);
  y = addText(doc, `Né(e) le: ${info?.dateNaissance} à ${info?.lieuNaissance}`, 15, y);
  y = addText(doc, `Nationalité: ${info?.nationalite}`, 15, y);
  y = addText(doc, `Adresse: ${info?.adresse}, ${info?.codePostal} ${info?.ville}`, 15, y);
  y = addText(doc, `Situation familiale: ${info?.situationFamiliale}`, 15, y);
  y += 5;

  y = addSectionTitle(doc, "Situation administrative", y);
  y = addText(doc, `Statut de séjour: ${admin?.statutSejour}`, 15, y);
  y = addText(doc, `Type de titre: ${admin?.typeTitre || "N/A"}`, 15, y);
  y = addText(doc, `Préfecture: ${admin?.prefecture || "N/A"}`, 15, y);
  y = addText(doc, `Date d'entrée: ${admin?.dateEntree || "N/A"}`, 15, y);
  y = addText(doc, `Expiration: ${admin?.dateExpiration || "N/A"}`, 15, y);
  y += 5;

  // === ANALYSE ===
  if (analyse) {
    doc.addPage();
    addHeader(doc, "Analyse de la situation");
    y = 35;

    y = addSectionTitle(doc, "Résumé", y);
    y = addText(doc, analyse.resume, 15, y);
    y += 5;

    if (analyse.forces.length) {
      y = addSectionTitle(doc, "Forces du dossier", y);
      y = addBulletList(doc, analyse.forces, 15, y);
      y += 3;
    }

    if (analyse.faiblesses.length) {
      y = addSectionTitle(doc, "Faiblesses du dossier", y);
      y = addBulletList(doc, analyse.faiblesses, 15, y);
      y += 3;
    }

    if (analyse.risques.length) {
      y = addSectionTitle(doc, "Risques identifiés", y);
      y = addBulletList(doc, analyse.risques, 15, y);
      y += 3;
    }

    if (analyse.documentsManquants.length) {
      y = addSectionTitle(doc, "Documents manquants", y);
      y = addBulletList(doc, analyse.documentsManquants, 15, y);
      y += 3;
    }

    if (analyse.argumentsFavorables.length) {
      y = addSectionTitle(doc, "Arguments favorables", y);
      y = addBulletList(doc, analyse.argumentsFavorables, 15, y);
      y += 3;
    }

    // === RECOMMANDATIONS ===
    doc.addPage();
    addHeader(doc, "Recommandations");
    y = 35;

    if (analyse.demarchesRecommandees.length) {
      y = addSectionTitle(doc, "Démarches recommandées", y);
      analyse.demarchesRecommandees.forEach((d) => {
        if (y > 260) { doc.addPage(); y = 20; }
        doc.setFontSize(11);
        doc.setTextColor(0, 51, 153);
        doc.text(`[${d.priorite.toUpperCase()}] ${d.titre}`, 15, y);
        y += 5;
        y = addText(doc, d.description, 20, y, 165);
        if (d.delai) y = addText(doc, `Délai conseillé: ${d.delai}`, 20, y, 165);
        y += 4;
      });
    }

    if (analyse.ordreActions.length) {
      y += 3;
      if (y > 250) { doc.addPage(); y = 20; }
      y = addSectionTitle(doc, "Ordre conseillé des actions", y);
      analyse.ordreActions.forEach((a, i) => {
        if (y > 270) { doc.addPage(); y = 20; }
        y = addText(doc, `${i + 1}. ${a}`, 15, y);
      });
    }

    // === ADMINISTRATIONS ===
    doc.addPage();
    addHeader(doc, "Administrations concernées");
    y = 35;
    y = addBulletList(doc, analyse.administrationsConcernees, 15, y);
  }

  // === CHECKLIST ===
  doc.addPage();
  addHeader(doc, "Checklist des pièces justificatives");
  y = 35;
  dossier.checklist.forEach((item) => {
    if (y > 270) { doc.addPage(); y = 20; }
    const check = item.coche ? "✓" : "☐";
    doc.setFontSize(10);
    doc.setTextColor(40, 40, 40);
    doc.text(`${check} ${item.document}${item.obligatoire ? " (obligatoire)" : ""}`, 15, y);
    y += 5;
    y = addText(doc, item.description, 25, y, 160);
    y += 2;
  });

  // === COURRIERS ===
  if (dossier.courriers.length) {
    dossier.courriers.forEach((courrier) => {
      doc.addPage();
      addHeader(doc, `Courrier: ${courrier.titre}`);
      y = 35;
      y = addText(doc, courrier.contenu, 15, y);
    });
  }

  // === MENTIONS LÉGALES ===
  doc.addPage();
  addHeader(doc, "Mentions légales");
  y = 35;
  const mentions = [
    "Ce document est généré automatiquement par la plateforme DroitSéjour.",
    "Il constitue une aide informative et ne remplace en aucun cas les conseils d'un avocat ou d'un professionnel qualifié du droit des étrangers.",
    "Les informations contenues dans ce rapport sont basées sur les données fournies par l'utilisateur et sur l'analyse automatisée.",
    "L'exactitude des informations ne peut être garantie. Il est recommandé de vérifier toutes les données avec un professionnel.",
    "Ce rapport ne constitue pas un acte juridique et ne saurait engager la responsabilité de la plateforme DroitSéjour.",
    "Les délais et procédures mentionnés sont indicatifs et peuvent varier selon les préfectures et les périodes.",
    "Pour toute question juridique, veuillez consulter un avocat spécialisé en droit des étrangers.",
    "",
    `Rapport généré le ${formatDate(new Date())}`,
    `Identifiant du dossier: ${dossier.id}`,
  ];
  y = addBulletList(doc, mentions, 15, y);

  return doc;
}

export function downloadPDF(doc: jsPDF, filename: string): void {
  doc.save(filename);
}
