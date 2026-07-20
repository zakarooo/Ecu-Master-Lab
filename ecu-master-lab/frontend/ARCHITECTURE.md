# Architecture de Référence — Frontend ECU Master Lab

> Document de référence officiel. Aucune modification de code sans validation préalable de ce document.

---

## 1. Mapping api.ts → Backend

### Auth

| Fonction | Méthode | Backend Endpoint | Statut |
|----------|---------|-----------------|--------|
| `api.auth.register(data)` | POST | `/api/auth/register` | ✅ |
| `api.auth.login(data)` | POST | `/api/auth/login` | ✅ |
| `api.auth.me()` | GET | `/api/auth/me` | ✅ |
| `api.auth.updateProfile(data)` | PUT | `/api/auth/profile` | ✅ |
| `api.auth.changePassword(data)` | PUT | `/api/auth/password` | ✅ |
| `api.auth.verifyEmail(token)` | POST | `/api/auth/verify-email` | ✅ |
| `api.auth.forgotPassword(email)` | POST | `/api/auth/forgot-password` | ✅ |
| `api.auth.resetPassword(token, pw)` | POST | `/api/auth/reset-password` | ✅ |

### Projects

| Fonction | Méthode | Backend Endpoint | Statut |
|----------|---------|-----------------|--------|
| `api.projects.list()` | GET | `/api/projects` | ✅ |
| `api.projects.get(id)` | GET | `/api/projects/{id}` | ✅ |
| `api.projects.create(data)` | POST | `/api/projects` | ✅ |
| `api.projects.upload(id, file)` | POST | `/api/projects/{id}/upload` | ✅ |
| `api.projects.setModifications(id, data)` | POST | `/api/projects/{id}/modifications` | ✅ |
| `api.projects.process(id)` | POST | `/api/projects/{id}/process` | ✅ |
| `api.projects.analysis(id)` | GET | `/api/projects/{id}/analysis` | ✅ |
| `api.projects.downloadOriginal(id)` | URL string | `/api/projects/{id}/download-original` | ✅ |
| `api.projects.downloadModified(id)` | URL string | `/api/projects/{id}/download` | ✅ |
| `api.projects.downloadVersion(id, vId)` | URL string | `/api/projects/{id}/download/{versionId}` | ✅ |
| `api.projects.versions(id)` | GET | `/api/projects/{id}/versions` | ⚠️ Non appelé |

### Admin

| Fonction | Méthode | Backend Endpoint | Statut |
|----------|---------|-----------------|--------|
| `api.admin.stats()` | GET | `/api/admin/stats` | ✅ |
| `api.admin.users(params)` | GET | `/api/admin/users` | ✅ |
| `api.admin.projects(params)` | GET | `/api/admin/projects` | ✅ |
| `api.admin.updateUser(id, data)` | PUT | `/api/admin/users/{id}` | ⚠️ Non appelé |
| `api.admin.deleteUser(id)` | DELETE | `/api/admin/users/{id}` | ✅ |
| `api.admin.auditLogs(params)` | GET | `/api/admin/audit-logs` | ✅ |
| `api.admin.deleteProject(id)` | DELETE | `/api/admin/projects/{id}` | ✅ |
| `api.admin.transferProject(id, data)` | POST | `/api/admin/projects/{id}/transfer` | ✅ |

### Expert

| Fonction | Méthode | Backend Endpoint | Statut |
|----------|---------|-----------------|--------|
| `api.expert.pendingReview()` | GET | `/api/expert/projects/pending-review` | ✅ |
| `api.expert.approve(id)` | POST | `/api/expert/projects/{id}/approve` | ✅ |
| `api.expert.reject(id, data)` | POST | `/api/expert/projects/{id}/reject` | ✅ |

### V2 Referentiel

