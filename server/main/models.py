import random
import string

from django.db import models

chars = string.digits + string.ascii_lowercase + string.ascii_uppercase


# don't write random_num or rides_left on card, only id and checksum
class Card(models.Model):
    id = models.CharField(max_length=16, unique=True, primary_key=True)
    active = models.BooleanField(default=True)
    rides_left = models.IntegerField(default=5)
    random_num = models.CharField(max_length=16)
    checksum = models.CharField(max_length=16)

    @staticmethod
    def encode_str(string):
        out = ""

        for c in string:
            code = ord(c)
            char = ""
            if code >= 48 and code <= 57:
                char += str(code - 48)
            elif code >= 65 and code <= 90:
                char += str(code - 65 + 10)
            elif code >= 97 and code <= 122:
                char += str(code - 97 + 10 + 26)
            else:
                raise ValueError(f"Invalid character '{c}' in string. Only alphanumeric characters are allowed.")

            if len(char) == 1:
                char = "0" + char

            out += char

        return out

    @staticmethod
    def decode_str(encoded_str):
        out = ""

        i = 0
        while i < len(encoded_str) - 1:
            c = int(encoded_str[i : i + 2])
            if c >= 0 and c <= 9:
                out += chr(c + 48)
            elif c >= 10 and c <= 35:
                out += chr(c - 10 + 65)
            elif c >= 36 and c <= 61:
                out += chr(c - 36 + 97)

        return out

    def generate_checksum(self, card_id=None, random_num=None):
        if not card_id:
            card_id = self.id

        if not random_num:
            random_num = self.random_num

        if len(card_id) != len(random_num):
            raise ValueError("Card ID and random number must be of the same length")

        if len(card_id) != 16:
            raise ValueError("Card ID must be 16 characters long")

        out = ""

        card_id_encoded = Card.encode_str(card_id)
        random_num_encoded = Card.encode_str(random_num)

        for i in range(16):
            out += str((int(card_id_encoded[i]) + int(random_num_encoded[i])) % 61)

        return out

    @property
    def last_ride(self):
        return self.rides.order_by(Ride.timestamp.desc()).first()

    def pay_ride(self, bus_line):
        if self.rides_left <= 0:
            raise ValueError("No rides left on the card")

        Ride.objects.create(
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

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = self._generate_random_number()
            self._update_security()

        return super().save(*args, **kwargs)


class Ride(models.Model):
    card = models.ForeignKey(Card, related_name="rides", on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    random_num_at_time = models.CharField(max_length=16)
    rides_left_at_time = models.IntegerField()
    bus_line = models.CharField(max_length=10)
