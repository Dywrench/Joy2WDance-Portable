import asyncio
from bleak import BleakScanner

async def main():
    print("Buscando dispositivos Bluetooth LE durante 15 segundos...")
    devices = await BleakScanner.discover(timeout=15, return_adv=True)

    for address, (device, adv) in devices.items():
        print("\n" + "=" * 55)
        print("Nombre:", device.name or adv.local_name or "(sin nombre)")
        print("Dirección:", address)
        print("Fabricante:", adv.manufacturer_data)
        print("Servicios anunciados:", adv.service_uuids)
        print("Datos adicionales:", adv.service_data)
        print("RSSI:", adv.rssi)

    print("\nFin del escaneo.")

asyncio.run(main())
