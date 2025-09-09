from django.contrib import admin

from main.models import Card, Ride


class RideInline(admin.TabularInline):
    model = Ride
    extra = 0
    readonly_fields = ("timestamp", "random_num_at_time", "rides_left_at_time", "bus_line")

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    inlines = [RideInline]
    list_display = ("id", "active", "rides_left")


@admin.register(Ride)
class RideAdmin(admin.ModelAdmin):
    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False
