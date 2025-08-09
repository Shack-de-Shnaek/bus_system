import time
import board
import busio
from digitalio import DigitalInOut
from adafruit_pn532.adafruit_pn532 import MIFARE_CMD_AUTH_A
from adafruit_pn532 import i2c as pn532_i2c

# --- SETUP I2C + PN532 ---
i2c = busio.I2C(board.SCL, board.SDA)
pn532 = pn532_i2c.PN532_I2C(i2c, debug=False)
pn532.SAM_configuration()  # Put PN532 in normal mode (polling)

print("Waiting for a card")

# Block layout: MIFARE Classic 1K = 16 sectors × 4 blocks × 16 bytes
SECTOR_COUNT = 16
BLOCKS_PER_SECTOR = 4
BYTES_PER_BLOCK = 16

# Default key (for factory-new Classic tags)
KEY_DEFAULT = b"\xFF\xFF\xFF\xFF\xFF\xFF"

while True:
    uid = pn532.read_passive_target(timeout=0.5)
    if not uid:
        # no card, loop again
        continue

    print("Tag detected! UID:", [hex(i) for i in uid])

    full_dump = bytearray()

    # Loop over each sector
    for sector in range(SECTOR_COUNT):
        # Try Key A (0xFF…FF) on block 0 of this sector to authenticate
        block0 = sector * BLOCKS_PER_SECTOR
        success = pn532.mifare_classic_authenticate_block(
            uid, block0, MIFARE_CMD_AUTH_A, KEY_DEFAULT
        )
        if not success:
            print(f"Sector {sector}: Authentication failed")
            full_dump.extend(b"\x00" * (BLOCKS_PER_SECTOR * BYTES_PER_BLOCK))
            continue

        # Read all 4 blocks in this sector
        for block_offset in range(BLOCKS_PER_SECTOR):
            block_num = block0 + block_offset
            data = pn532.mifare_classic_read_block(block_num)
            if data is None:
                print(f"Sector {sector} block {block_offset}: Read failed")
                data = b"\x00" * BYTES_PER_BLOCK
            full_dump.extend(data)

    # Now full_dump is 1024 bytes (16 sectors × 4 blocks × 16 bytes)
    # Print it in hex for inspection:
    for i in range(0, len(full_dump), 16):
        chunk = full_dump[i : i + 16]
        hexed = " ".join(f"{b:02X}" for b in chunk)
        print(f"0x{i:03X}: {hexed}")

    print("Done reading. Remove the card and press Ctrl-C to exit or wait for next card.")
    time.sleep(1)

