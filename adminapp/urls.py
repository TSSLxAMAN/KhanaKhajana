from django.urls import path
from .views import *

urlpatterns = [
    path('', adminDashboard, name='adminDashboard'),
    path('ordersCompleted/', ordersCompleted, name='ordersCompleted'),
    path('pendingOrders/', pendingOrders, name='pendingOrders'),
    path('pendingOrders/<uuid:order_id>', pendingOrders, name='pendingOrders_details'),
    path('cancelledOrders/', cancelledOrders, name='cancelledOrders'),
    path('addCusine/', addCusine, name='addCusine'),
    path('userReview/', userReview, name='userReview'),
    path('revenue/', revenue, name='revenue'),
    path('editCuisine/<uuid:cuisine_id>/', editCuisine, name='editCuisine'),
]