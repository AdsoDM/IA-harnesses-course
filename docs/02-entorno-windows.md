# 02 — Entorno de trabajo en Windows y PowerShell

Tiempo: 3 horas. Objetivo: separar el entorno Python del runtime Node de Pi, registrar una instalación reproducible y hacer una primera ejecución de Pi **sin credenciales**.

## Tres herramientas, tres responsabilidades

Python ejecutará el harness didáctico y el evaluador; Node ejecutará Pi y el SDK; Git gestionará versiones del curso. Activar `spyder-env-1` cambia el Python de la sesión, pero no instala Pi ni inicializa Node.

Tu entorno Conda conocido puede usarse para los ejercicios de biblioteca estándar:

```powershell
& "C:\Users\ogarcia\AppData\Local\anaconda3\shell\condabin\conda-hook.ps1"
conda activate spyder-env-1
python -c "import sys; print(sys.executable)"
```

Solo ejecútalo si sigue correspondiendo a tu instalación. El hook integra Conda en esa sesión. Para estos ejemplos no necesitas instalar paquetes en el entorno de Spyder. Si prefieres aislamiento, crea un entorno del curso en el laboratorio; así no alteras dependencias de tu trabajo.

```powershell
Set-Location 'E:\Oscar\PR260101\Harness'
python --version
node --version
npm.cmd --version
git --version
```

En Windows, `npm.cmd` evita seleccionar el wrapper `npm.ps1` si tu política impide scripts. Si no tienes Node, instálalo desde su web oficial; toma Node 24 LTS como ruta del curso (Pi exige 22.19 o posterior). Instala Git for Windows: Pi usa Git Bash para su herramienta `bash`.

## Instalar Pi

La versión de referencia está en [VERSIONES.md](../VERSIONES.md). La instalación, la ayuda y los tipos de esa versión se han verificado; consulta [VALIDACION.md](../VALIDACION.md).

```powershell
npm.cmd install -g --ignore-scripts @earendil-works/pi-coding-agent@0.99.1
pi --version
pi --help
```

`pi --version` debe mostrar `0.99.1`. Si PowerShell selecciona un wrapper `pi.ps1` bloqueado, prueba `pi.cmd --version` y usa `pi.cmd` en los comandos posteriores. Comprueba con `Get-Command pi -All` qué archivo resuelve. No necesitas modificar la política global de ejecución para resolver un wrapper.

**La documentación de tu versión viaja con el paquete.** `npm.cmd root -g` te da la carpeta global; dentro, `@earendil-works\pi-coding-agent\docs` contiene los mismos `.md` que la web para la versión instalada, y `examples\` los ejemplos comprobados. Es la fuente preferente cuando la web `latest` avance.

## Una configuración de Pi solo para el curso

Pi guarda credenciales, ajustes y sesiones en `~\.pi\agent`. Para practicar sin tocar tu configuración personal, apunta `PI_CODING_AGENT_DIR` a una carpeta del curso (ya ignorada por Git):

```powershell
$env:PI_CODING_AGENT_DIR = "$PWD\.pi-curso\agente"   # solo en esta sesión de PowerShell
$env:PI_OFFLINE = "1"                                # sin actualizaciones de catálogo al arrancar
```

Distingue **variable de PowerShell** (`$destino = ...`, solo existe en el shell) de **variable de entorno** (`$env:NOMBRE = ...`, la heredan los procesos hijos como Pi). Cuando uses un modelo real, quita la primera (`Remove-Item Env:PI_CODING_AGENT_DIR`) para volver a tus credenciales de `/login`, o haz `/login` también en la configuración del curso.

## Primera ejecución sin credenciales

El curso incluye un **modelo de guion**: una extensión que registra un proveedor simulado (`curso/guion`). No es una IA ni llama a la red; sigue reglas fijas sobre las preguntas del catálogo. Sirve para comprobar que Pi carga extensiones y ejecuta herramientas antes de configurar un proveedor.

```powershell
pi -ne -ns -np -nc --no-session `
  -e .\ejemplos\pi-package\dobles\modelo-guion.ts `
  -e .\ejemplos\pi-package\extensions\catalogue.ts `
  --prompt-template .\ejemplos\pi-package\prompts\respuesta-documental.md `
  --tools lookup_document --provider curso --model guion `
  --print "/respuesta-documental ¿Cuál es la retención vigente de backups?"
```

