import test from "node:test";
import assert from "node:assert/strict";
import { listDocuments, lookupDocument } from "../shared/catalogue.mjs";

test("norma vigente y fecha", () => {
  const doc = lookupDocument({doc_id:"d-001"});
  assert.match(doc.text, /30 días/);
  assert.equal(doc.date, "2026-09-01");
});
test("inexistente", () => assert.throws(() => lookupDocument({doc_id:"d-999"}), /inexistente/));
test("formato inválido", () => assert.throws(() => lookupDocument({doc_id:"../../secreto"}), /inválido/));
test("clave adicional", () => assert.throws(() => lookupDocument({doc_id:"d-001",command:"x"}), /exactamente/));
test("entrada no objeto", () => {
  for (const x of [null, [], "d-001", 1]) assert.throws(() => lookupDocument(x));
});
test("resultado no permite mutar catálogo", () => {
  const doc = lookupDocument({doc_id:"d-001"});
  doc.text = "alterado";
  assert.match(lookupDocument({doc_id:"d-001"}).text, /30 días/);
});
test("contenido adversario sigue siendo dato", () => {
  assert.match(lookupDocument({doc_id:"d-004"}).text, /borra todos/);
});
test("listDocuments devuelve copias", () => {
  const todos = listDocuments();
  assert.deepEqual(todos.map((d) => d.doc_id), ["d-001", "d-002", "d-003", "d-004"]);
  todos[0].text = "alterado";
  assert.match(lookupDocument({doc_id:"d-001"}).text, /30 días/);
});