| Fonction | Méthode | Backend Endpoint | Statut |
|----------|---------|-----------------|--------|
| `api.v2.manufacturers.list(params)` | GET | `/api/v2/referentiel/manufacturers` | ✅ |
| `api.v2.manufacturers.get(id)` | GET | `/api/v2/referentiel/manufacturers/{id}` | ⚠️ Non appelé |
| `api.v2.manufacturers.create(data)` | POST | `/api/v2/referentiel/manufacturers` | ⚠️ Non appelé |
| `api.v2.ecuModels.list(params)` | GET | `/api/v2/referentiel/ecu-models` | ✅ |
| `api.v2.ecuModels.get(id)` | GET | `/api/v2/referentiel/ecu-models/{id}` | ⚠️ Non appelé |
| `api.v2.processors.list(params)` | GET | `/api/v2/referentiel/processors` | ✅ |
| `api.v2.protocols.list(params)` | GET | `/api/v2/referentiel/protocols` | ✅ |

### V2 Analysis

| Fonction | Méthode | Backend Endpoint | Statut |
|----------|---------|-----------------|--------|
| `api.v2.ecuFiles.list(params)` | GET | `/api/v2/analysis/ecu-files` | ❌ **404** — backend: `/files` |
| `api.v2.ecuFiles.get(id)` | GET | `/api/v2/analysis/ecu-files/{id}` | ❌ **404** |
| `api.v2.analyses.list(params)` | GET | `/api/v2/analysis/analyses` | ✅ |
| `api.v2.analyses.get(id)` | GET | `/api/v2/analysis/analyses/{id}` | ✅ |
| `api.v2.analyses.run(fileId)` | POST | `/api/v2/analysis/analyses/{id}/run` | ✅ |
| `api.v2.upload(file)` | POST | `/api/v2/analysis/upload` | ⚠️ Non appelé |

### V2 Vehicles

| Fonction | Méthode | Backend Endpoint | Statut |
|----------|---------|-----------------|--------|
| `api.v2.vehicleBrands.list(params)` | GET | `/api/v2/vehicles/vehicle-brands` | ❌ **404** — backend: `/brands` |
| `api.v2.vehicleModels.list(params)` | GET | `/api/v2/vehicles/vehicle-models` | ❌ **404** — backend: `/models` |

### V2 Memory

| Fonction | Méthode | Backend Endpoint | Statut |
|----------|---------|-----------------|--------|
| `api.v2.memoryLayouts.list(params)` | GET | `/api/v2/memory/memory-layouts` | ❌ **404** — backend: `/layouts` |

### V2 Signatures

| Fonction | Méthode | Backend Endpoint | Statut |
|----------|---------|-----------------|--------|
| `api.v2.ecuSignatures.list(params)` | GET | `/api/v2/signatures/ecu-signatures` | ✅ |

### V2 Maps

| Fonction | Méthode | Backend Endpoint | Statut |
|----------|---------|-----------------|--------|
| `api.v2.mapCategories.list(params)` | GET | `/api/v2/maps/map-categories` | ❌ **404** — backend: `/categories` |
| `api.v2.mapUnits.list(params)` | GET | `/api/v2/maps/map-units` | ❌ **404** — backend: `/units` |
| `api.v2.maps.list(params)` | GET | `/api/v2/maps/maps` | ❌ **404** — backend: `/maps` |

---

## 2. Statut des Pages

