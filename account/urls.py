from django.urls import path, include
from fcm_django.api.rest_framework import FCMDeviceAuthorizedViewSet
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from rest_framework.routers import DefaultRouter

from account.telegram import tg_message_handler
from account.views import (
    VillagesView,
    GetUserView,
    UserRegisterView,
    UserSendCodeView,
    RegisterCodeVerifyView,
    PasswordResetVerifyView,
    PhoneResetVerifyView,
    UpdateUserInfoView,
    RegionsView,
    DistrictsView,
)

router = DefaultRouter()

router.register("devices", FCMDeviceAuthorizedViewSet)

urlpatterns = [
    path("device/", include(router.urls)),
    path("token/", TokenObtainPairView.as_view()),
    path("token/refresh/", TokenRefreshView.as_view()),
    path("register/", UserRegisterView.as_view()),
    path("code/send/", UserSendCodeView.as_view()),
    path("code/verify/", RegisterCodeVerifyView.as_view()),
    path("password/verify/reset/", PasswordResetVerifyView.as_view()),
    path("phone/verify/reset/", PhoneResetVerifyView.as_view()),
    path("update/info/", UpdateUserInfoView.as_view()),
    path("get/", GetUserView.as_view()),
    path("regions/", RegionsView.as_view()),
    path("districts/", DistrictsView.as_view()),
    path("villages/", VillagesView.as_view()),
    path("telegram/", tg_message_handler),
]
