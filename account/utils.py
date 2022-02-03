from django.conf import settings
from random import randint
import requests
from uuid import uuid4


class SendSMS:
    __url = 'http://smspro.nikita.kg/api/message'
    
    __headers = {'Content-Type': 'application/xml'}
    
    __xml = '<?xml version="1.0" encoding="UTF-8"?>' \
        '<message>' \
        '<login>{login}</login>' \
        '<pwd>{password}</pwd>' \
        '<id>{id}</id>' \
        '<sender>{sender}</sender>' \
        '<text>{text}</text>' \
        '<phones>{phones}</phones>' \
        '</message>' \
    
    def __init__(self, phone, text):
        if type(phone) not in (list, tuple):
            self.phone = [phone]
        else:
            self.phone = phone
        self.text = text
    
    def __get_phones(self):
        phones = ''
        for phone in self.phone:
            phones += f'<phone>{phone}</phone>'
        return phones
    
    def __get_xml(self):
        xml = self.__xml.format(
            login=settings.NIKITA_LOGIN,
            password=settings.NIKITA_PASSWORD,
            id=self.__get_id(),
            sender=settings.NIKITA_SENDER,
            text=self.text,
            phones=self.__get_phones()
            )
        return xml
    
    def __get_id(self):
        id = str(uuid4())[:10]
        return id
    
    @property
    def send(self):
        response = requests.post(
            url=self.__url,
            data=self.__get_xml(),
            headers=self.__headers
        )


def get_otp() -> int:
    return randint(10000, 99999)
