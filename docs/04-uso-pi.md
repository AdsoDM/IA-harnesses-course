# 04 — Usar Pi como harness

Tiempo: 4 horas. Objetivo: conseguir una ejecución reproducible, diferenciar las interfaces de Pi y leer su flujo de eventos.

## Primera sesión controlada

Desde la raíz del curso inicia Pi solo con herramientas de lectura:

```powershell
pi --tools read,grep,find,ls
```

Configura `/login` y `/model` si aún no lo has hecho. Pregunta: «Lee README.md y enumera tres entregables del curso, indicando dónde aparecen». Observa las herramientas usadas. Una respuesta que se basa solo en tu pregunta no demuestra lectura del archivo.

`--tools` **sustituye** la selección por defecto (`read`, `bash`, `edit`, `write`): nombra todas las que quieras. `--exclude-tools` quita algunas, `--no-builtin-tools` conserva solo las de extensiones y `--no-tools` empieza sin ninguna. El allowlist reduce herramientas anunciadas para esa ejecución; no encierra el proceso en la carpeta.

Los recursos personales y de proyecto tienen su propia carga. Para una comparación controlada añade `--no-extensions --no-skills --no-prompt-templates --no-context-files --no-session` (formas cortas: `-ne -ns -np -nc`) y aporta explícitamente el contexto necesario. Las rutas `-e`, `--skill` y `--prompt-template` explícitas siguen cargando. Registra la invocación completa.

## Cuatro interfaces

| Interfaz | Úsala para | Resultado que debes observar |
| --- | --- | --- |
| Interactiva | Aprender y dirigir una sesión | Conversación y herramientas en terminal |
| Print (`-p`) | Obtener una respuesta en un script | Texto final en stdout |
| JSON (`--mode json`) | Capturar eventos de una invocación | JSONL: cabecera de sesión y eventos |
| RPC/SDK | Integrar el harness | Comandos/eventos o métodos TypeScript |

Reglas verificadas en 0.99.1: si stdin o stdout están redirigidos y no eliges JSON ni RPC, Pi usa modo print; `--mode json` ejecuta los prompts y termina; `--mode text` sigue abriendo la interfaz si hay terminal. La web agrupa RPC y SDK como integración; en el curso los tratamos por separado.

```powershell
pi --tools read,grep,find,ls --print "Lee README.md y resume los entregables"
New-Item -ItemType Directory -Path .\trazas -Force | Out-Null
pi --tools read --mode json "Lee README.md y resume el objetivo" > .\trazas\pi-primera.jsonl
```

PowerShell 7 redirige en UTF-8; Windows PowerShell 5.1 puede crear redirecciones UTF-16. El normalizador del curso admite UTF-8, BOM y UTF-16. Si tu propio parser espera UTF-8, captura con `Out-File -Encoding utf8` o usa un cliente que lea stdout directamente. No mezcles logs propios con stdout si consumes un protocolo JSONL: Pi escribe diagnósticos en stderr.

## Practicar sin credenciales

El modelo de guion (módulo 02) permite repetir todo este módulo sin coste. Sustituye `/login` por:

```powershell
$env:PI_CODING_AGENT_DIR = "$PWD\.pi-curso\agente"
pi -ne -ns -np -nc --no-session -e .\ejemplos\pi-package\dobles\modelo-guion.ts `
  -e .\ejemplos\pi-package\extensions\catalogue.ts --tools lookup_document `
  --provider curso --model guion --mode json "¿A qué hora UTC se realiza el backup?" > .\trazas\guion.jsonl
```

Sin plantilla, el guion en modo `auto` no recibe la orden de consultar ni el contrato JSON: responde «de memoria» en prosa, con un dato **obsoleto**. Es deliberado: acabas de ver una respuesta plausible, sin llamada y equivocada.

## Leer el flujo JSON

Un run con una herramienta produce, recortado, esta secuencia (traza real en [trazas-ejemplo/json-c02-guion.jsonl](../evaluacion/trazas-ejemplo/json-c02-guion.jsonl)):

