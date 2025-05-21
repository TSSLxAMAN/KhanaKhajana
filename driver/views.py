from django.shortcuts import render, redirect
from adminapp.models import OrderCreated
from django.utils import timezone


# Create your views here.
def driverDashboard(request):
    return render(request, 'driver/driverDashboard.html')

def pendingDelivery(request,order_id=None):
    if order_id:
        pendingOrder = OrderCreated.objects.get(id=order_id,is_delivered=False)
        return render(request, 'driver/particularPendingOrder.html', {'order': pendingOrder})
    else:
        driver = request.user.driver_profile 
        driver_deliveries = OrderCreated.objects.filter(delivered_by=driver, is_delivered=False)
        print(driver_deliveries)
    return render(request, 'driver/pendingDelivery.html', {'driver_deliveries':driver_deliveries})

def ordersdelivered(request):   
    return render(request, 'driver/ordersdelivered.html')

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


