from django.urls import path, include
from fcm_django.api.rest_framework import FCMDeviceAuthorizedViewSet
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from rest_framework.routers import DefaultRouter

from account.views import (
    UserRegisterView,
    UserSendCodeView,
    RegisterCodeVerifyView,
    PasswordResetVerifyView,
    UpdateUserInfoView
)

router = DefaultRouter()

router.register('devices', FCMDeviceAuthorizedViewSet)

urlpatterns = [
    path('token/', TokenObtainPairView.as_view()),
    path('token/refresh/', TokenRefreshView.as_view()),
    path('register/', UserRegisterView.as_view()),
    path('code/send/', UserSendCodeView.as_view()),
    path('code/verify/', RegisterCodeVerifyView.as_view()),
    path('password/verify/reset/', PasswordResetVerifyView.as_view()),
    path('update/info/<str:phone>/', UpdateUserInfoView.as_view())
]