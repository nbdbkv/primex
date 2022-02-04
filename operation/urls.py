from django.urls import path, include

from .views import (CreateParcelView,
                    UpdateParcelView,
                    ListParcelView,
                    PaymentParcelView,
                    PaymentParcelWithBonusView,
                    DirectionsView,
                    DirectionView,
                    ParametersView,
                    DeliveryTypeView,
                    EnvelopeView,
                    RecipientView,
                    DeliveryDateView,
                    SenderView,
                    )

urlpatterns = [
    path('direction/', DirectionView.as_view()),
    path('directions/', DirectionsView.as_view()),
    path('parameters/', ParametersView.as_view()),
    path('delivery_type/', DeliveryTypeView.as_view()),
    path('envelope/', EnvelopeView.as_view()),
    path('recipient/', RecipientView.as_view()),
    path('delivery_date/', DeliveryDateView.as_view()),
    path('sender/<int:pk>', SenderView.as_view()),

    path('create/', CreateParcelView.as_view()),
    path('update/<int:pk>', UpdateParcelView.as_view()),
    path('list/', ListParcelView.as_view()),
    path('payment/<int:pk>', PaymentParcelView.as_view()),
    path('bonus/<int:pk>', PaymentParcelWithBonusView.as_view())


]