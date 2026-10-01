# Incidente INC-001 — Ejecución sin respuesta final en c01 (ejemplo resuelto)

## Impacto

Durante una batería de desarrollo, c01 terminó sin JSON. No hubo efectos externos: la única herramienta disponible es de lectura. Duración ≈0,5 s. Sin exposición de datos (catálogo sintético).

## Evidencia

Traza `trazas/B-guion-bucle-dev-r1/c01.jsonl`: siete `tool_execution_start/end` de `lookup_document` d-001 (`guion-1`…`guion-7`); las seis primeras con `isError: false` y la séptima con `isError: true` y el texto «Presupuesto agotado: 6 llamadas por ejecución». Último `message_end` del asistente con `stopReason: "toolUse"`. `agent_settled` presente. Fila normalizada: `output: null`, `meta.error_salida: "sin respuesta final del asistente"`, `meta.estado_rpc: "completado"`.

## Contención y recuperación

`presupuesto.ts` bloqueó la séptima llamada con `terminate: true` y el run se detuvo. No hay nada que restaurar. Se repitió el caso con `--guion auto`: `passed` verdadero.

## Causa

Confirmada: el modelo repitió la misma consulta sin producir respuesta (modo `bucle` del guion, activado para la práctica). Hipótesis descartada: fallo de la herramienta (todas las lecturas previas fueron correctas). Factor contribuyente: el estado RPC `completado` puede leerse erróneamente como éxito de la tarea.

## Cambio preventivo

Control ejecutable ya existente: presupuesto de llamadas. Nuevo: el informe de la batería distingue `estado_rpc` de `output` y cuenta como fallo todo caso sin salida válida (regresión: `test_bucle_detenido_sin_respuesta_final`). Responsable: autor del proyecto. «Mejorar el prompt» no se considera suficiente: un modelo real puede entrar en bucle igualmente.
