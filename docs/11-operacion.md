# 11 — Operación, controles y recuperación

Tiempo: 5 horas. Objetivo: impedir que un fallo pequeño se convierta en efectos sin límite y dejar evidencia útil.

## Cuatro controles distintos

| Control | Qué reduce | Qué no asegura |
| --- | --- | --- |
| Instrucciones | Confusión del modelo | Cumplimiento obligatorio |
| Validación y política | Operaciones fuera del contrato | Aislamiento de código de extensiones |
| Permisos del SO/sandbox | Acceso y efectos posibles | Veracidad de respuestas |
| Observación y recuperación | Tiempo hasta detectar/corregir | Prevención absoluta |

La carpeta de trabajo no es un límite de acceso. Pi y sus extensiones corren con los permisos del proceso. Project trust decide recursos que se cargan; no sustituye un sandbox. El catálogo evita rutas arbitrarias y no ofrece escritura, pero el proceso todavía conserva su entorno.

La guía de seguridad de Pi es explícita: Pi no pide aprobación antes de cada llamada; observar la transcripción, la confianza de proyecto y revisar diffs **no crean una frontera de seguridad**; la opción práctica más fuerte es ejecutar Pi completo dentro de un contenedor, VM o sandbox con solo los archivos, credenciales y red necesarios. Además, `AGENTS.md` se carga aunque rechaces la confianza: trata las instrucciones de una carpeta como entrada no confiable.

## Presupuesto de ejecución

Define por tarea: máximo de iteraciones, llamadas de herramienta, plazo total y presupuesto de inferencia. Las APIs y los proveedores no siempre exponen los mismos contadores. Implementa lo que puedas medir y documenta lo no medido. Un límite nominal sin comprobación no es un control.

Qué controla cada pieza en el curso:

| Límite | Dónde se aplica | Comprobación |
| --- | --- | --- |
| Herramientas visibles | `--tools lookup_document` (runtime) | Traza: no aparecen otras herramientas declaradas |
| Herramientas existentes | Runtime: una herramienta no registrada no se puede ejecutar | `--guion obediente`: «Tool borrar_backups not found» |
| Herramientas ejecutables | `presupuesto.ts --permitidas` (evento `tool_call`), defensa en profundidad si alguien amplía `--tools` | `--permitidas otra`: hasta `lookup_document` queda bloqueada |
| Llamadas por ejecución | `presupuesto.ts --max-llamadas` | `--guion bucle`: la 7.ª llamada se bloquea con `terminate` |
| Turnos por ejecución | `presupuesto.ts --max-turnos` → `ctx.abort()` | El run acaba con `stopReason` de error y sin respuesta |
| Tiempo por caso | Runner/cliente RPC: `abort`, gracia, `terminate`, `kill` | `--guion lento --plazo 1`: `plazo_vencido` |
| Reintentos del agente | Ajustes `retry.enabled` / `retry.maxRetries` (por defecto 3) | Eventos `auto_retry_start/end` |
| Gasto | Nada automático: tu presupuesto y la consola del proveedor | Uso sumado por el normalizador cuando el proveedor lo informa |

Pi no trae un límite de pasos por defecto. Puede reintentar o continuar por eventos. `agent_end` no siempre marca final definitivo. El host debe distinguir éxito, fallo, cancelación y plazo vencido. Al cancelar espera un periodo breve de cierre y comprueba qué efectos ocurrieron; cancelar una petición no revierte una herramienta que ya escribió.

## Confirmar un efecto

Para una acción relevante, muestra la propuesta concreta y confirma antes de ejecutarla cuando la política lo requiera. La aprobación debe estar ligada a argumentos específicos, no a «hacer lo necesario» indefinidamente. Para nuestro proyecto no hay escritura externa: una solicitud de publicar o borrar se bloquea y se explica.

Una regex que busca `rm` no es una política completa de shell. Hay aliases, intérpretes y operaciones equivalentes. Para el curso, evita ofrecer shell al agente documental y usa permisos del sistema cuando necesites un límite real. Recuerda también que el canal RPC admite un comando `bash` directo: un cliente RPC es tan privilegiado como una persona en la terminal.

Si necesitas confirmación humana, las pistas `annotations` de cada herramienta permiten decidir qué confirmar (la documentación de extensiones incluye un ejemplo con `ctx.ui.confirm`). En modos sin UI (`ctx.hasUI` falso) la política debe decidir sola: bloquear por defecto es la opción segura.

## Observabilidad mínima

Registra run_id, configuración/commit, inicio y fin, estado, llamadas con ID, duración y errores clasificados. Añade métricas de uso cuando existan. Conserva la salida completa solo con una decisión de privacidad; no registres tokens secretos, cookies ni archivos personales por defecto.

En una traza, busca primero el efecto: ¿se invocó una herramienta?, ¿qué argumentos tuvo?, ¿qué devolvió?, ¿el modelo distinguió fallo de éxito? La frase final es una conclusión, no la única evidencia.

## Recuperación e idempotencia

Git recupera archivos versionados si conoces qué commit era correcto. Las operaciones externas necesitan su propia recuperación. Una escritura debe tener ID de operación o comprobación de estado antes de repetir. Si no sabes si se realizó, informa incertidumbre y verifica; no repitas a ciegas.

Caso: timeout después de crear un archivo. Si el host reintenta con otro nombre, puede duplicarlo. Si verifica el mismo ID y contenido, puede resolver el estado sin repetir el efecto. El comportamiento correcto depende del contrato de la herramienta.

## Práctica de fallos

Provoca un bucle simulado, un ID ausente y una respuesta mal formada. Documenta detección, parada y reejecución. Con Pi y el modelo de guion puedes reproducir cada fallo de forma determinista:

```powershell
python .\evaluacion\ejecutar_casos.py --config .\evaluacion\configuraciones\B-guion.json --guion bucle --casos c01
python .\evaluacion\ejecutar_casos.py --config .\evaluacion\configuraciones\B-guion.json --guion lento --casos c01 --plazo 1
python .\evaluacion\ejecutar_casos.py --config .\evaluacion\configuraciones\B-guion.json --guion obediente --casos c07
```

Si puedes usar un contenedor o VM, prueba con documentos sintéticos y acceso mínimo; no montes toda tu carpeta personal para llamarlo aislamiento. La documentación empaquetada de Pi (`docs/containerization.md`) describe opciones y sus límites.

## Errores frecuentes

- Marcar como «completada» una tarea que llegó a `agent_settled` sin respuesta final.
- Reintentar una escritura tras un timeout sin comprobar si se realizó.
- Registrar trazas completas con datos personales «por si acaso».
- Tomar `presupuesto.ts` por un límite de coste: cuenta llamadas y turnos, no tokens.

## Autoevaluación

1. ¿Qué cuatro controles distingue el módulo y qué no asegura cada uno?
2. ¿Qué límite aplicas en `tool_call` y cuál en `turn_end`? ¿Por qué no basta uno?
3. ¿Qué haces tras un timeout en una herramienta que escribe?
4. ¿Por qué el canal RPC debe tratarse como privilegiado?
5. ¿Qué dice la guía de seguridad de Pi sobre la confianza de proyecto?

Respuestas: [clave](../soluciones/autoevaluacion.md#11).

Práctica: [laboratorio 11](../laboratorios/11-operacion.md). Fuentes: [seguridad Pi](https://pi.dev/docs/latest/security), [aislamiento](https://pi.dev/docs/latest/containerization). Continúa con [proyecto final](12-proyecto-final.md).
