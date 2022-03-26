from django.contrib.auth.models import Group
from django import forms


def get_group():
    group = Group.objects.get(name="Couriers")
    return group
