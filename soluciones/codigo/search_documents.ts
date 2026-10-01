// Solución de referencia: adaptador Pi de search_documents.
// Para probarlo, copia este archivo y search.mjs a ejemplos/pi-package/extensions/
// (ajusta las rutas de import) y cárgalo con -e junto al catálogo.
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { Type } from "typebox";
import { searchDocuments } from "./search.mjs";

export default function (pi: ExtensionAPI) {
  pi.registerTool({
    name: "search_documents",
    label: "Buscar documentos sintéticos",
    description:
      "Busca términos en el catálogo sintético y devuelve IDs candidatos con una puntuación léxica (0-1). " +
      "La puntuación NO indica verdad ni vigencia: consulta después el documento con lookup_document.",
    promptSnippet: "Busca IDs candidatos por términos antes de consultar documentos.",
    parameters: Type.Object(
      {
        query: Type.String({ minLength: 2, maxLength: 200 }),
        max_results: Type.Optional(Type.Integer({ minimum: 1, maximum: 4 })),
      },
      { additionalProperties: false },
    ),
    annotations: { readOnlyHint: true, destructiveHint: false, idempotentHint: true, openWorldHint: false },
    async execute(_toolCallId, params, signal) {
      if (signal?.aborted) throw new Error("Búsqueda cancelada");
      const resultado = searchDocuments(params);
      return {
        content: [{ type: "text", text: JSON.stringify(resultado) }],
        details: { total: resultado.total_matches },
      };
    },
  });
}
