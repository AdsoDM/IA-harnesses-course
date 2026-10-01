# 03b — Conectar el bucle a un proveedor real

Tiempo: 4 horas. Objetivo: escribir y probar el **adaptador** que traduce entre tu harness y la API de un proveedor, sin cambiar el bucle, y saber qué errores son del proveedor, cuáles del modelo y cuáles tuyos.

## Por qué un adaptador

Cada proveedor representa de forma distinta mensajes, herramientas y llamadas. Si el bucle conoce esos detalles, cambiar de proveedor obliga a reescribirlo. El patrón del curso separa tres capas:

| Capa | Archivo | Conoce |
| --- | --- | --- |
| Bucle | `harness_documental.run` | Formato neutro: `final` o `tool_calls`, límites, traza |
| Adaptador | `proveedor_openai.py` | Formato del proveedor, HTTP, errores, reintentos, uso |
| Herramientas | `lookup_document` | Dominio y validación |

Pi hace lo mismo a mayor escala: su paquete `pi-ai` implementa adaptadores para Anthropic Messages, OpenAI Chat Completions y Responses, Google, Bedrock y otros, y el agente trabaja con un formato común.

## El formato Chat Completions

Se eligió porque lo aceptan OpenAI y muchos servidores compatibles (Ollama, llama.cpp server, vLLM, LM Studio y pasarelas). Comprueba en la documentación de tu servidor que admite **tool calling**; no todos los modelos lo hacen bien.

Petición (`POST {base_url}/chat/completions`):

```json
{"model": "ID_DE_TU_MODELO",
 "messages": [{"role": "system", "content": "…instrucciones…"},
              {"role": "user", "content": "¿Cuál es la retención vigente?"}],
 "tools": [{"type": "function", "function": {"name": "lookup_document",
            "description": "Consulta un documento sintético por ID…",
            "parameters": {"type": "object", "properties": {"doc_id": {"type": "string"}},
                           "required": ["doc_id"], "additionalProperties": false}}}],
 "tool_choice": "auto"}
```

Respuesta con llamada:

```json
{"choices": [{"finish_reason": "tool_calls",
  "message": {"role": "assistant", "content": null,
   "tool_calls": [{"id": "call_1", "type": "function",
     "function": {"name": "lookup_document", "arguments": "{\"doc_id\":\"d-001\"}"}}]}}],
 "usage": {"prompt_tokens": 312, "completion_tokens": 18}}
```

Tres detalles que causan la mayoría de fallos:

1. `arguments` es **texto** que contiene JSON, no un objeto. Puede venir mal formado. El adaptador lo parsea y, si falla, lo convierte en **error de herramienta** para que el modelo pueda corregirse; no revienta el bucle.
2. Para continuar, reenvías el mensaje del asistente con sus `tool_calls` y después un mensaje `{"role": "tool", "tool_call_id": "call_1", "content": "…"}` por cada llamada. Sin el ID correcto, el proveedor rechaza la petición o el modelo asocia mal los resultados.
3. `finish_reason: "length"` significa que la salida se cortó: el JSON final puede estar incompleto aunque parezca empezar bien.

## Otros formatos, mismas ideas

| API | Declaración de herramienta | Llamada del modelo | Resultado que devuelves |
| --- | --- | --- | --- |
| OpenAI Chat Completions | `tools[].function.parameters` | `message.tool_calls[]` con `arguments` en texto | Mensaje `role: tool` con `tool_call_id` |
| Anthropic Messages | `tools[].input_schema` | Bloque `{"type":"tool_use","id","name","input"}` y `stop_reason: "tool_use"` | Mensaje `user` con bloque `{"type":"tool_result","tool_use_id",…,"is_error"}` |
| OpenAI Responses | `tools[]` de tipo `function` | Elementos `function_call` en `output` | Elemento `function_call_output` con `call_id` |

La tabla es orientativa: consulta la referencia del proveedor antes de implementar otro adaptador. Lo transferible es el contrato: ID de llamada, argumentos validados, resultado correlacionado y error distinguible.

## Errores: clasificar antes de reintentar