```text
session                      cabecera: id, versión, cwd (solo en modo JSON)
agent_start / turn_start
message_start/end  system    prompt y herramientas declaradas
message_start/end  user      tu petición (ya expandida si usaste una plantilla)
message_update …             deltas del asistente
message_end        assistant stopReason "toolUse" con un bloque toolCall
tool_execution_start/end     toolCallId, toolName, args / result, isError
message_end        toolResult
turn_end / turn_start
message_end        assistant stopReason "stop": respuesta final
turn_end / agent_end / agent_settled
```

La evidencia de una consulta es el par `tool_execution_start`/`tool_execution_end` con el mismo `toolCallId` e `isError: false`, no la frase del asistente. `message_end` contiene el mensaje autoritativo; los `message_update` solo son deltas. `agent_end` cierra un run de bajo nivel, pero reintentos o colas pueden continuar: `agent_settled` indica que Pi no seguirá por su cuenta.

Convierte la captura en una fila evaluable:

```powershell
python .\evaluacion\normalizar_pi.py .\trazas\guion.jsonl --case c02
```

## Una tarea bien definida

Compara «mejora el proyecto» con «lee el catálogo de ejemplo, responde al plazo y cita la fuente; si falta, abstente». La segunda especifica dato, evidencia y comportamiento de fallo. El harness necesita saber qué cuenta como fin; el modelo también necesita comprender el objetivo.

Para guardar progreso, Pi permite continuar sesiones. Comprueba `pi --continue` y `/tree` en un proyecto de práctica. Una rama de conversación explora otra continuación; no crea una rama de Git. Una rama Git conserva código y documentación; no conserva necesariamente contexto de sesión.

## Confianza de proyecto en modo no interactivo

Si la carpeta contiene `.pi/settings.json`, `.pi/extensions`, `.pi/mcp.json` u otros recursos protegidos, Pi pide una decisión de confianza. En print, JSON y RPC no puede preguntar: con la configuración por defecto **omite** esos recursos. Usa `--approve` o `--no-approve` para que una ejecución automatizada sea explícita. `AGENTS.md` y `CLAUDE.md` se cargan aunque no confíes en el proyecto, salvo que uses `-nc`.

## Separar propuesta y efecto

Que el asistente escriba «he validado el proyecto» no prueba ejecución. Busca llamadas y resultados. Verifica archivos por separado. Si decides habilitar edición, registra el diff y revisa los cambios antes del commit. El historial de Git proporciona recuperación de contenido versionado, pero no revierte un correo enviado o una operación externa.

Ejercicio: repite una pregunta tres veces con la misma configuración y sesión nueva. Observa diferencias. No interpretes una sola respuesta acertada como fiabilidad general. Con el modelo de guion las tres serán idénticas: ¿qué te dice eso sobre lo que mide una repetición?

## Errores frecuentes

- Redirigir la salida sin `--mode json` y esperar eventos: obtienes solo el texto final (modo print).
- Olvidar que `--tools` reemplaza la lista: `--tools lookup_document` desactiva también `read`.
- Tomar la sesión persistida (`~/.pi/agent/sessions`) por el flujo JSON: tienen propósitos y formatos distintos.
- Ejecutar en una carpeta con `.pi/` no confiable en modo JSON y no notar que se ignoraron sus recursos.

## Autoevaluación

1. ¿Qué evento demuestra que una herramienta terminó sin error?
2. ¿Por qué `agent_end` no basta para declarar terminada una tarea?
3. ¿Qué hace Pi en modo JSON con una carpeta que contiene `.pi/extensions` si no pasas `--approve`?
4. ¿Qué diferencia hay entre `--tools read` y `--exclude-tools bash`?
5. ¿Qué aprendes al comparar la respuesta del guion con y sin plantilla?

Respuestas: [clave](../soluciones/autoevaluacion.md#04).

Práctica: [laboratorio 04](../laboratorios/04-pi.md). Fuentes: [CLI](https://pi.dev/docs/latest/cli), [cómo funciona Pi](https://pi.dev/docs/latest/how-pi-works), [JSON](https://pi.dev/docs/latest/json), [seguridad](https://pi.dev/docs/latest/security).
