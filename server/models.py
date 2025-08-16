import random
import string
from peewee import Model, ForeignKeyField, DateTimeField, CharField, IntegerField, BooleanField, UUIDField, SQL


# add rides_left to checksum
# don't write random_num or rides_left on card, only id and checksum
class Card(Model):
    id = CharField(max_length=32, index=True, unique=True, primary_key=True)
    active = BooleanField(default=True)
    rides_left = IntegerField(default=0)
    random_num = CharField(max_length=32)
    checksum = CharField(max_length=32)

    @property
    def last_ride(self):
        return self.rides.order_by(Ride.timestamp.desc()).first()

    def pay_ride(self, bus_line):
        pass

    def save(self, force_insert=False, only=None):
        if not self.id:
            id = ""
            random_num = ""
            checksum = ""
            for i in range(32):
                id_dig = random.choice(string.digits)
                random_num_dig = random.choice(string.digits)
                checksum_dig = str(int(id_dig) + int(random_num_dig))[-1]

                id = id + id_dig
                random_num = random_num + random_num_dig
                checksum = checksum + checksum_dig

            self.id = id
            self.random_num = random_num
            self.checksum = checksum

        return super().save(force_insert, only)


class Ride(Model):
    card = ForeignKeyField(Card, bachref="rides", on_delete="CASCADE")
    timestamp = DateTimeField(constraints=[SQL("DEFAULT CURRENT_TIMESTAMP")])
    random_num_at_time = CharField(max_length=16)
    rides_left_at_time = IntegerField()
    bus_line = CharField(max_length=10)
