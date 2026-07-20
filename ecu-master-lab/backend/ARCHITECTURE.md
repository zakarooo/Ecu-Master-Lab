# Architecture de Référence — Backend ECU Master Lab

> Document de référence officiel. Aucune modification de code sans validation préalable de ce document.

---

## 1. Workflow Métier Officiel (UNIQUE)

Le parcours bout-en-bout est unique. Il n'existe aucun workflow parallèle capable de produire le résultat final (fichier MOD téléchargeable attaché à un projet).

### Étapes

| Étape | Frontend | Backend Endpoint | Rôle |
|-------|----------|-----------------|------|
| 1. Inscription/Connexion | `/register`, `/login` | `POST /api/auth/register`, `POST /api/auth/login` | PUBLIC |
| 2. Création projet | `/projects/new` (wizard 3 étapes) | `POST /api/projects` | CLIENT+ |
| 3. Upload fichier ECU | `/projects/[id]` (drag-drop) | `POST /api/projects/{id}/upload` | CLIENT+ |
| 4. Analyse automatique | Déclenchée par l'upload | `analyze_ecu_file()` (engine 10 couches) | INTERNE |
| 5. Sélection modifications | `/projects/[id]` (boutons mods) | `POST /api/projects/{id}/modifications` | CLIENT+ |
| 6. Processing | `/projects/[id]` (bouton traitement) | `POST /api/projects/{id}/process` | CLIENT+ |
| 7. Download | `/projects/[id]` (boutons download) | `GET /api/projects/{id}/download`, `GET /api/projects/{id}/download-original` | CLIENT+ |

### Endpoints parallèles NON connectés au workflow

| Endpoint | Pourquoi il existe | Pourquoi ce n'est PAS le workflow |
|----------|-------------------|-----------------------------------|
| `POST /api/v2/analysis/upload` | Upload standalone pour KB | Pas lié au state machine projet, pas de download possible |
| `POST /api/v3/modification/write-map` | Édition bas-niveau de maps | Utility technique, pas de sélection de mods nommées |
| `POST /api/ecu/analyze` | Analyse via intelligence | Même moteur, stockage différent, pas de workflow |

---

## 2. Matrice des Composants

### Légende

| Classification | Définition |
|---------------|-----------|
| **WP** | Workflow Principal — utilisé par le frontend |
| **SI** | Service Interne — logique métier réutilisée |
| **AT** | API Technique — exposé mais non utilisé par le frontend |
| **OBS** | Obsolète — remplacé, toujours monté |
| **SUP** | À Supprimer — code mort |

### Routes Backend

