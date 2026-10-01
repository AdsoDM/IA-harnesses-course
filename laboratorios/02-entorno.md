# 02 — Entorno reproducible

Duración: 90 minutos. Requiere Windows, Git y permisos habituales para instalar herramientas si faltan.

1. Sigue INICIO-WINDOWS.md y registra versiones en `entregas/02-entorno.md`.
2. Comprueba Python con `python -c "import sys; print(sys.executable)"`.
3. Si usas Conda, puedes crear un entorno independiente:

```powershell
conda create -n harness-course python=3.11
conda activate harness-course
```

La creación necesita descargar Python; puedes omitirla y usar tu entorno existente compatible para los ejemplos sin dependencias. No cambies los paquetes de Spyder para instalar Pi.

4. Comprueba Node y Git; instala Pi con la versión del curso.
5. Ejecuta `pi --version` y guarda solo versión/ayuda, sin secretos.
6. Ejecuta la **primera ejecución sin credenciales** del módulo 02 (modelo de guion) y guarda la salida JSON.
7. Si tienes acceso a un modelo: abre Pi con `--tools read,grep,find,ls`, configura acceso y haz una lectura de README.md.
8. Localiza la documentación empaquetada de tu versión (`npm.cmd root -g`) y anota la ruta.

Aceptación: puedes reproducir la invocación, identificas Python usado, el modelo de guion responde con `sources: ["d-001"]` y distingues PowerShell exterior de Git Bash interior. Si falta acceso al modelo real, marca esa parte pendiente y continúa: el resto del curso funciona con el guion.

Diagnóstico: si `npm.ps1` falla por política, utiliza `npm.cmd`; si falta `node`, resuelve instalación/PATH antes de culpar a Pi. No guardes la salida de comandos que muestren claves.

Lección: [módulo correspondiente](../docs/02-entorno-windows.md). Autocorrección: [guía de soluciones](../soluciones/guia.md).
