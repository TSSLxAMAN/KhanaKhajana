from django.urls import path
from .views import *

urlpatterns = [
    path('', homepage, name='home'), 
    path('cuisine/', cuisine, name='cuisine'), 
    path('contact/', contact, name='contact'), 
    path('aboutus/', aboutus, name='aboutus'), 
    path('login/', login, name='login'), 
    path('signup/', signup, name='signup'), 
]