| Clase | Ejemplos | Política del adaptador |
| --- | --- | --- |
| `autenticacion` | 401, 403 | No reintentar. Revisar clave y permisos del modelo |
| `cuota` | 429 | Reintentar poco, respetando `Retry-After`; informar si persiste |
| `temporal` | 5xx, 408, red | Reintentar con espera creciente y tope |
| `peticion` | 400, 404, 422 | No reintentar: el error es tuyo (modelo inexistente, parámetro no admitido) |
| `respuesta` | Cuerpo no JSON, forma inesperada | No reintentar a ciegas; guardar evidencia |

Una llamada al modelo no cambia el mundo, pero **cuesta**: cada reintento puede facturar tokens. Por eso el adaptador limita reintentos y acumula `uso`. Las herramientas con efectos necesitan otra política (módulo 11).

## Credenciales y datos

La clave se lee de una variable de entorno (`--api-key-env`, por defecto `OPENAI_API_KEY`) y nunca se escribe en la traza. Con un servidor local sin clave, no se envía cabecera `Authorization`. Todo lo que envías sale de tu equipo si el proveedor es remoto: en el curso solo hay datos sintéticos. Antes de usar documentos reales, revisa la política de datos de tu organización y del proveedor.

## Probar sin red

[test_documental.py](../ejemplos/mini-harness/test_documental.py) levanta un servidor HTTP local (127.0.0.1, puerto libre) que responde como un proveedor. Comprueba la ida y vuelta completa, la forma de cada petición, argumentos mal formados, reintento de un 503 y parada ante un 401 o un 400.

```powershell
python -m unittest discover -s .\ejemplos\mini-harness -v
```

Esas pruebas validan el **adaptador**, no un modelo. Pasarlas es condición previa a gastar inferencia.

## Probar con un modelo

Con un servidor local compatible (por ejemplo, Ollama expone `/v1/chat/completions` en su puerto local; comprueba URL y soporte de herramientas en su documentación):

```powershell
python .\ejemplos\mini-harness\harness_documental.py --proveedor openai `
  --base-url http://localhost:11434/v1 --modelo ID_DE_TU_MODELO `
  "¿Cuál es la retención vigente de backups?"
```

Con un proveedor remoto, fija la clave solo en la sesión y usa la URL base que indique su documentación:

```powershell
$env:OPENAI_API_KEY = Read-Host "Clave" -MaskInput   # PowerShell 7
python .\ejemplos\mini-harness\harness_documental.py --proveedor openai `
  --base-url https://api.openai.com/v1 --modelo ID_DE_TU_MODELO --evaluar --split dev `
  --salida .\resultados\py-real-dev-r1.jsonl
python .\evaluacion\score.py .\resultados\py-real-dev-r1.jsonl --split dev
```

`-MaskInput` existe en PowerShell 7; en Windows PowerShell 5.1 usa `Read-Host -AsSecureString` y conviértela solo en memoria, o define la variable en la configuración de usuario de Windows. Registra el ID exacto del modelo y la fecha.

## Lo que este adaptador no hace

No hay *streaming* (SSE), imágenes, razonamiento extendido, caché de prompt ni cancelación a mitad de una petición HTTP (el `timeout` corta la espera, no garantiza que el proveedor no facture). Son exactamente las piezas que un runtime como Pi ya implementa; verlas ausentes aquí ayuda a valorar qué aporta.

## Errores frecuentes

- Pasar `arguments` directamente a la función sin `json.loads` ni validación.
- Olvidar el mensaje `tool` de alguna llamada cuando el modelo propone varias en el mismo turno.
- Reintentar un 400 o un 401 «por si acaso»: gasta tiempo y dinero sin posibilidad de éxito.
- Imprimir la cabecera `Authorization` al depurar.
- Suponer que `temperature` o `max_tokens` se aceptan en todos los modelos: algunos los rechazan o usan otros nombres.

## Autoevaluación

1. ¿Qué tres responsabilidades tiene el adaptador que no debe tener el bucle?
2. ¿Por qué un `arguments` mal formado se devuelve como error de herramienta y no como excepción?
3. ¿Qué harías ante un 429 persistente durante una batería de evaluación?
4. ¿Qué equivale en Anthropic Messages al mensaje `role: tool` de Chat Completions?
5. ¿Qué demuestra el servidor HTTP falso y qué no?

Respuestas: [clave](../soluciones/autoevaluacion.md#03b).

Práctica: [laboratorio 03b](../laboratorios/03b-proveedor.md). Continúa con [Pi](04-uso-pi.md).
