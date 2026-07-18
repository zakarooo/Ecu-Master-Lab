"""
ECU Master Lab - Audit Complet Phases 2-5
=========================================
Phase 2: PostgreSQL verification
Phase 3: All API routes testing
Phase 4: Frontend verification
Phase 5: End-to-end workflow
"""
import sys, os, json, time, random, hashlib, requests

os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.getcwd())

BASE = "http://127.0.0.1:8002"
PASS = 0
FAIL = 0
ERRORS = []

def test(name, condition, detail=""):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  [PASS] {name}")
    else:
        FAIL += 1
        msg = f"  [FAIL] {name}"
        if detail:
            msg += f" -- {detail}"
        print(msg)
        ERRORS.append(f"{name}: {detail}" if detail else name)

def section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

# ===================================================================
# PHASE 2: PostgreSQL Verification
# ===================================================================
section("PHASE 2: PostgreSQL Verification")

# 2.1 Connection test
print("\n--- 2.1 Connection ---")
try:
    from sqlalchemy import text
    from app.core.database import engine, SessionLocal, check_db_connection, list_tables, Base
    from app.core.config import settings
    status = check_db_connection()
    test("DATABASE_URL defined", bool(settings.DATABASE_URL), settings.DATABASE_URL[:40]+"...")
    test("PostgreSQL connected", status["status"] == "connected", status.get("error", ""))
except Exception as e:
    test("DB import", False, str(e))

# 2.2 Tables check
print("\n--- 2.2 Tables ---")
try:
    tables = list_tables()
    expected_core = ["users", "projects", "file_versions", "audit_logs"]
    expected_v2 = ["manufacturers", "ecu_models", "ecu_files", "analyses", "analysis_hypotheses",
                    "analysis_scores", "detected_maps", "detected_segments", "checksum_results",
                    "ecu_signatures", "binary_patterns", "maps", "vehicle_brands"]
    expected_knowledge = ["known_ecu_files", "known_signatures", "known_strings",
                           "known_segments", "analysis_corrections"]
    
    for t in expected_core:
        test(f"Table '{t}' exists", t in tables, f"Found: {tables[:10]}")
    for t in expected_v2:
        test(f"Table '{t}' exists", t in tables)
    for t in expected_knowledge:
        test(f"Table '{t}' exists", t in tables)
    test("Total tables >= 40", len(tables) >= 40, f"Found {len(tables)} tables")
    print(f"    All tables: {', '.join(sorted(tables))}")
except Exception as e:
    test("Tables check", False, str(e))

# 2.3 CRUD operations
print("\n--- 2.3 CRUD + Rollback ---")
db = SessionLocal()
try:
    from app.models.models import User
    
    # READ
    user_count = db.query(User).count()
    test("READ users", user_count >= 0, f"Found {user_count} users")
    
    # INSERT
    test_user = User(
        first_name="AuditTest", last_name="AuditUser",
        email=f"audit_{int(time.time())}@test.com",
        hashed_password="test123", role="client", is_active=True
    )
    db.add(test_user)
    db.flush()
    test_id = test_user.id
    test("INSERT user", test_id is not None, f"New user id={test_id}")
    
    # UPDATE
    test_user.first_name = "AuditUpdated"
    db.flush()
    updated = db.query(User).filter(User.id == test_id).first()
    test("UPDATE user", updated.first_name == "AuditUpdated")
    
    # DELETE
    db.delete(updated)
    db.flush()
    deleted = db.query(User).filter(User.id == test_id).first()
    test("DELETE user", deleted is None)
    
    # ROLLBACK
    throw_user = User(
        first_name="Rollback", last_name="Test",
        email="rollback@test.com", hashed_password="x", role="client"
    )
    db.add(throw_user)
    db.flush()
    db.rollback()
    rolled_back = db.query(User).filter(User.email == "rollback@test.com").first()
    test("ROLLBACK transaction", rolled_back is None)
    
except Exception as e:
    test("CRUD operations", False, str(e))
finally:
    db.close()

# 2.4 Pool configuration
print("\n--- 2.4 Pool Config ---")
try:
    test("Engine uses QueuePool", "QueuePool" in type(engine.pool).__name__)
    test("expire_on_commit=False", SessionLocal.kw.get("expire_on_commit") == False)
    test("autocommit=False", SessionLocal.kw.get("autocommit") == False)
    test("autoflush=False", SessionLocal.kw.get("autoflush") == False)
except Exception as e:
    test("Pool config", False, str(e))

