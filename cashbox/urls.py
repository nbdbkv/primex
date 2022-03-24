from rest_framework.routers import DefaultRouter

from cashbox import views

router = DefaultRouter()
router.register("", views.PaymentViewSet)

urlpatterns = router.urls
