# 08 — SDK y cliente RPC

Duración: 2,5 horas. El SDK requiere red para la instalación npm; la ejecución funciona con el modelo de guion.

1. Sigue `ejemplos/sdk/README.md`: `npm.cmd install --ignore-scripts` y `npm.cmd run check` en ese directorio. Confirma el `package-lock.json` generado.
2. Ejecuta `npm.cmd start` sin credenciales y registra el error esperado. Si tienes modelo, repite y guarda versión, modelo efectivo y salida.
3. Ejecuta `run-documental.ts` con `CURSO_MODELO=guion` para c01, c05 y c06. Después provoca el plazo con `CURSO_GUION=lento` y `CURSO_PLAZO_MS=800`.
4. Cambia el contrato pedido para provocar una salida no JSON (por ejemplo `CURSO_GUION=json-roto`) y comprueba que se detecta.
5. Ejecuta las pruebas del cliente RPC offline:

```powershell
python -m unittest discover -s .\ejemplos\rpc -v
python .\ejemplos\rpc\cliente_rpc.py --guion correcto "¿Cuál es el presupuesto de práctica?"
python .\ejemplos\rpc\cliente_rpc.py --guion lento --plazo 1 "¿Cuál es la retención vigente?"
```

6. Compara el diagrama de estados del módulo con `transiciones` impresas por el cliente en ambos casos. Añade a `pi_falso.py` un modo `sin-settled` (emite `agent_end` pero nunca `agent_settled`) y una prueba que demuestre que el cliente termina en `plazo_vencido`.

Aceptación: distingues respuesta de aceptación y final de tarea, liberas recursos en `finally`, tu parser soporta fragmentación y tu nueva prueba pasa. El cliente incluido no gestiona UI de extensiones ni colas de steering; no lo presentes como integración de producción.

Entregable: `entregas/08-integracion.md`. Si no puedes llamar a un modelo real, el chequeo de tipos, el guion y el cliente RPC son evidencia de integración identificada como tal.

Lección: [módulo correspondiente](../docs/08-sdk-rpc.md). Autocorrección: [guía de soluciones](../soluciones/guia.md).
