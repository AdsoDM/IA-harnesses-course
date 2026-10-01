"""Pi FALSO para probar clientes RPC sin red, sin Pi y sin modelo.

Implementa un subconjunto mínimo del protocolo (get_state, prompt, abort) y
permite provocar fallos: ``python pi_falso.py MODO [argumentos ignorados]``.

Modos: normal, lento, rechazo, cae, ruido, fragmentado, id-ajeno, terco.
No reproduce todos los eventos de Pi: sirve para probar el CLIENTE.
"""
import json
import sys
import threading
import time

MODO = sys.argv[1] if len(sys.argv) > 1 else "normal"
salida = sys.stdout.buffer
cerrojo = threading.Lock()
abortado = threading.Event()


def emitir(registro):
    datos = json.dumps(registro, ensure_ascii=False).encode("utf-8") + b"\n"
    with cerrojo:
        if MODO == "fragmentado":
            for i in range(len(datos)):  # un byte cada vez: parte caracteres UTF-8
                salida.write(datos[i:i + 1])
                salida.flush()
        else:
            salida.write(datos)
            salida.flush()


def asistente(texto, stop="stop", error=None):
    m = {"role": "assistant", "content": [{"type": "text", "text": texto}] if texto else [],
         "provider": "falso", "model": "falso-1", "stopReason": stop}
    if error:
        m["errorMessage"] = error
    return m


def run(mensaje):
    emitir({"type": "agent_start"})
    emitir({"type": "turn_start"})
    emitir({"type": "message_end", "message": {"role": "user", "content": mensaje}})
    pasos = 100 if MODO in ("lento", "terco") else 1
    for _ in range(pasos):
        if abortado.is_set():
            m = asistente("", "aborted", "Request was aborted")
            emitir({"type": "message_end", "message": m})
            emitir({"type": "agent_end", "messages": [m], "willRetry": False})
            emitir({"type": "agent_settled"})
            return
        time.sleep(0.1 if pasos > 1 else 0)
    m = asistente('{"saludo":"año"}')
    emitir({"type": "message_end", "message": m})
    emitir({"type": "turn_end", "message": m, "toolResults": []})
    emitir({"type": "agent_end", "messages": [m], "willRetry": False})
    emitir({"type": "agent_settled"})


def main():
    if MODO == "ruido":
        sys.stderr.write("diagnóstico " * 20000 + "\n")  # ~240 KB: llenaría una tubería no leída
        sys.stderr.flush()
    hilos = []
    for linea in sys.stdin.buffer:
        cmd = json.loads(linea)
        rid, tipo = cmd.get("id"), cmd.get("type")
        if MODO == "id-ajeno":
            emitir({"type": "response", "id": "otro-id", "command": tipo, "success": True})
        if tipo == "get_state":
            emitir({"type": "response", "id": rid, "command": tipo, "success": True,
                    "data": {"model": {"provider": "falso", "id": "falso-1"}, "isStreaming": False}})
        elif tipo == "prompt":
            if MODO == "rechazo":
                emitir({"type": "response", "id": rid, "command": tipo, "success": False, "error": "Prompt rechazado"})
                continue
            emitir({"type": "response", "id": rid, "command": tipo, "success": True, "data": {"disposition": "started"}})
            if MODO == "cae":
                sys.exit(3)
            h = threading.Thread(target=run, args=(cmd.get("message", ""),))
            h.start()
            hilos.append(h)
        elif tipo == "abort":
            abortado.set()
            for h in hilos:
                h.join()
            emitir({"type": "response", "id": rid, "command": tipo, "success": True})
        else:
            emitir({"type": "response", "id": rid, "command": tipo, "success": False, "error": f"Comando no soportado: {tipo}"})
    if MODO == "terco":  # ignora el cierre de stdin: el cliente tendrá que terminarlo
        while True:
            time.sleep(1)


if __name__ == "__main__":
    main()
