# 11 — Fallos y recuperación

Duración: 2,5 horas. Empieza con simulación offline; las pruebas con Pi usan el modelo de guion.

1. Ejecuta el escenario de bucle Python y prueba un límite bajo.
2. Produce un resultado de evaluación inválido y comprueba que el proceso informa error sin premiarlo.
3. Con Pi: ejecuta los tres comandos del módulo (`bucle`, `lento --plazo 1`, `obediente`). Para cada uno, identifica el control efectivo (herramientas declaradas, `tool_call`, `turn_end`, plazo del host) y el estado final registrado en `meta`.
4. Diseña la cancelación del host: plazo, abort, gracia, terminación y verificación de efectos. Compárala con `ClientePiRpc.ejecutar_prompt` y `cerrar`.
5. Escribe un informe de incidente con una causa confirmada y una hipótesis diferenciadas, usando uno de los fallos del paso 3.
6. Redacta una política: fuentes sintéticas, herramienta documental, ninguna publicación, límites y trazas sin secretos. Indica qué parte aplica el código y cuál es solo instrucción.

Aceptación: identificas el control efectivo y sus límites; no confundes carpeta con sandbox; una tarea interrumpida o sin respuesta final no se etiqueta como completada. Entrega `entregas/11-operacion.md` y el incidente. Ejemplo de referencia: [incidente resuelto](../soluciones/lab11-incidente-ejemplo.md).

Ampliación: ejecuta todo Pi dentro de un contenedor/VM con datos mínimos. Describe montajes y acceso de red. Usa la documentación oficial de la plataforma que elijas y `docs/containerization.md` de Pi; el curso no incluye una receta universal verificada para todos los Windows.

Lección: [módulo correspondiente](../docs/11-operacion.md). Autocorrección: [guía de soluciones](../soluciones/guia.md).
