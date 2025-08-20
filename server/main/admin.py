from django.contrib import admin

from main.models import Card, Ride


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    pass


@admin.register(Ride)
class RideAdmin(admin.ModelAdmin):
    pass
