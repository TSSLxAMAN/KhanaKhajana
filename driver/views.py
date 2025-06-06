from django.shortcuts import render, redirect,get_object_or_404
from adminapp.models import OrderCreated
from django.utils import timezone
from django.db.models import Sum

# Create your views here.
def driverDashboard(request):
    driver = request.user.driver_profile 
    driver_deliveries = OrderCreated.objects.filter(delivered_by=driver, is_delivered=False)
    total_assigned = OrderCreated.objects.filter(delivered_by=driver).count()
    total_earnings = driver_deliveries.aggregate(
            total=Sum('total_amount')
        )['total'] or 0
    return render(request, 'driver/driverDashboard.html',{'total_assigned':total_assigned,'total_earnings':total_earnings})

def pendingDelivery(request,order_id=None):
    if order_id:
        pendingOrder = OrderCreated.objects.get(id=order_id,is_delivered=False)
        return render(request, 'driver/particularPendingOrder.html', {'order': pendingOrder})
    else:
        driver = request.user.driver_profile 
        driver_deliveries = OrderCreated.objects.filter(delivered_by=driver, is_delivered=False)
        print(driver_deliveries)
    return render(request, 'driver/pendingDelivery.html', {'driver_deliveries':driver_deliveries})

def deliveredOrders(request, order_id=None):
    if order_id:
        # Show particular delivered order details
        delivered_order = get_object_or_404(OrderCreated, id=order_id, is_delivered=True)
        return render(request, 'driver/particularDeliveredOrder.html', {'order': delivered_order})
    else:
        # Show all delivered orders for the driver
        driver = request.user.driver_profile 
        driver_deliveries = OrderCreated.objects.filter(
            delivered_by=driver, 
            is_delivered=True
        ).order_by('-delivered_at')
        
        # Calculate total earnings
        total_earnings = driver_deliveries.aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        
        # Calculate success rate (assuming all delivered orders are successful)
        total_assigned = OrderCreated.objects.filter(delivered_by=driver).count()
        success_rate = (driver_deliveries.count() / total_assigned * 100) if total_assigned > 0 else 0
        
        context = {
            'driver_deliveries': driver_deliveries,
            'total_earnings': total_earnings,
            'success_rate': round(success_rate, 1)
        }
        
        return render(request, 'driver/deliveryCompleted.html', context)
def verifyOTP(request,order_id):   
    if request.method == 'POST':
        otp = request.POST.get('delivery_otp')
        order = OrderCreated.objects.get(id=order_id)
        if order.delivery_otp == otp:
            order.otp_confirmed = True
            order.is_delivered = True
            order.delivered_at = timezone.now()
            order.save()
            return render(request, 'driver/deliveryCompleted.html')
        else:
            error_msg = "Wrong OTP, try again"
            return redirect('pendingDelivery',order_id=order_id)
    return render(request, 'driver/deliveryCompleted.html')


