from django.contrib import admin

from flight.models import Flight
@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = ('created_at',)
