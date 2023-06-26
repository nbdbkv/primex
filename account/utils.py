import json
import random
from io import BytesIO
from random import randint
from uuid import uuid4
from firebase_admin.messaging import Message, Notification
import qrcode
import requests
from django.conf import settings
from django.core.files import File
from transliterate import translit
from core.settings import FCM_DJANGO_SETTINGS


def user_verify(user):
    user.is_active = True
    user.save()
    generate_qr(user)
    generate_code_logistic(user)


def send_push(token):
    FCM_SERVER_KEY = FCM_DJANGO_SETTINGS['FCM_SERVER_KEY']
    code = get_otp()
    requests.post(
        url='https://fcm.googleapis.com/fcm/send',
        headers={
            'Content-Type': "application/json; charset=UTF-8",
            'Authorization': f'key={FCM_SERVER_KEY}'
        },
        data=json.dumps({
            'registration_ids': [token],
            'notification': {
                'title': "Taura Express",
                'body': f"Код подтверждения : {code}",
            },
            'data': {
                'code': f'{code}',
                'type': 'verification'
            }
        }))
    return code


class SendSMS:
    __url = "http://smspro.nikita.kg/api/message"

    __headers = {"Content-Type": "application/xml"}

    __xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        "<message>"
        "<login>{login}</login>"
        "<pwd>{password}</pwd>"
        "<id>{id}</id>"
        "<sender>{sender}</sender>"
        "<text>{text}</text>"
        "<phones>{phones}</phones>"
        "</message>"
    )

    def __init__(self, phone, text):
        if type(phone) not in (list, tuple):
            self.phone = [phone]
        else:
            self.phone = phone
        self.text = text

    def __get_phones(self):
        phones = ""
        for phone in self.phone:
            phones += f"<phone>{phone}</phone>"
        return phones

    def __get_xml(self):
        xml = self.__xml.format(
            login=settings.NIKITA_LOGIN,
            password=settings.NIKITA_PASSWORD,
            id=self.__get_id(),
            sender=settings.NIKITA_SENDER,
            text=self.text,
            phones=self.__get_phones(),
        )
        return xml

    def __get_id(self):
        id = str(uuid4())[:10]
        return id

    @property
    def send(self):
        response = requests.post(
            url=self.__url,
            data=self.__get_xml().encode("utf-8"),
            headers=self.__headers,
        )


def get_otp() -> int:
    return randint(100000, 999999)


def generate_qr(user, code=None):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    if code:
        qr.add_data(code)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        buffer = BytesIO()
        img.save(buffer)
        buffer.seek(0)
        user.qr_logistic.save(f'{code}.png', File(buffer), save=True)
    else:
        qr.add_data(user.phone)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        buffer = BytesIO()
        img.save(buffer)
        buffer.seek(0)
        user.qr_phone.save(f'{user.phone}.png', File(buffer), save=True)


def generate_code_logistic(user):
    startswith = user.region.name
    text = translit(startswith, language_code='ru', reversed=True)
    code_logistic = text.upper()[:4] + str(random.randint(11111, 99999))
    user.code_logistic = code_logistic
    user.save()
    generate_qr(user, code_logistic)
