# Programa y método de estudio

El resultado esperado es que puedas explicar y demostrar un harness que usa herramientas, respeta un contrato, deja evidencias y se compara con una referencia. El curso no entrena pesos de un modelo; construye el sistema que lo rodea.

## Ruta principal — 58 horas

| Semana orientativa | Módulos | Entregable |
| --- | --- | --- |
| 1 | 01 y 02, inicio de 03 | Contrato y entorno |
| 2 | 03 y 03b | Bucle, traza y adaptador de proveedor |
| 3 | 04 y 05 | Pi y contexto |
| 4 | 06 y comienzo de 07 | Herramienta validada |
| 5 | 07 y comienzo de 08 | Extensión y controles |
| 6 | 08 y 09 | Integración |
| 7 | 10 y comienzo de 11 | Evaluación |
| 8 | 11 y comienzo de 12 | Controles y arquitectura |
| 9–10 | 12 | Demostración final |

| Nº | Lección | Horas | Necesita |
| --- | --- | --- | --- |
| 01 | [Fundamentos](01-fundamentos.md) | 2 | Nada |
| 02 | [Entorno Windows](02-entorno-windows.md) | 3 | Python, Node, Git; Pi |
| 03 | [Bucle Python](03-bucle-python.md) | 4 | Python |
| 03b | [Proveedor real](03b-proveedor-real.md) | 4 | Python; opcional: API o modelo local |
| 04 | [Uso de Pi](04-uso-pi.md) | 4 | Pi; modelo de guion o real |
| 05 | [Contexto y memoria](05-contexto-memoria.md) | 4 | Pi opcional |
| 06 | [Herramientas](06-herramientas.md) | 5 | Node |
| 07 | [Extensiones](07-extensiones-pi.md) | 5 | Pi; modelo de guion o real |
| 08 | [SDK y RPC](08-sdk-rpc.md) | 5 | Pi, npm; modelo de guion o real |
| 09 | [MCP y composición](09-mcp.md) | 4 | Pi, npm; modelo real para la conexión |
| 10 | [Evaluación](10-evaluacion.md) | 5 | Python; Pi para la batería |
| 11 | [Operación](11-operacion.md) | 5 | Python; Pi |
| 12 | [Proyecto final](12-proyecto-final.md) | 8 | Todo lo anterior |

## Tres niveles de evidencia

El curso distingue siempre qué demuestra cada prueba:

| Nivel | Qué ejecutas | Qué demuestra | Qué NO demuestra |
| --- | --- | --- | --- |
| Offline | Tests Python/Node, `pi_falso.py`, servidor HTTP falso | Contratos deterministas del código | Que Pi cargue tu código |
| Pi + modelo de guion | Pi real con [el proveedor simulado](../ejemplos/pi-package/dobles/README.md) | Carga, herramientas, eventos, RPC, evaluación y cancelación en el runtime real | Cómo decide un modelo de IA |
| Pi + modelo real | Tu proveedor o un modelo local | Comportamiento observado en esas condiciones | Superioridad general o fiabilidad futura |

El **modelo de guion** es un doble de prueba: sigue reglas fijas sobre las preguntas del curso y no cuesta dinero. Úsalo para depurar el harness antes de gastar inferencia y para provocar fallos (respuesta de memoria, JSON roto, bucle, lentitud, obediencia a una inyección) de forma reproducible.

## Rutas alternativas

- **Sin credenciales todavía:** completa 01–08 y 10–11 con el modelo de guion y deja pendiente, etiquetada, la parte de modelo real. El laboratorio 09 queda como diseño hasta tener un modelo.
- **Sin Pi (npm bloqueado por la organización):** usa el harness Python de [03b](03b-proveedor-real.md) con un modelo local compatible y el mismo evaluador. Registra la limitación en `VALIDACION.md` de tu rama.
- **Con experiencia previa:** haz el diagnóstico de [PROGRESO.md](../PROGRESO.md), lee las secciones «Errores frecuentes» y responde a la autoevaluación de cada módulo; si aciertas, pasa a su laboratorio.

## Puente opcional — seis horas

Dedica dos horas a Git: crea un repositorio de prueba, confirma un archivo, cámbialo en una rama y revisa el diff. Dos a Python: funciones, diccionarios, excepciones, JSON, `unittest` y `subprocess`. Dos a TypeScript: tipos de objetos, módulos ES, `Promise`, `async/await` y `try/finally`. Usa [el puente](puente-programacion.md) y sus ejercicios.

## Método por módulo

1. Lee la lección y dibuja el flujo con tus palabras.
2. Ejecuta el caso mínimo con datos sintéticos.
3. Introduce un fallo deliberado: argumento inválido, dato ausente o límite de pasos.
4. Explica la causa usando la traza y una comprobación independiente.
5. Responde a la autoevaluación sin mirar la [clave](../soluciones/autoevaluacion.md).
6. Confirma informe y cambios en Git.

Los ejercicios sin modelo real no tienen coste de inferencia. Los ejercicios con un proveedor pueden tener coste o cuotas. Antes de una batería, ejecuta un caso y fija tu límite de gasto. Este curso no presupone que una suscripción cubra cualquier API.

## Comprobación completa

`python scripts/verificar_todo.py` ejecuta todas las pruebas offline, el comprobador documental y el de consistencia. Con Pi instalado, `python scripts/verificar_todo.py --con-pi` añade la batería A/B real con el modelo de guion (sin credenciales ni red).

## Evaluación del aprendizaje

Cada práctica tiene aceptación concreta y [orientación de solución](../soluciones/guia.md). El proyecto final se puntúa con [la rúbrica](../evaluacion/rubrica.md). Una prueba offline demuestra propiedades del código determinista; una batería con un modelo demuestra comportamiento observado en esas condiciones. Conserva esa distinción en todo informe.
