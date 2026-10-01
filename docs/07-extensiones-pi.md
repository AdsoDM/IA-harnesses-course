# 07 — Extender Pi y distribuir tu harness

Tiempo: 5 horas. Objetivo: conectar el núcleo determinista al runtime de Pi sin perder su contrato y añadir controles ejecutables con eventos.

## Separar núcleo y adaptador

El núcleo `catalogue.mjs` conoce documentos y validación. [catalogue.ts](../ejemplos/pi-package/extensions/catalogue.ts) conoce Pi y TypeBox. Esa división permite probar el dominio sin instalar Pi y cambiar el adaptador si cambia una API.

Una extensión exporta por defecto una *factory* que recibe `ExtensionAPI`. El ejemplo registra `lookup_document` con `registerTool`: nombre, etiqueta, descripción, `promptSnippet`, `promptGuidelines`, esquema de parámetros, `outputSchema`, `annotations` y `execute(toolCallId, params, signal, onUpdate, ctx)`. Esa firma, la carga con `-e` y la ejecución se han **verificado con Pi 0.99.1** (tipos con `tsc` y ejecución real con el modelo de guion; véase [VALIDACION.md](../VALIDACION.md)). Vuelve a comprobarlo si cambias de versión.

```powershell
pi --no-extensions --no-skills --no-prompt-templates --no-context-files `
  --extension .\ejemplos\pi-package\extensions\catalogue.ts `
  --prompt-template .\ejemplos\pi-package\prompts\respuesta-documental.md `
  --tools lookup_document --no-session
```

Los backticks continúan la línea en PowerShell; no pongas espacios después. Puedes escribir toda la invocación en una sola línea. `--no-extensions` elimina carga automática (también las extensiones integradas `codemode`, `tool_search` y MCP), pero las rutas `--extension` explícitas siguen cargando. Esto acota recursos para el experimento; una extensión ejecuta código dentro del proceso y conserva sus permisos. Pi carga TypeScript con `jiti`: no hace falta compilar.

Dentro de Pi usa `/respuesta-documental ¿Cuál es la retención vigente?`. El prompt explica los cuatro IDs para que el modelo encuentre fuentes sin una búsqueda adicional. En el proyecto final añadirás búsqueda si amplías el corpus. Sin credenciales, añade `-e .\ejemplos\pi-package\dobles\modelo-guion.ts --provider curso --model guion`.

## Comprobar tipos sin ejecutar

`node --check` solo valida sintaxis. Para comprobar tipos contra la versión de Pi:

```powershell
Set-Location .\ejemplos\pi-package
npm.cmd install --ignore-scripts      # instala las devDependencies fijadas (no afecta a Pi global)
npm.cmd run check                     # tsc --noEmit sobre extensions/ y dobles/
npm.cmd test                          # pruebas del núcleo
Set-Location ..\..
```

Las dependencias que Pi proporciona a las extensiones (`@earendil-works/pi-coding-agent`, `pi-ai`, `pi-agent-core`, `pi-tui`, `typebox`) van en `peerDependencies` con `"*"` y nunca en `dependencies`: una copia física puede duplicar clases y registros. Aquí también aparecen en `devDependencies` fijadas, solo para `tsc`.

## Qué revisar en execute

Debe respetar cancelación, validar parámetros, devolver datos coherentes y evitar efectos ocultos. El ejemplo comprueba `signal` antes de una consulta síncrona breve. Esa comprobación no convertiría una operación larga bloqueada en cancelable. No captura errores para fingir éxito: una excepción se convierte en resultado fallido para el modelo.

## Controles con eventos: presupuesto y allowlist

Pi **no impone un máximo de pasos** por ejecución. [presupuesto.ts](../ejemplos/pi-package/extensions/presupuesto.ts) muestra cómo lo añade el harness:

| Evento | Qué hace la extensión | Contrato usado |
| --- | --- | --- |
| `agent_start` | Reinicia contadores por ejecución | Notificación |
| `tool_call` | Bloquea herramientas fuera de `--permitidas` y llamadas por encima de `--max-llamadas` | Devolver `{ block: true, reason, terminate? }` |
| `turn_end` | Llama a `ctx.abort()` al alcanzar `--max-turnos` | Parada del host; el run termina con error |

```powershell
pi -ne -ns -np -nc --no-session -e .\ejemplos\pi-package\dobles\modelo-guion.ts `
  -e .\ejemplos\pi-package\extensions\catalogue.ts -e .\ejemplos\pi-package\extensions\presupuesto.ts `
  --tools lookup_document --provider curso --model guion --guion bucle --max-llamadas 3 `
  --mode json "¿Cuál es la retención vigente?" > .\trazas\bucle.jsonl
```

