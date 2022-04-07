from core.celery import app
from operation.models import Parcel
from account.models import User, UserRole
from account.telegram import bot

@app.task()
def new_parcel(code: str):
    parcel_regions = Parcel.objects.get(code=code).direction.values_list("type", flat=True)
    users = User.objects.filter(role=UserRole.OPERATOR, region__in=parcel_regions)
    print('hello')
    for user in users:
        bot.send_message(user.tg_chat_id, f"Новая посылка с кодом {code}")
    return 1232
