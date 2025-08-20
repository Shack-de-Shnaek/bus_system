from django.http import JsonResponse, HttpResponse, HttpResponseNotFound, HttpResponseBadRequest
from django.shortcuts import render

from main.models import Card, OutOfRidesError


def index(request):
    return render(request, "index.html")


def admin(request):
    return render(request, "admin.html")


def pay_ride(request, card_id, bus_line):
    if request.method != "POST":
        return HttpResponse(status=405)

    request_checksum = request.POST.get("checksum", None)

    if not request_checksum:
        return HttpResponseBadRequest

    try:
        card = Card.objects.get(id=card_id)
    except Card.DoesNotExist:
        return HttpResponseNotFound

    if card.checksum != request_checksum:
        card.blacklist()
        return HttpResponseBadRequest("Illegitimate card detected. Card has been blacklisted.")

    try:
        card.pay_ride(bus_line)
    except OutOfRidesError:
        return HttpResponseBadRequest("No rides left on the card.")

    return JsonResponse({"random_num": card.random_num})


def refill(request, card_id):
    try:
        card = Card.objects.get(id=card_id)
    except Card.DoesNotExist:
        return HttpResponseNotFound

    card.refill(5)

    return JsonResponse({"random_num": card.random_num})


def register(request):
    card = Card.objects.create(rides_left=5)
    return JsonResponse({"card_id": card.id, "random_num": card.random_num})
