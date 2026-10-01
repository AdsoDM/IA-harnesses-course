# Clave de autoevaluación

Léela después de responder. Si fallas más de dos preguntas de un módulo, vuelve a su sección «Errores frecuentes» antes del laboratorio.

<a id="01"></a>
## 01 — Fundamentos

1. El harness (dispatcher y validación de la herramienta). El modelo solo propone.
2. Porque `sources` lo escribe el modelo. La evidencia es una llamada observada en la traza con ese ID y resultado exitoso.
3. Cualquiera de: máximo de pasos o llamadas, plazo total, allowlist de herramientas, presupuesto de inferencia, validación de salida.
4. `abstained`: la pregunta es legítima pero no hay evidencia. `blocked`: la petición es una acción fuera de alcance (publicar, borrar) y no se ejecuta.
5. El de agente ejecuta tareas (modelo, contexto, herramientas, estado, control); el de evaluación ejecuta casos contra el primero y mide resultados.

<a id="02"></a>
## 02 — Entorno

1. `$x` solo existe en el shell actual; `$env:X` es una variable de entorno que heredan los procesos hijos, como Pi.
2. Porque la política de ejecución puede bloquear los wrappers `.ps1`; los `.cmd` no dependen de ella.
3. Que Pi está instalado, carga extensiones TypeScript y ejecuta una herramienta. No demuestra acceso a ningún modelo ni su comportamiento.
4. En `…\node_modules\@earendil-works\pi-coding-agent\docs` bajo `npm.cmd root -g`.
5. Git Bash (o `shellPath`, o `bash.exe` del PATH). La herramienta `powershell` es opcional y aparte.

<a id="03"></a>
## 03 — Bucle Python

1. Es sintácticamente JSON, pero `"2"` es texto y el contrato exige un entero: la validación de dominio lo rechaza.
2. Porque el modelo simulado nunca emite respuesta final; éxito de herramienta no es fin de tarea.
3. Al modelo: mensajes, resultados de herramienta y errores interpretables. A la traza: IDs, pasos, tiempos, estados; no se envían al modelo secretos ni infraestructura de logging.
4. `step_limit`: el único paso se usa para proponer la herramienta y no queda paso para la respuesta final.
5. Porque la escritura pudo realizarse antes del timeout; repetirla puede duplicar el efecto. Primero se verifica el estado.

<a id="03b"></a>
## 03b — Proveedor real

1. Traducir formatos (mensajes, herramientas, `arguments`), clasificar errores y reintentar con límite, y contabilizar uso. El bucle solo ve `final` o `tool_calls`.
2. Porque es un fallo del modelo recuperable: devolverlo como resultado permite que el modelo corrija los argumentos; una excepción detendría la tarea sin oportunidad de reparación.
3. Respetar `Retry-After`, reducir concurrencia o pausar la batería, registrar los casos afectados como fallidos o pendientes y no mezclar resultados de condiciones distintas.
4. Un mensaje `user` con bloques `tool_result` (`tool_use_id`, contenido y, si procede, `is_error`).
5. Demuestra que el adaptador construye y entiende el formato y aplica su política de errores. No demuestra que un servidor real acepte esos parámetros ni cómo decide un modelo.

<a id="04"></a>
## 04 — Uso de Pi

1. `tool_execution_end` con el mismo `toolCallId` que el `tool_execution_start` e `isError: false`.
2. Porque tras `agent_end` pueden seguir reintentos, recuperación por desbordamiento o mensajes en cola; `agent_settled` indica que Pi no continuará por su cuenta.
3. Sin UI no puede preguntar: con `defaultProjectTrust` por defecto (`ask`) omite los recursos protegidos del proyecto.
4. `--tools read` deja **solo** `read`; `--exclude-tools bash` quita `bash` y conserva el resto de la selección.
5. Que una plantilla cambia lo que el runtime envía y, con ello, la conducta: sin ella el guion responde de memoria y en prosa; con ella consulta y cumple el contrato. Con un modelo real el efecto no es determinista.

<a id="05"></a>
## 05 — Contexto y memoria

1. `AGENTS.md` en la carpeta del proyecto.
2. Porque la carga automática requiere que el modelo lea `SKILL.md` con `read`; sin esa herramienta, solo funciona `/skill:nombre`.
3. Qué norma sustituye a cuál, sus IDs y fechas, y la regla de aplicación («usar la vigente»).
4. Instrucciones definen la tarea y su autoridad; datos son contenido recuperado. El control ejecutable: el contenido de un documento no puede ampliar herramientas ni permisos (allowlist, `tool_call`, permisos del SO).
5. Se ignoran: los recursos de `.pi/` requieren confianza y en modo JSON no hay prompt para concederla.

