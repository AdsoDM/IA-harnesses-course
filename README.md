# Creación y uso de harnesses para modelos de IA

Curso práctico en español · edición 1.1 · 30 de septiembre de 2026.

**Objetivo:** diseñar, construir y evaluar el software que convierte un modelo de lenguaje en un agente controlable. Usaremos un harness pequeño en Python para comprenderlo y **Pi, el proyecto de pi.dev**, para extender uno real. No es el asistente conversacional llamado Pi de Inflection.

Destino previsto en tu equipo: `E:\Oscar\PR260101\Harness`.

## Empieza aquí

1. Sigue [INICIO-WINDOWS.md](INICIO-WINDOWS.md) para colocar el proyecto en tu carpeta y crear el repositorio Git.
2. Lee [el programa](docs/00-programa.md) y marca tu punto de partida en [PROGRESO.md](PROGRESO.md).
3. Completa [el primer módulo](docs/01-fundamentos.md) y su laboratorio. Guarda tus respuestas en `entregas/`.
4. Antes de usar Pi, completa [la instalación](docs/02-entorno-windows.md) y lee [VERSIONES.md](VERSIONES.md).

La ruta principal dura **58 horas**, unas diez semanas a seis horas por semana. Hay un puente opcional de seis horas para Git, Python y TypeScript. El ritmo es una estimación: avanza cuando superes los criterios, no cuando termine el calendario.

## Novedades de la edición 1.1

- **Verificado contra Pi 0.99.1 real**: instalación, `--help`, tipos (`tsc`) de la extensión y del SDK, carga y ejecución de la extensión, flujo JSON, RPC, cancelación y MCP. Se corrigió un error de tipos del SDK. Detalle en [VALIDACION.md](VALIDACION.md).
- **Modelo de guion**: un proveedor simulado para Pi que permite hacer casi todo el curso **sin credenciales ni coste** y provocar fallos reproducibles ([README](ejemplos/pi-package/dobles/README.md)).
- **Código que faltaba**: normalizador de trazas, runner de evaluación A/B, cliente RPC en Python con pruebas, extensión de presupuesto y allowlist, SDK documental, harness documental en Python y adaptador a APIs compatibles con Chat Completions.
- **Módulo nuevo 03b**: conectar el bucle a un proveedor real.
- **Lecciones ampliadas** con ejemplos resueltos, errores frecuentes y autoevaluación; **soluciones de referencia** separadas.

## Qué vas a construir

| Etapa | Resultado que puedes enseñar |
| --- | --- |
| Fundamentos | Diagrama y contrato de un harness |
| Python | Bucle con modelo simulado, herramienta validada, límite de pasos y traza |
| Proveedor real | Adaptador Chat Completions probado offline y con un modelo |
| Pi interactivo | Sesión reproducible con contexto y herramientas seleccionadas |
| Pi extendido | Herramienta de catálogo, prompt reutilizable y control de presupuesto |
| Integración | SDK documental y cliente RPC con plazo y cancelación |
| Evaluación | Batería de 12 casos, trazas reales, criba y comparación A/B |
| Proyecto final | Asistente de documentación de PR260101 con informe de calidad |

El proyecto documental es ficticio y usa datos sintéticos. No precisa tus documentos de trabajo. Cuando lo domines podrás adaptar los contratos a un repositorio de código o a documentación de datos/BI.

## Mapa del proyecto

| Carpeta o archivo | Uso |
| --- | --- |
| `docs/` | Trece lecciones, programa y puente de programación |
| `laboratorios/` | Trece prácticas con pasos y aceptación |
| `ejemplos/mini-harness/` | Harness Python, harness documental y adaptador de proveedor, sin dependencias externas |
| `ejemplos/pi-package/` | Extensión, prompt y control de presupuesto de Pi; modelo de guion en `dobles/` |
| `ejemplos/sdk/` | Integración TypeScript con Pi (mínima y documental) |
| `ejemplos/rpc/` | Framing JSONL, cliente RPC y Pi falso para pruebas |
| `evaluacion/` | Casos, runner, normalizador, criba, configuraciones A/B, trazas de ejemplo y rúbrica |
| `proyecto-final/` | Requisitos, arquitectura e hitos |
| `plantillas/` | Bitácora, experimento, revisión humana, ADR, incidente e informe final |
| `referencias/` | Fuentes oficiales y glosario |
| `soluciones/` | Autocorrección, clave de autoevaluación y soluciones de referencia |
| `scripts/` | Comprobaciones: documentación, consistencia y verificación completa |
| `entregas/` | Tu trabajo; empieza con su README |
| `.github/` | Plantillas para issues y pull requests |

No se incluye `.git`: tú crearás el historial en tu ordenador. Tampoco se carga automáticamente ninguna extensión al abrir el curso: no hay carpeta `.pi/`. Los ejemplos se activan en los laboratorios correspondientes.

## Comprobación inicial

Desde la raíz del proyecto, en PowerShell:

```powershell
python .\scripts\verificar_todo.py
```

Ejecuta las pruebas Python y Node, el comprobador documental, el de consistencia y la criba de la fixture. Sin modelos ni red. Con Pi instalado, `--con-pi` añade la batería A/B real con el modelo de guion (esperado: A 3/12, B 12/12), y `--con-tipos` comprueba los tipos TypeScript tras `npm.cmd install --ignore-scripts` en `ejemplos\pi-package` y `ejemplos\sdk`.

`resultados-demo.jsonl` es una fixture escrita a mano para probar el evaluador; **no son respuestas de un modelo**. Las trazas de `evaluacion/trazas-ejemplo` sí proceden de Pi real, pero con el modelo de guion: tampoco miden un modelo de IA.

## Estado de verificación

Consulta [VALIDACION.md](VALIDACION.md) para las comprobaciones realmente ejecutadas y dónde. Resumen: todo lo que no necesita un proveedor se ejecutó contra Pi 0.99.1 en Linux; queda pendiente de tu parte la ejecución en Windows y cualquier prueba con un modelo real. No se ha generado ninguna llamada de pago.

La documentación de Pi cambia con rapidez. Se toma `0.99.1` como versión de referencia; la documentación empaquetada con esa versión es la fuente contrastada. No se promete compatibilidad con cualquier versión anterior o posterior. Véanse [fuentes](referencias/fuentes.md) y [mantenimiento](MANTENIMIENTO.md).
