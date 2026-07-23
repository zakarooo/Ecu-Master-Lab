import { test, expect } from "@playwright/test";

test.describe("API Dossiers", () => {
  const testDossier = {
    nom: "Test E2E Dossier",
    statut: "brouillon",
    informationsPersonnelles: {
      nom: "Dupont",
      prenom: "Marie",
      dateNaissance: "1990-05-15",
      lieuNaissance: "Paris",
      nationalite: "Sénégal",
      adresse: "10 rue de la Paix",
      codePostal: "75002",
      ville: "Paris",
      telephone: "0612345678",
      email: "marie@test.fr",
      situationFamiliale: "celibataire",
      nombreEnfants: 0,
    },
    situationAdministrative: {
      statutSejour: "irregulier",
    },
    situationFamiliale: { situation: "celibataire" },
    demarchesPrecedentes: [],
    documents: [],
    memos: [],
    courriers: [],
    checklist: [],
    rapportGenere: false,
  };

  test("POST /api/dossiers crée un dossier", async ({ request }) => {
    const res = await request.post("/api/dossiers", { data: testDossier });
    expect(res.status()).toBe(201);
    const body = await res.json();
    expect(body.id).toBeTruthy();
    expect(body.nom).toBe("Test E2E Dossier");
  });

  test("GET /api/dossiers liste les dossiers", async ({ request }) => {
    const res = await request.get("/api/dossiers");
    expect(res.status()).toBe(200);
    const body = await res.json();
    expect(Array.isArray(body)).toBe(true);
  });

  test("GET /api/dossiers/[id] récupère un dossier", async ({ request }) => {
    const createRes = await request.post("/api/dossiers", { data: testDossier });
    const created = await createRes.json();

    const res = await request.get(`/api/dossiers/${created.id}`);
    expect(res.status()).toBe(200);
    const body = await res.json();
    expect(body.id).toBe(created.id);
  });

  test("PUT /api/dossiers/[id] met à jour un dossier", async ({ request }) => {
    const createRes = await request.post("/api/dossiers", { data: testDossier });
    const created = await createRes.json();

    const res = await request.put(`/api/dossiers/${created.id}`, {
      data: { ...testDossier, nom: "Dossier Modifié" },
    });
    expect(res.status()).toBe(200);
    const body = await res.json();
    expect(body.nom).toBe("Dossier Modifié");
  });

  test("GET /api/dossiers/[id] avec ID inexistant renvoie 404", async ({ request }) => {
    const res = await request.get("/api/dossiers/nonexistent-id-xyz");
    expect(res.status()).toBe(404);
  });

  test("POST /api/dossiers avec body invalide renvoie 400", async ({ request }) => {
    const res = await request.post("/api/dossiers", { data: {} });
    expect(res.status()).toBe(400);
  });

  test("POST /api/dossiers/[id]/analyse lance l'analyse IA", async ({ request }) => {
    const createRes = await request.post("/api/dossiers", { data: testDossier });
    const created = await createRes.json();

    const res = await request.post(`/api/dossiers/${created.id}/analyse`);
    expect(res.status()).toBe(200);
    const body = await res.json();
    expect(body.resume).toBeTruthy();
    expect(body.forces).toBeDefined();
    expect(body.faiblesses).toBeDefined();
  });

  test("POST /api/dossiers/[id]/checklist génère la checklist", async ({ request }) => {
    const createRes = await request.post("/api/dossiers", { data: testDossier });
    const created = await createRes.json();

    const res = await request.post(`/api/dossiers/${created.id}/checklist`);
    expect(res.status()).toBe(200);
    const body = await res.json();
    expect(Array.isArray(body)).toBe(true);
    expect(body.length).toBeGreaterThan(0);
  });

  test("POST /api/dossiers/[id]/letters génère un courrier", async ({ request }) => {
    const createRes = await request.post("/api/dossiers", { data: testDossier });
    const created = await createRes.json();

    const res = await request.post(`/api/dossiers/${created.id}/letters`, {
      data: { type: "demande_info" },
    });
    expect(res.status()).toBe(200);
    const body = await res.json();
    expect(body.contenu).toBeTruthy();
    expect(body.titre).toBeTruthy();
  });
});
