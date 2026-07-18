# Audit Sécurité — ECU Master Lab
**Date:** 2026-07-17
**Port:** 8000 (Docker)
**Stack:** FastAPI + PostgreSQL (Neon) + SQLAlchemy 2.x

---

## CRITIQUE (bloquant avant mise en ligne)

### 1. SECRET_KEY faible en production
- **Fichier:** `.env` ligne 1
- **Problème:** `SECRET_KEY=ecu-master-lab-super-secret-key-change-in-production-2026` — clé prévisible, basée sur un mot connu
- **Risque:** Attaquant peut forger des JWT tokens et impersonner n'importe quel utilisateur/admin
- **Fix:** Générer une vraie clé aléatoire: `python -c "import secrets; print(secrets.token_urlsafe(64))"`

### 2. 63 routes V2 sans aucune authentification
- **Fichiers:** `activity.py`, `ai.py`, `maps.py`, `memory.py`, `referentiel.py`, `reports.py`, `signatures.py`, `vehicles.py`, `versions.py`
- **Problème:** 63 routes GET + 1 route POST (`/ai/heuristics/{id}/hit`) totalement publiques
- **Données exposées:** Activity logs (audit trail), AI predictions, datasets, reports, exports, heuristics
- **Risque:** Fuite d'informations sensibles — n'importe qui peut lire l'historique complet des actions utilisateur
- **Fix minimum:** Ajouter `Depends(get_current_user)` sur toutes les routes GET sauf le référentiel de base (brands, models, processors)

### 3. Route POST mutation sans auth
- **Route:** `POST /api/v2/ai/heuristics/{heuristic_id}/hit`
- **Problème:** Incrémente un compteur de heuristiques sans aucune authentification
- **Risque:** Manipulation des données de production
- **Fix:** Ajouter `Depends(get_current_user)` au minimum

### 4. Admin check inline au lieu de Depends(require_admin)
- **Fichiers:** Tous les V2 POST/PUT (15 routes)
- **Problème:** Utilisent `if current_user.role != "admin": raise HTTPException(403)` au lieu de `Depends(require_admin)`
- **Risque:** Le check s'exécute APRÈS le code du handler — potentiel d'exécution de code avant le check
- **Fix:** Remplacer par `current_user=Depends(require_admin)`

### 5. Upload fichier non sanitizé (path traversal)
- **Fichier:** `app/services/file_service.py:15` — `file_path = original_dir / filename`
- **Problème:** Le nom de fichier original est utilisé directement sans sanitization
- **Risque:** Un filename comme `../../etc/passwd` pourrait écrire en dehors du répertoire upload
- **Fix:** Utiliser `secure_filename()` de werkzeug ou sanitiser le nom

---

## ÉLEVÉ (à corriger rapidement)

### 6. Rate limiting en mémoire uniquement
- **Fichier:** `app/routes/auth.py:12` — dict `_login_attempts`
- **Problème:** Le rate limiting est en mémoire Python, reset à chaque redémarrage du container
- **Risque:** Redémarrage Docker = reset du lockout
- **Fix:** Utiliser Redis ou une table DB pour la persistance

### 7. Token expiration très longue
- **Fichier:** `app/core/config.py:15` — `ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7` (7 jours)
- **Risque:** Token volé = accès pendant 7 jours sans possibilité de révoquer
- **Fix:** Réduire à 24-48h avec refresh token

### 8. Pas de HTTPS forcé
- **Problème:** CORS autorise `http://localhost:3000`, pas de redirect HTTP→HTTPS
- **Risque:** Tokens transmis en clair sur le réseau
- **Fix:** Configurer un reverse proxy (nginx/caddy) avec TLS devant le backend

### 9. `ProjectResponse` schema reference des colonnes qui n'existent pas dans le modèle Pydantic
- **Fichier:** `app/models/schemas.py:86-109`
- **Problème:** `ProjectResponse` a `vehicle_make`, `ecu_filename`, `ai_detected_ecu` etc. mais le modèle Pydantic les a tous comme Optional avec `Config: from_attributes = True`. La réponse contiendra `null` pour toutes ces colonnes si le projet est créé sans ces champs.
- **Note:** Corrigé dans `models.py` (les colonnes existent maintenant en ORM), mais le schema retourne des champs vides à l'utilisateur

---

## MOYEN

### 10. CORS trop restreint pour production
- **Fichier:** `.env` — `CORS_ORIGINS=["http://localhost:3000"]`
- **Problème:** Uniquement localhost — le frontend ne pourra pas appeler le backend depuis un domaine distant
- **Fix:** Ajouter l'URL du frontend en production

### 11. Pas de Content-Security-Policy ni security headers
- **Problème:** Pas de headers de sécurité (CSP, X-Frame-Options, etc.)
- **Fix:** Ajouter middleware de sécurité

### 12. Logs d'audit dans la table `audit_logs` sans protection
- **Problème:** Les logs d'audit contiennent `user_id`, `action`, `ip_address` — mais les routes V2 les exposent publiquement
- **Impact:** Attaquant peut tracer toutes les actions de tous les utilisateurs

### 13. `DEBUG=false` mais logs détaillés exposés via `/docs` et `/openapi.json`
- **Problème:** Swagger UI et OpenAPI schema sont accessibles publiquement
- **Risque:** Mapping complet de l'API pour un attaquant
- **Fix:** Désactiver `/docs` et `/openapi.json` en production

---

## VALIDÉ (OK)

| Contrôle | Statut |
|---|---|
| SQL Injection (SQLAlchemy ORM) | PASS — requêtes paramétrées |
| Password hashing (bcrypt) | PASS — passlib + bcrypt |
| Password validation (8+ chars, upper, lower, digit) | PASS |
| Auth routes (register/login/me) | PASS — rate limiting actif |
| Admin routes (V1) | PASS — `require_admin` dependency |
| Project isolation (user A ne voit pas user B) | PASS |
| Token validation (expired, tampered, missing sub) | PASS |
| DEBUG mode désactivé | PASS |
| CORS non wildcard | PASS |
| File upload size limit (50MB) | PASS |
| File upload extension filter | PASS |
| Database connection pooling | PASS |
| Alembic migrations fonctionnelles | PASS |
| 50 tables DB, 48 modèles ORM | PASS |

---

## RÉSUMÉ

| Sévérité | Nombre |
|---|---|
| CRITIQUE | 5 |
| ÉLEVÉ | 4 |
| MOYEN | 4 |
| OK | 14 |

**Verdict:** Le backend ne peut PAS être mis en ligne en l'état. Les 5 problèmes critiques doivent être corrigés, en particulier le SECRET_KEY et les routes sans auth.
