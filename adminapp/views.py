from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.cache import never_cache
from django.utils import timezone
from django.utils.timezone import localtime
from .forms import Cuisine_Form, DriverForm
from .models import *

import json

# Create your views here.
@never_cache
@login_required(login_url='/accounts/login')
def adminDashboard(request):
    cuisines = Cuisine.objects.all()

    if request.method == 'POST':
        cuisine_id = request.POST.get('cuisine_id')
        cuisine_instance = get_object_or_404(Cuisine, id=cuisine_id)
        form = Cuisine_Form(request.POST, request.FILES, instance=cuisine_instance)

        if form.is_valid():
            form.save()
            messages.success(request, 'Cuisine updated successfully!', extra_tags='cuisine')
            return redirect('adminDashboard')
        else:
            messages.error(request, 'Form validation failed', extra_tags='cuisine_edit_success')
    else:
        form = Cuisine_Form()

    return render(request, 'adminapp/adminDashboard.html', {
        "cuisines": cuisines,
        "form": form
    })

@never_cache
@login_required(login_url='/accounts/login')
def ordersCompleted(request):
    return render(request, 'adminapp/ordersCompleted.html')

@never_cache
@login_required(login_url='/accounts/login')
def pendingOrders(request, order_id=None):
    if order_id:
        pendingOrder = OrderCreated.objects.get(id=order_id)
        drivers = Driver.objects.all()
        return render(request, 'adminapp/particular_pendingOrder.html', {'order': pendingOrder, 'drivers':drivers})
    else:
        pendingOrders = OrderCreated.objects.filter(is_delivered=False).order_by('-order_date')
        return render(request, 'adminapp/pendingOrders.html', {'pendingOrders':pendingOrders})

@never_cache
@login_required(login_url='/accounts/login')
def cancelledOrders(request):
    return render(request, 'adminapp/cancelledOrders.html')

@never_cache
@login_required(login_url='/accounts/login')
def addCusine(request):
    if request.method == 'POST':
        form = Cuisine_Form(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cuisine added successfully!',extra_tags='cuisine')
            form = Cuisine_Form()
    else:
        form = Cuisine_Form()
    return render(request, 'adminapp/addCusine.html', {'form': form})

@never_cache
@login_required(login_url='/accounts/login')
def userReview(request):
    return render(request, 'adminapp/userReview.html')

@never_cache
@login_required(login_url='/accounts/login')
def addDriver(request):
    drivers = Driver.objects.all()
    if request.method == 'POST':
        driver_form = DriverForm(request.POST, request.FILES)
        if driver_form.is_valid():
            driver_form.save()
            messages.success(request, "Driver added successfully!",extra_tags='driver')
            driver_form = DriverForm()  
    else:
        driver_form = DriverForm()
    
    return render(request, 'adminapp/addDriver.html',{'drivers':drivers,'form':driver_form})

@never_cache
@login_required(login_url='/accounts/login')
def revenue(request):
    return render(request, 'adminapp/revenue.html')

@never_cache
@login_required(login_url='/accounts/login')
def editCuisine(request,cuisine_id):
    if request.method == 'GET':
        try:
            cuisine = Cuisine.objects.get(id=cuisine_id)
            data = {
                'id' : cuisine.id,
                'cusine_name' : cuisine.cusine_name,
                'cusine_description' : cuisine.cusine_description,
                'type' : cuisine.type,
                'region' : cuisine.region,
                'price' : cuisine.price,
                'time' : cuisine.time,
                'cusine_image' : cuisine.cusine_image.url
            }
            return JsonResponse(data)
        except Cuisine.DoesNotExist:
            return JsonResponse({'error':'Cuisine not found'})

@never_cache
@login_required(login_url='/accounts/login')
def editDriver(request,driver_id):
    if request.method == 'GET':
        try:
            driver = Driver.objects.get(id=driver_id)
            username = driver.username
            user_password = User.objects.get(username=username)
            password = user_password.password
            data = {
                'id' : driver.id,
                'username':username,
                'password':password,
                'driver_name' : driver.driver_name,
                'mobile_number' : driver.mobile_number,
                'gender' : driver.gender,
                'driver_image' : driver.driver_image.url
            }
            return JsonResponse(data)
        except Cuisine.DoesNotExist:
            return JsonResponse({'error':'Cuisine not found'})

@never_cache
@login_required(login_url='/accounts/login')
def start_prepration(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            cuisine_id = data.get('query')
            order = OrderCreated.objects.get(id=cuisine_id)
            order.is_started = True
            order.started_at = timezone.now()
            order.save()
            formatted_time = localtime(order.started_at).strftime('%b %d, %Y • %I:%M %p')
            print(formatted_time)
            return JsonResponse({'success': True,'started_at': formatted_time})
        except Exception as e:
            return JsonResponse({'success': False,'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request'}, status=400)

@never_cache
@login_required(login_url='/accounts/login')
def complete_cooking(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            cuisine_id = data.get('query')
            order = OrderCreated.objects.get(id=cuisine_id)
            order.is_cooking_completed = True
            order.cooking_completed_at = timezone.now()
            order.save()
            formatted_time = localtime(order.started_at).strftime('%b %d, %Y • %I:%M %p')
            print(formatted_time)
            drivers = Driver.objects.all()
            driver_list = [{'id': driver.id, 'name': driver.username} for driver in drivers]
            print(driver_list)
            return JsonResponse({'success': True,'started_at': formatted_time,'driver_list':driver_list})
        except Exception as e:
            return JsonResponse({'success': False,'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request'}, status=400)

@never_cache
@login_required(login_url='/accounts/login')
def send_for_delivery(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            order_id = data.get("order_id")
            driver_id = data.get("driver_id")
            order = OrderCreated.objects.get(id=order_id)
            order.is_out_for_delivery = True
            order.out_for_delivery_at = timezone.now()
            driver = Driver.objects.get(id=driver_id)
            order_otp = order.delivery_otp
            print(order_otp)
            order.delivered_by = driver
            order.save()
            formatted_time = localtime(order.started_at).strftime('%b %d, %Y • %I:%M %p')
            return JsonResponse({'success': True,'started_at': formatted_time, 'driver': {'name' : driver.driver_name}, 'order_otp':order_otp})
        except Exception as e:
            return JsonResponse({'success': False,'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request'}, status=400)