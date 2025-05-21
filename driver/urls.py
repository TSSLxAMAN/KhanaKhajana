from django.urls import path
from .views import *

urlpatterns = [
    path('', driverDashboard, name='driverDashboard'),
]