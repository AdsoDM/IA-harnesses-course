# Evaluación del asistente documental

## Archivos y alcance

| Archivo | Uso |
| --- | --- |
| `casos.jsonl` | 12 casos: ocho de desarrollo y cuatro reservados |
| `score.py` | Criba determinista de filas normalizadas |
| `normalizar_pi.py` | Traza de Pi (JSON o RPC) → fila normalizada |
| `ejecutar_casos.py` | Runner: un proceso Pi RPC por caso, trazas, filas y criba |
| `configuraciones/` | A/B con modelo de guion (`*-guion.json`) y plantillas para modelo real (`*-real.json`) |
| `resultados-demo.jsonl` | Fixture manual, sin inferencia real |
| `trazas-ejemplo/` | Trazas **reales** de Pi 0.99.1 con el modelo de guion, anonimizadas, para las pruebas del normalizador |
| `test_*.py` | Regresiones del checker, del normalizador y del runner |

## Formato de una ejecución normalizada

```json
{"case_id":"c01","output":{"status":"answered","answer":"30 días","sources":["d-001"]},"tool_calls":[{"name":"lookup_document","arguments":{"doc_id":"d-001"},"ok":true}]}
```

El host debe extraer `output` de la respuesta final y `tool_calls` de eventos realmente observados (`tool_execution_start`/`_end` por `toolCallId`). El JSONL de Pi contiene muchos registros; **no se entrega directamente a score.py**: pásalo por `normalizar_pi.py`, que conserva una referencia a la traza original. No dejes que el modelo declare qué herramientas utilizó como única evidencia.

`meta` puede contener lo que quieras (`run_id`, commit, proveedor, modelo, duración, uso, estado RPC, error). El checker solo interpreta las claves del contrato. Para repeticiones guarda un archivo por repetición; IDs duplicados se rechazan para impedir que un caso sustituya a otro.

Una ejecución con timeout o JSON inválido sigue siendo un caso: `output: null` y metadata con el error. El checker lo cuenta como fallo. No excluyas intentos difíciles del denominador.

## Uso

```powershell
# Criba de una fixture o de resultados ya normalizados
python .\evaluacion\score.py .\evaluacion\resultados-demo.jsonl
python .\evaluacion\score.py .\resultados\B-real-dev-r1.jsonl --split dev

# Normalizar una captura manual de pi --mode json
python .\evaluacion\normalizar_pi.py .\trazas\c01.jsonl --case c01 --salida .\resultados\manual.jsonl

# Batería completa con el runner
python .\evaluacion\ejecutar_casos.py --config .\evaluacion\configuraciones\B-guion.json
python .\evaluacion\ejecutar_casos.py --config .\evaluacion\configuraciones\B-guion.json --guion memoria --casos c01,c05
python .\evaluacion\ejecutar_casos.py --config .\evaluacion\configuraciones\B-real.json --split dev --repeticiones 3 --plazo 180
python .\evaluacion\ejecutar_casos.py --config .\evaluacion\configuraciones\B-real.json --simular
```

`score.py` y el runner salen con 0 si todos pasan la criba, 1 si alguno falla y 2 ante un archivo, dataset, configuración o protocolo inválido. Un caso ausente cuenta como fallo; un ID desconocido o repetido es error. Los archivos dev/holdout deben contener solo IDs de su división.

Una configuración tiene `nombre`, `descripcion`, `pi_args` (rutas relativas a la raíz del curso), `prompt` (con `{pregunta}`), `entorno` opcional y `agente_aislado` (usa `.pi-curso\agente` como `PI_CODING_AGENT_DIR`; útil con el guion, no con tus credenciales). El runner rechaza cualquier valor `REEMPLAZAR`.

## Interpretar métricas

`contract`: claves y tipos correctos. `status`: estado esperado. `terms`: substrings normalizados, insensibles a mayúsculas/acentos. `sources`: contiene todas las fuentes exigidas y ninguna fuera de las exigidas o de `allowed_sources`. `evidence`: consultas exitosas necesarias y respaldo de IDs citados. `policy`: ninguna herramienta distinta de lookup_document. `passed`: todas las condiciones.

Limitaciones: el checker no autentica trazas, no analiza negaciones y no prueba que una llamada no registrada no ocurrió. No detecta un secreto en respuesta si pasa otros criterios. Una llamada documental puede fallar y después recuperarse sin invalidar todo el caso; inspecciona errores y presupuesto en el informe. Evalúa efecto real mediante el entorno y traza completa, y revisa manualmente significado, vigencia, ausencia de datos inventados y exposición de información con [la plantilla de revisión](../plantillas/revision-humana.md).

## Resultados de referencia del pipeline (modelo de guion, Pi 0.99.1)

| Configuración | Aprobados | contract | status | terms | sources | evidence | policy |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A-guion | 3/12 | 12 | 10 | 7 | 11 | 3 | 12 |
| B-guion | 12/12 | 12 | 12 | 12 | 12 | 12 | 12 |

Son resultados **del harness con un doble de prueba**: si tu instalación no los reproduce, hay un problema de entorno, versión o rutas, no de «calidad del modelo».

## Protocolo recomendado

Fija corpus/herramientas/modelo, sesión nueva por caso, mismo prompt base, tres repeticiones si puedes, presupuesto y deadline. Ajusta con dev; congela y ejecuta holdout una vez por repetición. Para una ampliación seria, crea casos nuevos no vistos y más numerosos. Estos doce casos son un punto de partida pedagógico.
