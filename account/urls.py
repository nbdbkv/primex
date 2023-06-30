from django.urls import path, include
from fcm_django.api.rest_framework import FCMDeviceAuthorizedViewSet
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.routers import DefaultRouter

from account.telegram import tg_message_handler
from account.views import (
    VillagesView,
    AppVersionView,
    GetUserView,
    UserRegisterView,
    UserSendCodeView,
    RegisterCodeVerifyView,
    PasswordUpdateView,
    PasswordResetVerifyView,
    PhoneResetVerifyView,
    CustomTokenObtainPairView,
    UpdateUserInfoView,
    RegionsView,
    DistrictsView, FcmDeleteView, FcmCreateView,
    PhoneVerifyView, LoginGoogleView, LoginView,
)

router = DefaultRouter()

router.register("devices", FCMDeviceAuthorizedViewSet)

urlpatterns = [
    path("device/", FcmCreateView.as_view(), name="fcm-create"),
    path("device/<int:device_id>/", FcmDeleteView.as_view(), name='fcm_delete'),
    path("token/", CustomTokenObtainPairView.as_view()),
    path("token/refresh/", TokenRefreshView.as_view()),
    path("register/", UserRegisterView.as_view()),
    path("code/send/", UserSendCodeView.as_view()),
    path("code/verify/", RegisterCodeVerifyView.as_view()),
    path("password/change/", PasswordUpdateView.as_view()),
    path("password/verify/reset/", PasswordResetVerifyView.as_view()),
    path("phone/verify/reset/", PhoneResetVerifyView.as_view()),
    path("update/info/", UpdateUserInfoView.as_view()),
    path("get/", GetUserView.as_view()),
    path("regions/", RegionsView.as_view()),
    path("districts/", DistrictsView.as_view()),
    path("villages/", VillagesView.as_view()),
    path("app_version/", AppVersionView.as_view()),
    path("telegram/", tg_message_handler),
    path('phone/verify/', PhoneVerifyView.as_view()),
    path('login_google_appleID/', LoginGoogleView.as_view()),
    path('login_create/', LoginView.as_view()),
]
