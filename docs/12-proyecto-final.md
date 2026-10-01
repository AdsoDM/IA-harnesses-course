# 12 — Construir y defender el proyecto final

Tiempo: 8 horas. Objetivo: integrar capacidades y presentar resultados que otra persona pueda reproducir.

## Encargo

Construye un asistente de documentación para PR260101. Debe responder sobre un corpus sintético, citar IDs, usar la norma vigente, abstenerse cuando falte evidencia y bloquear acciones fuera de alcance. Consulta [los requisitos](../proyecto-final/README.md) y [la arquitectura inicial](../proyecto-final/arquitectura.md).

La opción base es una extensión Pi más plantilla de prompt, la extensión de presupuesto y el runner de evaluación del curso. Puedes integrar SDK/RPC si quieres practicar automatización, pero no reemplaces contratos claros por una interfaz vistosa. Una app completa, un almacén vectorial o varios agentes quedan como ampliaciones justificadas.

Piezas de partida verificadas con Pi 0.99.1: `catalogue.ts`, `presupuesto.ts`, `respuesta-documental.md`, `cliente_rpc.py`, `ejecutar_casos.py`, `normalizar_pi.py` y `score.py`. Tu trabajo es decidir, justificar y medir; no reescribirlas desde cero.

## Desarrollo por incrementos

1. Fija contrato y baseline. Ejecuta A y B con el modelo de guion: el pipeline debe dar 3/12 y 12/12. Si no, depura el harness antes de gastar inferencia.
2. Añade catálogo y evidencia con tu modelo real. Demuestra una llamada real y un resultado en la traza.
3. Añade regla de vigencia y rechazo de inyección. Ejecuta casos negativos y el modo `obediente` como control.
4. Ejecuta desarrollo con el runner. Identifica fallos por componente: modelo, prompt, herramienta, harness o evaluador.
5. Congela configuración (commit), ejecuta reservados y repeticiones, registra coste y tiempos.
6. Redacta el informe, completa la revisión humana y demuestra cancelación (`--plazo`) o parada por presupuesto.

Cada incremento termina en commit. No cambies simultáneamente fuente, modelo y prompt si quieres explicar la mejora. Si cambias el contrato, actualiza dataset y evaluador con una decisión documentada.

## Qué cuenta como evidencia

Una salida factual con fuente y llamada real; una negativa sin efectos; una ejecución con error correctamente reportado; versiones y comandos de reproducción. Una captura bonita o una frase como «funciona bien» es insuficiente. Incluye fragmentos sintéticos y no credenciales.

## Demostración de cinco minutos

Primero explica en una frase qué problema resuelve. Muestra el flujo y una decisión de arquitectura. Ejecuta una pregunta de retención, una pregunta sin respuesta en el corpus y una petición de borrar/publicar. Enseña la traza y el resultado del evaluador. Cierra con un fallo conocido y la próxima mejora concreta.

Guion sugerido (≈ 5 min): 30 s problema y contrato → 60 s arquitectura y ADR → 90 s tres casos en vivo con `cliente_rpc.py` (acierto, abstención, bloqueo) → 60 s traza y `score.json` → 30 s un modo de fallo (`--guion bucle` o `lento`) y cómo se detiene → 30 s límites y siguiente paso.

Si una llamada falla durante la demo, no ocultes el fallo: muestra que el sistema conserva el estado y lo comunica. Puedes presentar resultados anteriores identificados como tales, con el commit que los produjo.

## Extensiones tras la base

Una adaptación a BI puede consultar definiciones de indicadores y trazabilidad de una base SQLite con conexión de solo lectura. Una adaptación de programación puede revisar cambios y ejecutar tests en un entorno limitado. Ambas necesitan datasets propios: el conjunto documental no demuestra corrección de SQL ni de código.

La búsqueda vectorial solo merece añadirse si el corpus o el vocabulario muestran límites de búsqueda léxica. La memoria persistente merece añadirse cuando una tarea necesita continuidad comprobable. Cada capacidad debe traer prueba, presupuesto y control de acceso.

## Criterio de dominio

Deberías poder explicar: qué decide el modelo, qué decide el harness, por qué una herramienta puede fallar, cómo sabes que se consultó una fuente y qué no garantiza tu evaluación. Si no puedes responder, vuelve al módulo correspondiente y mejora el informe.

## Errores frecuentes

- Cambiar prompt, modelo y herramienta en el mismo commit y atribuir la mejora a uno de ellos.
- Entregar solo el `score.json` sin la revisión humana ni las trazas que lo respaldan.
- Dejar marcadores `REEMPLAZAR` o datos personales en configuraciones confirmadas.
- Presentar la versión con modelo de guion como proyecto validado con IA.

## Autoevaluación

1. ¿Qué decide el modelo y qué decide el harness en tu proyecto?
2. ¿Cómo demuestras que una respuesta se apoyó en una consulta real?
3. ¿Qué cambiarías primero si B falla c09 de forma intermitente?
4. ¿Qué evidencia presentarías de que una acción prohibida no ocurrió?
5. ¿Qué queda sin medir en tu evaluación?

Respuestas: [clave](../soluciones/autoevaluacion.md#12).

Práctica: [laboratorio 12](../laboratorios/12-proyecto.md). Entrega con [informe final](../plantillas/informe-final.md), [rúbrica](../evaluacion/rubrica.md) y [plan de hitos](../proyecto-final/hitos.md).
