# Glosario

| Término | Uso en el curso |
| --- | --- |
| Harness de agente | Software que ejecuta modelo, contexto, herramientas, estado y controles |
| Harness de evaluación | Sistema que ejecuta casos y mide comportamiento |
| Agente | Conjunto que observa, decide acciones y continúa hacia una tarea |
| Tool call | Propuesta estructurada de invocar una herramienta |
| Dispatcher | Código que valida y enruta una propuesta |
| Context engineering | Selección y mantenimiento del contexto útil |
| Prompt template | Texto reutilizable con argumentos |
| Skill | Procedimiento especializado con instrucciones y recursos |
| Extensión | Código que añade comportamiento al runtime |
| SDK | API de integración dentro de una aplicación |
| RPC | Protocolo de comandos y eventos entre procesos |
| MCP | Protocolo de acceso a capacidades de servidores |
| RAG | Recuperación de evidencia para incluirla en generación |
| Compaction | Reducción del contexto mediante resumen/selección |
| Idempotencia | Repetir una operación no añade un efecto distinto |
| Sandbox | Frontera técnica que limita recursos y efectos accesibles |
| Prompt injection | Contenido que intenta modificar el comportamiento o autoridad del agente |
| Grounding | Correspondencia de afirmaciones con evidencia disponible |
| Holdout | Conjunto reservado que no se usa para ajustar el sistema |
| Ablación | Quitar una capacidad para medir su contribución |
| Latencia p50/p95 | Percentiles de duración observada |
| Backpressure | Acumulación que frena un productor cuando el consumidor no sigue el ritmo |
| JSONL | Objetos JSON separados por LF, un registro por línea |
| ADR | Registro de una decisión de arquitectura |
| Doble de prueba | Sustituto determinista de un componente (modelo, proceso, servidor) para probar el resto |
| Modelo de guion | Proveedor simulado del curso para Pi (`curso/guion`); no es una IA |
| Adaptador de proveedor | Código que traduce entre el formato del harness y la API de un proveedor |
| Tool calling / function calling | Capacidad de un modelo de proponer llamadas estructuradas a herramientas declaradas |
| Normalización de trazas | Convertir eventos de ejecución en una fila evaluable con evidencia observada |
| Runner de evaluación | Programa que ejecuta casos contra el harness y guarda trazas y resultados |
| Criba | Comprobación automática y limitada que precede a la revisión humana |
| Asentamiento (`agent_settled`) | Momento en que Pi no continuará automáticamente |
| Disposition | Resultado de enviar un prompt por RPC: `started`, `queued` o `handled` |
| Allowlist | Lista explícita de lo permitido; lo demás se rechaza |
| Presupuesto de ejecución | Límites de llamadas, turnos, tiempo e inferencia por tarea |
| Exposure (Pi) | Cómo alcanza el modelo una herramienta: `direct`, `codemode`, `deferred`, `hidden`… |
| Codemode | Herramienta de Pi que ejecuta JavaScript en un sandbox QuickJS para componer otras herramientas |
| Project trust | Decisión que permite cargar recursos de `.pi/` de un proyecto; no es un sandbox |
| structuredContent | Resultado de herramienta para llamadores programáticos, conforme a `outputSchema` |
| Annotations | Pistas MCP sobre una herramienta: solo lectura, destructiva, idempotente, mundo abierto |
| Peer dependency | Dependencia que proporciona el host (Pi) y que el paquete no debe incluir |
