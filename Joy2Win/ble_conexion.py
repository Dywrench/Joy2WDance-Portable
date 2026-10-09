
import asyncio
from bleak import BleakClient

DIRECCION = "98:B6:37:70:5E:F6"


async def main():
    print("Intentando conectar con BOL TOOL...")

    try:
        async with BleakClient(
            DIRECCION,
            timeout=20,
            pair=False,
            winrt={"use_cached_services": True},
        ) as client:
            print("¿Conectado?:", client.is_connected)
            print("Esperando 5 segundos sin consultar servicios...")
            await asyncio.sleep(5)
            print("¿Sigue conectado?:", client.is_connected)

    except Exception as error:
        print(f"Error: {type(error).__name__}: {error}")


asyncio.run(main())
