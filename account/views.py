from rest_framework import generics
from rest_framework import generics, status
from rest_framework.response import Response

from django.conf import settings
from django.utils.translation import gettext_lazy as _

from account.messages import Message
from account.permissions import IsOwner
from account.models import User
from account.serailizers import (
    PasswordResetVerifySerializer,
    RegisterCodeVerifySerializer,
    UpdateUserInfoSerializer, 
    UserRegisterSerializer, 
    UserSendCodeSerializer
)


class UserRegisterView(generics.CreateAPIView):
    queryset = User
    serializer_class = UserRegisterSerializer


class UserSendCodeView(generics.GenericAPIView):
    serializer_class = UserSendCodeSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(Message.CODE_SENT.value, status=status.HTTP_202_ACCEPTED)


class RegisterCodeVerifyView(generics.GenericAPIView):
    serializer_class = RegisterCodeVerifySerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(Message.USER_ACTIVATED.value, status=status.HTTP_202_ACCEPTED)


class PasswordResetVerifyView(generics.GenericAPIView):
    serializer_class = PasswordResetVerifySerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(Message.PASSWORD_CHANGED.value, status=status.HTTP_202_ACCEPTED)


class UpdateUserInfoView(generics.UpdateAPIView):
    serializer_class = UpdateUserInfoSerializer
    queryset = User.objects.filter(is_active=True)
    permission_classes = [IsOwner]
    lookup_field = 'phone'
