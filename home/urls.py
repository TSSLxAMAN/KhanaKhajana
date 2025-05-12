from django.urls import path, include
from .views import *

urlpatterns = [
    path('', homepage, name='home'), 
    path('cuisine/', cuisine, name='cuisine'), 
    path('contact/', contact, name='contact'), 
    path('aboutus/', aboutus, name='aboutus'), 
    path('dashboard/', dashboard, name='dashboard'), 
    path('myprofile/', myprofile, name='myprofile'), 
    path('myorders/', myorders, name='myorders'), 
    path('mycart/', mycart, name='mycart'), 
    path('addToCart/', addToCart, name='addToCart'), 
    path('removeItem/', removeItem, name='removeItem'),
    path('get_cart_data_json/', get_cart_data_json, name='get_cart_data_json'),
    path('cart_total_price/', cart_total_price, name='cart_total_price'),
    path('cart_items_quantity_increase/', cart_items_quantity_increase, name='cart_items_quantity_increase'),
    path('cart_items_quantity_decrease/', cart_items_quantity_decrease, name='cart_items_quantity_decrease'),
]
