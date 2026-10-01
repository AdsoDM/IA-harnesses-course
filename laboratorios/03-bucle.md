# 03 — Bucle, validación y límites

Duración: 2 horas. Ejecutable offline.

```powershell
python .\ejemplos\mini-harness\harness.py
python .\ejemplos\mini-harness\harness.py --scenario invalid
python .\ejemplos\mini-harness\harness.py --scenario loop --max-steps 3
python -m unittest discover -s .\ejemplos\mini-harness -v
```

1. Guarda los estados finales y reconstruye una llamada mediante su ID.
2. Explica por qué el caso invalid no ejecuta una suma válida.
3. Cambia a dos pasos: ¿qué ocurre en cada escenario?
4. Añade `multiplicar` en tu rama y una prueba positiva y otra negativa.
5. Describe por qué `max_steps` no interrumpe una función bloqueada.

Salida normal: `status=completed`, respuesta `5`. El caso invalid debe terminar con una respuesta explícita de fallo del modelo simulado. El bucle termina como `step_limit`, aunque las herramientas hayan devuelto éxito.

Aceptación: todas las pruebas pasan, los tipos inválidos son rechazados y una propuesta sin fin se detiene. Entrega `entregas/03-bucle.md` y el diff del código.

6. Ejecuta `harness_documental.py --evaluar --split dev` y compara su bucle con el de `harness.py`: ¿qué cambia al admitir varias llamadas por turno?

Ampliación: añade validación estricta de la forma de la respuesta final. Explica qué parte del contrato formal sigue sin probar verdad semántica.

Lección: [módulo correspondiente](../docs/03-bucle-python.md). Autocorrección: [guía de soluciones](../soluciones/guia.md).