Debes obtener un JSON con `"status":"answered"`, los 30 días y `"sources":["d-001"]`. Si falla, el problema es de instalación, rutas o carga de extensiones, no de credenciales: esa separación es el objetivo.

## Shell exterior y herramienta interior

Puedes iniciar Pi desde PowerShell y que su herramienta `bash` use Git Bash. Son capas distintas. No deduzcas que el modelo ejecuta PowerShell por ver un prompt `PS` antes de iniciar Pi. Pi resuelve Bash en este orden: `shellPath` de `settings.json`, Git Bash en `Program Files` y `bash.exe` en `PATH`. Para tareas nativas Windows existe una herramienta `powershell` opcional (usa `pwsh.exe` si existe; si no, Windows PowerShell) que se activa con `defaultTools`. El curso empieza sin herramientas de shell.

Dentro de Pi, `/login` configura acceso y `/model` permite elegir un modelo. Elige según tus credenciales reales, sin asumir que una cuenta tenga todos los modelos. `pi auth check --provider <proveedor>` informa `ready`, `not_ready` o `invalid` sin iniciar sesión. Guarda las claves por el mecanismo del proveedor y Pi; no las pegues en `AGENTS.md` ni las confirmes en Git. Los comandos `pi auth print-api-key` imprimen secretos: no los ejecutes en una sesión que estés grabando.

## Diagnóstico razonado

Si un comando no existe, inspecciona resolución y PATH; si existe y está bloqueado, inspecciona el wrapper; si arranca pero el modelo falla, inspecciona autenticación, ID y conectividad. Son fallos distintos. Reinicia la terminal después de instalar herramientas que cambian PATH.

| Síntoma | Capa probable | Comprobación |
| --- | --- | --- |
| `pi` no se reconoce | PATH / instalación | `Get-Command pi -All`, `npm.cmd root -g` |
| «no se puede cargar ... pi.ps1» | Política de scripts | Usar `pi.cmd` |
| El modelo de guion falla | Rutas o carga de extensión | Rutas relativas a la carpeta actual; mensaje de error de la extensión |
| «No API key found» | Credenciales | `/login` o `pi auth check --provider X` |
| Error 401/403/429 | Proveedor | Clave, permisos del modelo, cuota |

El coste se controla inicialmente con pocas preguntas y un límite personal. Anota un presupuesto antes de ejecutar lotes: no hay un presupuesto en euros que funcione automáticamente en todas las configuraciones de Pi.

## Errores frecuentes

- Instalar Pi «dentro» de Conda: Pi es un paquete Node global; Conda no interviene.
- Olvidar que `$env:` dura lo que la ventana de PowerShell: anota qué variables usaste en la bitácora.
- Pegar una clave en un comando que queda en el historial (`Get-History`) o en una captura.
- Confundir el fallo del modelo de guion (rutas) con el de un proveedor (credenciales).

## Autoevaluación

1. ¿Qué diferencia hay entre `$x = 1` y `$env:X = "1"` para un proceso que lanzas después?
2. ¿Por qué el curso recomienda `npm.cmd` y, a veces, `pi.cmd`?
3. ¿Qué demuestra la primera ejecución con el modelo de guion y qué no?
4. ¿Dónde encuentras la documentación exacta de la versión instalada de Pi?
5. ¿Qué shell usa la herramienta `bash` de Pi en Windows nativo?

Respuestas: [clave](../soluciones/autoevaluacion.md#02).

Aceptación: registrar versiones, resolver la ruta de Python, ejecutar el modelo de guion y explicar qué shell ejecuta cada capa. Práctica: [laboratorio 02](../laboratorios/02-entorno.md). Fuentes: [quickstart](https://pi.dev/docs/latest/quickstart), [Windows](https://pi.dev/docs/latest/windows), [variables de entorno](https://pi.dev/docs/latest/environment-variables), [Node](https://nodejs.org/en/download).
