# Paquete de práctica Pi

| Ruta | Qué es | ¿En el manifest? |
| --- | --- | --- |
| `shared/catalogue.mjs` | Núcleo del catálogo sintético (sin Pi) | — |
| `extensions/catalogue.ts` | Adaptador Pi: herramienta `lookup_document` | Sí |
| `prompts/respuesta-documental.md` | Plantilla `/respuesta-documental` | Sí |
| `extensions/presupuesto.ts` | Control: allowlist, máximo de llamadas y de turnos | No: cárgalo con `-e` |
| `dobles/modelo-guion.ts` | Proveedor simulado sin red ([README](dobles/README.md)) | No: cárgalo con `-e` |
| `tests/` | Pruebas del núcleo con `node --test` | — |

El núcleo se prueba sin dependencias (`node --test .\tests\catalogue.test.mjs`). Para comprobar tipos de los adaptadores contra Pi 0.99.1, instala las devDependencies fijadas: `npm.cmd install --ignore-scripts` y `npm.cmd run check`. Eso crea `node_modules` aquí (ignorado por Git) y no modifica tu Pi global. Pi proporciona sus propios paquetes y TypeBox a las extensiones en ejecución: por eso aparecen como `peerDependencies`.

Sigue [módulo 07](../../docs/07-extensiones-pi.md) y [laboratorio 07](../../laboratorios/07-extension.md). El manifest permite después instalar el paquete local en un proyecto de ensayo. No publica nada: `private: true` previene publicación npm accidental.

El catálogo es sintético y está embebido. La extensión no lee tus documentos ni usa rutas arbitrarias. Eso limita la herramienta; no cambia los permisos del proceso Pi. Carga, tipos y ejecución del adaptador se verificaron con Pi 0.99.1 (véase [VALIDACION.md](../../VALIDACION.md)); repítelo en tu instalación.
