import random
import string
from peewee import Model, ForeignKeyField, DateTimeField, CharField, IntegerField, BooleanField, UUIDField, SQL

chars = string.digits + string.ascii_lowercase + string.ascii_uppercase


# don't write random_num or rides_left on card, only id and checksum
class Card(Model):
    id = CharField(max_length=16, index=True, unique=True, primary_key=True)
    active = BooleanField(default=True)
    rides_left = IntegerField(default=0)
    random_num = CharField(max_length=16)
    checksum = CharField(max_length=16)

    def generate_checksum(self):
        card_id = self.id
        random_num = self.random_num

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

    @property
    def last_ride(self):
        return self.rides.order_by(Ride.timestamp.desc()).first()

    def pay_ride(self, bus_line):
        if self.rides_left <= 0:
            raise ValueError("No rides left on the card")

        Ride.create(
            card=self,
            timestamp=Ride.timestamp,
            random_num_at_time=self.random_num,
            rides_left_at_time=self.rides_left,
            bus_line=bus_line,
        )
        self.rides_left -= 1
        self._update_security()
        self.save()

    def refill(self, ride_count):
        self.rides_left += ride_count
        self._update_security()
        self.save()

    def _generate_random_number(self):
        out = ""
        for i in range(16):
            out += random.choice(chars)

        return out

    def _update_security(self):
        self.random_num = self._generate_random_number()
        self.checksum = self.generate_checksum()

    def save(self, force_insert=False, only=None):
        if not self.id:
            self.id = self._generate_random_number()
            self._update_security()

        return super().save(force_insert, only)


class Ride(Model):
    card = ForeignKeyField(Card, bachref="rides", on_delete="CASCADE")
    timestamp = DateTimeField(constraints=[SQL("DEFAULT CURRENT_TIMESTAMP")])
    random_num_at_time = CharField(max_length=16)
    rides_left_at_time = IntegerField()
    bus_line = CharField(max_length=10)
