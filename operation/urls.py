from django.urls import path
from .views import (
    CreateParcelInfoView,
    ListParcelInfoView,
)
urlpatterns = [
    path('create/', CreateParcelInfoView.as_view()),
    path('list/', ListParcelInfoView.as_view())

]