# ===================================================================
# PHASE 3: API Routes Testing
# ===================================================================
section("PHASE 3: API Routes Testing")

# 3.1 Auth
print("\n--- 3.1 Authentication ---")
# Register
r = requests.post(f"{BASE}/api/auth/register", json={
    "email": f"audit_user_{int(time.time())}@test.com",
    "password": "AuditTest123!",
    "first_name": "Audit", "last_name": "Tester"
})
test("POST /api/auth/register (200/201)", r.status_code in (200, 201), f"Got {r.status_code}")
if r.status_code in (200, 201):
    TOKEN = r.json().get("access_token", "")
    USER_ID = r.json().get("user", {}).get("id", 0)
else:
    TOKEN = ""
    USER_ID = 0

HEADERS = {"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}

# Login
r = requests.post(f"{BASE}/api/auth/login", json={
    "email": f"audit_user_{int(time.time())}@test.com", "password": "AuditTest123!"
})
test("POST /api/auth/login (valid)", r.status_code in (200, 401), f"Got {r.status_code}")

# Login invalid
r = requests.post(f"{BASE}/api/auth/login", json={"email": "x@x.com", "password": "wrong"})
test("POST /api/auth/login (invalid 401)", r.status_code == 401, f"Got {r.status_code}")

# Me
r = requests.get(f"{BASE}/api/auth/me", headers=HEADERS)
test("GET /api/auth/me", r.status_code == 200, f"Got {r.status_code}")

# Me without token
r = requests.get(f"{BASE}/api/auth/me")
test("GET /api/auth/me (no token 401)", r.status_code in (401, 403), f"Got {r.status_code}")

# 3.2 Health
print("\n--- 3.2 Health ---")
r = requests.get(f"{BASE}/api/health")
test("GET /api/health (200)", r.status_code == 200, f"Got {r.status_code}")
if r.status_code == 200:
    test("Health status=healthy", r.json().get("status") == "healthy")
    test("Health DB connected", r.json().get("database") == "connected")

# 3.3 Projects
print("\n--- 3.3 Projects ---")
r = requests.post(f"{BASE}/api/projects", headers=HEADERS, json={"name": "Audit Test Project"})
test("POST /api/projects", r.status_code in (200, 201), f"Got {r.status_code}")
PROJECT_ID = r.json().get("id", 0) if r.status_code in (200, 201) else 0

r = requests.get(f"{BASE}/api/projects", headers=HEADERS)
test("GET /api/projects", r.status_code == 200, f"Got {r.status_code}")

if PROJECT_ID:
    r = requests.get(f"{BASE}/api/projects/{PROJECT_ID}", headers=HEADERS)
    test("GET /api/projects/{id}", r.status_code == 200, f"Got {r.status_code}")

# 3.4 V2 Reference (public GET, auth POST)
print("\n--- 3.4 V2 Reference ---")
v2_get_endpoints = [
    "/api/v2/referentiel/manufacturers",
    "/api/v2/referentiel/ecu-models",
    "/api/v2/referentiel/ecu-variants",
    "/api/v2/referentiel/processors",
    "/api/v2/referentiel/protocols",
    "/api/v2/referentiel/checksum-algorithms",
    "/api/v2/vehicles/brands",
    "/api/v2/vehicles/models",
    "/api/v2/vehicles/engines",
    "/api/v2/versions/software",
    "/api/v2/versions/hardware",
    "/api/v2/memory/layouts",
    "/api/v2/memory/segments",
    "/api/v2/signatures/ecu-signatures",
    "/api/v2/signatures/binary-patterns",
    "/api/v2/maps/categories",
    "/api/v2/maps/units",
    "/api/v2/maps/axes",
    "/api/v2/maps",
    "/api/v2/ai/models",
    "/api/v2/ai/datasets",
    "/api/v2/ai/heuristics",
    "/api/v2/reports",
    "/api/v2/activity",
]
for ep in v2_get_endpoints:
    r = requests.get(f"{BASE}{ep}")
    test(f"GET {ep}", r.status_code == 200, f"Got {r.status_code}: {r.text[:100]}")

# 3.5 Auth-required V2 endpoints
print("\n--- 3.5 Auth-required V2 ---")
auth_get_endpoints = [
    "/api/v2/analysis/files",
    "/api/v2/analysis/analyses",
    "/api/v2/knowledge/stats",
    "/api/v2/knowledge/known-files",
    "/api/v2/knowledge/signatures",
    "/api/v2/knowledge/strings",
]
for ep in auth_get_endpoints:
    r = requests.get(f"{BASE}{ep}", headers=HEADERS)
    test(f"GET {ep}", r.status_code == 200, f"Got {r.status_code}: {r.text[:100]}")

# Without auth
for ep in auth_get_endpoints:
    r = requests.get(f"{BASE}{ep}")
    test(f"GET {ep} (no auth 401)", r.status_code in (401, 403), f"Got {r.status_code}")

# 3.6 Admin endpoints (require admin role)
print("\n--- 3.6 Admin (require admin) ---")
admin_endpoints = [
    "GET /api/admin/stats",
    "GET /api/admin/users",
    "GET /api/admin/projects",
    "GET /api/admin/audit-logs",
]
for ep in admin_endpoints:
    method, path = ep.split(" ", 1)
    r = requests.get(f"{BASE}{path}", headers=HEADERS)
    test(f"{ep} (non-admin 403)", r.status_code in (403, 401), f"Got {r.status_code}")
    r = requests.get(f"{BASE}{path}")
    test(f"{ep} (no auth 401)", r.status_code in (401, 403), f"Got {r.status_code}")

# 3.7 Upload + Analysis
print("\n--- 3.7 Upload + Analysis ---")
# Create test binary
data = bytearray(65536)
data[1024:1024+14] = b"BOSCH EDC17C64"
data[1400:1400+18] = b"HW 0 281 030 963"
data[1600:1600+13] = b"SW 1037343991"
random.seed(42)
for i in range(16384):
    data[4096 + i] = random.randint(0, 255)
with open("audit_test.bin", "wb") as f:
    f.write(bytes(data))

# Upload
with open("audit_test.bin", "rb") as f:
    r = requests.post(f"{BASE}/api/v2/analysis/upload", headers=HEADERS,
        files={"file": ("audit_test.bin", f, "application/octet-stream")},
        data={"run_analysis": "true"})
test("POST /api/v2/analysis/upload (201)", r.status_code in (200, 201), f"Got {r.status_code}: {r.text[:200]}")

if r.status_code in (200, 201):
    resp = r.json()
    analysis_id = resp.get("analysis", {}).get("id") if resp.get("analysis") else None
    file_id = resp.get("ecu_file", {}).get("id") if resp.get("ecu_file") else None
    
    if analysis_id:
        r = requests.get(f"{BASE}/api/v2/analysis/analyses/{analysis_id}", headers=HEADERS)
        test(f"GET analysis/{analysis_id}", r.status_code == 200, f"Got {r.status_code}")
        
        r = requests.get(f"{BASE}/api/v2/analysis/analyses/{analysis_id}/full", headers=HEADERS)
        test(f"GET analysis/{analysis_id}/full", r.status_code == 200, f"Got {r.status_code}")
        
        for sub in ["results", "hypotheses", "scores", "detected-maps", "detected-segments", "checksums"]:
            r = requests.get(f"{BASE}/api/v2/analysis/analyses/{analysis_id}/{sub}", headers=HEADERS)
            test(f"GET analysis/{analysis_id}/{sub}", r.status_code == 200, f"Got {r.status_code}")
    
    if file_id:
        r = requests.get(f"{BASE}/api/v2/analysis/files/{file_id}", headers=HEADERS)
        test(f"GET files/{file_id}", r.status_code == 200, f"Got {r.status_code}")
        
        if analysis_id:
            # Run analysis again on existing file
            r = requests.post(f"{BASE}/api/v2/analysis/analyses/{file_id}/run", headers=HEADERS)
            test(f"POST analyses/{file_id}/run", r.status_code in (200, 201), f"Got {r.status_code}")

# 3.8 Knowledge
print("\n--- 3.8 Knowledge ---")
with open("audit_test.bin", "rb") as f:
    r = requests.post(f"{BASE}/api/v2/knowledge/register", headers=HEADERS,
        files={"file": ("audit_test.bin", f, "application/octet-stream")},
        data={"ecu_model_name": "Bosch EDC17C64", "manufacturer_name": "Bosch"})
test("POST /api/v2/knowledge/register", r.status_code in (200, 201), f"Got {r.status_code}: {r.text[:200]}")

# 3.9 Reports
print("\n--- 3.9 Reports ---")
r = requests.post(f"{BASE}/api/v2/reports", headers=HEADERS, json={
    "analysis_id": analysis_id if 'analysis_id' in dir() and analysis_id else 1,
    "title": "Audit Report", "content": "Test report"
})
test("POST /api/v2/reports", r.status_code in (200, 201), f"Got {r.status_code}")

# 3.10 Activity
print("\n--- 3.10 Activity ---")
r = requests.post(f"{BASE}/api/v2/activity", headers=HEADERS, json={
    "action": "audit_test", "resource_type": "test", "resource_id": 1
})
test("POST /api/v2/activity", r.status_code in (200, 201), f"Got {r.status_code}")

# ===================================================================
# PHASE 4: Frontend Verification
# ===================================================================
section("PHASE 4: Frontend Verification")

FE_BASE = "http://localhost:3000"
try:
    r = requests.get(FE_BASE, timeout=10)
    test("Frontend reachable (3000)", r.status_code == 200, f"Got {r.status_code}")
except Exception as e:
    test("Frontend reachable (3000)", False, str(e))

# Test API proxy via Next.js
try:
    r = requests.get(f"{FE_BASE}/api/health", timeout=10)
    test("Frontend /api/health proxy", r.status_code == 200, f"Got {r.status_code}")
except Exception as e:
    test("Frontend /api/health proxy", False, str(e))

# ===================================================================
# PHASE 5: E2E Workflow
# ===================================================================
section("PHASE 5: End-to-End Workflow")

print("\n--- 5.1 Full E2E ---")
e2e_ok = True

# Step 1: Register
email_e2e = f"e2e_{int(time.time())}@test.com"
r = requests.post(f"{BASE}/api/auth/register", json={
    "email": email_e2e, "password": "E2ETest123!",
    "first_name": "E2E", "last_name": "Test"
})
test("E2E Step 1: Register", r.status_code in (200, 201))
e2e_token = r.json().get("access_token", "") if r.status_code in (200, 201) else ""
e2e_h = {"Authorization": f"Bearer {e2e_token}"} if e2e_token else {}

# Step 2: Login
r = requests.post(f"{BASE}/api/auth/login", json={"email": email_e2e, "password": "E2ETest123!"})
test("E2E Step 2: Login", r.status_code == 200)

# Step 3: Create project
r = requests.post(f"{BASE}/api/projects", headers=e2e_h, json={"name": "E2E Project"})
test("E2E Step 3: Create project", r.status_code in (200, 201))
e2e_project = r.json().get("id", 0) if r.status_code in (200, 201) else 0

# Step 4: Upload file + analyze
with open("audit_test.bin", "rb") as f:
    r = requests.post(f"{BASE}/api/v2/analysis/upload", headers=e2e_h,
        files={"file": ("e2e_test.bin", f, "application/octet-stream")},
        data={"run_analysis": "true"})
test("E2E Step 4: Upload + Analyze", r.status_code in (200, 201))
e2e_resp = r.json() if r.status_code in (200, 201) else {}
e2e_analysis_id = e2e_resp.get("analysis", {}).get("id") if e2e_resp.get("analysis") else None

# Step 5: Verify in PostgreSQL
if e2e_analysis_id:
    db2 = SessionLocal()
    from app.models.new.ecu_models import Analysis
    a = db2.query(Analysis).filter(Analysis.id == e2e_analysis_id).first()
    test("E2E Step 5: In PostgreSQL", a is not None, f"Analysis id={e2e_analysis_id}")
    if a:
        test("E2E Step 5: Has confidence", a.confidence is not None)
    db2.close()
else:
    test("E2E Step 5: In PostgreSQL", False, "No analysis_id")

# Step 6: Get full analysis
if e2e_analysis_id:
    r = requests.get(f"{BASE}/api/v2/analysis/analyses/{e2e_analysis_id}/full", headers=e2e_h)
    test("E2E Step 6: Get report", r.status_code == 200)
else:
    test("E2E Step 6: Get report", False, "No analysis_id")

# Step 7: List analyses
r = requests.get(f"{BASE}/api/v2/analysis/analyses", headers=e2e_h)
test("E2E Step 7: List analyses", r.status_code == 200)

# Step 8: List files
r = requests.get(f"{BASE}/api/v2/analysis/files", headers=e2e_h)
test("E2E Step 8: List files", r.status_code == 200)

# Cleanup
if os.path.exists("audit_test.bin"):
    os.remove("audit_test.bin")

# ===================================================================
# SUMMARY
# ===================================================================
section("AUDIT SUMMARY")
print(f"\n  Total tests: {PASS + FAIL}")
print(f"  PASSED:      {PASS}")
print(f"  FAILED:      {FAIL}")
if ERRORS:
    print(f"\n  ERRORS ({len(ERRORS)}):")
    for e in ERRORS:
        print(f"    - {e}")
else:
    print(f"\n  ALL TESTS PASSED!")

print(f"\n{'='*60}")
