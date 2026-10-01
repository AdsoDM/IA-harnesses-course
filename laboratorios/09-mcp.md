# 09 — Integración MCP opcional y ADR

Duración: 2 horas. El ADR es obligatorio; la conexión requiere descargar el servidor y un modelo real para la consulta (el modelo de guion no usa MCP).

1. Crea un directorio de ensayo fuera del curso:

```powershell
New-Item -ItemType Directory -Path 'E:\Oscar\PR260101\Harness-MCP-Practica\datos' -Force
Set-Content -Path 'E:\Oscar\PR260101\Harness-MCP-Practica\datos\nota.txt' -Value 'Dato sintetico: retencion 30 dias'
Set-Location 'E:\Oscar\PR260101\Harness-MCP-Practica'
pi mcp --help
npm.cmd view @modelcontextprotocol/server-filesystem version
```

2. Anota la versión devuelta y úsala sustituyendo `VERSION_VERIFICADA` (no ejecutes el marcador literalmente):

```powershell
pi mcp add -l filesystem --exposure direct -- npx -y @modelcontextprotocol/server-filesystem@VERSION_VERIFICADA 'E:\Oscar\PR260101\Harness-MCP-Practica\datos'
Get-Content .\.pi\mcp.json
```

Pi avisará de que `.pi/mcp.json` se ignora hasta que confíes en el proyecto. Inicia `pi` en esa carpeta y acepta la confianza (o usa `/trust`). Después, `pi mcp list` debe mostrar el servidor conectado y sus herramientas.

3. **Limita la exposición.** Edita `.pi\mcp.json` como en el módulo: `"exposure": "hidden"` y `toolExposure` solo para `read_text_file`, `list_directory` y `list_allowed_directories`. Ejecuta `pi mcp list` y comprueba que solo esas tres aparecen como `[direct]`.
4. En `pi`, inspecciona `/mcp`. Pide que lea la nota y registra la llamada `mcp__filesystem__read_text_file` en la traza (`--mode json` si lo haces en una sola invocación). Pide después que escriba un archivo: la herramienta no debe estar disponible. No pruebes borrados ni rutas personales.
5. En Windows, si `npx` no se resuelve, consulta la configuración stdio de tu versión y usa la ruta del ejecutable correspondiente, sin convertir argumentos en una cadena de shell improvisada.
6. Vuelve a la carpeta del curso y escribe un ADR comparando MCP y extensión local con [la plantilla](../plantillas/adr.md).

Aceptación: declaras qué proceso accede a qué directorio, qué herramientas anunció el servidor, cuáles expusiste y qué límites faltan (el proceso del servidor sigue pudiendo escribir en el directorio permitido). Si omites la conexión, marca el resultado como diseño, no como prueba ejecutada.

Lección: [módulo correspondiente](../docs/09-mcp.md). Autocorrección: [guía de soluciones](../soluciones/guia.md).
