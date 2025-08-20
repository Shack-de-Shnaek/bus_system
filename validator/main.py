import argparse
import board
import busio
from time import sleep
from adafruit_pn532 import i2c as pn532_i2c

from card import CardHandler

# --- SETUP I2C + PN532 ---
i2c = busio.I2C(board.SCL, board.SDA)
pn532 = pn532_i2c.PN532_I2C(i2c, debug=False)
pn532.SAM_configuration()  # Put PN532 in normal mode (polling)

print("Waiting for a card")

mode_choices = ["pay", "register", "disable", "refill"]

parser = argparse.ArgumentParser()

parser.add_argument("--mode", help="mode to run the validator in", choices=mode_choices)
parser.add_argument("--domain", help="the domain of the server", default="localhost:5000")
parser.add_argument("--bus_line", help="the bus line to pay for, if in pay mode", default=1)

args = parser.parse_args()

mode = None
if args.mode:
    mode = args.mode

domain = args.domain

bus_line = None
if mode == "pay":
    bus_line = args.bus_line

cardHandler = CardHandler(pn532, domain)

while True:
    card = cardHandler.read_passive(timeout=1)

    if not card:
        sleep(1)
        continue

    print(card)
    for sector_i, sector in enumerate(card.sectors):
        print(f"Sector {sector_i}:")
        for block_i, block in enumerate(sector):
            print(f"\tBlock {block_i}: {block}")

    if not mode:
        print("Done reading. Remove the card and press Ctrl-C to exit or wait for next card.")
        sleep(1)

        continue

    if mode == "pay":
        card.pay_ride(bus_line)
        print(f"Paid for bus line {bus_line} on card {card.uid}")
        sleep(3)
    elif mode == "register":
        card.register()
        print(f"Registered card {card.uid}")
        sleep(3)
    elif mode == "disable":
        print("Disabling card...")
        sleep(3)
    elif mode == "refill":
        print("Refilling card...")
        sleep(3)
