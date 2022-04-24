from operation.models import Parcel, Payment, PaymentHistory, PaymentType
from operation.choices import PaymentHistoryType, PaymentTypeChoices
from decimal import Decimal


class Cashbox:
    def get_parcel(self, code):
        parcel = Parcel.objects.get(code=code)
        return parcel

    def get_payment_type(self, type):
        payment_type = PaymentType.objects.get(type=type)
        return payment_type

    def __init__(self, code, amount, type) -> None:
        self.parcel = self.get_parcel(code)
        self.sum = float(amount)
        self.type = self.get_payment_type(type)

    def get_user(self):
        user = self.parcel.sender
        return user

    def create_pay_history(self, payment_type):
        parcel_history = PaymentHistory.objects.create(
            user=self.get_user(),
            parcel=self.parcel,
            type=self.type,
            sum=self.sum,
            payment_type=payment_type,
        )
        return parcel_history

    def create_parcel_payment(self):
        cash = Payment.objects.get(
            type__type=PaymentTypeChoices.CASH, parcel=self.parcel.payment
        )
        cash.sum -= Decimal(self.sum)
        cash.save()
        self.parcel.payment.payment.create(type=self.type, sum=self.sum)

    def save(self):
        self.create_pay_history(PaymentHistoryType.DEBIT)
        self.create_pay_history(PaymentHistoryType.CREDIT)
        self.create_parcel_payment()
