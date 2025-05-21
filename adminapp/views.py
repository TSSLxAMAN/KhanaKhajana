from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.cache import never_cache
from django.utils import timezone
from django.utils.timezone import localtime
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import get_template
from django.http import HttpResponse
from django.db.models import Sum, Avg, Count
from django.db.models.functions import TruncDate
from django.utils.timezone import now
from xhtml2pdf import pisa


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
def ordersCompleted(request,order_id=None):
    completed_orders = OrderCreated.objects.filter(is_delivered=True).order_by('-delivered_at')
    return render(request, 'adminapp/ordersCompleted.html', {'completed_orders':completed_orders})

@never_cache
@login_required(login_url='/accounts/login')
def pendingOrders(request, order_id=None):
    if order_id:
        pendingOrder = OrderCreated.objects.get(id=order_id)
        drivers = Driver.objects.all()
        return render(request, 'adminapp/particular_pendingOrder.html', {'order': pendingOrder, 'drivers':drivers})
    else:
        pendingOrders = OrderCreated.objects.filter(is_delivered=False, is_cancelled=False).order_by('-order_date')
        return render(request, 'adminapp/pendingOrders.html', {'pendingOrders':pendingOrders})

@never_cache
@login_required(login_url='/accounts/login')
def cancelledOrders(request):
    cancelled_order = OrderCreated.objects.filter(is_cancelled=True).order_by('-delivered_at')
    return render(request, 'adminapp/cancelledOrders.html',{'cancelled_order':cancelled_order})

@never_cache
@login_required(login_url='/accounts/login')
def cancel_order(request,order_id):
    order = OrderCreated.objects.get(id=order_id)
    order.is_cancelled = True
    order.save()
    return redirect('pendingOrders')

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
    today = now().date()
    month = today.month
    year = today.year

    # Total Revenue
    total_revenue = OrderCreated.objects.filter(is_paid=True).aggregate(
        total=Sum('total_amount'))['total'] or 0

    # Revenue Today
    revenue_today = OrderCreated.objects.filter(is_paid=True, order_date__date=today).aggregate(
        total=Sum('total_amount'))['total'] or 0

    # Revenue This Month
    revenue_month = OrderCreated.objects.filter(is_paid=True, order_date__year=year, order_date__month=month).aggregate(
        total=Sum('total_amount'))['total'] or 0

    # Total Orders
    total_orders = OrderCreated.objects.filter(is_paid=True).count()

    # Average Order Value
    avg_order_value = OrderCreated.objects.filter(is_paid=True).aggregate(
        avg=Avg('total_amount'))['avg'] or 0

    # Cancelled Orders
    cancelled_orders = OrderCreated.objects.filter(is_cancelled=True).count()

    # Completed Orders
    completed_orders = OrderCreated.objects.filter(is_paid=True, is_delivered=True).count()

    # Top Selling Items
    top_items = OrderItem.objects.values(
        'cuisine__cusine_name'
    ).annotate(
        total_sold=Sum('quantity')
    ).order_by('-total_sold')[:5]

    # Daily Revenue for Chart
    daily_revenue = OrderCreated.objects.filter(is_paid=True).annotate(
        date=TruncDate('order_date')
    ).values('date').annotate(
        total=Sum('total_amount')
    ).order_by('date')

    context = {
        'total_revenue': total_revenue,
        'revenue_today': revenue_today,
        'revenue_month': revenue_month,
        'total_orders': total_orders,
        'avg_order_value': avg_order_value,
        'cancelled_orders': cancelled_orders,
        'completed_orders': completed_orders,
        'top_items': top_items,
        'daily_revenue': daily_revenue,
    }

    return render(request, 'adminapp/revenue.html', context)

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
            order.delivered_by = driver
            order.save()
            formatted_time = localtime(order.started_at).strftime('%b %d, %Y • %I:%M %p')

            driver_email = driver.driver_email

            subject = f"New Delivery Assigned - Order #{order_id}"
            message = f"""
                Hi {driver.driver_name},

                You have been assigned a new delivery.

                Order ID: {order_id}

                Please check your dashboard for more details.

                Regards,
                Delivery Management Team
            """
            send_mail(subject, message, from_email='ramdomlassi@gmail.com',recipient_list=[driver_email])


            return JsonResponse({'success': True,'started_at': formatted_time, 'driver': {'name' : driver.driver_name}, 'order_otp':order_otp})
        except Exception as e:
            print("SEND MAIL ERROR:", str(e))
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
        
    return JsonResponse({'error': 'Invalid request'}, status=400)

def generate_receipt_pdf(request, order_id):
    order = get_object_or_404(OrderCreated, id=order_id)
    items = OrderItem.objects.filter(order=order)

    template_path = 'receipt.html'
    context = {'order': order, 'items': items}

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename="receipt_{order.id}.pdf"'

    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('Error generating PDF receipt', status=500)
    return response