from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.contrib.auth import update_session_auth_hash
from django.http import JsonResponse
from django.contrib import messages
from django.conf import settings
from django.shortcuts import get_object_or_404

from .forms import CustomSetPasswordForm
from .forms import SetAddressForm, SetMobileForm

from .models import *

from adminapp.models import Cuisine, UserProfile

import json
import razorpay
client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

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

def myprofile(request):
    return render(request, 'home/myprofile.html')

def myorders(request):
    return render(request, 'home/myorders.html')


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

    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    address_form = SetAddressForm(instance=user_profile)
    if request.method == 'POST' and 'address' in request.POST:
        address_form = SetAddressForm(request.POST, instance=user_profile)
        if address_form.is_valid():
            address_form.save()
            messages.success(request, "Address set successfully!", extra_tags='address')
            return redirect('dashboard')
    
    mobile_form = SetMobileForm(instance=user_profile)
    if request.method == 'POST' and 'mobile_number' in request.POST:
        mobile_form = SetMobileForm(request.POST, instance=user_profile)
        if mobile_form.is_valid():
            mobile_form.save()
            messages.success(request, "Mobile number set successfully!", extra_tags='mobile')
            return redirect('dashboard')
    
    return render(request, 'home/dashboard.html', {
        'form': form, 
        'address_form': address_form,
        'mobile_form': mobile_form,
        'user_profile': user_profile
    })


@never_cache
@login_required(login_url='/accounts/login')
def mycart(request):
    cart_items = None
    cuisines = None
    user_address = None
    user_number = None
    try:
        user_cart = UserCart.objects.get(user=request.user, is_ordered=False)
        cart_items = user_cart.items.all()
        for item in cart_items:
            item.total_price = item.cuisine.price * item.quantity
        is_empty = not user_cart.items.exists()
        cuisines = Cuisine.objects.filter(region="SNACK")
        user_info = UserProfile.objects.get(user=request.user)
        user_address = user_info.address
        user_number = user_info.mobile_number
    except UserCart.DoesNotExist:
        is_empty = True
    return render(request, 'home/mycart.html',{'is_empty': is_empty, 'cart_items': cart_items, 'cuisines':cuisines, 'user_address':user_address, 'user_number':user_number})


@login_required(login_url='/accounts/login')
def get_cart_data_json(request):
    try:
        user_cart = UserCart.objects.get(user=request.user, is_ordered=False)
        cart_items = user_cart.items.select_related('cuisine')

        data = []
        for item in cart_items:
            cuisine = item.cuisine
            data.append({
                "cart_item_id": item.id,
                "quantity": item.quantity,
                "cuisine": {
                    "id": str(cuisine.id),
                    "cusine_name": cuisine.cusine_name,
                    "cusine_description": cuisine.cusine_description,
                    "type": cuisine.type,
                    "region": cuisine.region,
                    "price": cuisine.price,
                    "time": cuisine.time,
                    "cusine_image_url": cuisine.cusine_image.url if cuisine.cusine_image else ""
                }
            })
        return JsonResponse({"cart_items": data})
    except UserCart.DoesNotExist:
        return JsonResponse({"cart_items": []})

@login_required(login_url='/accounts/login')
def cart_items_quantity_increase(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            cuisine_id = data.get('query')
            cuisine = get_object_or_404(Cuisine, id=cuisine_id)
            cart = get_object_or_404(UserCart, user=request.user)
            cart_item = get_object_or_404(CartItem, cart=cart, cuisine=cuisine)

            cart_item.quantity += 1
            cart_item.save()

            return JsonResponse({'quantity': cart_item.quantity})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required(login_url='/accounts/login')
def cart_items_quantity_decrease(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            cuisine_id = data.get('query')
            cuisine = get_object_or_404(Cuisine, id=cuisine_id)
            cart = get_object_or_404(UserCart, user=request.user)
            cart_item = get_object_or_404(CartItem, cart=cart, cuisine=cuisine)
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
            cart_item.save()

            return JsonResponse({'quantity': cart_item.quantity})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request'}, status=400)
    
@login_required(login_url='/accounts/login')
def addToCart(request):
    data = json.loads(request.body)
    cuisine_id = data.get('query')
    if request.method == 'POST':
        try:
            user_cart, created = UserCart.objects.get_or_create(user=request.user, is_ordered=False)           
            cuisine = Cuisine.objects.get(id=cuisine_id)
            
            if CartItem.objects.filter(cart=user_cart, cuisine=cuisine).exists():
                return JsonResponse({'exist': True})

            cart_item = CartItem.objects.create(cart=user_cart, cuisine=cuisine)

            cuisine = cart_item.cuisine
            data = {
                "cart_item_id": cart_item.id,
                "quantity": cart_item.quantity,
                "cuisine": {
                    "id": str(cuisine.id),
                    "cusine_name": cuisine.cusine_name,
                    "cusine_description": cuisine.cusine_description,
                    "type": cuisine.type,
                    "region": cuisine.region,
                    "price": cuisine.price,
                    "time": cuisine.time,
                    "cusine_image_url": cuisine.cusine_image.url if cuisine.cusine_image else ""
                }
            }
            return JsonResponse({'success': True, "cart_item": data})
        except Cuisine.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Cuisine not found'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'error': 'An error occurred'}, status=500)


@login_required(login_url='/accounts/login')
def removeItem(request):
    try:
        data = json.loads(request.body)
        cuisine_id = data.get('query')
        if not cuisine_id:
            return JsonResponse({'success': False, 'error': 'Invalid cuisine ID'}, status=400)

        user_cart, created = UserCart.objects.get_or_create(user=request.user, is_ordered=False)
        cuisine = Cuisine.objects.get(id=cuisine_id)
        CartItem.objects.filter(cart=user_cart, cuisine=cuisine).delete()
        return JsonResponse({'success': True})
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON payload'}, status=400)
    except Cuisine.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Cuisine not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required(login_url='/accounts/login')
def cart_total_price(request):
    if request.method == 'GET':
        try:
            user_cart = UserCart.objects.get(user=request.user, is_ordered=False)
            cart_items = user_cart.items.all()
            total = sum(item.cuisine.price * item.quantity for item in cart_items)

            if total < 500:
                total += 50  
            total += 18 

            return JsonResponse({"success": True, "total": total})
        except UserCart.DoesNotExist:
            return JsonResponse({"success": False, "error": "Cart not found."})
    return JsonResponse({"success": False, "error": "Invalid request."})    

@login_required(login_url='/accounts/login')
def create_razorpay_order(request):
    if request.method == 'POST':
        try:
            user_cart = UserCart.objects.get(user=request.user, is_ordered=False)
            cart_items = user_cart.items.all()
            total = sum(item.cuisine.price * item.quantity for item in cart_items)

            # Add delivery and tax
            if total < 500:
                total += 50
            total += 18

            amount_in_paisa = total * 100  # Razorpay expects amount in paise

            razorpay_order = client.order.create({
                "amount": amount_in_paisa,
                "currency": "INR",
                "payment_capture": "1"
            })

            return JsonResponse({
                "success": True,
                "order_id": razorpay_order["id"],
                "amount": amount_in_paisa,
                "currency": "INR",
                "key": settings.RAZORPAY_KEY_ID,
            })

        except UserCart.DoesNotExist:
            return JsonResponse({"success": False, "error": "Cart not found."})
    return JsonResponse({"success": False, "error": "Invalid request."})

@login_required(login_url='/accounts/login')
def payment_success(request):
    payment_id = request.GET.get('payment_id')
    # You can use payment_id to verify and update the order
    return redirect('myorders')