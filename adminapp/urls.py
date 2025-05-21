from django.urls import path
from .views import *

urlpatterns = [
    path('', adminDashboard, name='adminDashboard'),
    path('ordersCompleted/', ordersCompleted, name='ordersCompleted'),
    path('ordersCompleted/<uuid:order_id>', ordersCompleted, name='ordersCompleted'),
    path('pendingOrders/', pendingOrders, name='pendingOrders'),
    path('pendingOrders/<uuid:order_id>', pendingOrders, name='pendingOrders_details'),
    path('cancelledOrders/', cancelledOrders, name='cancelledOrders'),
    path('cancel_order/<uuid:order_id>', cancel_order, name='cancel_order'),
    path('addCusine/', addCusine, name='addCusine'),
    path('addDriver/', addDriver, name='addDriver'),
    path('revenue/', revenue, name='revenue'),
    path('editCuisine/<uuid:cuisine_id>/', editCuisine, name='editCuisine'),
    path('editDriver/<uuid:driver_id>/', editDriver, name='editDriver'),
    path('start_prepration/', start_prepration, name='start_prepration'),
    path('complete_cooking/', complete_cooking, name='complete_cooking'),
    path('send_for_delivery/', send_for_delivery, name='send_for_delivery'),
    path('receipt/<uuid:order_id>/', generate_receipt_pdf, name='generate_receipt'),

]