// Consulta documental con el SDK: carga la extensión del catálogo y la plantilla,
// limita herramientas, observa eventos reales, aplica plazo con abort y valida el
// contrato. Con CURSO_MODELO=guion usa el modelo de guion (simulado, sin red).
//
//   $env:CURSO_MODELO = "guion"; npm.cmd run documental -- "¿Cuál es la retención vigente?"
//   Remove-Item Env:CURSO_MODELO; npm.cmd run documental -- "¿Cuál es la retención vigente?"
import path from "node:path";
import { fileURLToPath } from "node:url";
import {
  createAgentSession,
  DefaultResourceLoader,
  getAgentDir,
  SessionManager,
} from "@earendil-works/pi-coding-agent";

const aqui = path.dirname(fileURLToPath(import.meta.url));
const paquete = path.resolve(aqui, "../pi-package");
const pregunta = process.argv.slice(2).join(" ").trim() || "¿Cuál es la retención vigente de backups?";
const usarGuion = process.env.CURSO_MODELO === "guion";
const plazoMs = Number(process.env.CURSO_PLAZO_MS ?? 120_000);

const extensiones = [path.join(paquete, "extensions/catalogue.ts")];
if (usarGuion) extensiones.unshift(path.join(paquete, "dobles/modelo-guion.ts"));

const resourceLoader = new DefaultResourceLoader({
  cwd: process.cwd(),
  agentDir: getAgentDir(),
  noExtensions: true, // sin descubrimiento: solo lo que se nombra aquí
  noSkills: true,
  noPromptTemplates: true,
  noContextFiles: true,
  additionalExtensionPaths: extensiones,
  additionalPromptTemplatePaths: [path.join(paquete, "prompts/respuesta-documental.md")],
});
await resourceLoader.reload();

const { session } = await createAgentSession({
  cwd: process.cwd(),
  resourceLoader,
  sessionManager: SessionManager.inMemory(),
  tools: ["lookup_document"],
});

type Llamada = { id: string; name: string; arguments: unknown; ok: boolean };
const llamadas = new Map<string, Llamada>();
let asentado = false;
const baja = session.subscribe((event) => {
  if (event.type === "tool_execution_start") {
    llamadas.set(event.toolCallId, { id: event.toolCallId, name: event.toolName, arguments: event.args, ok: false });
  } else if (event.type === "tool_execution_end") {
    const c = llamadas.get(event.toolCallId);
    if (c) c.ok = !event.isError;
  } else if (event.type === "agent_settled") {
    asentado = true;
  }
});

const temporizador = setTimeout(() => {
  console.error(JSON.stringify({ aviso: `plazo de ${plazoMs} ms vencido: abort` }));
  void session.abort();
}, plazoMs);

try {
  if (usarGuion) {
    const modelo = session.modelRuntime.getModel("curso", "guion");
    if (!modelo) throw new Error("No se registró el modelo de guion");
    await session.setModel(modelo);
  }
  if (!session.model) throw new Error("No hay modelo: configura uno con /login o usa CURSO_MODELO=guion");
  console.error(JSON.stringify({ provider: session.model.provider, model: session.model.id, tools: session.getActiveToolNames() }));

  await session.prompt(`/respuesta-documental ${pregunta}`);
  const texto = session.getLastAssistantText()?.trim() ?? "";
  let output: unknown = null;
  let error_salida: string | null = null;
  try {
    output = JSON.parse(texto);
  } catch {
    error_salida = "la respuesta no es un objeto JSON";
  }
  const ok = !!output && typeof output === "object" && !Array.isArray(output) &&
    ["status", "answer", "sources"].every((k) => k in (output as object));
  if (!error_salida && !ok) error_salida = "faltan claves del contrato";
  // Misma forma que una fila normalizada de evaluacion/score.py
  console.log(JSON.stringify({ output: error_salida ? null : output, tool_calls: [...llamadas.values()],
    meta: { asentado, error_salida, texto_final: texto } }, null, 2));
  process.exitCode = error_salida ? 1 : 0;
} finally {
  clearTimeout(temporizador);
  baja();
  session.dispose();
}
