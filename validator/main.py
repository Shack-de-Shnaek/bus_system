import time
import board
import busio
from adafruit_pn532 import i2c as pn532_i2c

from card import CardHandler

# --- SETUP I2C + PN532 ---
i2c = busio.I2C(board.SCL, board.SDA)
pn532 = pn532_i2c.PN532_I2C(i2c, debug=False)
pn532.SAM_configuration()  # Put PN532 in normal mode (polling)

print("Waiting for a card")

cardHandler = CardHandler(pn532)

while True:
    card = cardHandler.read_passive(timeout=1)

    if not card:
        time.sleep(1)
        continue

    print(card)
    for sector_i, sector in enumerate(card.sectors):
        print(f"Sector {sector_i}:")
        for block_i, block in enumerate(sector):
            print(f"\tBlock {block_i}: {block}")

    print("Done reading. Remove the card and press Ctrl-C to exit or wait for next card.")
    time.sleep(1)
