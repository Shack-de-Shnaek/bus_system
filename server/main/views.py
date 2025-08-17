from django.http import JsonResponse, HttpResponse, Http404
from django.shortcuts import render

from main.models import Card


def index(request):
    return render(request, "index.html")


def admin(request):
    return render(request, "admin.html")


def pay_ride(request, card_id, bus_line):
    try:
        card = Card.objects.get(id=card_id)
    except Card.DoesNotExist:
        return Http404

    card.pay_ride(bus_line)

    return JsonResponse({"checksum": card.checksum})


def refill(request, card_id):
    try:
        card = Card.objects.get(id=card_id)
    except Card.DoesNotExist:
        return Http404

    card.refill(5)

    return JsonResponse(
        {
            "checksum": card.checksum,
        }
    )


def register(request):
    card = Card.objects.create(rides_left=5)
    return JsonResponse({"card_id": card.id, "checksum": card.checksum})
