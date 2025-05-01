from django.db import models
from django.contrib.auth.models import User
from adminapp.models import Cuisine
# Create your models here.

class UserCart(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)
    is_ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username

class CartItem(models.Model):
    cart = models.ForeignKey(UserCart, on_delete=models.CASCADE, related_name='items')
    cuisine = models.ForeignKey(Cuisine, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('cart', 'cuisine')

    def __str__(self):
        return f'User - {self.cart}  Item - {self.cuisine}'