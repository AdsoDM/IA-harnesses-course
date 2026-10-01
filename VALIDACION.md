# Validación de esta edición

Edición 1.1 · 30/09/2026. Entorno de verificación: VM Linux del espacio de trabajo de Cowork en el propio equipo del destinatario (Linux 6.8, Python 3.10.12, Node 22.23.2, npm 10.9.8, Git 2.34.1), con acceso al registro npm. **No es el Windows nativo del destinatario**: rutas, wrappers `.cmd`, PowerShell y terminación de procesos en Windows siguen pendientes de tu ejecución. Las pruebas se hicieron sobre una copia del curso, sin escribir trazas ni resultados en tu carpeta.

Pi se instaló en una carpeta aislada (`npm install --ignore-scripts @earendil-works/pi-coding-agent@0.99.1`) con una configuración de agente temporal (`PI_CODING_AGENT_DIR`), sin credenciales y con `PI_OFFLINE=1`.

## Pruebas offline

| Comprobación | Resultado | Qué demuestra |
| --- | --- | --- |
| Harness Python: 9 tests | Pasan | Validación, correlación, errores y límite de pasos |
| Harness documental y adaptador Chat Completions: 9 tests | Pasan | 12/12 con el doble de prueba; ida y vuelta HTTP contra servidor local falso; argumentos mal formados; reintento de 503; parada ante 400/401 |
| Framing JSONL: 8 tests | Pasan | Fragmentación UTF-8, LF/CRLF, límites, EOF y modo tolerante |
| Cliente RPC contra `pi_falso.py`: 8 tests | Pasan | Asentamiento, rechazo, plazo con abort, caída, stderr voluminoso, fragmentación, ID ajeno, cierre forzado |
| Evaluador: 10 tests | Pasan | Contrato, evidencia, fuentes admisibles, duplicados, casos ausentes |
| Normalizador con trazas reales: 11 tests | Pasan | JSON y RPC, herramienta inexistente, bucle, prosa, UTF-16, sin asentamiento |
| Runner contra `pi_falso.py`: 4 tests | Pasan | Flujo completo, marcadores `REEMPLAZAR`, `--simular`, casos desconocidos |
| Soluciones: 4 tests Python y 5 Node | Pasan | `multiplicar` y `search_documents` |
| Catálogo JavaScript: 8 tests | Pasan | IDs, forma de entrada, ausencia, mutación, `listDocuments` |
| `check_docs.py` | Sin errores | Enlaces locales, fences, JSON y estructura de lecciones/laboratorios |
| `check_consistencia.py` | Sin errores | Catálogo JS = catálogo Python; casos, fixture, plantilla y configuraciones coherentes |

Total: 76 pruebas automáticas, reproducibles con `python scripts/verificar_todo.py`. Verifican propiedades deterministas; no acreditan selección de herramientas ni fidelidad de respuestas de un modelo real.

## Verificación contra Pi 0.99.1

| Comprobación | Resultado |
| --- | --- |
| `pi --version`, `pi --help`, `pi mcp --help` | 0.99.1; flags usados en el curso presentes (`--tools`, `-ne/-ns/-np/-nc`, `--no-session`, `-e`, `--prompt-template`, `--mode json/rpc`, `--print`, `--offline`, `--approve`) |
| `tsc --noEmit` de `catalogue.ts`, `presupuesto.ts`, `modelo-guion.ts` y `search_documents.ts` | Sin errores (TypeScript 5.9.3, tipos de 0.99.1) |
| `tsc --noEmit` de `run.ts` (edición 1.0) | **Error**: `noTools: true` no es asignable a `"all" \| "builtin"`. Corregido |
| `tsc --noEmit` de `run.ts` y `run-documental.ts` (1.1) | Sin errores |
| Carga de `catalogue.ts` con `-e` y ejecución de `lookup_document` | Correcta en modos print, JSON y RPC |
| Plantilla `/respuesta-documental` en modos print/JSON/RPC | Se expande antes de llegar al agente |
| Flujo JSON | Cabecera `session`, `message_*`, `tool_execution_*`, `turn_*`, `agent_end`, `agent_settled`, como en la documentación |
| `presupuesto.ts` | Bloquea una herramienta activa fuera de `--permitidas` (probado con `--permitidas otra_herramienta`), corta en la llamada N+1 con `terminate` y aborta por turnos. Una herramienta no registrada la rechaza antes el runtime («Tool borrar_backups not found») |
| Cliente RPC Python contra Pi | `completado` en consultas; `plazo_vencido` con `stopReason: "aborted"` al vencer el plazo |
| Runner A/B con modelo de guion | A-guion 3/12, B-guion 12/12; modos `memoria`, `json-roto`, `obediente`, `bucle` y `lento` detectados |
| SDK: `run-documental.ts` con modelo de guion | Abstención correcta citando d-002; plazo vencido con `abort` |
| SDK: `run.ts` sin credenciales | Error «No API key found» (esperado) |
| MCP: `pi mcp add` + `pi mcp list` con `@modelcontextprotocol/server-filesystem` 2026.8.31 | Conectado, 14 herramientas (incluidas de escritura); `exposure: "hidden"` + `toolExposure` deja 3 lecturas `direct`; `.pi/mcp.json` ignorado sin confianza de proyecto |

El modelo de guion es un doble de prueba: las ejecuciones anteriores demuestran que el **harness** funciona sobre el runtime real, no cómo decide un modelo de IA.

## Pendiente de ejecución local

- Todo lo anterior en Windows nativo con PowerShell (instalación global, `pi.cmd`, rutas con `\`, terminación de `node` desde el cliente RPC).
- Inicio de sesión/autenticación con un proveedor y cualquier ejecución con un modelo real.
- Consulta MCP hecha por un modelo real (la conexión y la exposición sí se verificaron).
- Evaluación A/B con respuestas y trazas de un modelo real, con repeticiones.
- Aislamiento en contenedor o VM.
- Los enlaces web de `pi.dev` no se volvieron a consultar en 1.1; el contraste se hizo con la documentación empaquetada en 0.99.1.

No se ha generado ninguna llamada de pago ni se han usado credenciales.

## Repetir la validación

Desde la raíz del proyecto:

```powershell
python .\scripts\verificar_todo.py
python .\scripts\verificar_todo.py --con-pi
# Tras npm.cmd install --ignore-scripts en ejemplos\pi-package y ejemplos\sdk:
python .\scripts\verificar_todo.py --con-tipos
```

Completa esta tabla en tu rama después de ejecutar las integraciones pendientes. Conserva comando, versión, configuración sin secretos y evidencia; no marques una prueba como realizada basándote solo en su diseño.
