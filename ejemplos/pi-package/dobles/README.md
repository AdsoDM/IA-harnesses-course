# Modelo de guion (proveedor simulado)

`modelo-guion.ts` es una extensión que registra el proveedor `curso` con el modelo `guion`. **No es una IA**: aplica reglas fijas a las preguntas del catálogo sintético y responde sin red, credenciales ni coste. Está construido sobre el proveedor *faux* que `@earendil-works/pi-ai` usa en sus propias pruebas.

Sirve para ejercitar el runtime real de Pi —carga de extensiones, herramientas, eventos JSON, RPC, SDK, evaluación, presupuesto y cancelación— antes de gastar inferencia, y para provocar fallos reproducibles. Sus resultados demuestran propiedades del **harness**, nunca la calidad de un modelo.

```powershell
pi -ne -ns -np -nc --no-session -e .\ejemplos\pi-package\dobles\modelo-guion.ts `
  -e .\ejemplos\pi-package\extensions\catalogue.ts `
  --prompt-template .\ejemplos\pi-package\prompts\respuesta-documental.md `
  --tools lookup_document --provider curso --model guion --guion auto `
  --mode json "/respuesta-documental ¿Cuál es la retención vigente de backups?"
```

## Modos

Se eligen con `--guion MODO` o con la variable `CURSO_GUION` (el flag tiene prioridad).

| Modo | Comportamiento |
| --- | --- |
| `auto` (defecto) | Sigue instrucciones: consulta solo si el prompt contiene «Consulta los documentos»; responde en JSON solo si pide «objeto JSON» |
| `correcto` | Consulta los documentos necesarios y responde en JSON aunque no se le pida |
| `memoria` | Responde sin consultar, con datos obsoletos o inventados |
| `json-roto` | Consulta, pero responde en prosa |
| `bucle` | Pide `lookup_document` d-001 indefinidamente |
| `lento` | Como `correcto`, emitiendo unos 4 tokens por segundo |
| `obediente` | Ante una petición prohibida, lee d-004 y llama a la herramienta inexistente `borrar_backups` |

## Límites

- Solo conoce las preguntas del curso y variantes cercanas; ante otras se abstiene o responde de «memoria».
- No usa MCP, skills ni `read`; no sirve para los laboratorios que exigen esas capacidades.
- No se incluye en el manifest del paquete: cárgalo siempre con `-e` explícito.
- Verificado con Pi 0.99.1. Si cambias de versión, `npm.cmd run check` en `ejemplos\pi-package` detecta cambios de tipos.
