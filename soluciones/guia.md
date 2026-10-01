# Orientaciones de autocorrección

Lee después de intentar la práctica. Hay múltiples diseños válidos; comprueba contratos y evidencia en vez de copiar una arquitectura. La [clave de autoevaluación](autoevaluacion.md) responde a las preguntas de cada lección.

| Lab | Una solución satisfactoria demuestra | Error frecuente | Referencia |
| --- | --- | --- | --- |
| 01 | Modelo propone, dispatcher valida, host limita | Permitir todo y confiar en el prompt | [contrato comentado](lab01-contrato.md) |
| 02 | Python, Node y shell identificados por separado; guion ejecutado | Instalar Pi dentro de Conda esperando que sea Python | Módulo 02 |
| 03 | Llamada y resultado correlacionados; bucle limitado | Confundir éxito de herramienta con tarea terminada | [lab03_multiplicar.py](codigo/lab03_multiplicar.py) |
| 03b | Adaptador probado offline; errores clasificados | Pasar `arguments` sin parsear ni validar | [test_documental.py](../ejemplos/mini-harness/test_documental.py) |
| 04 | Lectura observada y versión/modelo registrados | Aceptar «he leído» como traza | Traza de ejemplo en `evaluacion/trazas-ejemplo` |
| 05 | Descripción precisa y resumen con vigencia/IDs | Cargar toda documentación siempre | [skill resuelta](lab05-skill/SKILL.md) |
| 06 | Validación estricta y error de ausencia específico | Éxito vacío ante documento inexistente | [search.mjs](codigo/search.mjs) |
| 07 | Adaptador carga, núcleo mantiene tests, presupuesto detiene el bucle | Afirmar integración porque solo pasó un test JS | Módulo 07 |
| 08 | Aceptación distinta de final; recursos cerrados | Esperar cinco segundos y declarar fin | Abajo: modo `sin-settled` |
| 09 | Permisos, exposición y herramientas revisados; ADR razonado | Apuntar filesystem a toda la unidad | [ADR resuelto](lab09-adr-ejemplo.md) |
| 10 | Mismas condiciones y fallos incluidos | Ajustar continuamente contra casos reservados | [experimento resuelto](lab10-experimento-ejemplo.md) |
| 11 | Parada, estado y efectos verificados | Tratar cwd como sandbox | [incidente resuelto](lab11-incidente-ejemplo.md) |
| 12 | Otra persona puede reproducir la evidencia | Demo convincente sin contrato ni resultados | Rúbrica |

## Respuestas conceptuales

Dato ausente: problema de información; el comportamiento correcto puede ser abstención. Esquema laxo: problema de herramienta/harness; valida antes del efecto. Consultas repetidas: política de ejecución y contexto; añade límites y diagnostica el motivo. Benchmark que acepta «30» en cualquier frase: problema de evaluador; verifica significado y evidencia.

`max_steps=1` en el escenario normal realiza una propuesta de herramienta y se queda sin paso para obtener la respuesta final: `step_limit`. Con dos pasos completa la suma. El escenario inválido comunica fallo mediante el modelo simulado; no demuestra reparación inteligente de argumentos.

La skill adecuada identifica cuándo revisar evidencias, consulta fuentes y conserva ID/fecha. Un resumen adecuado mantiene restricciones y la relación de sustitución entre normas.

Un cliente RPC debe leer stdout continuamente y separar respuesta correlacionada de eventos. Una aceptación puede ir seguida de fallo: registra ambos estados. Un cliente en Python puede compartir permisos con el padre aunque Pi esté en otro proceso.

Una evaluación automática puede aprobar una negación que contiene un término esperado. Añade revisión humana o un juez diseñado y auditado; no ocultes ese límite del checker simple.

## Laboratorio 07: ¿quién bloquea `borrar_backups`?

El runtime. La traza muestra `tool_execution_end` con `isError: true` y el texto «Tool borrar_backups not found»: la herramienta no está registrada, así que no existe nada que ejecutar, con o sin `presupuesto.ts`. Ni el prompt ni la extensión intervienen. Para ver actuar el allowlist de la extensión, ejecuta la misma pregunta con `--guion correcto --permitidas otra`: `lookup_document` queda bloqueada con «Herramienta no permitida por la política del curso» y el guion se abstiene. Ambas capas son necesarias: una define qué existe; la otra, qué se permite de lo que existe.

## Laboratorio 08: modo `sin-settled`

En `pi_falso.py`, dentro de `run`, emite `agent_end` y retorna sin `agent_settled` cuando `MODO == "sin-settled"` (y responde a `abort` como en `lento`). La prueba:

```python
def test_sin_asentamiento_vence_el_plazo(self):
    c = cliente("sin-settled")
    try:
        c.iniciar()
        r = c.ejecutar_prompt("hola", plazo_s=0.5)
    finally:
        c.cerrar()
    self.assertEqual(r.estado, "plazo_vencido")
```

Si tu cliente declara `completado` al ver `agent_end`, esta prueba lo detecta.

## Criterio para seguir

Si conoces qué evidencia falta y puedes proponer una prueba, avanza con ese pendiente explícito. Si etiquetas un resultado simulado como real o no distingues validación de aislamiento, vuelve a los fundamentos.
