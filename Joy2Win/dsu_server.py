import socket
import struct
import random
import zlib
import asyncio
import threading

IP_ADDRESS = '0.0.0.0'
PORT = 26760
SERVER_ID = random.randint(0, 0xFFFFFFFF)

sendWaitClientMsg = False
sendClientConnectedMsg = False

idPacket = 0
isReadyToSend = False
DSUClientAddr = None

sock = None

def incrementIdPacket():
    global idPacket
    idPacket += 1
    if idPacket > 0xFFFFFFFF:  # Reset if it exceeds 32-bit unsigned int
        idPacket = 1
    return idPacket

## DSU Server response functions: Controller information ##
async def responseInfoController():
    slotInfo = bytearray([
        0x01, 0x00, 0x10, 0x00, # Message type: 0x01001000 (Information about controllers) | 4 bytes
        0x00, # Slot ID | 1 byte
        0x02, # Connected (0x02) or not connected (0x00) | 1 byte
        0x02, # Type gyro (0x02 = complet) | 1 byte
        0x02, # Type de connexion (0x02 = Bluetooth) | 1 byte
        *bytes.fromhex('AABBCCDDEEFF')[::-1], # Serial number (reversed) | 6 bytes
        0x05, # Type de manette (0x05 = Pro Controller) | 1 byte
        0x00  # always 0x00 | 1 byte
    ])

    if len(slotInfo) != 16:
        raise ValueError(
            f"slotInfo length is {len(slotInfo)}, expected 16"
        )

    header = bytearray([
        *b'DSUS', # Header identifier: 'DSUS' | 4 bytes
        0xE9, 0x03, # Version 0xE903 | 2 bytes
        0x10, 0x00, # Length of slotInfo (payload) | 2 bytes
        0x00, 0x00, 0x00, 0x00, # CRC placeholder | 4 bytes
        *SERVER_ID.to_bytes(4, 'little'), # Server ID | 4 bytes
    ])

    struct_response = header + slotInfo
    crc = zlib.crc32(struct_response) & 0xFFFFFFFF
    header[8:12] = struct.pack('<I', crc)
    struct_response = header + slotInfo

    return struct_response

## DSU Server response functions: Controller data ##
async def responseDataController(timestampMotion, accel, gyro):
    global idPacket
    idPacket = incrementIdPacket()  # Increment packet ID

    slotInfo = bytearray([
        0x02, 0x00, 0x10, 0x00, # Message type: 0x02001000
        0x00, # Slot ID | 1 byte
        0x02, # Connected (0x02) or not connected (0x00) | 1 byte
        0x02, # Type gyro (0x02 = complet) | 1 byte
        0x02, # Type de connexion (0x02 = Bluetooth) | 1 byte
        *bytes.fromhex('AABBCCDDEEFF')[::-1], # Serial number (reversed) | 6 bytes
        0x05, # Type de manette (0x05 = Pro Controller) | 1 byte
    ])

    controllerStats = bytearray([
        0x01,  # connected
        *idPacket.to_bytes(4, 'little'),  # packet ID
        0b00000000,  # buttons byte 1
        0b00000000,  # buttons byte 2
        0x00,  # HOME
        0x00,  # Touch
        128, 128,  # Left Stick X/Y
        128, 128,  # Right Stick X/Y
        0, 0, 0, 0,  # analog D-PAD L/D/R/U
        0, 0, 0, 0,  # analog Y/B/A/X
        0, 0, 0, 0,  # analog R1/L1/R2/L2
        0, 0, 0, 0, 0, 0,  # touch 1 (inactive)
        0, 0, 0, 0, 0, 0,  # touch 2 (inactive)
        *b'\x00\x00\x00\x00', *struct.pack("<i", timestampMotion), # Timestamp | 8 bytes
        *struct.pack("<3f", accel["X"], accel["Y"], accel["Z"]), # Accelerometer
        *struct.pack("<3f", gyro["X"], gyro["Y"], gyro["Z"]) # Gyroscope
    ])

    data = slotInfo + controllerStats

    header = bytearray([
        *b'DSUS',
        0xE9, 0x03, # Version 0xE903
        len(data) & 0xFF, (len(data) >> 8) & 0xFF,
        0x00, 0x00, 0x00, 0x00, # CRC placeholder
        *SERVER_ID.to_bytes(4, 'little'),
    ])

    struct_response = header + data
    crc = zlib.crc32(struct_response) & 0xFFFFFFFF
    header[8:12] = struct.pack('<I', crc)
    struct_response = header + data

    return struct_response

## Send message to DSU client ##
async def send_message(data, addr):
    sock.sendto(data, addr)

## Initialize DSU server ##

async def wait_response():
    global DSUClientAddr, isReadyToSend
    global sendWaitClientMsg, sendClientConnectedMsg

    while True:
        try:
            data, addr = sock.recvfrom(1024)

            if len(data) < 20:
                print(f"Received too short packet: {data.hex()}")
                continue

            # Verify DSU client header and protocol version
            if data[0:4] != b'DSUC' or data[4:6] != b'\xE9\x03':
                continue

            # Message type is a little-endian uint32 at offset 16
            message_type = struct.unpack_from('<I', data, 16)[0]

            if message_type == 0x100001:
                # Client requests controller information
                await send_message(await responseInfoController(), addr)

            elif message_type == 0x100002:
                # Register or update the active DSU data client
                if DSUClientAddr != addr:
                    DSUClientAddr = addr
                    print(f"DSU Client connected: {addr}")

                sendClientConnectedMsg = True
                isReadyToSend = True

        except ConnectionResetError:
            DSUClientAddr = None
            isReadyToSend = False
            sendWaitClientMsg = False
            sendClientConnectedMsg = False

        except socket.timeout:
            continue

        except Exception as e:
            print(f"DSU server error: {e}")

_dbg = 0

async def controller_update(timestampBytes, accelBytes, gyroBytes):
    global DSUClientAddr, isReadyToSend, _dbg

    _dbg += 1
    if _dbg % 200 == 1:
        print(
            f"[dbg] update #{_dbg} addr={DSUClientAddr} "
            f"ready={isReadyToSend} ts={timestampBytes!r}"
        )

    if DSUClientAddr is not None and isReadyToSend is True:
        try:
            response = await responseDataController(
                timestampBytes, accelBytes, gyroBytes
            )
            await send_message(response, DSUClientAddr)
        except Exception as e:
            print("[dbg] error:", repr(e))

def main_dsu():
    global sendWaitClientMsg, sock
    if sock is None:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((IP_ADDRESS, PORT))
        sock.settimeout(1)
        print(f"DSU Server listening on {IP_ADDRESS}:{PORT}")
    if sendWaitClientMsg == False and sock is not None:
        sendWaitClientMsg = True
        print("Waiting for DSU client to connect...")
        threading.Thread(target=lambda: asyncio.run(wait_response()), daemon=True).start()