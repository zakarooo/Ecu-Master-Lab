#Requires -Version 5.1
<#
.SYNOPSIS
    Déploie ECU Master Lab sur Railway
.DESCRIPTION
    Script automatique qui déploie le backend FastAPI et le frontend Next.js sur Railway
.NOTES
    Prérequis: Railway CLI, Git, Docker (optionnel)
    Usage: .\deploy-railway.ps1
#>

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot

# ═══════════════════════════════════════════════════════════════
#  FONCTIONS UTILITAIRES
# ═══════════════════════════════════════════════════════════════

function Write-Step {
    param([string]$Step, [string]$Message)
    Write-Host ""
    Write-Host "[$Step] $Message" -ForegroundColor Cyan
}

function Write-OK {
    param([string]$Message)
    Write-Host "  OK $Message" -ForegroundColor Green
}

function Write-Warn {
    param([string]$Message)
    Write-Host "  !! $Message" -ForegroundColor Yellow
}

function Write-Fail {
    param([string]$Message)
    Write-Host "  ERREUR: $Message" -ForegroundColor Red
}

function Test-RailwayInstalled {
    try {
        $v = railway --version 2>$null
        return $true
    } catch {
        return $false
    }
}

function Install-RailwayCLI {
    Write-Step "1" "Installation Railway CLI..."
    try {
        irm https://railway.app/install.sh | iex
        Write-OK "Railway CLI installé"
    } catch {
        Write-Fail "Impossible d'installer Railway CLI"
        Write-Host "  Installez manuellement: https://docs.railway.com/cli" -ForegroundColor Gray
        exit 1
    }
}

function Generate-SecretKey {
    python -c "import secrets; print(secrets.token_urlsafe(64))"
}

# ═══════════════════════════════════════════════════════════════
#  ÉTAPE 0: VÉRIFICATIONS PRÉALABLES
# ═══════════════════════════════════════════════════════════════

Write-Host ""
Write-Host "=============================================" -ForegroundColor Magenta
Write-Host "  ECU Master Lab - Déploiement Railway" -ForegroundColor Magenta
Write-Host "=============================================" -ForegroundColor Magenta

Write-Step "0" "Vérifications préalables..."

# Railway CLI
if (-not (Test-RailwayInstalled)) {
    Write-Warn "Railway CLI non trouvé"
    $install = Read-Host "  Voulez-vous l'installer ? (O/n)"
    if ($install -ne "n") {
        Install-RailwayCLI
    } else {
        Write-Fail "Railway CLI requis. Installez-le depuis https://docs.railway.com/cli"
        exit 1
    }
}
$railwayVersion = railway --version
Write-OK "Railway CLI v$railwayVersion"

# Vérifier que nous sommes dans le bon répertoire
if (-not (Test-Path "$ProjectRoot\backend\app\main.py")) {
    Write-Fail "backend/app/main.py non trouvé. Exécutez ce script depuis le dossier du projet."
    exit 1
}
Write-OK "Structure du projet valide"

# ═══════════════════════════════════════════════════════════════
#  ÉTAPE 1: CONNEXION RAILWAY
# ═══════════════════════════════════════════════════════════════

Write-Step "1" "Connexion à Railway..."
try {
    $whoami = railway whoami 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-OK "Connecté en tant que: $whoami"
    } else {
        throw "Not logged in"
    }
} catch {
    Write-Warn "Non connecté à Railway"
    Write-Host "  Ouverture du navigateur pour authentification..." -ForegroundColor Gray
    railway login
    if ($LASTEXITCODE -ne 0) {
        Write-Fail "Connexion échouée"
        exit 1
    }
    Write-OK "Connecté à Railway"
}

# ═══════════════════════════════════════════════════════════════
#  ÉTAPE 2: CRÉER OU SÉLECTIONNER LE PROJET
# ═══════════════════════════════════════════════════════════════

Write-Step "2" "Configuration du projet Railway..."

# Vérifier si un projet est déjà lié
$linked = railway status --json 2>$null
$isLinked = $false
if ($LASTEXITCODE -eq 0 -and $linked -match '"projectId"') {
    $isLinked = $true
    Write-OK "Projet déjà lié"
}

