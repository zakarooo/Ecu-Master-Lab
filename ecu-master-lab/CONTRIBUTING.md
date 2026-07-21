# Guide de Contribution — ECU Master Lab

Merci de votre interet pour ECU Master Lab ! Ce guide explique comment contribuer au projet.

## Types de Contributions

- **Bug Reports** : Signaler un probleme via les issues GitHub
- **Feature Requests** : Proposer une nouvelle fonctionnalite
- **Code** : Corriger des bugs ou ajouter des fonctionnalites
- **Documentation** : Ameliorer la documentation
- **Tests** : Ajouter ou corriger des tests

## Demarrage

### 1. Fork et Clone

```bash
git clone https://github.com/votre-user/Ecu-Master-Lab.git
cd Ecu-Master-Lab
git remote add upstream https://github.com/zakarooo/Ecu-Master-Lab.git
```

### 2. Branch de developpement

```bash
git checkout -b feature/nom-de-la-feature
```

Convention de nommage :
- `feature/description` — nouvelle fonctionnalite
- `fix/description` — correction de bug
- `docs/description` — documentation
- `test/description` — tests

### 3. Configuration

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

# Frontend
cd ../frontend
npm install
```

### 4. Developpement

#### Backend (Python)

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

Style de code :
- Suivre PEP 8 pour Python
- Utiliser les types Python (type hints)
- Docstrings pour les fonctions publiques

#### Frontend (TypeScript/React)

```bash
cd frontend
npm run dev
```

Style de code :
- Composants fonctionnels avec hooks
- TypeScript strict
- Tailwind CSS pour le style

### 5. Tests

```bash
# Tests E2E
cd frontend
npx playwright test e2e/ --reporter=list
```

**Tous les tests doivent passer avant de soumettre une PR.**

### 6. Commit

Utiliser des messages de commit descriptifs :

```
type: description breve

Description detaillee si necessaire.

Ref: #numero-de-issue
```

Types : `feat`, `fix`, `docs`, `test`, `refactor`, `chore`

### 7. Push et PR

```bash
git push origin feature/nom-de-la-feature
```

Puis ouvrir une Pull Request sur GitHub avec :
- Un titre descriptif
- La reference de l'issue (si applicable)
- La description des changements
- Les captures d'ecran (si applicable)

## Architecture du Projet

Voir `backend/ARCHITECTURE.md` et `frontend/ARCHITECTURE.md` pour la documentation officielle de l'architecture.

## Questions ?

En cas de question, ouvrir une issue avec le tag `question`.
