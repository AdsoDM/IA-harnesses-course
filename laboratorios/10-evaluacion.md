# 10 — Comparación controlada

Duración: 3 horas. El evaluador se prueba offline; el pipeline completo, con Pi y el modelo de guion; la comparación real, con tu modelo.

```powershell
python .\evaluacion\score.py .\evaluacion\resultados-demo.jsonl
python -m unittest discover -s .\evaluacion -v
```

1. Lee el contrato en `evaluacion/README.md` y prueba la fixture.
2. Cambia un término, una fuente y una llamada en una copia dentro de `resultados/`. Comprueba que bajan las métricas correspondientes.
3. Ejecuta A-guion y B-guion con el runner. Comprueba 3/12 y 12/12 y explica, caso por caso, por qué falla A. Abre una traza de `trazas/` y localiza la evidencia que falta.
4. Ejecuta los modos `memoria`, `json-roto`, `obediente`, `bucle` y `lento` (este con `--plazo 1`) sobre c01 y c07. Completa una tabla modo → métrica que falla → evidencia en la traza.
5. Con un modelo real: copia `A-real.json` y `B-real.json`, sustituye `REEMPLAZAR` por proveedor e ID exacto y ejecuta los ocho casos de desarrollo con `--repeticiones 3`.
6. Congela B (commit) y ejecuta los cuatro casos reservados sin retocar el prompt.
7. Revisa manualmente todas las respuestas con [la plantilla de revisión](../plantillas/revision-humana.md) y anota desacuerdos con la criba.

Aceptación: informe con todos los casos, condiciones fijas, errores incluidos y límites del evaluador. Los resultados del guion y de la fixture no cuentan como calidad de un modelo. Si solo has probado guion y fixture, decláralo.

Entregable: `entregas/10-evaluacion.md` con una comparación defendible. Usa la plantilla de experimento y evita hacer una afirmación estadística amplia con esta batería pequeña. Ejemplo de informe, para después: [experimento resuelto](../soluciones/lab10-experimento-ejemplo.md).

Lección: [módulo correspondiente](../docs/10-evaluacion.md). Autocorrección: [guía de soluciones](../soluciones/guia.md).
