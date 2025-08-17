import string
import copy
import requests
from adafruit_pn532.adafruit_pn532 import MIFARE_CMD_AUTH_A

class Card:
    def __init__(self, card_handler, uid, sectors, domain):
        self.handler = card_handler
        self.uid = uid
        self.sectors = sectors

        self.SERVER_URL = f"http://{domain}/"
        self.PAY_URL = self.SERVER_URL + "api/pay"
        self.REGISTER_URL = self.SERVER_URL + "api/register"
        self.DISABLE_URL = self.SERVER_URL + "api/disable"
        self.REFILL_URL = self.SERVER_URL + "api/refill"

    @staticmethod
    def encode_str(str):
        out = ""

        for c in str:
            code = ord(c)
            if code >= 48 and code <= 57:
                out += code - 48
            elif code >= 65 and code <= 90:
                out += code - 65 + 10
            elif code >= 97 and code <= 122:
                out += code - 97 + 10 + 26
            else:
                raise ValueError(f"Invalid character '{c}' in string. Only alphanumeric characters are allowed.")

        return out

    @staticmethod
    def decode_str(encoded_str):
        out = ""

        for c in encoded_str:
            if c >= 0 and c <= 9:
                out += chr(c + 48)
            elif c >= 10 and c <= 35:
                out += chr(c - 10 + 65)
            elif c >= 36 and c <= 61:
                out += chr(c - 36 + 97)

        return out

    @staticmethod
    def generate_checksum(card_id, random_num):
        if len(card_id) != len(random_num):
            raise ValueError("Card ID and random number must be of the same length")

        if len(card_id) != 16:
            raise ValueError("Card ID must be 16 characters long")

        out = ""

        card_id_encoded = Card.encode_str(card_id)
        random_num_encoded = Card.encode_str(random_num)

        for i in range(16):
            out += (int(card_id_encoded[i]) + int(random_num_encoded[i])) % 61

        return out

    def pay_ride(self): ...

    def register(self):
        response = requests.post(REGISTER_URL)

        if response.status_code != 200:
            raise RuntimeError(f"Failed to register card: {response.text}")

        data = response.json()

        card_id = data["card_id"]
        random_num = data["random_num"]
        checksum = self.generate_checksum(card_id, random_num)

        self.handler.write_block(self, 1, 0, card_id.encode("utf-8"))
        self.handler.write_block(self, 1, 1, checksum.encode("utf-8"))

    def disable(self): ...

    def refill(self, ride_count):
        if not (1 <= ride_count <= 10):
            raise ValueError("Ride count must be between 1 and 10")

        card_id = self.sectors[1][0]
        checksum = self.sectors[1][1]

        response = requests.post(f"{REFILL_URL}/{card_id}", json={"ride_count": ride_count, "checksum": checksum})

        if response.status_code != 200:
            raise RuntimeError(f"Failed to refill card: {response.text}")

        data = response.json()

        random_num = data["random_num"]
        checksum = self.generate_checksum(card_id, random_num)

        self.handler.write_block(self, 1, 1, checksum.encode("utf-8"))

    def __str__(self):
        return f"Card UID: {self.uid}"


class CardHandler:
    SECTOR_COUNT = 16
    BLOCKS_PER_SECTOR = 4
    BYTES_PER_BLOCK = 16

    KEY_DEFAULT = b"\xff\xff\xff\xff\xff\xff"

    def __init__(self, reader, domain):
        self.reader = reader
        self.domain = domain

    def read_passive(self, timeout=1):
        uid = self.reader.read_passive_target(timeout=timeout)

        if not uid:
            return

        print("Found card with UID:", [hex(i) for i in uid])

        sectors = []
        for sector_i in range(self.SECTOR_COUNT):
            block0 = sector_i * self.BLOCKS_PER_SECTOR

            authenticated = self.reader.mifare_classic_authenticate_block(
                uid,
                block0,
                MIFARE_CMD_AUTH_A,
                self.KEY_DEFAULT,
            )

            if not authenticated:
                return

            blocks = []
            for block_i in range(self.BLOCKS_PER_SECTOR):
                block_num = block0 + block_i
                data = self.reader.mifare_classic_read_block(block_num)

                if data is None:
                    return

                # change this at some point
                # this skips the first block of the first segment
                # and the last block of every segment
                # this is done because they can't be decoded as standard utf-8
                # eventually find a way to store this information
                # keeping the uid and the key/access data ought to be possible
                if sector_i == block_i == 0:
                    blocks.append("UID block")
                    continue
                if block_i == 3:
                    blocks.append("ACCESS INFO block")
                    continue

                blocks.append(data.decode())

            sectors.append(blocks)

        return Card(self, [hex(i) for i in uid], sectors, domain=self.domain)

    def read_block(self, card, sector, block):
        uid = copy.deepcopy(card.uid)

        if isinstance(uid, str):
            uid = uid.encode("utf-8")
        elif not isinstance(uid, bytes):
            raise TypeError("UID must be a string or bytes")

        if len(uid) != 4:
            raise ValueError("UID must be 4 bytes long")

        block_num = sector * self.BLOCKS_PER_SECTOR + block

        authenticated = self.reader.mifare_classic_authenticate_block(
            uid, block_num, MIFARE_CMD_AUTH_A, self.KEY_DEFAULT
        )

        if not authenticated:
            raise RuntimeError("Authentication failed")

        data = self.reader.mifare_classic_read_block(block_num)

        return data.decode()

    def write_block(self, card, sector, block, data):
        uid = copy.deepcopy(card.uid)
        data = copy.deepcopy(data)

        if isinstance(uid, str):
            uid = uid.encode("utf-8")
        elif not isinstance(uid, bytes):
            raise TypeError("UID must be a string or bytes")

        if len(uid) != 4:
            raise ValueError("UID must be 4 bytes long")

        if isinstance(data, str):
            data = uid.encode("utf-8")
        elif not isinstance(data, bytes):
            raise TypeError("data must be a string or bytes")

        if len(data) > self.BYTES_PER_BLOCK:
            raise ValueError(f"Data must not be longer than {self.BYTES_PER_BLOCK} bytes")
        elif len(data) < self.BYTES_PER_BLOCK:
            data = data.ljust(self.BYTES_PER_BLOCK, b"\x00")

        if block == 3 or (sector == 0 and block == 0):
            raise ValueError("Cannot write to reserved blocks")

        block_num = sector * self.BLOCKS_PER_SECTOR + block

        authenticated = self.reader.mifare_classic_authenticate_block(
            uid, block_num, MIFARE_CMD_AUTH_A, self.KEY_DEFAULT
        )

        if not authenticated:
            raise RuntimeError("Authentication failed")

        return self.reader.mifare_classic_write_block(block_num, data)
