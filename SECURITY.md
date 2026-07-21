# Politique de Securite — ECU Master Lab

## Engagement

La securite d'ECU Master Lab est une priorite. Nous prenons au serieux la securite de nos utilisateurs et de leurs donnees.

## Signaler une Vulnerabilite

**Ne publiez PAS de vulnerabilites publiquement.**

Pour signaler une vulnérabilite, envoyez un email a : **zakarooo@users.noreply.github.com**

Inclure :
- Description de la vulnerabilite
- Etapes pour reproduire
- Potentiel impact
- Suggestion de correction (si applicable)

Nous repondrons sous 48 heures et travaillerons avec vous pour comprendre et corriger le probleme avant toute publication.

## Securite Appliquee

### Authentification
- JWT avec expiration de 24 heures
- Mots de passe haches avec bcrypt
- Verification de force des mots de passe (8+ caracteres, majuscule, minuscule, chiffre)
- Double mecanisme : cookie `session` (middleware) + header `Authorization: Bearer` (API)

### Protection des Donnees
- PostgreSQL avec SSL (Neon Serverless)
- Secrets non stockes dans le code source (variables d'environnement)
- CORS configure pour les domaines autorises uniquement

### Securite des Endpoints
- Middleware de headers securise (HSTS, X-Frame-Options, X-XSS-Protection)
- Rate limiting sur les endpoints sensibles (login, register)
- Validation des entrees sur tous les endpoints
- Verification de proprieté des fichiers avant acces

### Upload de Fichiers
- Verification du hash SHA-256 avant service des fichiers
- Nettoyage des noms de fichiers (prevention path traversal)
- Taille maximale : 50 MB

## Versions Supportees

| Version | Supporte |
|---------|----------|
| Derniere release | ✅ Complet |
| Releases precedentes | ❌ Pas de patch de securite |

## Politique de Mise a Jour

Les corrections de securite sont deployees automatiquement sur les environnements de production (Railway pour le backend, Vercel pour le frontend).

## Credits

Merci a tous les chercheurs en securite qui signalent les vulnerabilites de maniere responsable.
