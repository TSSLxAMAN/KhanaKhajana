from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.contrib.auth import update_session_auth_hash
from django.http import JsonResponse
from django.contrib import messages
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.db.models import Sum, Avg

from .utils import send_otp_via_sms

from .forms import CustomSetPasswordForm
from .forms import SetAddressForm, SetMobileForm
from KhanaKhajana.celery import send_otp_sms_async
from .models import *

from adminapp.models import Cuisine, UserProfile, OrderCreated, OrderItem

import json
import razorpay
import random

client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

# Create your views here.
def homepage(request):
    return render(request, 'home/home.html')

def cuisine(request):
    cuisines = Cuisine.objects.all()
    return render(request, 'home/cuisine.html',{"cuisines":cuisines})

def fetch_cuisine_btn(request):
    if request.method == "GET":
        cuisines = Cuisine.objects.all()
        cuisine_data = []
        for cuisine in cuisines:
            cuisine_data.append({
                "id": str(cuisine.id),
                "name": cuisine.cusine_name,
                "description": cuisine.cusine_description,
                "type": cuisine.type,
                "region": cuisine.region,
                "price": cuisine.price,
                "time": cuisine.time,
                "image_url": cuisine.cusine_image.url,
            })
        return JsonResponse({"cuisines": cuisine_data}, status=200)
    return JsonResponse({"error": "Invalid request"}, status=400)

def aboutus(request):
    return render(request, 'home/aboutus.html')

def contact(request):
    return render(request, 'home/contact.html')

def myprofile(request):
    user_profile = UserProfile.objects.get(user=request.user)
    return render(request, 'home/myprofile.html', {'user_profile':user_profile})

@login_required(login_url='/accounts/login')
def myorders(request, order_id=None):
    if order_id:
        order_created = get_object_or_404(OrderCreated, id=order_id, user=request.user, is_cancelled=False)
        return render(request, 'home/particular_order.html', {'order_created': order_created})
    else:
        all_orders = OrderCreated.objects.filter(user=request.user,is_cancelled=False)
        return render(request, 'home/myorders.html', {'orders': all_orders})

@login_required(login_url='/accounts/login')
def cancel_order_by_user(request):
    try:
        order_id = request.POST.get('order_id')
        print('xx',order_id)
        order = OrderCreated.objects.get(id=order_id)
        print(order.is_started)
        print(order.is_cancelled)
        if order.is_started == True:
            print("hi")
            return redirect('myorders', order_id=order_id)
        else:
            print("no")
            order.is_cancelled = True
            order.save()
            return redirect('myorders', order_id=order_id)

    except Exception as e:
        return redirect('myorders')
       
@never_cache
@login_required(login_url='/accounts/login')
def dashboard(request):
    if request.user.username == 'admin':
        return redirect('adminDashboard')
    
    if hasattr(request.user, 'driver_profile') and request.user.driver_profile.role == "driver":
        return redirect('driverDashboard')

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
    
    user = request.user
    
    total_orders = OrderCreated.objects.filter(user=user, is_paid=True, is_delivered=True).count()
    total_spent = OrderCreated.objects.filter(user=user, is_paid=True, is_delivered=True).aggregate(
            total=Sum('total_amount')
        )['total'] or 0    
    delivered_orders = OrderCreated.objects.filter(user=user, is_paid=True, is_delivered=True).count()
    avg_order_value = OrderCreated.objects.filter(user=user, is_paid=True, is_delivered=True).aggregate(
        avg=Avg('total_amount')
    )['avg'] or 0

    return render(request, 'home/dashboard.html', {
        'form': form, 
        'address_form': address_form,
        'mobile_form': mobile_form,
        'user_profile': user_profile,
        'total_orders': total_orders,
        'total_spent': total_spent,
        'delivered_orders': delivered_orders,
        'avg_order_value': avg_order_value,
    })

