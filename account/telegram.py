from rest_framework import status, decorators
from rest_framework.response import Response
from django.conf import settings
from telebot import types
import telebot

from .models import User


bot = telebot.TeleBot(settings.TG_TOKEN, threaded=False)


@decorators.api_view(["POST"])
def tg_message_handler(request):
    bot.process_new_updates(
        [telebot.types.Update.de_json(request.stream.read().decode("utf-8"))]
    )
    return Response(status=status.HTTP_200_OK)


@bot.message_handler(commands=["start"])
def start(request):
    chat_id = request.chat.id
    bot.send_message(chat_id, "Вас приветствует бот Doce Express!")
    msg = bot.reply_to(request, "Введите номер телефона в формате 996*********")
    bot.register_next_step_handler(msg, tg_register)


@bot.message_handler(func=lambda msg: True)
def msg_handler(request):
    chat_id = request.chat.id
    bot.send_message(chat_id, "Вас приветствует бот Doce Express!")
    msg = bot.reply_to(request, "Введите номер телефона в формате 996*********")
    bot.register_next_step_handler(msg, tg_register)


def tg_register(request):
    phone = request.text
    chat_id = request.chat.id
    if user := User.objects.filter(phone=phone):
        user = user.first()
        user.tg_chat_id = chat_id
        user.tg_user_id = request.from_user.id
        user.save()
        bot.send_message(chat_id, "Пользователь успешно зарегистрирован")
    elif request.text == "exit":
        pass
    else:
        bot.send_message(chat_id, f"Пользователь с номером телефона {phone} не найден")
        msg = bot.reply_to(
            request,
            "Введите номер телефона в формате 996*********\nесли хотите выйти напишете exit",
        )
        bot.register_next_step_handler(msg, tg_register)
