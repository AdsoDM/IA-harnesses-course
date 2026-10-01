# Experimento — EXP-A-B-guion (ejemplo resuelto)

> Ejemplo con el **modelo de guion**: muestra cómo redactar el informe. Sus números describen el pipeline con un doble de prueba, no un modelo de IA. Tu informe real debe usar tu modelo y tus repeticiones.

## Pregunta

¿Exigir la consulta y la regla de vigencia en la plantilla (B) mejora el cumplimiento frente a pedir solo el contrato JSON (A)?

## Diseño

Variable cambiada: instrucciones (`contrato-minimo.md` frente a `respuesta-documental.md`). Fijas: Pi 0.99.1, modelo `curso/guion` modo `auto`, catálogo, `lookup_document` como única herramienta, `presupuesto.ts` (6 llamadas, 8 turnos), plazo 120 s, sesión nueva por caso. Conjunto: los 12 casos (en un informe real: dev para ajustar, holdout una vez). Repeticiones: 1 (el guion es determinista; con un modelo real, al menos 3).

## Configuración

Commit: el de tu rama. Configuraciones: `evaluacion/configuraciones/A-guion.json` y `B-guion.json`. Coste: 0 (no hay proveedor). Caché: no aplica.

## Resultados

| Configuración | Casos/repeticiones | Aciertos | Rechazos correctos | Errores | Latencia p50/p95 | Coste |
| --- | --- | --- | --- | --- | --- | --- |
| A | 12/1 | 3 | 3 de 3 bloqueos | 0 | ≈0,4 s / no significativo | 0 |
| B | 12/1 | 12 | 3 de 3 bloqueos | 0 | ≈0,4 s / no significativo | 0 |

Detalle de A: `evidence` 3/12 (ninguna respuesta factual consultó), `terms` 7/12 (datos obsoletos: 15 días, 03:00 UTC, 100 EUR), `status` 10/12 (c05 y c10 inventan teléfono y correo en lugar de abstenerse). c04 acierta «equipo Atlas» por casualidad y falla igualmente por falta de evidencia.

## Interpretación

La diferencia se explica por completo por la regla del guion: consulta solo si se le ordena. Con un modelo real el efecto esperado va en la misma dirección, pero su tamaño debe medirse: un modelo puede consultar sin que se lo pidan, o ignorar la orden. La criba no revisó el significado: la revisión humana confirmó que en B c09 la respuesta afirma que prevalece d-001.

## Decisión

Conservar B como baseline del proyecto. Repetir con el modelo real (3 repeticiones, dev) antes de mirar holdout.
