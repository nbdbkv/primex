from rest_framework import generics, status, permissions
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from django.utils.translation import gettext_lazy as _

from account.messages import Message
from account.permissions import IsOwner
from account.models import District, Village, Region, User
from account.serailizers import (
    VillagesSerializer,
    PasswordResetVerifySerializer,
    RegisterCodeVerifySerializer,
    PhoneResetVerifySerializer,
    UpdateUserInfoSerializer,
    UserRegisterSerializer,
    UserRetrieveSerializer,
    UserSendCodeSerializer,
    RegionsSerializer,
    DistrictsSerializer,
)


class UserRegisterView(generics.CreateAPIView):
    queryset = User
    serializer_class = UserRegisterSerializer


class UserSendCodeView(generics.GenericAPIView):
    serializer_class = UserSendCodeSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.send_otp_code()
        return Response(Message.CODE_SENT.value, status=status.HTTP_202_ACCEPTED)


class RegisterCodeVerifyView(generics.GenericAPIView):
    serializer_class = RegisterCodeVerifySerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.update()
        return Response(Message.USER_ACTIVATED.value, status=status.HTTP_202_ACCEPTED)


class PasswordResetVerifyView(generics.GenericAPIView):
    serializer_class = PasswordResetVerifySerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.update()
        return Response(Message.PASSWORD_CHANGED.value, status=status.HTTP_202_ACCEPTED)


class PhoneResetVerifyView(generics.GenericAPIView):
    serializer_class = PhoneResetVerifySerializer
    # permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.update(instance=self.get_object())
        return Response(Message.PHONE_CHANGED.value, status=status.HTTP_202_ACCEPTED)


class UpdateUserInfoView(generics.UpdateAPIView):
    serializer_class = UpdateUserInfoSerializer
    # permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class GetUserView(generics.RetrieveAPIView):
    serializer_class = UserRetrieveSerializer
    # permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class RegionsView(generics.ListAPIView):
    serializer_class = RegionsSerializer
    queryset = Region.objects.all()


class DistrictsView(generics.ListAPIView):
    serializer_class = DistrictsSerializer
    queryset = District.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["region"]


class VillagesView(generics.ListAPIView):
    serializer_class = VillagesSerializer
    queryset = Village.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["region"]
