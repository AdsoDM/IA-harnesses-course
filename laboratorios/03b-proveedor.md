# 03b — Adaptador a un proveedor real

Duración: 2,5 horas. La parte offline no necesita red; la conexión real necesita un servidor local compatible o una clave de API.

```powershell
python -m unittest discover -s .\ejemplos\mini-harness -v
python .\ejemplos\mini-harness\harness_documental.py --evaluar --split dev --salida .\resultados\py-reglas-dev.jsonl
python .\evaluacion\score.py .\resultados\py-reglas-dev.jsonl --split dev
```

1. Lee `proveedor_openai.py` y señala dónde se hace cada traducción: mensajes, herramientas, `arguments` y resultados.
2. En `test_documental.py`, localiza la prueba que comprueba el orden `system, user, assistant, tool` de la segunda petición. Explica por qué el `tool_call_id` es imprescindible.
3. Añade una prueba con **dos** `tool_calls` en la misma respuesta (d-001 y d-003). Comprueba que la siguiente petición contiene dos mensajes `tool` con los IDs correctos.
4. Añade una prueba para `finish_reason: "length"` y decide qué debe hacer el bucle con una respuesta cortada. Documenta la decisión.
5. Opcional con modelo: ejecuta la batería de desarrollo contra tu servidor local o proveedor y evalúala con `score.py`. Registra URL base (sin claves), ID exacto del modelo, fecha y uso de tokens (`meta.uso`).

Aceptación: todas las pruebas offline pasan, incluidas las tuyas; ningún argumento mal formado rompe el bucle; la clave no aparece en ningún archivo ni salida; distingues un error `autenticacion` de uno `peticion`. Si no ejecutas el paso 5, márcalo como pendiente.

Entregable: `entregas/03b-proveedor.md` y el diff de tus pruebas.

Pregunta de defensa: ¿qué ventaja tiene que el bucle no sepa nada de HTTP? Piensa en qué cambiaría para pasar a Anthropic Messages.

Lección: [módulo correspondiente](../docs/03b-proveedor-real.md). Autocorrección: [guía de soluciones](../soluciones/guia.md).
