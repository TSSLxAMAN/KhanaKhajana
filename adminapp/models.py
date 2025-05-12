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
