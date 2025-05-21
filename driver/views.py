from django.shortcuts import render

# Create your views here.
def driverDashboard(request):
    return render(request, 'driver/driverDashboard.html')