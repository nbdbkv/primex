from django.http import HttpResponse
from django.shortcuts import render


def add_to_flight(request):
    print(request.POST)
    return HttpResponse('HELLO')
