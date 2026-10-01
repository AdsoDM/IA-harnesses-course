// Solución de referencia del laboratorio 06: search_documents sobre el catálogo.
// Búsqueda LÉXICA: la puntuación mide coincidencia de términos, no verdad ni vigencia.
import { listDocuments } from "../../ejemplos/pi-package/shared/catalogue.mjs";

export const LIMITES = { minQuery: 2, maxQuery: 200, maxResults: 4 };
const VACIAS = new Set(["el", "la", "los", "las", "de", "del", "que", "es", "un", "una", "y", "a", "en", "por", "cual", "se"]);

function normal(texto) {
  return texto.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
}

function terminos(texto) {
  return [...new Set(normal(texto).split(/[^a-z0-9:-]+/).filter((t) => t.length > 1 && !VACIAS.has(t)))];
}

export function searchDocuments(args) {
  if (!args || typeof args !== "object" || Array.isArray(args)) throw new Error("Se requiere un objeto");
  const extra = Object.keys(args).filter((k) => k !== "query" && k !== "max_results");
  if (extra.length) throw new Error(`Claves no permitidas: ${extra.join(", ")}`);
  const { query, max_results = 3 } = args;
  if (typeof query !== "string") throw new Error("query debe ser texto");
  const q = query.trim();
  if (q.length < LIMITES.minQuery || q.length > LIMITES.maxQuery) {
    throw new Error(`query debe tener entre ${LIMITES.minQuery} y ${LIMITES.maxQuery} caracteres`);
  }
  if (!Number.isInteger(max_results) || max_results < 1 || max_results > LIMITES.maxResults) {
    throw new Error(`max_results debe ser un entero entre 1 y ${LIMITES.maxResults}`);
  }
  const buscados = terminos(q);
  if (buscados.length === 0) throw new Error("query sin términos significativos");
  const resultados = [];
  for (const doc of listDocuments()) {
    const propios = new Set(terminos(`${doc.title} ${doc.text}`));
    const coinciden = buscados.filter((t) => [...propios].some((p) => p.startsWith(t.slice(0, 5))));
    if (coinciden.length === 0) continue;
    resultados.push({
      doc_id: doc.doc_id,
      title: doc.title,
      date: doc.date,
      score: Number((coinciden.length / buscados.length).toFixed(3)),
      matched_terms: coinciden,
    });
  }
  // Orden estable: puntuación descendente y, a igualdad, fecha más reciente primero.
  resultados.sort((a, b) => b.score - a.score || b.date.localeCompare(a.date) || a.doc_id.localeCompare(b.doc_id));
  return { query: q, results: resultados.slice(0, max_results), total_matches: resultados.length };
}
