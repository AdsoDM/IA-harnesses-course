import test from "node:test";
import assert from "node:assert/strict";
import { searchDocuments } from "./search.mjs";

test("encuentra la norma vigente y la histórica", () => {
  const r = searchDocuments({ query: "retención de backups" });
  const ids = r.results.map((x) => x.doc_id);
  assert.ok(ids.includes("d-001") && ids.includes("d-003"));
  for (const x of r.results) assert.ok(x.score > 0 && x.score <= 1);
});
test("la puntuación no decide vigencia: d-003 también aparece", () => {
  const r = searchDocuments({ query: "norma retención 15 días" });
  assert.equal(r.results[0].doc_id, "d-003"); // más coincidencias léxicas, pero NO es la vigente
});
test("limita resultados y respeta el máximo", () => {
  assert.equal(searchDocuments({ query: "PR260101", max_results: 1 }).results.length, 1);
  assert.throws(() => searchDocuments({ query: "backup", max_results: 10 }), /max_results/);
});
test("sin coincidencias devuelve lista vacía, no un error ni un documento inventado", () => {
  assert.deepEqual(searchDocuments({ query: "teléfono móvil satélite" }).results.filter((x) => x.doc_id === "d-999"), []);
  assert.equal(searchDocuments({ query: "zzzz qqqq" }).results.length, 0);
});
test("contrato de entrada", () => {
  for (const mal of [null, [], "backup", { query: "" }, { query: "x" }, { query: 3 }, { query: "backup", cmd: "rm" }, { query: "a".repeat(201) }]) {
    assert.throws(() => searchDocuments(mal));
  }
});
