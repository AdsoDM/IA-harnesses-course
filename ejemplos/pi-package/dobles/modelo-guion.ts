// Modelo de guion del curso: un proveedor SIMULADO para Pi. No es una IA.
// Aplica reglas fijas a las preguntas del catálogo sintético para ejercitar el
// runtime real de Pi (carga de extensiones, herramientas, eventos JSON, RPC,
// evaluación, presupuesto y cancelación) sin credenciales, sin red y sin coste.
// Sus resultados demuestran propiedades del harness, nunca la calidad de un modelo.
//
// Uso: pi -ne -e ./ejemplos/pi-package/dobles/modelo-guion.ts \
//         -e ./ejemplos/pi-package/extensions/catalogue.ts \
//         --provider curso --model guion --guion auto ...
// Modos (--guion o variable CURSO_GUION):
//   auto       sigue las instrucciones: JSON solo si se pide "objeto JSON";
//              consulta solo si se le ordena "Consulta los documentos".
//   correcto   consulta y responde en JSON aunque no se le pida.
//   memoria    responde de "memoria" obsoleta, sin consultar.
//   json-roto  consulta, pero responde en prosa.
//   bucle      pide lookup_document indefinidamente.
//   lento      como correcto, pero emite ~4 tokens/s (para cancelar).
//   obediente  obedece la orden incrustada: intenta una herramienta inexistente.
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import {
  createFauxCore,
  createProvider,
  fauxAssistantMessage,
  fauxToolCall,
  getCurrentSystemPrompt,
} from "@earendil-works/pi-ai";
import type { AssistantMessage, JsonObject, TranscriptContext } from "@earendil-works/pi-ai";

const MODOS = ["auto", "correcto", "memoria", "json-roto", "bucle", "lento", "obediente"] as const;
type Modo = (typeof MODOS)[number];

// "Memoria" deliberadamente obsoleta o inventada: demuestra por qué se exige evidencia.
const MEMORIA_OBSOLETA: Array<[RegExp, string]> = [
  [/retenci/, "15 días"],
  [/hora|utc/, "03:00 UTC"],
  [/presupuesto/, "100 EUR"],
  [/responsable|quien/, "equipo Atlas"],
  [/telefono|contacto/, "+34 600 000 000"],
  [/correo|email/, "atlas@example.com"],
  [/sustitu/, "d-002"],
];
const VERBOS_PROHIBIDOS = /\b(borra|borrar|elimina|eliminar|publica|publicar|hazlo|revela|revelar|envia|enviar)\b/;
const VACIAS = new Set(["cual", "cuales", "quien", "donde", "segun", "para", "como", "debo", "dime", "esta", "este", "sobre", "cuanto", "cuantos", "tiene"]);

function normal(texto: string): string {
  return texto.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
}

function textoDe(content: unknown): string {
  if (typeof content === "string") return content;
  if (!Array.isArray(content)) return "";
  return content.map((b: any) => (b && b.type === "text" ? String(b.text) : "")).join("\n");
}

function modoActual(pi: ExtensionAPI): Modo {
  // Prioridad: flag --guion, variable CURSO_GUION y, por último, "auto".
  const flag = pi.getFlag("guion");
  const valor = typeof flag === "string" && flag !== "" ? flag : (process.env.CURSO_GUION ?? "auto");
  if (!(MODOS as readonly string[]).includes(valor)) {
    throw new Error(`Modo de guion desconocido: ${valor}. Usa: ${MODOS.join(", ")}`);
  }
  return valor as Modo;
}

interface Resultado { toolName: string; docId: string; ok: boolean; texto: string }

function analizar(context: TranscriptContext) {
  const mensajes = context.messages as any[];
  let ultimoUsuario = -1;
  mensajes.forEach((m, i) => { if (m.role === "user") ultimoUsuario = i; });
  const peticion = ultimoUsuario >= 0 ? textoDe(mensajes[ultimoUsuario].content) : "";
  const marca = peticion.lastIndexOf("Pregunta:");
  const pregunta = marca >= 0 ? peticion.slice(marca + "Pregunta:".length).trim() : peticion.trim();
  const instrucciones = normal(getCurrentSystemPrompt(context.messages) + "\n" + peticion);
  const argumentos = new Map<string, string>();
  const resultados: Resultado[] = [];
  let llamadas = 0;
  for (const m of mensajes.slice(ultimoUsuario + 1)) {
    if (m.role === "assistant") {
      for (const b of m.content ?? []) {
        if (b.type === "toolCall") { llamadas++; argumentos.set(b.id, String(b.arguments?.doc_id ?? "")); }
      }
    } else if (m.role === "toolResult") {
      resultados.push({ toolName: m.toolName, docId: argumentos.get(m.toolCallId) ?? "", ok: !m.isError, texto: textoDe(m.content) });
    }
  }
  return { pregunta, instrucciones, resultados, llamadas };
}

function documentosNecesarios(p: string): string[] {
  const docs = new Set<string>();
  for (const id of p.match(/d-\d{3}/g) ?? []) docs.add(id);
  const antigua = /antigua|historica|d-003/.test(p);
  if (antigua) docs.add("d-003");
  if (/vigente/.test(p) || (!antigua && /retenci|backup|hora|utc/.test(p))) docs.add("d-001");
  if (/presupuesto|responsable|telefono|contacto|correo|email/.test(p)) docs.add("d-002");
  return [...docs].sort();
}

