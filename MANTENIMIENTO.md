# Actualizar el curso sin perder reproducibilidad

Mantén un tag de la edición utilizada antes de actualizar. Haz una rama `docs/actualizar-pi` y registra la versión nueva. Consulta el changelog, `pi --help` y la documentación empaquetada de la nueva versión (`node_modules/@earendil-works/pi-coding-agent/docs`).

## Regresión mínima tras cambiar de versión de Pi

1. `npm.cmd install --ignore-scripts` con la versión nueva en `ejemplos\pi-package` y `ejemplos\sdk` (actualiza las versiones fijadas en sus `package.json`).
2. `python .\scripts\verificar_todo.py --con-tipos`: detecta cambios de tipos en extensiones, modelo de guion y SDK.
3. `python .\scripts\verificar_todo.py --con-pi`: la batería A/B con el modelo de guion debe seguir dando 3/12 y 12/12. Si cambia, compara una traza nueva con `evaluacion/trazas-ejemplo` antes de tocar el normalizador.
4. Repite a mano los modos `bucle` y `lento` (presupuesto y cancelación) y `pi mcp list`.
5. Solo después, ejecuta con tu modelo real.

Ejecuta el mismo conjunto de casos con la edición anterior y la nueva. Si has cambiado modelo y harness a la vez, no podrás atribuir la diferencia. Usa un diseño de dos comparaciones: primero harness con modelo fijo; después modelo con harness fijo.

Actualiza [VERSIONES.md](VERSIONES.md), [fuentes](referencias/fuentes.md) y [VALIDACION.md](VALIDACION.md). Explica en CHANGELOG los cambios incompatibles. Los hechos del catálogo sintético deben cambiar conjuntamente en `catalogue.mjs`, `catalogo.json`, dataset, fixtures, plantilla y reglas del modelo de guion; `python .\scripts\check_consistencia.py` comprueba lo automatizable. Si regeneras `trazas-ejemplo`, anonimiza rutas y revisa que no contengan datos personales.

Después de revisar y confirmar los cambios puedes etiquetar una edición, por ejemplo `git tag -a curso-v1.2 -m "Actualizar compatibilidad de Pi"`. Un tag local no publica nada; un push explícito lo sube al remoto.