Con `--guion bucle` el modelo pide la misma consulta sin fin. Verás tres `tool_execution_end` con `isError: false`, un cuarto con `isError: true` («Presupuesto agotado») y un último mensaje del asistente con `stopReason: "toolUse"`: **no hay respuesta final**, aunque Pi llegue a `agent_settled`. Un fallo en un handler de `tool_call` también bloquea la herramienta (fallo seguro). Ojo al atribuir controles: si el modelo pide una herramienta **no registrada** (modo `obediente`), la rechaza el propio runtime («Tool borrar_backups not found») antes de que actúe la extensión; el allowlist de `presupuesto.ts` protege frente a herramientas registradas y activas que no deberían usarse, por ejemplo si alguien añade `bash` a `--tools`. Compruébalo con `--permitidas otra`. Las extensiones registran flags propios con `pi.registerFlag` y los leen con `pi.getFlag`; aparecen en `pi --help` cuando la extensión está cargada.

## Eventos y ciclo de vida

Un handler de evento puede observar o modificar según su contrato. No asumas que devolver cualquier objeto cancela algo: usa el tipo de resultado declarado para cada evento en `types.ts`. `tool_call` puede mutar la entrada o bloquear; `tool_result` puede reemplazar el resultado; `turn_end` y `agent_before_settle` pueden pedir **una** continuación con `continue: true`. Si añades continuaciones, limita su condición: continuar incondicionalmente crea un bucle.

No inicies procesos, sockets, watchers ni temporizadores en la factory: algunas invocaciones cargan extensiones sin iniciar sesión. Arráncalos en `session_start` o en la herramienta que los necesite, y ciérralos en un `session_shutdown` idempotente. También necesitas un comportamiento no interactivo: `ctx.hasUI` es falso en JSON y print, y una confirmación visual no puede quedarse esperando en un lote sin UI.

## Empaquetar

[package.json](../ejemplos/pi-package/package.json) declara los recursos mediante la clave `pi`. Con manifest, **solo** se cargan las rutas declaradas: `presupuesto.ts` y el modelo de guion (`dobles/`) quedan fuera a propósito para que instalar el paquete no bloquee herramientas en otras sesiones ni añada un proveedor falso. El SDK, en cambio, es una aplicación que instala Pi como dependencia local.

La práctica carga rutas explícitas y no modifica tu configuración global. Tras validar puedes probar `pi install -l <ruta absoluta del paquete>` en un proyecto de ensayo: escribe en `.pi/settings.json`, que solo se lee tras confiar en el proyecto. Revisa el diff y registra el origen. `pi -e <ruta>` prueba un paquete una sola vez sin añadirlo a ajustes.

## Errores frecuentes

- Poner la lógica de dominio en el adaptador: entonces no se puede probar sin Pi.
- Declarar `@earendil-works/pi-coding-agent` en `dependencies` de un paquete.
- Confiar en que `presupuesto.ts` limite el coste: limita llamadas y turnos, no tokens ni euros.
- Suponer que `agent_settled` implica éxito: el run del bucle se asienta sin respuesta final.
- Probar solo con `--print`: oculta las llamadas; usa `--mode json` para ver la evidencia.

## Autoevaluación

1. ¿Qué parte del catálogo puedes probar sin Pi y qué parte no?
2. ¿Qué devuelve un handler de `tool_call` para impedir una ejecución?
3. ¿Por qué `presupuesto.ts` no está en el manifest del paquete?
4. ¿Dónde se debe arrancar un watcher de archivos que usa tu extensión?
5. En el experimento `--guion bucle --max-llamadas 3`, ¿cuántas llamadas ves y cuál es el `stopReason` final?

Respuestas: [clave](../soluciones/autoevaluacion.md#07).

Aceptación: observar llamada y resultado, provocar un ID inexistente, detener un bucle con el presupuesto y mantener las pruebas del núcleo. Práctica: [laboratorio 07](../laboratorios/07-extension.md). Fuentes: [extensiones](https://pi.dev/docs/latest/extensions), [tipos](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/src/core/extensions/types.ts), [paquetes](https://pi.dev/docs/latest/packages), [proveedores personalizados](https://pi.dev/docs/latest/custom-provider).
