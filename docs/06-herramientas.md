# 06 — Diseñar herramientas con contratos

Tiempo: 5 horas. Objetivo: diseñar y probar una herramienta que devuelva evidencia fiable y errores interpretables.

## Una herramienta no es solo una función

Tiene nombre, descripción para el modelo, esquema, validación, implementación, política y resultado. Cada parte influye en el comportamiento. «consulta» es un nombre ambiguo; `lookup_document` comunica una acción delimitada. La descripción debe decir qué IDs acepta, qué devuelve y cuándo no sirve.

El ejemplo [catalogue.mjs](../ejemplos/pi-package/shared/catalogue.mjs) contiene cuatro documentos sintéticos. Su acceso por ID es intencionadamente pequeño. No recibe rutas, comandos ni URLs. Una herramienta que solo necesita un ID no debe aceptar una expresión de shell.

## Contrato del catálogo

Entrada: objeto exacto `{"doc_id":"d-001"}`. Salida exitosa: `doc_id`, `title`, `date`, `text`. ID inválido, clave adicional o documento inexistente: error específico. El catálogo no calcula vigencia ni redacta una respuesta; el harness y el modelo tienen esa tarea.

Las fuentes son sintéticas:

| ID | Función en los ejercicios |
| --- | --- |
| d-001 | Norma vigente: retención y backup |
| d-002 | Presupuesto y responsable |
| d-003 | Norma antigua, expresamente sustituida |
| d-004 | Nota con instrucción incrustada para probar inyección |

## Dos niveles de validación

Un esquema de parámetros ayuda al proveedor y a Pi. La función de dominio debe validar también: puede invocarse desde tests u otro adaptador. TypeScript no comprueba JSON externo durante ejecución. En el ejemplo, el núcleo JavaScript rechaza claves adicionales y un formato de ID incorrecto.

Los errores deben permitir una decisión: reparar argumento, informar que falta el dato o detener. No devuelvas un resultado ficticio cuando falle la lectura. Una excepción de contrato no se convierte en «documento vacío» porque entonces el modelo podría afirmar que no existe contenido.

## Texto y estructura

El modelo necesita contenido legible. Un programa necesita estructura estable. En Pi la extensión de ejemplo devuelve texto JSON en `content`, datos en `structuredContent` y detalles para inspección. La redundancia es deliberada y debe mantenerse coherente. Contrato verificado en 0.99.1 (`AgentToolResult`):

| Campo | Quién lo recibe | Uso |
| --- | --- | --- |
| `content` | El modelo | Texto (o imágenes) del resultado; obligatorio |
| `details` | UI, sesión y extensiones | Datos para renderizar o reconstruir estado; obligatorio (puede ser `undefined`) |
| `structuredContent` | Llamadores programáticos, p. ej. scripts de `codemode` | Debe cumplir `outputSchema` si lo declaras |
| `isError` | Modelo y llamadores | Informar un fallo **con datos** sin lanzar excepción |
| `terminate` | El agente | Pedir que no haya seguimiento automático tras el lote |

Lanzar una excepción desde `execute` produce un resultado fallido; devolver un objeto normal nunca marca error. Si el resultado es grande, trúncalo en `content` e indica al modelo dónde está el completo.

## Efectos y reintentos

Una lectura puede repetirse normalmente sin cambiar el mundo. Una escritura necesita reglas adicionales: idempotency key, verificación posterior, secuencialidad cuando comparte estado y registro de efectos. Un timeout después de escribir no implica que no haya escrito.

En Pi, las llamadas de un mismo mensaje del asistente pueden ejecutarse **en paralelo**. Si dos herramientas comparten estado mutable en memoria, declara `executionMode: "sequential"`; si modifican archivos, envuelve la lectura-modificación-escritura con `withFileMutationQueue()`. Las `annotations` (`readOnlyHint`, `destructiveHint`, `idempotentHint`, `openWorldHint`, con la semántica de MCP) describen la herramienta para que una extensión de permisos decida qué confirmar; Pi no las verifica por sí solo. `lookup_document` se declara de solo lectura, idempotente y sin mundo abierto.

No construyas un validador de SQL mediante búsquedas de palabras para conectarlo a una base real. Para una futura herramienta de datos, usa una conexión con permisos de solo lectura, operaciones predefinidas o un parser adecuado, límites de filas y aislamiento. El contrato del catálogo muestra el patrón sin exponer datos reales.

## Prueba independiente

Ejecuta `node --test ejemplos/pi-package/tests/catalogue.test.mjs`. Esto comprueba el núcleo determinista, no que el modelo elija bien el ID. La elección y el uso de evidencia se evalúan después.

Ejercicio: diseña `search_documents` con consulta limitada, un máximo de resultados y una puntuación que no se confunda con verdad. Para el catálogo de cuatro documentos, una búsqueda léxica basta como ejercicio; no necesitas embeddings para justificar todo acceso. Solución de referencia, para después de intentarlo: [search.mjs](../soluciones/codigo/search.mjs) y su [adaptador Pi](../soluciones/codigo/search_documents.ts). Observa uno de sus tests: la consulta «norma retención 15 días» sitúa **primero** la norma sustituida. Una puntuación léxica alta no es vigencia.

## Errores frecuentes

- Nombres genéricos (`consulta`, `tool1`) y descripciones que no dicen qué entradas acepta ni cuándo no sirve.
- Aceptar rutas o comandos «por flexibilidad» cuando basta un ID.
- Devolver `{}` o texto vacío ante un documento inexistente: el modelo puede concluir que el documento existe y no dice nada.
- Confiar solo en el esquema TypeBox: protege la llamada desde Pi, no la función invocada desde otro adaptador.

## Autoevaluación

1. ¿Qué dos niveles de validación tiene `lookup_document` y por qué no basta uno?
2. ¿Cuándo devolverías `isError: true` en vez de lanzar una excepción?
3. ¿Qué campo del resultado ve el modelo y cuál recibe un script de `codemode`?
4. ¿Por qué una búsqueda que devuelve primero d-003 no está «mal», y qué debe hacer el agente después?
5. ¿Qué declararías para dos herramientas que modifican el mismo objeto en memoria?

Respuestas: [clave](../soluciones/autoevaluacion.md#06).

Práctica: [laboratorio 06](../laboratorios/06-herramientas.md). Referencia de adaptación: [contratos de extensión](https://pi.dev/docs/latest/extensions).
