from django.contrib import admin

from account.models import (
    User,
    Region,
    City
)

admin.site.register(User)
admin.site.register(Region)
admin.site.register(City)