// Demo de transporte y contrato. No realiza consulta documental.
// Verificado con tsc contra Pi 0.99.1. Requiere un modelo configurado (/login).
import { createAgentSession, SessionManager } from "@earendil-works/pi-coding-agent";

const { session } = await createAgentSession({
  cwd: process.cwd(),
  sessionManager: SessionManager.inMemory(),
  noTools: "all", // "all" desactiva todas las herramientas; "builtin", solo las integradas
});
try {
  console.error(JSON.stringify({ provider: session.model?.provider, model: session.model?.id }));
  await session.prompt('Devuelve únicamente el objeto JSON {"saludo":"hola"}.');
  const text = session.getLastAssistantText();
  if (!text) throw new Error("No hay respuesta final");
  const result: unknown = JSON.parse(text);
  if (!result || typeof result !== "object" || Array.isArray(result) ||
      Object.keys(result).length !== 1 || !("saludo" in result) || result.saludo !== "hola") {
    throw new Error("La respuesta incumple el contrato de saludo");
  }
  console.log(JSON.stringify(result));
} finally {
  session.dispose();
}
