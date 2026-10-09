import os, sys, asyncio, time

J2W = r"C:\Users\juan0\Documents\Codigos\Joy2Win"
os.chdir(J2W)
sys.path.insert(0, J2W)

import main as j2w_main
from control_type import duo_joycon

_orig = duo_joycon.notify_duo_joycons
_last = 0.0

async def patched(client, side, data):
    global _last
    result = await _orig(client, side, data)
    now = time.time()
    if side == "Left" and now - _last > 0.5:
        _last = now
        L = duo_joycon.joyconLeft
        pressed = [k for k, v in L.buttons.items() if v]
        acc = {k: round(v, 2) for k, v in L.accelerometer.items()}
        print("[probe-L]", pressed, L.analog_stick, acc, flush=True)
    return result

duo_joycon.notify_duo_joycons = patched
asyncio.run(j2w_main.main())