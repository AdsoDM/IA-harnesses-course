# 03 — Construir el bucle de un harness en Python

Tiempo: 4 horas. Objetivo: recorrer una llamada de herramienta y demostrar paradas controladas sin usar un proveedor.

## El ejemplo ejecutable

Abre [harness.py](../ejemplos/mini-harness/harness.py). Su modelo es una simulación programada: propone sumar dos enteros y después emite el resultado. No razona ni mide capacidad de una IA; permite observar el contrato del harness sin red ni costes.

```powershell
python .\ejemplos\mini-harness\harness.py
python .\ejemplos\mini-harness\harness.py --scenario invalid
python .\ejemplos\mini-harness\harness.py --scenario loop --max-steps 3
python -m unittest discover -s .\ejemplos\mini-harness -v
```

Cada evento incluye `run_id` y número de paso. Una llamada tiene `id`, nombre y argumentos; el resultado conserva ese ID para relacionar petición y respuesta. El modelo nunca invoca directamente la función Python: entrega datos al dispatcher.

## Sigue una ejecución

1. El harness registra la entrada.
2. El modelo simulado devuelve `tool_call` para `sumar`.
3. El dispatcher valida nombre y estructura exacta de argumentos.
4. La herramienta devuelve el entero calculado.
5. El harness incorpora un `tool_result` al historial.
6. El modelo emite una respuesta final; el harness valida su forma y termina.

El caso inválido demuestra que un JSON bien formado puede incumplir el contrato. `{"a":"2","b":3}` es JSON correcto y entrada incorrecta para esta herramienta. La validación vive antes del efecto. El caso de bucle demuestra que una herramienta exitosa no garantiza que el agente termine.

## Estado y errores

La lista de mensajes representa contexto; la traza representa evidencia. Pueden solaparse, pero tienen consumidores distintos. El modelo necesita el resultado para continuar. Una persona necesita IDs, estados y tiempos para depurar. No le envíes al modelo secretos o toda la infraestructura de logging porque aparezcan en la traza.

En el ejemplo, una entrada inválida produce un resultado `ok: false`. El harness permite que el modelo reaccione, pero el límite total evita reparaciones interminables. La política de producción debe distinguir un error de contrato, una cuota temporal y un efecto parcialmente realizado. Volver a intentar un pago o una escritura después de un timeout puede duplicar el efecto.

El ejemplo valida también una respuesta final; no acepta cualquier objeto como éxito. Esa validación formal aún no prueba que la respuesta sea verdadera. En módulos posteriores añadirás evidencia documental y evaluación semántica.

## Límites reales del ejemplo

`max_steps` limita propuestas del modelo. No es un timeout duro de una herramienta bloqueada. Una comprobación de tiempo alrededor de una llamada no la interrumpe mientras está bloqueada; para eso necesitas cancelación cooperativa o un proceso con supervisión. Tampoco hay persistencia, concurrencia o adaptación de API real. Son límites deliberados que debes registrar.

## Leer una traza real

Esta es la salida (recortada) del escenario normal. Cada evento lleva el mismo `run_id`; el `id` de la propuesta reaparece como `tool_call_id` del resultado:

```json
{"run_id": "5ae4…", "step": 1, "event": "proposal",
 "data": {"type": "tool_call", "id": "call-1", "name": "sumar", "arguments": {"a": 2, "b": 3}}}
{"run_id": "5ae4…", "step": 1, "event": "tool_result", "tool_call_id": "call-1",
 "result": {"ok": true, "data": {"value": 5}}}
{"run_id": "5ae4…", "step": 2, "event": "proposal", "data": {"type": "final", "answer": "5"}}
```

Para reconstruir qué pasó, lee en este orden: ¿qué propuso el modelo?, ¿qué validó el dispatcher?, ¿qué devolvió la herramienta?, ¿qué concluyó el modelo con ese resultado? La respuesta final es lo último que se mira, no lo primero.

## Del ejemplo a un harness documental

[harness_documental.py](../ejemplos/mini-harness/harness_documental.py) aplica el mismo bucle al catálogo del curso con cuatro diferencias que aparecen en cualquier harness real:

1. **Varias llamadas por turno.** Los proveedores pueden proponer varias herramientas en una misma respuesta; el bucle las ejecuta y devuelve un resultado por ID.
2. **Presupuesto de llamadas** además de límite de pasos: un turno puede contener muchas llamadas.
3. **Contrato de salida** explícito: la respuesta final debe ser un objeto JSON `{status, answer, sources}`.
4. **Fila normalizada**: `run` devuelve `output`, `tool_calls` y `meta`, el mismo formato que usará el evaluador en el módulo 10.

```powershell
python .\ejemplos\mini-harness\harness_documental.py "¿Cuál es la retención vigente de backups?"
python .\ejemplos\mini-harness\harness_documental.py --evaluar --split dev
python -m unittest discover -s .\ejemplos\mini-harness -v
```

Su `ModeloReglas` es otro doble de prueba: reglas fijas, sin red. En el [módulo 03b](03b-proveedor-real.md) lo sustituirás por un adaptador a un proveedor real sin cambiar el bucle.

## Ejercicio

Añade una herramienta `multiplicar` sin usar `eval`. Define esquema, validación, resultado y casos negativos. No introduzcas un intérprete de código arbitrario para resolver dos operaciones. Pista de diseño: un registro `nombre → función` evita tocar el bucle cada vez que añades una herramienta. Solución de referencia, para después: [lab03_multiplicar.py](../soluciones/codigo/lab03_multiplicar.py).

## Errores frecuentes

- Usar `isinstance(x, int)`: acepta `True`, porque `bool` es subclase de `int`.
- Convertir el error de validación en excepción que rompe el bucle: el modelo no puede reaccionar y la traza pierde el motivo.
- Reutilizar IDs de llamada: dos resultados con el mismo ID impiden saber qué respondió a qué.
- Tomar `max_steps` por un timeout: limita propuestas, no interrumpe una función bloqueada.

## Autoevaluación

1. ¿Por qué `{"a":"2","b":3}` es JSON válido y, aun así, entrada inválida?
2. En el escenario `loop`, ¿por qué el estado es `step_limit` si todas las herramientas tuvieron éxito?
3. ¿Qué información va al modelo y cuál solo a la traza?
4. ¿Qué ocurre con `--max-steps 1` en el escenario normal y por qué?
5. ¿Por qué no se reintenta automáticamente una escritura tras un timeout?

Respuestas: [clave](../soluciones/autoevaluacion.md#03).

Aceptación: reconstruir la secuencia usando IDs, rechazar una cadena y demostrar el límite de pasos. Práctica: [laboratorio 03](../laboratorios/03-bucle.md). Continúa con [proveedor real](03b-proveedor-real.md).
