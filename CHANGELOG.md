# Historial

## 1.1 — 2026-09-30

Verificación y corrección
- Verificado contra Pi 0.99.1 instalado: `--help`, tipos con `tsc`, carga y ejecución de la extensión, flujo JSON, RPC, cancelación, SDK y MCP (véase VALIDACION.md).
- Corregido `ejemplos/sdk/run.ts`: `noTools: true` → `noTools: "all"` (error de tipos en 0.99.1).
- Lección 09 y laboratorio 09: exposición por defecto `codemode`, `toolExposure` para dejar solo lecturas, confianza de proyecto para `.pi/mcp.json`.
- Lección 04: modo print implícito al redirigir, confianza de proyecto en modos no interactivos, selección de herramientas (`--tools` sustituye la lista).
- Lección 05: carga de skills mediante `read` o `/skill:nombre`; `AGENTS.md` se carga sin confianza de proyecto.
- Evaluación: `allowed_sources` para fuentes adicionales pertinentes (c12).
- Laboratorio 05: eliminada una referencia a una herramienta ajena al curso.

Nuevo código
- `ejemplos/pi-package/dobles/modelo-guion.ts`: proveedor simulado para Pi con siete modos, sin red ni credenciales.
- `ejemplos/pi-package/extensions/presupuesto.ts`: allowlist, máximo de llamadas y de turnos.
- `ejemplos/rpc/cliente_rpc.py` y `pi_falso.py`: cliente RPC con máquina de estados y Pi simulado para pruebas; modo tolerante en `framing.py`.
- `evaluacion/normalizar_pi.py`, `ejecutar_casos.py`, `configuraciones/` y `trazas-ejemplo/`: pipeline de evaluación A/B de extremo a extremo.
- `ejemplos/sdk/run-documental.ts`: consulta documental con SDK, eventos, plazo y abort.
- `ejemplos/mini-harness/harness_documental.py`, `proveedor_openai.py` y `catalogo.json`: harness documental Python y adaptador Chat Completions.
- `scripts/verificar_todo.py` y `scripts/check_consistencia.py`.
- `listDocuments()` en el núcleo del catálogo.

Contenido
- Módulo y laboratorio 03b: conectar el bucle a un proveedor real (58 horas en total).
- Todas las lecciones: errores frecuentes y autoevaluación; ejemplos resueltos en 01, 03, 04, 07, 08, 10 y 11.
- Soluciones de referencia: clave de autoevaluación, contrato, `multiplicar`, `search_documents`, skill, ADR, experimento e incidente.
- Plantilla de revisión humana. Glosario y fuentes ampliados.

## 1.0 — 2026-09-30

- Curso de 12 módulos y 12 laboratorios con ruta Windows/PowerShell.
- Harness Python con modelo simulado y pruebas sin red.
- Catálogo sintético y extensión Pi; ejemplo SDK y guía RPC.
- Evaluador de 12 casos, proyecto final, rúbrica y plantillas Git.
- Fuentes oficiales consultadas y limitaciones de validación explícitas.
