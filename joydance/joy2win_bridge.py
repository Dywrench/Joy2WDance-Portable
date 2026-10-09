
import os
import sys
import socket
import struct
import asyncio
import threading
import time

# ==========================================
# Joy2Win Bridge - JoyDance Portable
# ==========================================

# Detectar automaticamente la carpeta Joy2Win
# Estructura:
# Joy2WDance-Portable/
# ├── JoyDance/
# │   └── joy2win_bridge.py
# └── Joy2Win/
#     └── main.py

J2W = os.environ.get(
    "J2W",
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "Joy2Win")
    )
)

BRIDGE_ADDR = ("127.0.0.1", 26761)
DEBUG = True

# Comprobar que Joy2Win exista
if not os.path.isfile(os.path.join(J2W, "main.py")):
    print(
        f"[ERROR] No se encontro Joy2Win/main.py en:\n{J2W}",
        flush=True
    )
    input("Presiona Enter para salir...")
    sys.exit(1)

# Preparar el entorno de Joy2Win
os.chdir(J2W)
sys.path.insert(0, J2W)

try:
    import main as j2w_main
    import dsu_server
    from control_type import duo_joycon
except Exception as e:
    print(f"[ERROR] No se pudo importar Joy2Win: {e!r}", flush=True)
    input("Presiona Enter para salir...")
    sys.exit(1)


_sock = None
_client = None
_last_dbg = 0.0


def _listen():
    global _client

    while True:
        try:
            data, addr = _sock.recvfrom(1024)

        except ConnectionResetError:
            _client = None
            continue

        except OSError:
            return

        # Solicitud de registro DSU para el mando izquierdo
        if (
            len(data) >= 20
            and data[:4] == b"DSUC"
            and struct.unpack_from("<I", data, 16)[0] == 0x100002
        ):
            if _client != addr:
                _client = addr
                print(
                    f"[bridge-L] cliente DSU_LEFT registrado: {addr}",
                    flush=True
                )


# Abrir puerto DSU exclusivo para el mando izquierdo
try:
    _sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    _sock.bind(BRIDGE_ADDR)

    threading.Thread(target=_listen, daemon=True).start()

    print(
        f"[bridge-L] escuchando en {BRIDGE_ADDR}",
        flush=True
    )

except OSError as e:
    _sock = None
    print(
        f"[bridge-L] no se pudo abrir {BRIDGE_ADDR}: {e}. "
        "Joy2Win sigue normal.",
        flush=True
    )


# Conservar la función original de Joy2Win
_orig = duo_joycon.notify_duo_joycons


async def _patched(client, side, data):
    global _last_dbg

    result = await _orig(client, side, data)

    # Reenviar los datos de movimiento del Joy-Con izquierdo
    if side == "Left" and _sock is not None:
        try:
            L = duo_joycon.joyconLeft

            if _client is not None:
                pkt = await dsu_server.responseDataController(
                    L.motionTimestamp,
                    L.accelerometer,
                    L.gyroscope
                )

                _sock.sendto(bytes(pkt), _client)

            # Mostrar datos de diagnostico cada 2 segundos
            now = time.time()

            if DEBUG and now - _last_dbg > 2.0:
                _last_dbg = now

                acc = {
                    k: round(v, 2)
                    for k, v in L.accelerometer.items()
                }

                print(
                    "[bridge-L]",
                    "con cliente" if _client else "sin cliente",
                    acc,
                    flush=True
                )

        except Exception as e:
            print(
                "[bridge-L] error:",
                repr(e),
                flush=True
            )

    return result


# Activar el puente sin modificar los archivos originales de Joy2Win
duo_joycon.notify_duo_joycons = _patched


if __name__ == "__main__":
    try:
        asyncio.run(j2w_main.main())

    except KeyboardInterrupt:
        print("\n[bridge-L] puente detenido.", flush=True)

    except Exception as e:
        print(f"[ERROR] El puente se detuvo: {e!r}", flush=True)
        raise

