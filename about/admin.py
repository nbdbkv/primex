from django.contrib import admin

from about.models import (
    Partner,
    Contact,
    New,
    NewGallery,
    Fillial,
    Option
)


class NewGalleryInline(admin.StackedInline):
    model=NewGallery
    extra = 1
    

class NewAdmin(admin.ModelAdmin):
    inlines = [NewGalleryInline,]
    

admin.site.register(Partner)
admin.site.register(Contact)
admin.site.register(New, NewAdmin)
admin.site.register(Fillial)
admin.site.register(Option)
