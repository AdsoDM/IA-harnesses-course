# Versiones y reproducibilidad

| Elemento | Referencia del curso | Cómo registrar tu ejecución |
| --- | --- | --- |
| Pi | 0.99.1 (verificada: instalación, tipos y ejecución) | `pi --version` y `pi --help` |
| Paquete CLI/SDK | `@earendil-works/pi-coding-agent` | Nombre y versión instalada |
| Tipos para `tsc` | `@earendil-works/pi-ai` 0.99.1, `typebox` 1.3.27, `typescript` 5.9.3, `@types/node` 24.19.0 | `package-lock.json` confirmado |
| Node | Mínimo 22.19 según quickstart; ruta recomendada: Node 24 LTS. Verificado con 22.23.2 | `node --version` |
| Python | 3.10 o posterior (verificado con 3.10.12); 3.11+ recomendado | `python --version` |
| Git | Versión que admita `git init -b` y `git switch` | `git --version` |
| Servidor MCP de práctica | `@modelcontextprotocol/server-filesystem` 2026.8.31 en la verificación; usa la que devuelva `npm view` | Versión fijada en `mcp.json` |
| Proveedor/modelo | Elegido por ti, sin identificador supuesto | Proveedor, ID exacto y fecha |

No se fija un modelo porque disponibilidad, acceso y precio dependen del proveedor. Usa un ID de tu catálogo y registra los parámetros que el proveedor realmente acepte. Temperatura cero no garantiza determinismo en todo servicio. El modelo de guion (`curso/guion`) no es un modelo: regístralo como «simulado».

Instalación de referencia: `npm install -g --ignore-scripts @earendil-works/pi-coding-agent@0.99.1`. Si no puedes obtenerla, verifica en el registro y el changelog el nombre/versión disponibles; registra cualquier sustitución. No cambies a un nombre de paquete antiguo por intuición. (Pi 0.99.1 mantiene alias de importación `@mariozechner/*` para extensiones antiguas, pero el curso usa `@earendil-works/*`.)

La documentación de la versión instalada está en `node_modules/@earendil-works/pi-coding-agent/docs` (y los ejemplos comprobados en `examples/`). Es la referencia a usar cuando la web `latest` ya describa otra versión.

Los ejemplos SDK y del paquete generan `package-lock.json` al instalar. Confírmalo en Git cuando lo hayas creado. Se ha omitido un lockfile inventado: los hashes deben proceder de una instalación real. Después usa `npm ci --ignore-scripts` para reproducirla.

En Pi 0.99 el changelog anuncia MCP y codemode integrados, y la verificación lo confirma (`pi mcp`, extensión `builtin:mcp`, herramienta `codemode` con sandbox QuickJS). Tutoriales antiguos que describen Pi sin MCP pueden corresponder a otro estado del proyecto. El curso no asume soporte nativo de subagentes ni un modo de planificación completo: existen como **ejemplos** de extensión, no como capacidades integradas.

Fuentes: [quickstart](https://pi.dev/docs/latest/quickstart), [changelog](https://pi.dev/changelog), [Windows](https://pi.dev/docs/latest/windows), [Node](https://nodejs.org/en/download).
