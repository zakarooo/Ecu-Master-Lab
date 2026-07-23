import lighthouse from "lighthouse";
import * as chromeLauncher from "chrome-launcher";

const BASE = "http://localhost:3000";

async function run() {
  const chrome = await chromeLauncher.launch({ headless: true });

  const result = await lighthouse(`${BASE}/dossier/new`, {
    port: chrome.port,
    output: "json",
    logLevel: "error",
    onlyCategories: ["accessibility", "performance"],
  });

  await chrome.kill();

  const reportStr = typeof result.report === "string" ? result.report : JSON.stringify(result.report);
  const json = JSON.parse(reportStr);

  console.log("\n=== ACCESSIBILITY ISSUES ===");
  for (const [id, audit] of Object.entries(json.audits || {})) {
    if (audit.score !== null && audit.score < 1) {
      console.log(`\n❌ ${audit.title} (score: ${audit.score})`);
      console.log(`   ${audit.description}`);
      if (audit.details?.items) {
        for (const item of audit.details.items.slice(0, 3)) {
          console.log(`   → ${JSON.stringify(item.node?.snippet || item)}`);
        }
      }
    }
  }

  console.log("\n=== PERFORMANCE OPPORTUNITIES ===");
  for (const [id, audit] of Object.entries(json.audits || {})) {
    if (audit.details?.type === "opportunity" && audit.score !== null && audit.score < 0.9) {
      console.log(`\n⚠️  ${audit.title}`);
      console.log(`   Savings: ${audit.details.overallSavingsMs || "N/A"}ms`);
    }
  }
}

run().catch(console.error);
