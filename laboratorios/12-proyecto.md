# 12 — Entrega y defensa

Duración: 8 horas del módulo final.

1. Revisa requisitos y crea issues para los hitos.
2. Confirma contrato, ADR y baseline. Ejecuta `python scripts/verificar_todo.py --con-pi`: el pipeline debe dar A 3/12 y B 12/12 con el modelo de guion.
3. Implementa el harness documental y produce resultados reales con `ejecutar_casos.py` (o `harness_documental.py --evaluar` si tu ruta es Python).
4. Ejecuta desarrollo, congela configuración y ejecuta reservados.
5. Prueba fallo, abstención, inyección y una acción fuera de alcance.
6. Completa informe final, [revisión humana](../plantillas/revision-humana.md) y rúbrica con evidencias.
7. Reproduce la instalación en un entorno nuevo o documenta por qué no se ha hecho.
8. Crea un tag local de tu entrega solo después de revisar y confirmar cambios.

Aceptación: otra persona puede seguir README y reproducir la demo; se distinguen tests deterministas y evaluación real; no hay secretos; todos los límites están identificados. Entrega `entregas/12-proyecto.md`, implementación, informe y resultados anonimizados.

Preguntas de defensa: ¿cuál es tu frontera de acceso?, ¿cómo evitas repetir efectos?, ¿cómo sabes qué fuente consultó?, ¿qué evidencia demuestra una mejora?, ¿qué queda sin medir?

Si no tienes acceso a un modelo, puedes entregar una versión offline con simulación y contratos. Etiquétala así y deja pendiente la validación de agente real; no la presentes como proyecto completo validado con Pi.

Lección: [módulo correspondiente](../docs/12-proyecto-final.md). Autocorrección: [guía de soluciones](../soluciones/guia.md).
