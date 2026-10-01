# ADR-001 — Exponer la búsqueda documental como extensión Pi (ejemplo resuelto)

Estado: aceptada (ejemplo del curso). Fecha: 2026-09-30.

## Contexto

El asistente de PR260101 necesita buscar documentos por términos además de consultarlos por ID. Hoy solo Pi lo usa. El corpus es sintético y está embebido; no hay servicio externo. Se quiere medir el comportamiento con la batería del curso y controlar llamadas con `presupuesto.ts`.

## Opciones

| Criterio | A. Extensión Pi (`search_documents.ts`) | B. Servidor MCP propio (stdio) |
| --- | --- | --- |
| Reutilización | Solo Pi | Cualquier cliente MCP |
| Despliegue | Un archivo cargado con `-e` o en el paquete | Otro proceso, su versión y su configuración `mcp.json` |
| Permisos | Mismo proceso Pi | Proceso aparte; puede ejecutarse con otro usuario o contenedor |
| Pruebas | Núcleo con `node --test`; adaptador con `tsc` y el modelo de guion | Núcleo igual; además, pruebas del protocolo y del transporte |
| Observabilidad | Eventos `tool_execution_*` con nombre propio | Mismos eventos (`mcp__<servidor>__…`) + log del servidor (`mcp.log`) |
| Exposición al modelo | `direct` por defecto | `codemode` por defecto: hay que fijar `direct` o `toolExposure` |

## Decisión

Opción A. Un solo cliente, sin requisito de aislamiento de proceso y con pruebas más sencillas. Se implementa en `extensions/search_documents.ts` sobre el núcleo `search.mjs`, declarada de solo lectura en `annotations`.

## Consecuencias

Beneficio: menos piezas y la batería existente mide el cambio directamente. Coste: si otro cliente necesita la búsqueda, habrá que envolver el mismo núcleo en un servidor MCP. Límite: la extensión comparte permisos con Pi. **Condición de revisión:** un segundo cliente, un corpus que requiera acceso a un servicio con credenciales propias o la necesidad de ejecutar la búsqueda con permisos distintos a los de Pi.
