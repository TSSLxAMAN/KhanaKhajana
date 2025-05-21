from django.urls import path
from .views import *

urlpatterns = [
    path('', driverDashboard, name='driverDashboard'),
    path('pendingDelivery/', pendingDelivery, name='pendingDelivery'),
    path('pendingDelivery/<uuid:order_id>', pendingDelivery, name='particularPendingDelivery'),
    path('ordersdelivered/', ordersdelivered, name='ordersdelivered'),
    path('verifyOTP/<uuid:order_id>', verifyOTP, name='verifyOTP'),
]