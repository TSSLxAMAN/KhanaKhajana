from django.urls import path, include
from .views import *

urlpatterns = [
    path('', homepage, name='home'), 
    path('cuisine/', cuisine, name='cuisine'), 
    path('contact/', contact, name='contact'), 
    path('aboutus/', aboutus, name='aboutus'), 
    path('dashboard/', dashboard, name='dashboard'), 
    path('mycart/', mycart, name='mycart'), 
    path('addToCart/', addToCart, name='addToCart'), 
    path('removeItem/', removeItem, name='removeItem'),
    path('get_cart_data_json/', get_cart_data_json, name='get_cart_data_json'),
 
]
