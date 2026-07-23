# DroitSéjour

Plateforme professionnelle d'aide aux démarches de séjour en France.

## Description

DroitSéjour est une application web conçue pour accompagner les personnes rencontrant des difficultés dans leurs démarches de séjour, de régularisation ou d'obtention de documents administratifs en France.

L'application guide l'utilisateur étape par étape afin de constituer un dossier clair, puis produit automatiquement :

- Une analyse structurée de sa situation
- Des recommandations personnalisées
- Une liste des démarches possibles
- Des modèles de courriers adaptés à son cas
- Une checklist des pièces justificatives
- Un rapport PDF professionnel récapitulatif

> **Avertissement** : Les résultats générés constituent une aide informative et ne remplacent pas un avocat ou un professionnel qualifié.

## Installation

```bash
# Cloner le projet
git clone <repository-url>
cd droitsejour

# Installer les dépendances
npm install

# Lancer en développement
npm run dev
```

L'application est accessible sur [http://localhost:3000](http://localhost:3000).

## Stack technique

| Technologie | Usage |
|-------------|-------|
| Next.js 16 (App Router) | Framework React |
| React 19 | UI Library |
| TypeScript | Typage statique |
| Tailwind CSS v4 | Styling |
| shadcn/ui | Composants UI |
| React Hook Form + Zod | Formulaires et validation |
| Framer Motion | Animations |
| Lucide Icons | Iconographie |
| jsPDF | Génération de PDF |
| Sonner | Notifications |

## Architecture

```
src/
├── app/                    # Pages et routes (Next.js App Router)
│   ├── api/               # Routes API
│   ├── dossier/           # Pages de gestion des dossiers
│   └── layout.tsx         # Layout principal
├── components/
│   ├── ui/                # Composants UI réutilisables (shadcn)
│   ├── layout/            # Header, Footer
│   ├── dossier/           # Composants du wizard
│   ├── analysis/          # Composants d'analyse
│   ├── letters/           # Composants de courriers
│   └── pdf/               # Composants PDF
├── features/
│   └── dossier/           # Schémas de validation Zod
├── services/
│   ├── ai/                # Service IA (OpenAI, Anthropic, Gemini, local)
│   ├── pdf/               # Génération de rapports PDF
│   ├── ocr/               # Architecture OCR (V2)
│   └── storage/           # Repository Pattern (JSON local)
├── hooks/                 # Hooks React personnalisés
├── types/                 # Types TypeScript
└── lib/                   # Utilitaires et constantes
```

## Fonctionnalités

### Parcours utilisateur
1. **Accueil** - Présentation de la plateforme
2. **Informations personnelles** - Nom, prénom, nationalité, adresse
3. **Situation administrative** - Statut de séjour, titre, préfecture
4. **Situation familiale** - Conjoint, enfants, famille en France
5. **Historique des démarches** - Démarches précédentes
6. **Documents** - Téléversement de fichiers (PDF, images)
7. **Mémo** - Notes libres
8. **Analyse IA** - Analyse automatisée du dossier
9. **Recommandations** - Démarches et ordre d'actions
10. **Courriers** - Génération de courriers administratifs
11. **Checklist** - Liste des pièces justificatives
12. **Rapport PDF** - Téléchargement du rapport

### Stockage (V1)
- Toutes les données sont stockées localement en JSON
- Aucune base de données requise
- Architecture Repository Pattern prête pour PostgreSQL, Supabase, Firebase

### IA
- Fonctionne sans clé API (analyse locale de base)
- Supporte OpenAI, Anthropic Claude, et Google Gemini
- Configuration via variables d'environnement

## Configuration IA

Copier `.env.example` en `.env` :

```bash
# Mode local (par défaut, sans clé API)
AI_PROVIDER=local

# OpenAI
AI_PROVIDER=openai
AI_API_KEY=sk-...

# Anthropic
AI_PROVIDER=anthropic
AI_API_KEY=sk-ant-...

# Gemini
AI_PROVIDER=gemini
AI_API_KEY=...
```

## Commandes

| Commande | Description |
|----------|-------------|
| `npm install` | Installer les dépendances |
| `npm run dev` | Lancer en développement |
| `npm run build` | Build de production |
| `npm start` | Lancer en production |
| `npm run lint` | Vérifier le code |

## Évolutions futures

- [ ] Authentification utilisateur
- [ ] OCR complet (Tesseract.js)
- [ ] Moteur RAG avec sources officielles
- [ ] Base PostgreSQL / Supabase
- [ ] Stockage cloud (S3, Azure Blob, Google Drive)
- [ ] Paiement Stripe
- [ ] Tableau de bord administrateur
- [ ] Notifications
- [ ] Messagerie sécurisée
- [ ] Signature électronique
- [ ] API REST / GraphQL
- [ ] Application mobile / PWA

## Sécurité

- Validation stricte des données (Zod)
- Sanitisation des entrées
- Stockage local uniquement (V1)
- Aucune donnée transmise à des tiers
- Architecture prête pour chiffrement et authentification

## Licence

Ce projet est destiné à un usage personnel et à des fins d'aide administrative. Il ne constitue pas un conseil juridique.
