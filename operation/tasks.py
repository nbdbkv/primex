from core.celery import app
from operation.models import Parcel
from operation.choices import DeliveryStatusChoices, DirectionChoices
from account.models import User, UserRole
from account.telegram import bot


@app.task()
def tg_parcel_operator(code: str):
    parcel_region = (
        Parcel.objects.get(code=code)
        .direction.get(type=DirectionChoices.FROM)
        .district.region
    )
    users = User.objects.filter(role=UserRole.OPERATOR, region=parcel_region)
    for user in users:
        bot.send_message(user.tg_chat_id, f"Новая посылка с кодом {code}")


@app.task()
def tg_parcel_subadmin(code: str):
    parcel = Parcel.objects.get(code=code)
    if parcel.status.title == DeliveryStatusChoices.IN_ANTICIPATION:
        parcel_region = parcel.direction.get(type=DirectionChoices.FROM).district.region
        users = User.objects.filter(role=UserRole.SUBADMIN, region=parcel_region)
        for user in users:
            bot.send_message(user.tg_chat_id, f"Новая посылка с кодом {code}")


@app.task()
def tg_parcel_to_operator(code: str):
    parcel_region = (
        Parcel.objects.get(code=code)
        .direction.get(type=DirectionChoices.TO)
        .district.region
    )
    users = User.objects.filter(role=UserRole.OPERATOR, region=parcel_region)
    for user in users:
        bot.send_message(user.tg_chat_id, f"Новая посылка с кодом {code}")