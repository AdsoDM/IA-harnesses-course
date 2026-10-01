# Cómo mantener este proyecto

Cada cambio debe explicar el problema, la solución y su verificación. Usa ramas `docs/tema`, `lab/numero` o `feat/capacidad`. Antes de confirmar: revisa `git diff`, ejecuta `python scripts/verificar_todo.py` (y `--con-pi` si tocas algo que use Pi) y comprueba que no incluyes claves, sesiones privadas ni la carpeta `.pi-curso/`.

Convenciones: nombres de archivos en minúsculas con guiones para nuevos capítulos; títulos y texto en español; enlaces relativos; código ejecutable marcado como tal; pseudocódigo identificado explícitamente. Las plantillas están en [plantillas](plantillas/README.md).

Cuando cambia una API, actualiza lección, práctica, ejemplo, fuentes y validación en el mismo cambio. Cada lección nueva necesita las secciones «Errores frecuentes» y «Autoevaluación», con su clave en `soluciones/autoevaluacion.md`; `check_docs.py` lo comprueba. Etiqueta como simulado todo resultado obtenido con el modelo de guion. Una respuesta convincente no demuestra que una herramienta haya ejecutado lo que afirma: incluye una traza anonimizada o una prueba independiente.

La documentación del curso no concede una licencia sobre el código original de Pi. Los ejemplos de este repositorio fueron redactados para el curso; las dependencias conservan sus licencias. Antes de distribuir una adaptación comercial, define la licencia del material que añadas.
