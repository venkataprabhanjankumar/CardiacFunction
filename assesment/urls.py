from django.urls import path
from . import views

urlpatterns = [
    path('getresult', views.get_result, name='result'),
]
