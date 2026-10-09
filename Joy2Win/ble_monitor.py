import asyncio
from datetime import datetime
from bleak import BleakScanner

seen = {}

def callback(device, adv):
    name = device.name or adv.local_name or "(sin nombre)"
    info = (
        name,
        dict(adv.manufacturer_data),
        list(adv.service_uuids),
        dict(adv.service_data),
        adv.rssi,
    )

    key = device.address
    if seen.get(key) != info:
        seen[key] = info
        print(f"\n[{datetime.now():%H:%M:%S}] {key}")
        print("Nombre:", name)
        print("RSSI:", adv.rssi)
        print("Fabricante:", {
            hex(k): v.hex() for k, v in adv.manufacturer_data.items()
        })
        print("Servicios:", adv.service_uuids)
        print("Datos de servicio:", {
            k: v.hex() for k, v in adv.service_data.items()
        })

async def main():
    print("Monitor BLE activo durante 45 segundos.")
    print("Enciende el mando en modo de conexión y observa los cambios.")
    scanner = BleakScanner(detection_callback=callback)
    await scanner.start()
    try:
        await asyncio.sleep(45)
    finally:
        await scanner.stop()
        print("\nMonitor finalizado.")

asyncio.run(main())
