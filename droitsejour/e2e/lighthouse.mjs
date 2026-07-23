import lighthouse from "lighthouse";
import * as chromeLauncher from "chrome-launcher";

const BASE = "http://localhost:3000";
const pages = [
  { name: "Homepage", url: `${BASE}/` },
  { name: "Creer un dossier", url: `${BASE}/dossier/new` },
  { name: "Entreprise", url: `${BASE}/entreprise` },
];

async function run() {
  const results = [];

  for (const p of pages) {
    console.log(`\n--- Auditing: ${p.name} (${p.url}) ---`);
    try {
      const chrome = await chromeLauncher.launch({ headless: true });
      const result = await lighthouse(p.url, {
        port: chrome.port,
        output: "json",
        logLevel: "error",
        onlyCategories: ["performance", "accessibility", "best-practices", "seo"],
      });

      await chrome.kill();

      if (!result?.report) {
        console.log(`  No report for ${p.name}`);
        continue;
      }

      const reportStr = typeof result.report === "string" ? result.report : JSON.stringify(result.report);
      const json = JSON.parse(reportStr);
      const scores = {};
      for (const [key, cat] of Object.entries(json.categories || {})) {
        scores[key] = Math.round((cat.score || 0) * 100);
      }
      results.push({ name: p.name, scores });
      console.log(`  Scores:`, JSON.stringify(scores));
    } catch (err) {
      console.error(`  Error: ${err.message}`);
    }
  }

  console.log("\n=== LIGHTHOUSE SUMMARY ===");
  for (const r of results) {
    const vals = Object.values(r.scores);
    const avg = Math.round(vals.reduce((a, b) => a + b, 0) / vals.length);
    console.log(`${r.name}: ${JSON.stringify(r.scores)} → avg: ${avg}/100`);
  }
  const allVals = results.flatMap(r => Object.values(r.scores));
  const globalAvg = Math.round(allVals.reduce((a, b) => a + b, 0) / allVals.length);
  console.log(`\nGLOBAL AVERAGE: ${globalAvg}/100`);
}

run().catch(console.error);
