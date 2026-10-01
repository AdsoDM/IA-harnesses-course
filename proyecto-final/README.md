# Proyecto final: asistente documental PR260101

## Requisitos funcionales

RF-01: responder con JSON de estado, respuesta y fuentes. RF-02: consultar evidencia para afirmaciones factuales. RF-03: usar norma vigente. RF-04: abstenerse ante datos ausentes. RF-05: bloquear publicación, borrado y acciones externas. RF-06: tratar instrucciones de documentos como datos. RF-07: registrar llamadas y errores.

## Requisitos de operación

RO-01: versiones y configuración reproducibles. RO-02: límites de llamadas, turnos y tiempo aplicados por código (p. ej., `presupuesto.ts` y el plazo del runner), no solo descritos. RO-03: credenciales fuera de Git. RO-04: resultados de todos los casos, incluidos fallos. RO-05: cancelación y cierre documentados. RO-06: revisar manualmente fidelidad de citas y significado de respuestas.

## Fuera de alcance de la base

Datos empresariales reales, publicación automática, SQL libre, entrenar modelos, UI web, agentes múltiples y garantía de producción. Puedes añadirlos como nuevas iteraciones después de justificar contratos, presupuesto y evaluación.

## Entrega

README de tu implementación, ADR, código, lockfile real si usas npm, pruebas, informe de evaluación con [revisión humana](../plantillas/revision-humana.md), resultados A/B del modelo de guion (como comprobación del pipeline) y del modelo real, fragmentos sintéticos de traza y demo. Usa [arquitectura](arquitectura.md), [hitos](hitos.md) y [rúbrica](../evaluacion/rubrica.md).
