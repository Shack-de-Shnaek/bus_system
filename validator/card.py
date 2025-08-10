from adafruit_pn532.adafruit_pn532 import MIFARE_CMD_AUTH_A


class Card:
    pass


class CardHandler:
    SECTOR_COUNT = 16
    BLOCKS_PER_SECTOR = 4
    BYTES_PER_BLOCK = 16

    KEY_DEFAULT = b"\xff\xff\xff\xff\xff\xff"

    def __init__(self, reader):
        self.reader = reader

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
                    blocks.append('UID block')
                    continue
                if block_i == 3:
                    blocks.append('ACCESS INFO block')
                    continue

                blocks.append(data.decode())

            sectors.append(blocks)

        return sectors
