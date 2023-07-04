import datetime

from django.conf import settings
from django.core.cache import cache
from rest_framework import generics, status
from rest_framework.generics import UpdateAPIView, GenericAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from django_filters.rest_framework import DjangoFilterBackend

from fcm_django.models import FCMDevice
from firebase_admin.auth import verify_id_token

from account.messages import Message
from account.models import District, Village, AppVersion, Region, User
from account.serailizers import (
    VillagesSerializer,
    AppVersionSerializer,
    PasswordResetVerifySerializer,
    RegisterCodeVerifySerializer,
    PasswordUpdateSerializer,
    PhoneResetVerifySerializer,
    CustomTokenObtainPairSerializer,
    UpdateUserInfoSerializer,
    UserRegisterSerializer,
    UserRetrieveSerializer,
    RegionsSerializer,
    DistrictsSerializer, FcmCreateSerializer,
    PhoneVerifySerializer, LoginGoogleSerializer, LoginSerializer,
)
from account.utils import generate_qr, generate_code_logistic, send_push, user_verify, get_otp, SendSMS, user_update


class UserRegisterView(generics.CreateAPIView):
    queryset = User
    serializer_class = UserRegisterSerializer
    
    def create(self, request, *args,  **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
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
            user = User.objects.create(phone=serializer.data['phone'], info=serializer.data['info'],
                                       region_id=serializer.data['region'])
            user.set_password(serializer.data['password'])
            user.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)


class UserSendCodeView(generics.GenericAPIView):

    def post(self, request, *args, **kwargs):
        type = request.POST.get('type')
        phone = request.POST.get('phone')
        user = get_object_or_404(User, phone=phone)
        if type:
            if int(type) == 0:
                user.send_code = send_push(request.POST.get('token'))
            else:
                code = get_otp()
                user.send_code = code
                SendSMS(phone, f"code: {code}").send
        user.verify_date = datetime.datetime.now()
        user.save()
        cache.set(user.send_code, phone, settings.SMS_CODE_TIME, version=type)
        return Response(status=status.HTTP_200_OK)


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
        phone = serializer.data['phone']
        code = serializer.data['code']
        try:
            user = User.objects.get(phone=phone, send_code=code)
            user.set_password(serializer.data['password'])
            user.save()
            return Response(status=status.HTTP_200_OK)
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


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


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


class AppVersionView(generics.GenericAPIView):
    queryset = AppVersion.objects.all()
    serializer_class = AppVersionSerializer

    def get(self, request, *args, **kwargs):
        data = AppVersion.objects.first()
        serializer = self.get_serializer(data, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)


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


class LoginGoogleView(GenericAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = LoginGoogleSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid()
        try:
            decoded_token = verify_id_token(serializer.data['token'])
        except:
            return Response({'message': 'Токен не действителен'}, status=status.HTTP_400_BAD_REQUEST)
        uid = decoded_token['uid']
        try:
            user = User.objects.get(uid=uid)
            return Response({'access': user.tokens()['access'], 'is_registered': False}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            full_name = serializer.data['full_name'].split(" ")
            first_name, last_name = full_name[0], " ".join(full_name[1:])
            user = User.objects.create(first_name=first_name, last_name=last_name, uid=uid, is_active=True)
            return Response({'access': user.tokens()['access'], 'is_registered': True}, status=status.HTTP_201_CREATED)


class LoginView(generics.GenericAPIView):
    queryset = User.objects.all()
    # permission_classes = [IsAuthenticated]
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        user_update(phone=serializer.data['phone'], first_name=serializer.data['first_name'],
                    last_name=serializer.data['last_name'], region=serializer.data['region'], user=user)
        generate_qr(user)
        generate_code_logistic(user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