@never_cache
@login_required(login_url='/accounts/login')
def mycart(request):
    cart_items = None
    cuisines = None
    user_address = None
    user_number = None
    try:
        user_cart = UserCart.objects.get(user=request.user)
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
        user_cart = UserCart.objects.get(user=request.user)
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

def fetch_cuisine_btn(request):
    cuisine_type = request.GET.get('type')  # 'VEG', 'NON VEG', or None
    if cuisine_type == 'VEG':
        cuisines = Cuisine.objects.filter(type='VEG')
    elif cuisine_type == 'NON VEG':
        cuisines = Cuisine.objects.filter(type='NON VEG')
    else:
        cuisines = Cuisine.objects.all()

    cuisine_data = [
        {
            'id': c.id,
            'name': c.cusine_name,
            'description': c.cusine_description,
            'type': c.type,
            'region': c.region,
            'price': c.price,
            'time': c.time,
            'image_url': c.cusine_image.url,
        }
        for c in cuisines
    ]
    return JsonResponse({'cuisines': cuisine_data})

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
            user_cart, created = UserCart.objects.get_or_create(user=request.user)           
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

        user_cart, created = UserCart.objects.get_or_create(user=request.user)
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
            user_cart = UserCart.objects.get(user=request.user)
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
            user_cart = UserCart.objects.get(user=request.user)
            cart_items = user_cart.items.all()
            total = sum(item.cuisine.price * item.quantity for item in cart_items)

            if total < 500:
                total += 50
            total += 18

            amount_in_paisa = total * 100

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

import datetime

@login_required(login_url='/accounts/login')
def payment_success(request):
    current_time3 = datetime.datetime.now()
    print(current_time3)
    payment_id = request.GET.get('payment_id')
    user_info = UserProfile.objects.get(user=request.user)
    address = user_info.address
    mobile_number = user_info.mobile_number
    try:
        user_cart = UserCart.objects.get(user=request.user)
        cart_items = user_cart.items.all()
        total = sum(item.cuisine.price * item.quantity for item in cart_items)
        if total < 500:
            total += 50
        total += 18

        otp = str(random.randint(100000, 999999))
        order = OrderCreated.objects.create(
            user=request.user,
            total_amount=total,
            payment_id=payment_id,
            is_paid=True,
            delivery_address=address,
            phone_number=mobile_number,
            delivery_otp=otp,
        )

        
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                cuisine=item.cuisine,
                quantity=item.quantity,
            )

        user_cart.is_ordered = True
        user_cart.save()
        cart_items.delete()

        current_time = datetime.datetime.now()
        print(current_time)

        send_otp_sms_async.delay(mobile_number, otp)

        current_time2 = datetime.datetime.now()
        print(current_time2)

        messages.success(request, "Payment successful! Order placed.")
        return redirect('myorders')

    except UserCart.DoesNotExist:
        messages.error(request, "No active cart found.")
        return JsonResponse({'msg':'some error occured'})
    
@login_required(login_url='/accounts/login')
def create_cod_order(request):
    if request.method == 'POST':
        user_info = UserProfile.objects.get(user=request.user)
        address = user_info.address
        mobile_number = user_info.mobile_number
        try:
            user_cart = UserCart.objects.get(user=request.user)
            cart_items = user_cart.items.all()
            total = sum(item.cuisine.price * item.quantity for item in cart_items)

            if total < 500:
                total += 50
            total += 18
    
            otp = str(random.randint(100000, 999999))

            order = OrderCreated.objects.create(
                user=request.user,
                total_amount=total,
                is_paid=False,
                payment_id=None,
                delivery_address=address,
                phone_number=mobile_number,
                delivery_otp=otp,
            )
            

            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    cuisine=item.cuisine,
                    quantity=item.quantity,
                )

            user_cart.is_ordered = True
            user_cart.save()
            cart_items.delete()

            send_otp_sms_async.delay(mobile_number, otp)

            return JsonResponse({"success": True})
        except UserCart.DoesNotExist:
            return JsonResponse({"success": False, "error": "No active cart found."})

    return JsonResponse({"success": False, "error": "Invalid request method."})