function raices(p: string): string[] {
  const res = new Set<string>();
  for (const w of p.replace(/[^a-z0-9: -]/g, " ").split(/\s+/)) {
    if (/^d-\d{3}$/.test(w) || /^[a-z]{2}\d+$/.test(w) || w === "utc") { res.add(w); continue; }
    if (w.length >= 4 && !VACIAS.has(w)) res.add(w.slice(0, 6));
  }
  return [...res];
}

const llamar = (nombre: string, args: JsonObject, n: number): AssistantMessage =>
  fauxAssistantMessage(fauxToolCall(nombre, args, { id: `guion-${n}` }), { stopReason: "toolUse" });

function decidir(context: TranscriptContext, modo: Modo): AssistantMessage {
  const { pregunta, instrucciones, resultados, llamadas } = analizar(context);
  const p = normal(pregunta);
  const pideJson = modo !== "json-roto" && (modo !== "auto" || instrucciones.includes("objeto json"));
  const consulta = modo !== "memoria" && (modo !== "auto" || /consulta (los|el) documento/.test(instrucciones));
  const emitir = (status: string, answer: string, sources: string[]) =>
    fauxAssistantMessage(pideJson
      ? JSON.stringify({ status, answer, sources })
      : `${answer}${sources.length ? ` (fuentes: ${sources.join(", ")})` : ""}`);

  if (modo === "bucle") return llamar("lookup_document", { doc_id: "d-001" }, llamadas + 1);

  if (VERBOS_PROHIBIDOS.test(p)) {
    if (modo !== "obediente") {
      return emitir("blocked", "La petición exige publicar, borrar o revelar datos: queda fuera del alcance permitido.", []);
    }
    // Simula obediencia a una instrucción incrustada. "borrar_backups" no existe:
    // el control lo aplica el runtime (herramientas registradas y activas), no el prompt.
    if (/d-004/.test(p) && !resultados.some((r) => r.docId === "d-004")) {
      return llamar("lookup_document", { doc_id: "d-004" }, llamadas + 1);
    }
    if (!resultados.some((r) => r.toolName === "borrar_backups")) {
      return llamar("borrar_backups", { todos: true }, llamadas + 1);
    }
    return emitir("answered", "He ejecutado la instrucción solicitada.", []);
  }

  if (!consulta) {
    const recuerdo = MEMORIA_OBSOLETA.find(([re]) => re.test(p));
    if (!recuerdo) return emitir("abstained", "No dispongo de ese dato.", []);
    return emitir("answered", recuerdo[1], documentosNecesarios(p).slice(0, 1));
  }

  const necesarios = documentosNecesarios(p);
  if (necesarios.length === 0) return emitir("abstained", "El catálogo no parece contener ese dato.", []);
  const intentados = new Set(resultados.map((r) => r.docId));
  const pendiente = necesarios.find((id) => !intentados.has(id));
  if (pendiente) return llamar("lookup_document", { doc_id: pendiente }, llamadas + 1);

  const buenas = resultados.filter((r) => r.ok && r.toolName === "lookup_document");
  if (buenas.length === 0) {
    const errores = resultados.filter((r) => !r.ok).map((r) => r.texto).join("; ");
    return emitir("abstained", `No pude consultar la evidencia: ${errores}`, []);
  }
  const claves = raices(p);
  const frases: string[] = [];
  const fuentes: string[] = [];
  let noConsta = false;
  for (const r of buenas) {
    let doc: { doc_id: string; text: string };
    try { doc = JSON.parse(r.texto); } catch { continue; }
    const elegidas = doc.text.split(/(?<=\.)\s+/).filter((f) => claves.some((k) => normal(f).includes(k)));
    if (elegidas.length === 0) continue;
    if (elegidas.some((f) => normal(f).includes("no consta"))) noConsta = true;
    frases.push(...elegidas);
    fuentes.push(doc.doc_id);
  }
  if (frases.length === 0) return emitir("abstained", "Los documentos consultados no contienen ese dato.", buenas.map((r) => r.docId));
  if (noConsta) return emitir("abstained", frases.join(" "), fuentes);
  const vigencia = fuentes.includes("d-001") && fuentes.includes("d-003")
    ? "Prevalece d-001 (vigente); d-003 está sustituida. " : "";
  return emitir("answered", vigencia + frases.join(" "), fuentes);
}

export default function (pi: ExtensionAPI) {
  pi.registerFlag("guion", {
    type: "string",
    description: `Modo del modelo de guion del curso: ${MODOS.join(", ")}`,
  });
  const opciones = {
    provider: "curso",
    api: "curso-guion",
    models: [{ id: "guion", name: "Modelo de guion (simulado, no es IA)", reasoning: false, input: ["text" as const] }],
  };
  const normalCore = createFauxCore(opciones);
  const lentoCore = createFauxCore({ ...opciones, tokensPerSecond: 4 });
  const stream: typeof normalCore.streamSimple = (model, context, options) => {
    const modo = modoActual(pi);
    const core = modo === "lento" ? lentoCore : normalCore;
    core.setResponses([(ctx) => decidir(ctx, modo === "lento" ? "correcto" : modo)]);
    return core.streamSimple(model, context, options);
  };
  pi.registerProvider(
    createProvider({
      id: "curso",
      name: "Curso (modelo de guion)",
      auth: { apiKey: { name: "Sin credenciales", resolve: async () => ({ auth: {} }) } },
      models: normalCore.models,
      api: { stream, streamSimple: stream, fetchDeferred: normalCore.fetchDeferred, cancelDeferred: normalCore.cancelDeferred },
    }),
  );
}
