from django.db import models
import uuid 
from django.contrib.auth.models import User

# Create your models here.
class Cuisine(models.Model):

    TYPE = [
         ('VEG' , 'VEG'),
         ('NON VEG' , 'NON VEG'),
    ]

    REGION = [
        ('NORTH INDIAN' , 'NORTH INDIAN'),
        ('SOUTH INDIAN' , 'SOUTH INDIAN'),
        ('PUNJABI FOOD' , 'PUNJABI FOOD'),
        ('FAST FOOD' , 'FAST FOOD'),
        ('DESSERT' , 'DESSERT'),
        ('SNACK' , 'SNACK'),
        ('REGIONAL SPECIAL' , 'REGIONAL SPECIAL'),
    ]

    id = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False) 
    cusine_name = models.CharField(max_length=255)
    cusine_description = models.TextField()
    type = models.CharField(max_length=20, choices=TYPE)
    region = models.CharField(max_length=20, choices=REGION)
    price = models.IntegerField()
    time = models.IntegerField()
    cusine_image = models.ImageField(upload_to='images/cusine_images/')

    def __str__(self):
        return self.cusine_name

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.TextField(blank=True, null=True)
    mobile_number = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.user.username

class Driver(models.Model):
    GENDER = [
         ('MALE' , 'MALE'),
         ('FEMALE' , 'FEMALE'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='driver_profile', null=True, blank=True)
    id = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
    driver_email = models.CharField(max_length=64, null=True, blank=True)
    username = models.CharField(max_length=16, blank=True, null=True)
    role = models.CharField(max_length=16, default="driver", blank=True, null=True)
    driver_name =  models.CharField(max_length=255)
    mobile_number = models.IntegerField()
    driver_image = models.ImageField(upload_to='images/driver_images/')
    gender = models.CharField(choices=GENDER, max_length=7)
    
    def __str__(self):
        return self.driver_name

class OrderCreated(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    items = models.ManyToManyField('Cuisine', through='OrderItem', related_name='ordered_in')

    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_id = models.CharField(max_length=100, blank=True, null=True)
    is_paid = models.BooleanField(default=False)

    delivery_address = models.TextField()
    phone_number = models.CharField(max_length=15)
    delivered_by = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='delivery', null=True, blank=True)

    is_received = models.BooleanField(default=True)
    received_at = models.DateTimeField(auto_now_add=True)

    is_started = models.BooleanField(default=False)
    started_at = models.DateTimeField(blank=True, null=True)

    is_cooking_completed = models.BooleanField(default=False)
    cooking_completed_at = models.DateTimeField(blank=True, null=True)

    is_out_for_delivery = models.BooleanField(default=False)
    out_for_delivery_at = models.DateTimeField(blank=True, null=True)

    is_delivered = models.BooleanField(default=False)
    delivered_at = models.DateTimeField(blank=True, null=True)

    otp_confirmed = models.BooleanField(default=False)
    delivery_otp = models.CharField(max_length=6, blank=True, null=True)

    is_cancelled = models.BooleanField(default=False)

    order_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(OrderCreated, on_delete=models.CASCADE)
    cuisine = models.ForeignKey('Cuisine', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.cuisine.cusine_name}"

class Driver_Delivery(models.Model):
    id = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False) 
    driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True, related_name='deliveries', blank=True)
    order_id = models.ForeignKey(OrderCreated,on_delete=models.CASCADE, related_name='orders', null=True)
    delivery_otp = models.CharField(max_length=6, blank=True, null=True)
    delivered_at = models.DateTimeField(blank=True, null=True)  # Optional: add timestamp