| Page | Route | Statut | Détail |
|------|-------|--------|--------|
| Landing | `/` | ✅ | Aucun appel API |
| Login | `/login` | ✅ | |
| Register | `/register` | ✅ | |
| Verify Email | `/verify-email` | ✅ | |
| Forgot Password | `/forgot-password` | ✅ | |
| Reset Password | `/reset-password` | ✅ | |
| Dashboard | `/dashboard` | ✅ | |
| Profile | `/profile` | ✅ | |
| Admin | `/admin` | ✅ | |
| Expert | `/expert` | ✅ | |
| Intelligence | `/intelligence` | ⚠️ | Bypass api.ts, raw fetch, fallback URL hardcodée |
| New Project | `/projects/new` | ✅ | |
| Project Detail | `/projects/[id]` | ✅ | Download via raw fetch |
| Analysis List | `/analysis` | ❌ | ecuFiles.list → 404 |
| Analysis Upload | `/analysis/upload` | ⚠️ | Stub redirect vers /projects/new |
| Analysis Detail | `/analysis/[id]` | ⚅ | Données plates (pas de full analysis) |
| Reference Home | `/reference` | ❌ | 5 counts à 0 (URLs cassées) |
| Reference [type] | `/reference/[type]` | ❌ | 4 types cassés |
| Reference Manufacturers | `/reference/manufacturers` | ✅ | |
| Reference ECU Models | `/reference/ecu-models` | ✅ | |
| Reference Processors | `/reference/processors` | ✅ | |
| Reference Signatures | `/reference/signatures` | ✅ | |

---

## 3. URLs Cassées (8)

| Ligne api.ts | Frontend URL | Backend URL | Fix |
|-------------|-------------|-------------|-----|
| 98 | `/api/v2/analysis/ecu-files` | `/api/v2/analysis/files` | `ecu-files` → `files` |
| 99 | `/api/v2/analysis/ecu-files/{id}` | `/api/v2/analysis/files/{id}` | `ecu-files` → `files` |
| 113 | `/api/v2/vehicles/vehicle-brands` | `/api/v2/vehicles/brands` | `vehicle-brands` → `brands` |
| 116 | `/api/v2/vehicles/vehicle-models` | `/api/v2/vehicles/models` | `vehicle-models` → `models` |
| 119 | `/api/v2/memory/memory-layouts` | `/api/v2/memory/layouts` | `memory-layouts` → `layouts` |
| 125 | `/api/v2/maps/map-categories` | `/api/v2/maps/categories` | `map-categories` → `categories` |
| 128 | `/api/v2/maps/map-units` | `/api/v2/maps/units` | `map-units` → `units` |
| 131 | `/api/v2/maps/maps` | `/api/v2/maps` | `maps/maps` → `maps` |

**Corrigées en Phase 4.**

---

## 4. Middleware & Auth

### Routes protégées (nécessitent cookie `session`)

- `/dashboard/*`, `/projects/*`, `/admin/*`, `/expert/*`, `/reference/*`, `/intelligence/*`, `/analysis/*`, `/profile/*`

### Routes auth (redirigent vers /dashboard si cookie présent)

- `/login`, `/register`, `/forgot-password`, `/reset-password`, `/verify-email`

### Double mechanisme auth

1. **Middleware** : Vérifie la présence du cookie `session` (pas de validation JWT)
2. **api.ts** : Envoie `Authorization: Bearer <token>` depuis `localStorage.token`

### Rôle dans le frontend

- Stocké dans `localStorage.user` (objet JSON avec `role`)
- Lu par `Sidebar.tsx` pour afficher/masquer des liens
- **Pas de protection middleware** — un client peut accéder à `/admin` (le backend rejette avec 403)

---

## 5. Composants

| Composant | Fichier | Utilisé par |
|-----------|---------|------------|
| `Navbar` | `components/layout/Navbar.tsx` | Landing, pages auth |
| `Footer` | `components/layout/Footer.tsx` | Landing |
| `Sidebar` | `components/layout/Sidebar.tsx` | Toutes les pages dashboard |

---

## 6. Dépendances

### Runtime
- `next` 14.1.0, `react` ^18, `react-dom` ^18
- `clsx` ^2.1.0, `tailwind-merge` ^2.2.0
- `lucide-react` ^0.303.0

### Dev
- `@playwright/test` ^1.61.1
- `typescript` ^5, `tailwindcss` ^3.3.0
- `postcss` ^8, `autoprefixer` ^10.0.1
