# Puente de Git, Python y TypeScript

## Git — dos horas

Un repositorio es un historial de snapshots confirmados. La carpeta de trabajo contiene tu estado actual; el índice contiene lo que irá al siguiente commit. `git add` prepara, `git commit` registra y `git diff --cached` revisa lo preparado. Una rama es una referencia móvil a commits, no una copia física del proyecto.

Ejercicio: crea `entregas/puente.md`, confirma una primera explicación, crea una rama, mejora un párrafo y revisa `git diff` antes del segundo commit. Comprueba que puedes explicar la diferencia entre un archivo modificado y uno preparado. Haz merge a `main` como se muestra en [inicio](../INICIO-WINDOWS.md).

## Python — dos horas

```python
import json

def duplicar(datos: dict) -> dict:
    n = datos.get("n")
    if type(n) is not int:
        raise ValueError("n debe ser entero")
    return {"resultado": 2 * n}

entrada = json.loads('{"n": 3}')
print(json.dumps(duplicar(entrada)))
```

`dict` organiza datos por clave. La validación evita aceptar una cadena solo porque se parezca a un número. `raise` comunica un fallo; el llamador puede capturarlo y convertirlo en un resultado de herramienta. Python considera `bool` un subtipo de `int`: `type(n) is int` lo excluye deliberadamente en este ejemplo.

Ejercicio: prueba `3`, `"3"`, `True` y una clave ausente. Define cuáles deberían aceptarse y por qué. Después lee `try/except` en el harness del módulo 03.

### Procesos e hilos (para el módulo 08)

```python
import subprocess, sys, threading

hijo = subprocess.Popen([sys.executable, "-c", "import sys; print(sys.stdin.read().upper())"],
                        stdin=subprocess.PIPE, stdout=subprocess.PIPE)
lectura = []
hilo = threading.Thread(target=lambda: lectura.append(hijo.stdout.read()))
hilo.start()                     # leer en paralelo evita bloqueos si el hijo escribe mucho
hijo.stdin.write(b"hola\n")
hijo.stdin.close()               # cerrar stdin = "no hay más entrada"
hijo.wait(timeout=5)
hilo.join()
print(lectura[0])                # b'HOLA\n\n'
```

Un proceso hijo se comunica por tuberías de **bytes**; decodificar texto es tarea tuya. Si nadie lee una tubería, se llena y el hijo se detiene esperando: por eso el cliente RPC lee stdout y stderr en hilos. `wait(timeout=...)` evita esperar para siempre; si vence, `terminate()` y, en último caso, `kill()`.

## TypeScript — dos horas

```typescript
type Resultado = { ok: boolean; texto: string };

async function consultar(id: string): Promise<Resultado> {
  return { ok: id === "d-001", texto: "dato sintético" };
}

async function ejecutar() {
  const resultado = await consultar("d-001");
  console.log(resultado.texto);
}
```

Una función `async` devuelve una promesa; `await` espera su resultado sin convertir todo el proceso en código síncrono. Los tipos ayudan durante desarrollo, pero no validan por sí solos JSON recibido de un modelo. Necesitarás validación en ejecución.

Un módulo exporta capacidades; otro las importa. `.ts` permite tipos; `.mjs` es JavaScript ES sin tipos. Pi carga extensiones TypeScript; Node ejecuta las pruebas del núcleo `.mjs` del curso. No necesitas convertirte en experto TypeScript antes de empezar: aprende a seguir el contrato de entrada y salida.

Aceptación: explica qué devolvería `consultar`, qué ocurre si olvidas `await` y por qué el tipado estático no sustituye el esquema de una herramienta. Fuente para continuar: [manual oficial TypeScript](https://www.typescriptlang.org/docs/handbook/intro.html).
