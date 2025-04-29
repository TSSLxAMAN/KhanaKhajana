from django.urls import path
from .views import *

urlpatterns = [
    path('', adminDashboard, name='adminDashboard'),
    path('ordersCompleted/', ordersCompleted, name='ordersCompleted'),
    path('pendingOrders/', pendingOrders, name='pendingOrders'),
    path('addCusine/', addCusine, name='addCusine'),
    path('userReview/', userReview, name='userReview'),
    path('revenue/', revenue, name='revenue'),
]