if (-not $isLinked) {
    Write-Host ""
    Write-Host "  Options:" -ForegroundColor Yellow
    Write-Host "    1. Créer un nouveau projet" -ForegroundColor White
    Write-Host "    2. Lier à un projet existant" -ForegroundColor White
    $choice = Read-Host "  Votre choix (1/2)"

    if ($choice -eq "2") {
        Write-Host "  Ouverture du Railway Dashboard..." -ForegroundColor Gray
        railway link
    } else {
        $projectName = Read-Host "  Nom du projet (défaut: ecu-master-lab)"
        if (-not $projectName) { $projectName = "ecu-master-lab" }
        railway init $projectName
    }

    if ($LASTEXITCODE -ne 0) {
        Write-Fail "Impossible de créer/lier le projet"
        exit 1
    }
    Write-OK "Projet configuré"
}

# ═══════════════════════════════════════════════════════════════
#  ÉTAPE 3: CONFIGURER LES VARIABLES D'ENVIRONNEMENT
# ═══════════════════════════════════════════════════════════════

Write-Step "3" "Configuration des variables d'environnement..."

# Générer SECRET_KEY
$secretKey = Generate-SecretKey
Write-OK "SECRET_KEY générée"

# Demander DATABASE_URL
Write-Host ""
Write-Host "  Base de données:" -ForegroundColor Yellow
Write-Host "    1. Utiliser Neon (recommandé - déjà configuré)" -ForegroundColor White
Write-Host "    2. Utiliser PostgreSQL Railway" -ForegroundColor White
Write-Host "    3. Entrer une URL personnalisée" -ForegroundColor White
$dbChoice = Read-Host "  Votre choix (1/2/3)"

switch ($dbChoice) {
    "2" {
        Write-Host "  Création de PostgreSQL Railway..." -ForegroundColor Gray
        railway variables set DATABASE_URL --skip-deploys
        Write-Warn "Copiez l'URL DATABASE_URL depuis le Dashboard Railway"
        Write-Host "  -> https://railway.app/dashboard (cliquez sur le service PostgreSQL)" -ForegroundColor Gray
        $databaseUrl = Read-Host "  Collez l'URL DATABASE_URL ici"
        if (-not $databaseUrl) {
            Write-Fail "DATABASE_URL requise"
            exit 1
        }
    }
    "3" {
        $databaseUrl = Read-Host "  Entrez l'URL DATABASE_URL"
        if (-not $databaseUrl) {
            Write-Fail "DATABASE_URL requise"
            exit 1
        }
    }
    default {
        $databaseUrl = "postgresql://neondb_owner:npg_klmGKxjE8F3o@ep-weathered-cloud-asl3vwh5-pooler.c-4.eu-central-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
        Write-OK "Utilisation de Neon (URL existante)"
    }
}

# Demander CORS_ORIGINS (on mettra à jour après le déploiement frontend)
$corsOrigins = '["http://localhost:3000"]'

# Définir les variables pour le backend
Write-Host "  Définition des variables backend..." -ForegroundColor Gray

$envVars = @(
    "SECRET_KEY=$secretKey",
    "DATABASE_URL=$databaseUrl",
    "DEBUG=false",
    "CORS_ORIGINS=$corsOrigins"
)

foreach ($var in $envVars) {
    railway variable set $var --skip-deploys 2>$null
}

Write-OK "Variables backend configurées"

# ═══════════════════════════════════════════════════════════════
#  ÉTAPE 4: DÉPLOYER LE BACKEND
# ═══════════════════════════════════════════════════════════════

Write-Step "4" "Déploiement du backend FastAPI..."

Write-Host "  Upload et build du backend..." -ForegroundColor Gray
railway up --path backend --service backend

if ($LASTEXITCODE -ne 0) {
    Write-Fail "Échec du déploiement backend"
    Write-Host "  Vérifiez les logs: railway logs --service backend" -ForegroundColor Gray
    exit 1
}

Write-OK "Backend déployé"

# Récupérer l'URL du backend
Write-Host "  Récupération de l'URL du backend..." -ForegroundColor Gray
Start-Sleep -Seconds 10

$backendUrl = ""
try {
    $backendUrl = railway variables get RAILWAY_PUBLIC_URL --service backend 2>$null
    if (-not $backendUrl -or $LASTEXITCODE -ne 0) {
        # Fallback: générer l'URL basée sur le nom du projet
        $status = railway status --json 2>$null
        if ($status -match '"name":"([^"]+)"') {
            $projectName = $matches[1]
            $backendUrl = "https://$projectName-backend.up.railway.app"
        }
    }
} catch {
    Write-Warn "URL backend non détectée automatiquement"
}

