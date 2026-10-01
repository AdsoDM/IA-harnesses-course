// Control de ejecución para el harness documental: allowlist, presupuesto de
// llamadas y límite de turnos por ejecución. Pi no impone un máximo de pasos:
// si lo necesitas, lo implementa el host o una extensión como esta.
// Se carga de forma explícita (-e); no figura en el manifest del paquete para
// no bloquear herramientas en otras sesiones si instalas el paquete.
//
// Flags: --permitidas lookup_document  --max-llamadas 6  --max-turnos 8
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

function entero(valor: unknown, porDefecto: number): number {
  const n = typeof valor === "string" && valor.trim() !== "" ? Number(valor) : porDefecto;
  if (!Number.isInteger(n) || n < 1) throw new Error(`Límite inválido: ${String(valor)}`);
  return n;
}

export default function (pi: ExtensionAPI) {
  pi.registerFlag("permitidas", { type: "string", default: "lookup_document", description: "Herramientas permitidas, separadas por comas" });
  pi.registerFlag("max-llamadas", { type: "string", default: "6", description: "Máximo de llamadas a herramientas por ejecución" });
  pi.registerFlag("max-turnos", { type: "string", default: "8", description: "Máximo de turnos del modelo por ejecución" });

  let llamadas = 0;
  let turnos = 0;

  // Contadores por ejecución: se reinician al empezar cada run del agente.
  pi.on("agent_start", async () => {
    llamadas = 0;
    turnos = 0;
  });

  pi.on("tool_call", async (event) => {
    const permitidas = new Set(String(pi.getFlag("permitidas") ?? "").split(",").map((s) => s.trim()).filter(Boolean));
    const maxLlamadas = entero(pi.getFlag("max-llamadas"), 6);
    llamadas++;
    if (!permitidas.has(event.toolName)) {
      return { block: true, reason: `Herramienta no permitida por la política del curso: ${event.toolName}` };
    }
    if (llamadas > maxLlamadas) {
      // terminate pide no continuar tras este lote: evita que el modelo insista.
      return { block: true, reason: `Presupuesto agotado: ${maxLlamadas} llamadas por ejecución`, terminate: true };
    }
    return undefined;
  });

  pi.on("turn_end", async (_event, ctx) => {
    turnos++;
    if (turnos >= entero(pi.getFlag("max-turnos"), 8)) {
      ctx.abort(); // Parada del host: el resultado debe registrarse como no completado.
    }
  });
}
