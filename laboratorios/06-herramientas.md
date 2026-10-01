# 06 — Contrato documental

Duración: 2,5 horas. Solo Node para las pruebas.

```powershell
node --test .\ejemplos\pi-package\tests\catalogue.test.mjs
python .\scripts\check_consistencia.py
```

1. Lee el catálogo y el contrato de entrada.
2. Prueba ID existente, inexistente, formato inválido y clave adicional.
3. Diseña en Markdown `search_documents`: campos, límites, resultados y errores.
4. Implementa, como ampliación, búsqueda simple sobre `listDocuments()` y sus pruebas. Compara después con la [solución de referencia](../soluciones/codigo/search.mjs) y ejecuta `node --test .\soluciones\codigo\search.test.mjs`.
5. Explica por qué una coincidencia textual no demuestra vigencia ni verdad.

Aceptación: ningún caso inválido se convierte en un éxito vacío; cada resultado conserva ID/fecha; las pruebas no dependen de un proveedor. Entrega `entregas/06-herramientas.md`.

Caso adversario: d-004 contiene una orden para borrar backups. La herramienta debe devolver el texto como dato; el agente debe tratarlo como contenido no autorizado. No alteres el documento para que desaparezca el problema: evalúa el comportamiento del sistema.

Lección: [módulo correspondiente](../docs/06-herramientas.md). Autocorrección: [guía de soluciones](../soluciones/guia.md).