if ($backendUrl) {
    Write-OK "URL Backend: $backendUrl"
} else {
    $backendUrl = Read-Host "  Entrez l'URL du backend (depuis Railway Dashboard)"
}

# ═══════════════════════════════════════════════════════════════
#  ÉTAPE 5: DÉPLOYER LE FRONTEND
# ═══════════════════════════════════════════════════════════════

Write-Step "5" "Déploiement du frontend Next.js..."

# Définir l'URL API pour le frontend
if ($backendUrl) {
    railway variable set "NEXT_PUBLIC_API_URL=$backendUrl" --service frontend --skip-deploys 2>$null
}

Write-Host "  Upload et build du frontend..." -ForegroundColor Gray
railway up --path frontend --service frontend

if ($LASTEXITCODE -ne 0) {
    Write-Fail "Échec du déploiement frontend"
    Write-Host "  Vérifiez les logs: railway logs --service frontend" -ForegroundColor Gray
    exit 1
}

Write-OK "Frontend déployé"

# Récupérer l'URL du frontend
Start-Sleep -Seconds 10
$frontendUrl = ""
try {
    $frontendUrl = railway variables get RAILWAY_PUBLIC_URL --service frontend 2>$null
    if (-not $frontendUrl -or $LASTEXITCODE -ne 0) {
        $status = railway status --json 2>$null
        if ($status -match '"name":"([^"]+)"') {
            $projectName = $matches[1]
            $frontendUrl = "https://$projectName-frontend.up.railway.app"
        }
    }
} catch {
    Write-Warn "URL frontend non détectée automatiquement"
}

if ($frontendUrl) {
    Write-OK "URL Frontend: $frontendUrl"
} else {
    $frontendUrl = Read-Host "  Entrez l'URL du frontend (depuis Railway Dashboard)"
}

# ═══════════════════════════════════════════════════════════════
#  ÉTAPE 6: METTRE À JOUR CORS AVEC L'URL FRONTEND
# ═══════════════════════════════════════════════════════════════

Write-Step "6" "Mise à jour CORS avec l'URL frontend..."

if ($frontendUrl) {
    $newCors = "[`"http://localhost:3000`",`"http://localhost:5173`",`"$frontendUrl`"]"
    railway variable set "CORS_ORIGINS=$newCors" --service backend --skip-deploys 2>$null
    Write-OK "CORS mis à jour: $newCors"
} else {
    Write-Warn "Mettez à jour CORS_ORIGINS manuellement dans le Dashboard Railway"
}

# ═══════════════════════════════════════════════════════════════
#  ÉTAPE 7: REDÉPLOYER LE BACKEND AVEC LES BONNES CORS
# ═══════════════════════════════════════════════════════════════

Write-Step "7" "Redéploiement backend avec CORS mis à jour..."

railway redeploy --service backend 2>$null
Write-OK "Backend redéployé"

# ═══════════════════════════════════════════════════════════════
#  RÉSUMÉ
# ═══════════════════════════════════════════════════════════════

Write-Host ""
Write-Host "=============================================" -ForegroundColor Green
Write-Host "  DÉPLOIEMENT TERMINÉ !" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green
Write-Host ""

if ($backendUrl) {
    Write-Host "  Backend (API):  $backendUrl" -ForegroundColor Cyan
}
if ($frontendUrl) {
    Write-Host "  Frontend (UI):  $frontendUrl" -ForegroundColor Cyan
}
Write-Host ""

Write-Host "  Health Check:   $backendUrl/api/health" -ForegroundColor Gray
Write-Host "  Dashboard:      https://railway.app/dashboard" -ForegroundColor Gray
Write-Host ""

Write-Host "  Commandes utiles:" -ForegroundColor Yellow
Write-Host "    railway logs --service backend     Logs du backend" -ForegroundColor Gray
Write-Host "    railway logs --service frontend    Logs du frontend" -ForegroundColor Gray
Write-Host "    railway status                     Statut du projet" -ForegroundColor Gray
Write-Host "    railway redeploy                   Tout redéployer" -ForegroundColor Gray
Write-Host ""
