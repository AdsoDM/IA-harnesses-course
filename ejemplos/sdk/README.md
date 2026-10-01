# Demostraciones SDK

Requieren Node 22.19 o posterior (Node 24 LTS recomendado) y Pi 0.99.1 como dependencia local. Ambas se comprobaron con `tsc` y se ejecutaron contra Pi 0.99.1; `run.ts` necesita credenciales, `run-documental.ts` funciona también con el modelo de guion.

| Archivo | Qué demuestra |
| --- | --- |
| `run.ts` | Sesión en memoria sin herramientas (`noTools: "all"`), contrato JSON trivial, `dispose` en `finally` |
| `run-documental.ts` | Catálogo + plantilla cargados explícitamente, allowlist, eventos reales, plazo con `abort`, fila compatible con `score.py` |

Desde la raíz, PowerShell:

```powershell
Set-Location .\ejemplos\sdk
npm.cmd install --ignore-scripts
npm.cmd run check
npm.cmd start                                   # sin credenciales: error "No API key found" (esperado)
$env:CURSO_MODELO = "guion"; npm.cmd run documental -- "¿Cuál es el presupuesto de práctica?"
Remove-Item Env:CURSO_MODELO
Set-Location ..\..
```

Node ejecuta estos `.ts` eliminando los tipos (activado por defecto en las versiones que exige Pi). No se usan enums ni otras construcciones que necesiten transformación. El chequeo de `tsc` ocurre por separado: ejecutar un `.ts` no equivale a comprobar sus tipos. En la edición 1.0, `noTools: true` se ejecutaba pero no compilaba.

La instalación crea `package-lock.json`: revisa y confírmalo para reproducir tus dependencias. En otra instalación usa `npm.cmd ci --ignore-scripts`. Si no resuelve versión o API, contrasta el changelog y los tipos del paquete instalado, documenta la diferencia y no afirmes validación hasta que compile y ejecute.

`noTools` desactiva herramientas, pero no equivale a no cargar recursos ni a un sandbox. `run.ts` usa la configuración descubierta por defecto; `run-documental.ts` desactiva el descubrimiento y nombra cada recurso. Para producción controla además settings y modelo según los tipos de tu versión y añade supervisión, cancelación y presupuesto.