| Composant | Fichier | Classification |
|-----------|---------|---------------|
| Auth (register, login, me, profile, password, verify, forgot, reset) | `routes/auth.py` | WP |
| Projects (CRUD, upload, modifications, process, download, analysis, versions) | `routes/projects.py` | WP |
| Admin (stats, users, projects, audit-logs, delete, transfer) | `routes/admin.py` | WP |
| Expert (pending-review, approve, reject) | `routes/expert.py` | WP |
| V2 Referentiel (manufacturers, ecu-models, processors, protocols) | `routes/v2/referentiel.py` | WP (read) + AT (write) |
| V2 Vehicles (brands, models, engines) | `routes/v2/vehicles.py` | AT |
| V2 Versions (software, hardware) | `routes/v2/versions.py` | AT |
| V2 Memory (layouts, segments) | `routes/v2/memory.py` | WP (layouts read) + AT |
| V2 Signatures (ecu-signatures, binary-patterns) | `routes/v2/signatures.py` | WP (read) + AT |
| V2 Maps (categories, units, axes, maps) | `routes/v2/maps.py` | WP (read) + AT |
| V2 Analysis (upload, files, analyses, run) | `routes/v2/analysis.py` | WP (upload, analyses, run) + AT (files/{id}, full, sub-results) |
| V2 AI (models, predictions, datasets, heuristics) | `routes/v2/ai.py` | AT |
| V2 Reports | `routes/v2/reports.py` | AT |
| V2 Activity | `routes/v2/activity.py` | AT |
| V2 Knowledge (stats, register, known-files, signatures, strings, corrections) | `routes/v2/knowledge.py` | WP (stats via intelligence) + AT |
| V2 Intelligence (ecu/identify, ecu/analyze, knowledge/*) | `routes/v2/intelligence.py` | WP (analyze, list, search, statistics, quality) + AT |
| V3 Modification (read-map, write-map, read-value, convert, checksum, conversions) | `routes/v3/modification.py` | AT |
| V2 Modification (**MORT** — jamais importé) | `routes/v2/modification.py` | **SUP** |

### Services

| Composant | Fichier | Classification |
|-----------|---------|---------------|
| file_service (save_uploaded_file, save_version, get_file_info) | `services/file_service.py` | SI |
| ecu_services (30+ services CRUD) | `services/v2/ecu_services.py` | SI |
| Repositories (30+ repositories) | `repositories/v2/ecu_repositories.py` | SI |
| user_repository, project_repository, etc. | `repositories/*.py` | SI |

### ECU Engine

| Composant | Fichier | Classification |
|-----------|---------|---------------|
| engine.py (orchestrateur 10 couches) | `ecu_engine/engine.py` | SI |
| format_detector, processor_identifier, memory_identifier, info_extractor, signature_scanner, segment_analyzer, map_detector, checksum_engine, cross_validator, report_generator | `ecu_engine/*.py` | SI |
| models.py (dataclasses), utils.py, scoring.py | `ecu_engine/models.py`, `utils.py`, `scoring.py` | SI |
| checksum_recalc, map_value_reader, map_value_writer, unit_converter | `ecu_engine/checksum_recalc.py`, etc. | SI |
| ecu_analyst, ecu_matcher, semantic_search, map_normalizer, damos_quality_report, knowledge_extractor | `ecu_engine/ecu_analyst.py`, etc. | SI |
| a2l_parser | `ecu_engine/a2l_parser.py` | AT |
| llm_enhancer (import cassé) | `ecu_engine/llm_enhancer.py` | OBS |
| telegram_notifier | `ecu_engine/telegram_notifier.py` | AT |

### Core

| Composant | Fichier | Classification |
|-----------|---------|---------------|
| settings | `core/config.py` | WP |
| engine, SessionLocal, Base | `core/database.py` | WP |
| get_current_user, require_admin, require_expert_or_admin | `core/deps.py` | WP |
| hash_password, verify_password, create_token | `core/security.py` | WP |

### Models

| Composant | Fichier | Classification |
|-----------|---------|---------------|
| User, Project, FileVersion, AuditLog, Job, Vehicle, ECU | `models/models.py` | WP |
| Pydantic schemas | `models/schemas.py` | WP |
| 40+ modèles V2 (ECUFile, Analysis, etc.) | `models/new/ecu_models.py` | SI |
| Re-exports (user.py, project.py, etc.) | `models/*.py` | OBS |
| ecu_schemas (Pydantic V2) | `schemas/ecu_schemas.py` | SI |

### Agents

| Composant | Fichier | Classification |
|-----------|---------|---------------|
| ecu_ai_engine (re-export shim 10 lignes) | `agents/ecu_ai_engine.py` | OBS |
| ecu_signatures | `agents/ecu_signatures.py` | AT |

---

## 3. DAG de Dépendances

```
core/config.py                          (leaf)
    ↑
core/database.py                        (imports: config)
    ↑
core/security.py                        (imports: config)
    ↑
models/models.py                        (imports: core/database)
models/new/ecu_models.py                (imports: core/database)
    ↑                    ↑
ecu_engine/models.py    services/repositories
(stdlib only leaf)          ↑
    ↑                       ↑
ecu_engine/utils.py      services/*
(stdlib only leaf)          ↑
    ↑                       ↑
ecu_engine/[10 layers]   routes/*
    ↑                       |
ecu_engine/engine.py       +→ agents/ecu_ai_engine.py → engine.py
    ↑                       |
ecu_engine/db_matcher.py   routes/v2/analysis.py (deferred import)
ecu_engine/knowledge_extractor.py
ecu_engine/damos_quality_report.py
    ↑
models.new.ecu_models  (consommé par ecu_engine ci-dessus)
```

**Aucune dépendance circulaire vérifiée.**

---

## 4. Flux de Fichiers

### Structure par projet

```
{UPLOAD_DIR}/{project_id}/
  original/{safe_name}              ← ORI (ecu_file_path)
  original_backup_{hash[:8]}.bin    ← Backup (ecu_original_backup)
  modified_{original_filename}      ← MOD (result_file_path)
  versions/version_1.{ext}          ← Copie ORI
  versions/version_2.{ext}          ← Copie MOD
```

### Upload (POST /api/projects/{id}/upload)

1. File validée (extension, taille ≤ 50MB)
2. ORI écrite via `file_service.save_uploaded_file()` → `{project_id}/original/{safe_name}`
3. Backup créée via `shutil.copy2()` → `{project_id}/original/original_backup_{hash[:8]}.bin`
4. SHA-256 calculé depuis les bytes en mémoire
5. DB mise à jour : `ecu_filename`, `ecu_file_path`, `ecu_file_size`, `ecu_file_hash`, `ecu_original_backup`, `status=ANALYZING`
6. Analyse engine lancée (10 couches)
7. Résultats stockés : champs `ai_*` sur Project + JSON `ai_analysis_json`
8. FileVersion v1 créée → `versions/version_1.{ext}`
9. ECUFile + Analysis V2 créés (bridge)
10. Status → `ANALYZED` ou `NEEDS_REVIEW`

### Processing (POST /api/projects/{id}/process)

1. ORI lue depuis `project.ecu_file_path`
2. Modifications appliquées (deltas ou offset direct)
3. Checksums recalculés via `recalculate_checksums()`
4. MOD écrite → `{project_id}/modified_{filename}`
5. FileVersion v2 créée → `versions/version_2.{ext}`
6. DB : `result_file_path`, `result_checksum`, `status=COMPLETED`

### Download

| Endpoint | Fichier servi | Vérification hash |
|----------|--------------|-------------------|
| `GET /{id}/download` | `result_file_path` (MOD) | SHA-256 vs `result_checksum` |
| `GET /{id}/download-original` | `ecu_original_backup` | SHA-256 vs `ecu_file_hash` |
| `GET /{id}/download/{version_id}` | `version.file_path` | SHA-256 vs `version.file_hash` |

---

## 5. Matrice Rôles

| Action | CLIENT | EXPERT | ADMIN |
|--------|--------|--------|-------|
| Register / Login | ✓ | ✓ | ✓ |
| View/Update own profile | ✓ | ✓ | ✓ |
| Create projects | ✓ | ✓ | ✓ |
| View own projects | ✓ | ✓ | ✓ |
| Upload ECU files | ✓ | ✓ | ✓ |
| Run analysis | ✓ | ✓ | ✓ |
| Select modifications | ✓ | ✓ | ✓ |
| Trigger processing | ✓ | ✓ | ✓ |
| Download results | ✓ | ✓ | ✓ |
| Review pending projects | ✗ | ✓ | ✓ |
| Approve/reject projects | ✗ | ✓ | ✓ |
| View admin dashboard | ✗ | ✗ | ✓ |
| Manage users | ✗ | ✗ | ✓ |
| Delete projects | ✗ | ✗ | ✓ |
| Create reference data | ✗ | ✗ | ✓ |
| View reference data | ✓ | ✓ | ✓ |
| Register known files (KB) | ✗ | ✓ | ✓ |
| Submit corrections | ✗ | ✓ | ✓ |
| Create AI predictions | ✗ | ✓ | ✓ |
| Create learning datasets | ✗ | ✓ | ✓ |
| Create activity logs | ✗ | ✓ | ✓ |
| Modify ECU files (V3) | ✓* | ✓* | ✓* |

\* V3 : vérification de propriété du fichier (pas seulement du projet)

---

## 6. Dettes Techniques Documentées

### INC-1 : Routes = monolithe
`projects.py` (434 lignes) cumule HTTP, file I/O, business logic, DB access, binary processing.
→ **Statut** : Fonctionnel, pas de bug. Refactoring à prévoir ultérieurement.

### INC-2 : ECU Engine accède à la DB
4 modules (`cross_validator`, `db_matcher`, `knowledge_extractor`, `damos_quality_report`) importent `ecu_models`.
→ **Statut** : Fonctionnel, acyclique. Déplacement dans un dossier dédié à prévoir.

### INC-3 : Pas de transaction wrapper
3 `db.commit()` séparés dans l'upload — échec partiel possible.
→ **Statut** : Risque de status `ANALYZING` stuck. À corriger en Phase 2bis.

### INC-4 : Pas de hash verification au download
Les download endpoints servent les fichiers sans vérifier le SHA-256.
→ **Statut** : Corrigé en Phase 2 (SEC-4).

### INC-5 : Fichiers orphelins possibles
Crash après écriture disque mais avant `db.commit()` → fichier sans référence DB.
→ **Statut** : Risque connu. Mitigation par nettoyage periodic à prévoir.
