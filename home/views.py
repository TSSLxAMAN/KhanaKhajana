from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.contrib.auth import update_session_auth_hash
from .forms import CustomSetPasswordForm
from django.contrib import messages
from adminapp.models import Cuisine
from .models import *

# Create your views here.
def homepage(request):
    return render(request, 'home/home.html')

def cuisine(request):
    cuisines = Cuisine.objects.all()
    return render(request, 'home/cuisine.html',{"cuisines":cuisines})

def aboutus(request):
    return render(request, 'home/aboutus.html')

def contact(request):
    return render(request, 'home/contact.html')

@never_cache
@login_required(login_url='/accounts/login')
def dashboard(request):
    if request.user.username == 'admin':
       return redirect('adminDashboard')
    
    if not request.user.has_usable_password():
        if request.method == 'POST':
            form = CustomSetPasswordForm(user=request.user, data=request.POST)
            if form.is_valid():
                form.save()
                update_session_auth_hash(request, request.user)
                messages.success(request, "Password set successfully!",extra_tags='password')
                return redirect('dashboard')
        else:
            form = CustomSetPasswordForm(user=request.user)
    else:
        form = None

    return render(request, 'home/dashboard.html' ,{'form': form})

@never_cache
@login_required(login_url='/accounts/login')
def mycart(request):
    user_id = request.user
    user_cart = UserCart.objects.get(user=request.user, is_ordered= False)
    cart_items = user_cart.items.all()
    items_count = cart_items.count()
    is_empty = True
    if items_count > 0:
        is_empty = False
    return render(request, 'home/mycart.html',{'is_empty': is_empty})

