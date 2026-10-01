# Fuentes y trazabilidad técnica

Consulta realizada: **30/09/2026**. Fuentes primarias; las páginas `latest` pueden cambiar. La explicación pedagógica, los casos y los ejemplos del curso son una elaboración propia, no una copia del manual.

## Fuente verificada en la edición 1.1

En 1.1 el contraste se hizo contra el **paquete instalado** `@earendil-works/pi-coding-agent@0.99.1`: su documentación empaquetada (`docs/*.md`, las mismas páginas que la web para esa versión), sus ejemplos (`examples/`) y sus declaraciones de tipos (`dist/**/*.d.ts`), además de la ejecución real descrita en [VALIDACION.md](../VALIDACION.md). Es la fuente preferente para reproducir el curso con esa versión:

| Documento empaquetado | Qué se verificó | Secciones |
| --- | --- | --- |
| `docs/cli.md`, `pi --help` | Flags, modos, herramientas, `codemode`, comandos `mcp` y `auth` | 02, 04, 07, 09 |
| `docs/extensions.md`, `dist/core/extensions/types.d.ts` | Factory, `registerTool`, `ToolDefinition`, `tool_call`/`turn_end`, flags, ciclo de vida | 06, 07, 11 |
| `pi-agent-core` `AgentToolResult` | `content`, `details`, `structuredContent`, `isError`, `terminate` | 06 |
| `docs/custom-provider.md`, `pi-ai` `providers/faux` | Registro de proveedores y proveedor *faux* (base del modelo de guion) | 02, dobles |
| `docs/json.md`, `docs/rpc.md`, `docs/rpc-commands.md` | Framing, eventos, `disposition`, `abort`, cierre | 04, 08 |
| `docs/sdk.md`, `dist/core/sdk.d.ts`, `resource-loader.d.ts` | `createAgentSession`, `noTools`, `DefaultResourceLoader`, `setModel` | 08 |
| `docs/mcp.md` | Configuración, exposición, `toolExposure`, confianza | 09 |
| `docs/security.md`, `docs/windows.md`, `docs/environment-variables.md` | Confianza de proyecto, Git Bash/PowerShell, `PI_CODING_AGENT_DIR`, `PI_OFFLINE` | 02, 04, 11 |
| `docs/skills.md`, `docs/prompt-templates.md`, `docs/packages.md`, `docs/settings.md` | Carga de skills, sustituciones, manifest y peer dependencies, `retry` | 05, 07, 11 |

Para localizarlos: `npm.cmd root -g` y, dentro, `@earendil-works\pi-coding-agent`.

## Fuentes web

| Fuente oficial | Qué se verificó | Secciones relacionadas |
| --- | --- | --- |
| [pi.dev](https://pi.dev/) | Identidad del proyecto y interfaces generales | 01, 04 |
| [Quickstart](https://pi.dev/docs/latest/quickstart) | Paquete npm, Node mínimo, login | 02 |
| [Windows](https://pi.dev/docs/latest/windows) | Git Bash y herramienta PowerShell | 02 |
| [Cómo funciona Pi](https://pi.dev/docs/latest/how-pi-works) | Bucle, contexto, sesiones | 04, 05 |
| [CLI](https://pi.dev/docs/latest/cli) | Flags de modos, recursos y herramientas | 04, 07, 09 |
| [Configuración](https://pi.dev/docs/latest/configuration) | Ámbito personal/proyecto y contexto | 05 |
| [Prompt templates](https://pi.dev/docs/latest/prompt-templates) | Markdown, argumentos y carga | 05, 07 |
| [Skills](https://pi.dev/docs/latest/skills) | SKILL.md y carga progresiva | 05 |
| [Extensiones](https://pi.dev/docs/latest/extensions) | Factory, herramientas, lifecycle y resultados | 06, 07 |
| [Tipos publicados](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/src/core/extensions/types.ts) | Firma de execute y esquema de herramienta | 07 |
| [Pi packages](https://pi.dev/docs/latest/packages) | Manifest pi, peer dependencies y paquetes locales | 07 |
| [SDK](https://pi.dev/docs/latest/sdk) | Sesión, memoria, prompt, dispose | 08 |
| [RPC](https://pi.dev/docs/latest/rpc) | Protocolo y correlación | 08 |
| [Comandos RPC](https://pi.dev/docs/latest/rpc-commands) | Prompt aceptado frente a tarea completada | 08 |
| [JSON events](https://pi.dev/docs/latest/json) | Framing LF y eventos | 04, 08 |
| [MCP en Pi](https://pi.dev/docs/latest/mcp) | Configuración local, transportes y herramientas | 09 |
| [Introducción MCP](https://modelcontextprotocol.io/docs/2026-07-28/getting-started/intro) | Protocolo de capacidades | 09 |
| [Variables de entorno](https://pi.dev/docs/latest/environment-variables) | `PI_CODING_AGENT_DIR`, `PI_OFFLINE` (añadida en 1.1) | 02 |
| [Proveedores personalizados](https://pi.dev/docs/latest/custom-provider) | `registerProvider`, streams (añadida en 1.1) | 07 |
| [Integración CLI](https://pi.dev/docs/latest/cli-integration) | Elección print/JSON/RPC/SDK (añadida en 1.1) | 08 |
| [Seguridad Pi](https://pi.dev/docs/latest/security) | Permisos, project trust y aislamiento | 11 |
| [Changelog](https://pi.dev/changelog) | Versiones 0.99.0/0.99.1 anunciadas | VERSIONES.md |
| [Release 0.99.1](https://github.com/earendil-works/pi/releases/tag/v0.99.1) | Referencia de release | VERSIONES.md |
| [Node](https://nodejs.org/en/download) | Descarga oficial del runtime | 02 |
| [Git init](https://git-scm.com/docs/git-init) | Creación de repositorio y rama inicial | INICIO-WINDOWS.md |

Lecturas complementarias oficiales: [aislamiento Pi](https://pi.dev/docs/latest/containerization), [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/intro.html), [Python](https://docs.python.org/3/tutorial/).

## Límites de contraste

Edición 1.0: se contrastó documentación web y contrato publicado, sin poder instalar el paquete. Edición 1.1: se instaló el paquete 0.99.1, se compilaron y ejecutaron adaptador, SDK, cliente RPC y runner, y se contrastó la documentación empaquetada. Las páginas web no se volvieron a consultar en 1.1: los enlaces añadidos siguen el mismo patrón `pi.dev/docs/latest/<página>` que los nombres de archivo empaquetados. Los tipos de GitHub enlazados son de `main`; los de tu paquete fijado son los que cuentan. Para Chat Completions, Anthropic Messages y OpenAI Responses (módulo 03b) consulta la referencia oficial de cada proveedor antes de implementar: la tabla del curso es orientativa.

Los documentos del catálogo son ficticios y no son fuentes sobre el mundo real. Las métricas y umbrales de la rúbrica son decisiones del curso. No se afirma una certificación oficial de Pi ni de ningún proveedor.
