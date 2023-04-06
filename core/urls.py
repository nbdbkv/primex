from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from core.yasg import urlpatterns as yasg
from cashbox import views


urlpatterns = [
    path("ckeditor/", include("ckeditor_uploader.urls")),
    path("_nested_admin/", include("nested_admin.urls")),
    path("account/", include("account.urls")),
    path("about/", include("about.urls")),
    path("operation/", include("operation.urls")),
    path("payment/", include("cashbox.urls")),
    path("getRequisite/<str:requisite>/", views.check_requisite),
    path("makePayment", views.make_payment),
    path("webpush/", include("webpush.urls")),
    path('m/', include('flight.urls')),
    path('__debug__/', include('debug_toolbar.urls')),

              ] + yasg

urlpatterns += i18n_patterns(
    path("admin/", admin.site.urls),
    prefix_default_language=False
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
