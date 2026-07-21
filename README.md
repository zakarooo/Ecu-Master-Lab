# ECU Master Lab

Plateforme SaaS d'analyse et de modification de fichiers ECU pour Calculateurs Electroniques Automobiles.

## Description

ECU Master Lab combine une intelligence artificielle spécialisée pour l'analyse de fichiers ECU (binaires, HEX, ORI, FRF) avec un workflow complet de calibration automobile. La plateforme identifie automatiquement le processeur, la mémoire, les maps de calibration, et génère des rapports d'analyse détaillés.

## Fonctionnalites

- **Analyse ECU** : Identification automatique du calculateur, detection des zones memoire, maps, checksums
- **Intelligence Artificielle** : Moteur Mistral pour l'analyse et la prédiction de fichiers ECU
- **Modification de fichiers** : Application de modifications (performance, economie, fonctions) avec verification d'integrité
- **Referentiel** : Base de donnees de fabricants, modeles ECU, processeurs, signatures
- **Workflow Expert** : Validation d'experts avant traitement, notifications
- **Administration** : Gestion des utilisateurs, projets, journaux d'audit

## Stack technique

| Composant | Technologie |
|-----------|-------------|
| Frontend | Next.js 14, React 18, TypeScript, Tailwind CSS |
| Backend | Python 3.11, FastAPI, SQLAlchemy, Alembic |
| Base de donnees | PostgreSQL (Neon Serverless) |
| IA | Mistral AI (mistral-small-latest) |
| Deploiement | Vercel (frontend), Railway (backend) |
| Tests | Playwright (E2E) |

## Architecture

```
ecu-master-lab/
├── backend/                    # API FastAPI
│   ├── app/
│   │   ├── core/              # Config, securite, JWT
│   │   ├── models/            # Modeles SQLAlchemy
│   │   ├── routes/            # Endpoints API
│   │   │   ├── v2/            # Routes V2 (referentiel, analysis, vehicles, memory, maps)
│   │   │   └── v3/            # Routes V3 (modification de fichiers)
│   │   ├── services/          # Logique metier
│   │   ├── ecu_engine/        # Moteur d'analyse ECU (10 couches)
│   │   └── agents/            # Agents IA
│   ├── alembic/               # Migrations DB
│   └── tests/                 # Tests backend
├── frontend/                  # Application Next.js
│   ├── src/
│   │   ├── app/               # Pages (App Router)
│   │   │   ├── (auth)/        # Login, register, forgot-password
│   │   │   └── (dashboard)/   # Dashboard, projects, analysis, reference, intelligence, profile
│   │   ├── components/        # Composants React
│   │   └── lib/               # Utilitaires, API client
│   └── e2e/                   # Tests E2E Playwright
└── uploads/                   # Fichiers ECU uploades
```

## Installation

### Pre-requis

- Python 3.11+
- Node.js 20+
- PostgreSQL (ou compte Neon)

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configurer l'environnement
cp .env.example .env
# Editer .env avec vos valeurs

# Migrations
alembic upgrade head

# Demarrer
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install

# Configurer l'environnement
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Demarrer
npm run dev
```

## Tests

### Tests E2E (Playwright)

```bash
cd frontend
npx playwright install
npx playwright test e2e/ --reporter=list
```

Les tests tournent contre les environnements de production :
- Frontend : `https://frontend-beige-rho-83.vercel.app`
- Backend : `https://ecu-backend-production.up.railway.app`

## API Endpoints

### Authentification
| Methode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/api/auth/register` | Inscription |
| POST | `/api/auth/login` | Connexion |
| GET | `/api/auth/me` | Profil utilisateur |
| PUT | `/api/auth/profile` | Modifier le profil |
| PUT | `/api/auth/password` | Changer le mot de passe |

### Projets
| Methode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/projects` | Lister les projets |
| POST | `/api/projects` | Creer un projet |
| POST | `/api/projects/{id}/upload` | Upload fichier ECU |
| POST | `/api/projects/{id}/process` | Traiter le projet |
| GET | `/api/projects/{id}/download` | Telecharger le fichier modifie |

### V2 Referentiel
| Methode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/v2/referentiel/manufacturers` | Fabricants |
| GET | `/api/v2/referentiel/ecu-models` | Modeles ECU |
| GET | `/api/v2/referentiel/processors` | Processeurs |
| GET | `/api/v2/signatures/ecu-signatures` | Signatures |

### Administration
| Methode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/admin/stats` | Statistiques |
| GET | `/api/admin/users` | Gestion utilisateurs |
| DELETE | `/api/admin/projects/{id}` | Supprimer un projet |

## Roles utilisateurs

| Role | Permissions |
|------|-------------|
| `client` | Creer des projets, upload des fichiers, telecharger les resultats |
| `expert` | Valider/Rejeter les projets, acceder au referentiel avance |
| `admin` | Gestion complete : utilisateurs, projets, audit |

## Environnement

| Variable | Description | Defaut |
|----------|-------------|--------|
| `SECRET_KEY` | Cle secrete JWT | Generee automatiquement |
| `DATABASE_URL` | URL PostgreSQL | localhost |
| `CORS_ORIGINS` | Origines autorisees | localhost:3000 |
| `MISTRAL_API_KEY` | Cle API Mistral AI | — |
| `DEBUG` | Mode debug | false |

## Licence

MIT — Voir [LICENSE](LICENSE)

## Contact

- Depot GitHub : [zakarooo/Ecu-Master-Lab](https://github.com/zakarooo/Ecu-Master-Lab)
