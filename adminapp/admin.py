from django.contrib import admin
from . models import *
# Register your models here.
admin.site.register(Cuisine)
admin.site.register(UserProfile)
admin.site.register(OrderCreated)
admin.site.register(OrderItem)
admin.site.register(Driver)
admin.site.register(Driver_Delivery)
