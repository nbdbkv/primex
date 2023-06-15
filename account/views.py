from rest_framework import generics, status, permissions
from rest_framework.generics import UpdateAPIView, GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from django.utils.translation import gettext_lazy as _
from fcm_django.models import FCMDevice
from firebase_admin.auth import verify_id_token

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
    DistrictsSerializer, FcmCreateSerializer,
    PhoneVerifySerializer,
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
    queryset = Region.objects.order_by('position')


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


class FcmCreateView(UpdateAPIView):
    serializer_class = FcmCreateSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        user = request.user
        if user:
            try:
                fcm = FCMDevice.objects.get(user_id=user.pk, device_id=request.data['device_id'])
                fcm.registration_id = request.data['registration_id']
                fcm.type = request.data['type']
                fcm.active = request.data['active']
                fcm.save()
            except FCMDevice.DoesNotExist:
                FCMDevice.objects.create(user=user, name=request.data['name'], device_id=request.data['device_id'],
                                         type=request.data['type'], registration_id=request.data['registration_id'])

            return Response({"data": request.data}, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class FcmDeleteView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    queryset = FCMDevice.objects.all()

    def delete(self, request, *args, **kwargs):
        try:
            fcm = FCMDevice.objects.get(user_id=request.user.pk, id=kwargs['device_id'])
            fcm.delete()
            return Response(
                {"massage": "Успешно удалено"}, status=status.HTTP_204_NO_CONTENT
            )
        except FCMDevice.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class PhoneVerifyView(GenericAPIView):
    queryset = User
    permission_classes = [IsAuthenticated]
    serializer_class = PhoneVerifySerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid()
        try:
            decoded_token = verify_id_token(serializer.data['token'])
        except:
            return Response({'message': 'Токен не действителен'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(phone=serializer.data['phone'])
            user.is_verified = True
            user.save()
            return Response({'token': user.tokens()}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'message': 'Неверный номер'}, status=status.HTTP_404_NOT_FOUND)
