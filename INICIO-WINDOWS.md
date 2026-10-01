# Colocar el curso en E:\Oscar\PR260101\Harness

## Extraer sin añadir una carpeta extra

El ZIP contiene los archivos en su raíz: `README.md`, `docs/`, `laboratorios/`, etc. Descárgalo y extráelo en `E:\Oscar\PR260101\Harness`. Si allí ya hay archivos, revisa las coincidencias antes de extraer; no sobrescribas trabajo previo.

Puedes usar el Explorador de Windows. Alternativamente, cambia la ruta del ZIP en este comando de PowerShell:

```powershell
$destinoCurso = 'E:\Oscar\PR260101\Harness'
$archivoCurso = "$HOME\Downloads\curso-harnesses-pi.zip"
New-Item -ItemType Directory -Path $destinoCurso -Force | Out-Null
Expand-Archive -LiteralPath $archivoCurso -DestinationPath $destinoCurso
Set-Location $destinoCurso
Get-ChildItem
```

Sin `-Force`, `Expand-Archive` evita reemplazar silenciosamente archivos existentes. Ajusta el nombre si tu navegador lo ha cambiado. Si ves otra carpeta `Harness` dentro, mueve su contenido al destino elegido.

## Crear el historial Git

Comprueba primero si ya estás dentro de un repositorio:

```powershell
git rev-parse --show-toplevel
```

Si devuelve una raíz, decide si el curso pertenece a ese proyecto. Si devuelve «not a git repository» y quieres un repositorio independiente:

```powershell
git init -b main
git status
git add .
git diff --cached --stat
git commit -m "docs: incorporar curso de harnesses con Pi"
```

Si Git solicita identidad, configúrala **solo para este repositorio** con tus datos reales:

```powershell
git config user.name "Tu nombre"
git config user.email "Tu correo"
```

Vuelve a ejecutar el commit. No necesitas GitHub para trabajar con Git. Para usar GitHub, crea allí un repositorio vacío y copia su URL; después ejecuta, sustituyendo la URL:

```powershell
git remote add origin https://github.com/TU_USUARIO/TU_REPOSITORIO.git
git push -u origin main
```

Ese último paso publica lo que hayas confirmado en Git. Revisa antes las entregas y cualquier dato personal. Los secretos, las trazas completas, los resultados y la configuración aislada de Pi (`.pi-curso/`) están excluidos mediante `.gitignore`.

## Trabajar un módulo

```powershell
git switch -c lab/01-fundamentos
# Crea entregas/01-fundamentos.md con tus respuestas.
git add entregas/01-fundamentos.md PROGRESO.md
git commit -m "lab: completar fundamentos del harness"
git switch main
git merge lab/01-fundamentos
```

Usa un commit por resultado verificable. `git diff` permite revisar cambios; `git log --oneline` muestra la progresión. No copies comandos de borrado o reinicio para resolver un problema sin comprenderlos.

## Primeras lecturas

Abre el proyecto en VS Code si lo tienes instalado:

```powershell
code .
```

Abre `README.md`, previsualiza Markdown y sigue los enlaces. Empieza con el [programa](docs/00-programa.md). Comprueba que todo funciona con `python .\scripts\verificar_todo.py` antes del primer commit. Si no tienes editor especializado, los `.md` son texto UTF-8 y puedes abrirlos con cualquier editor.