<a id="06"></a>
## 06 — Herramientas

1. El esquema TypeBox en el adaptador Pi y la validación en `lookupDocument`. La función puede llamarse desde tests u otros adaptadores sin pasar por el esquema.
2. Cuando el fallo lleva datos útiles para la UI o para scripts (`structuredContent`) y quieres que el modelo lo vea como error.
3. El modelo recibe `content`; un script de `codemode` recibe `structuredContent` si hay `outputSchema`.
4. Porque la búsqueda mide coincidencia léxica, no vigencia. El agente debe consultar los candidatos con `lookup_document` y aplicar la regla de vigencia.
5. `executionMode: "sequential"` en ambas (y, si tocan archivos, `withFileMutationQueue`).

<a id="07"></a>
## 07 — Extensiones

1. Sin Pi: el núcleo `catalogue.mjs` y su validación. Con Pi: la carga del adaptador, el registro, el esquema y la ejecución dentro del runtime.
2. `{ block: true, reason: "…" }`, opcionalmente con `terminate: true`.
3. Porque, instalado con el paquete, bloquearía herramientas en cualquier sesión que lo cargue.
4. En `session_start` o en la herramienta que lo necesite, cerrándolo en `session_shutdown`; nunca en la factory.
5. Cuatro llamadas (tres correctas y una bloqueada) y `stopReason: "toolUse"`, sin respuesta final.

<a id="08"></a>
## 08 — SDK y RPC

1. `started`: empezó un run; `queued`: quedó en cola durante otro; `handled`: lo consumió un comando o manejador de extensión y no habrá run que esperar.
2. Para que ninguna tubería se llene: si el hijo no puede escribir, se bloquea.
3. Envía `abort`, espera la respuesta y `agent_settled` durante la gracia, registra `plazo_vencido` y, al cerrar, cierra stdin, espera, `terminate` y `kill`.
4. `noTools: true` en lugar de `"all"`; `tsc --noEmit` contra los tipos de 0.99.1 lo rechazó.
5. Porque acepta comandos privilegiados (por ejemplo `bash` directo o cambiar de modelo): quien escribe en stdin controla Pi.

<a id="09"></a>
## 09 — MCP

1. `exposure: "hidden"` con `toolExposure` `direct` solo para las lecturas; se aplica en el cliente MCP de Pi (harness), no en el servidor.
2. Porque un servidor stdio ejecuta un comando: una carpeta no confiable podría ejecutar código al arrancar Pi.
3. `mcp__filesystem__read_text_file`.
4. Limita el código del script (QuickJS, solo alcanza herramientas). No limita los efectos de las herramientas que el script llama.
5. Cuando la capacidad debe compartirse entre varios clientes o desplegarse de forma independiente de Pi.

<a id="10"></a>
## 10 — Evaluación

1. `evidence` (y la revisión humana debería marcar la cita como no respaldada).
2. Porque en A el guion no consulta, pero los bloqueos no exigen consulta ni fuentes; el resto falla `evidence`.
3. Mantenerlo en el denominador de esa repetición, informar la variabilidad y examinar la causa (latencia del proveedor, bucle, plazo insuficiente).
4. Para admitir fuentes pertinentes adicionales cuando el caso lo justifica (c12). No se generaliza porque relajaría la exigencia de citar solo lo pertinente.
5. Que el pipeline (runner, normalizador, criba) funciona con Pi real y detecta lo previsto. No demuestra nada sobre un modelo de IA.

<a id="11"></a>
## 11 — Operación

1. Instrucciones (no obligan), validación y política (no aíslan el código de extensiones), permisos del SO/sandbox (no garantizan respuestas veraces), observación y recuperación (no previenen).
2. En `tool_call`: allowlist y máximo de llamadas. En `turn_end`: máximo de turnos. Un turno puede tener muchas llamadas y un bucle puede no llamar herramientas.
3. Verificar el estado con el ID de operación o una lectura antes de repetir; si no se puede saber, informar incertidumbre.
4. Porque el comando `bash` y otros comandos RPC actúan con los permisos de Pi sin pasar por el modelo.
5. Que controla qué recursos del proyecto se cargan, pero no limita lo que las herramientas pueden hacer y no es una frontera de seguridad.

<a id="12"></a>
## 12 — Proyecto final

Las respuestas dependen de tu diseño. Una buena respuesta cita artefactos concretos: el contrato y el ADR (1), la traza con `toolCallId` y resultado (2), un cambio aislado con repeticiones antes/después (3), la política de herramientas, la traza sin llamadas prohibidas y la ausencia de efectos verificada en el entorno (4), y una lista explícita de lo no medido: coste real, generalización, datos reales, concurrencia (5).
