import datetime

from rest_framework import generics, status
from rest_framework.generics import UpdateAPIView, GenericAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from fcm_django.models import FCMDevice
from firebase_admin.auth import verify_id_token

from account.messages import Message
from account.models import District, Village, Region, User
from account.serailizers import (
    VillagesSerializer,
    PasswordResetVerifySerializer,
    RegisterCodeVerifySerializer,
    PasswordUpdateSerializer,
    PhoneResetVerifySerializer,
    UpdateUserInfoSerializer,
    UserRegisterSerializer,
    UserRetrieveSerializer,
    UserSendCodeSerializer,
    RegionsSerializer,
    DistrictsSerializer, FcmCreateSerializer,
    PhoneVerifySerializer,
)
from account.utils import generate_qr, generate_code_logistic, send_push, user_verify


class UserRegisterView(generics.CreateAPIView):
    queryset = User
    serializer_class = UserRegisterSerializer
    
    def create(self, request, *args,  **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid()
        try:
            user = User.objects.get(phone=serializer.data['phone'])
            if user.is_active:
                return Response({'message': 'Пользователь существует'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                user.info = serializer.data['info']
                user.region_id = serializer.data['region']
                user.set_password(serializer.data['password'])
                user.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        except User.DoesNotExist:
            User.objects.create(phone=serializer.data['phone'], password=serializer.data['password'],
                                info=serializer.data['info'], region_id=serializer.data['region'])
            return Response(serializer.data, status=status.HTTP_201_CREATED)


class UserSendCodeView(generics.GenericAPIView):
    serializer_class = UserSendCodeSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = send_push(serializer.data['token'])
        user = get_object_or_404(User, phone=serializer.data['phone'])
        user.send_code = code
        user.verify_date = datetime.datetime.now()
        user.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class RegisterCodeVerifyView(generics.GenericAPIView):
    serializer_class = RegisterCodeVerifySerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.update()
        return Response(Message.USER_ACTIVATED.value, status=status.HTTP_202_ACCEPTED)


class PasswordUpdateView(generics.UpdateAPIView):
    serializer_class = PasswordUpdateSerializer
    # permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user


class PasswordResetVerifyView(generics.GenericAPIView):
    queryset = User
    permission_classes = [AllowAny]
    serializer_class = PasswordResetVerifySerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid()
        try:
            verify_id_token(serializer.data['token'])
        except:
            return Response({'message': 'Токен не действителен'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(phone=serializer.data['phone'])
            user.set_password(serializer.data['password'])
            user.save()
            return Response(user.tokens(), status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'message': 'Неверный номер'}, status=status.HTTP_404_NOT_FOUND)


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
    permission_classes = [AllowAny]
    serializer_class = PhoneVerifySerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid()
        if serializer.data['token'].isdigit() and len(serializer.data['token']):
            user = get_object_or_404(User, phone=serializer.data['phone'])
            current_date = datetime.datetime.now()
            if user.send_code != serializer.data['token'] and current_date - user.verify_date > datetime.timedelta(minutes=5):
                return Response({'message': 'Код не действителен'}, status=status.HTTP_400_BAD_REQUEST)
            user_verify(user)
            return Response(user.tokens(), status=status.HTTP_200_OK)
        try:
            verify_id_token(serializer.data['token'])
        except:
            return Response({'message': 'Токен не действителен'}, status=status.HTTP_400_BAD_REQUEST)
        user = get_object_or_404(User, phone=serializer.data['phone'])
        user_verify(user)
        return Response(user.tokens(), status=status.HTTP_200_OK)
