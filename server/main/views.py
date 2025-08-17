from django.http import JsonResponse, HttpResponse, Http404, HttpResponseBadRequest
from django.shortcuts import render

from main.models import Card


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
        card = Card.objects.get(id=card_id, checksum=request_checksum)
    except Card.DoesNotExist:
        return Http404

    card.pay_ride(bus_line)

    return JsonResponse({"random_num": card.random_num})


def refill(request, card_id):
    try:
        card = Card.objects.get(id=card_id)
    except Card.DoesNotExist:
        return Http404

    card.refill(5)

    return JsonResponse({"random_num": card.random_num})


def register(request):
    card = Card.objects.create(rides_left=5)
    return JsonResponse({"card_id": card.id, "random_num": card.random_num})
