# RPC sin red y contra Pi

| Archivo | Qué es |
| --- | --- |
| `framing.py` | Parser JSONL por bytes: fragmentación UTF-8, LF/CRLF, límites, EOF; modo estricto o tolerante |
| `cliente_rpc.py` | Cliente RPC completo para el curso: correlación por ID, lectores stdout/stderr, `agent_settled`, plazo con `abort`, cierre escalonado, historial de estados |
| `pi_falso.py` | Pi simulado para pruebas: normal, lento, rechazo, cae, ruido, fragmentado, id-ajeno, terco |
| `test_framing.py`, `test_cliente_rpc.py` | Pruebas offline |

```powershell
python -m unittest discover -s .\ejemplos\rpc -v
python .\ejemplos\rpc\cliente_rpc.py --guion correcto "¿Cuál es la retención vigente de backups?"
python .\ejemplos\rpc\cliente_rpc.py "¿Cuál es la retención vigente?" -- --provider TU_PROVEEDOR --model TU_MODELO
```

Con `--guion`, el cliente carga el modelo de guion, el catálogo y la plantilla, y usa `.pi-curso\agente` como configuración aislada (salvo que ya hayas definido `PI_CODING_AGENT_DIR`). Para lanzar Pi usa `PI_CMD` si está definida; si no, en Windows prefiere `node …\cli.js` sobre `pi.cmd`.

El cliente se verificó contra Pi 0.99.1 con el modelo de guion (finalización y plazo vencido con `abort`). No gestiona la UI de extensiones por RPC, colas de steering ni reconexión: es didáctico. Sigue el [módulo 08](../../docs/08-sdk-rpc.md) para su diseño.
