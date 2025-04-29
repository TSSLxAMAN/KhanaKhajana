from django.shortcuts import render
from django.contrib import messages
from .forms import Cuisine_Form

# Create your views here.
def adminDashboard(request):
    return render(request, 'adminapp/adminDashboard.html')

def ordersCompleted(request):
    return render(request, 'adminapp/ordersCompleted.html')

def pendingOrders(request):
    return render(request, 'adminapp/pendingOrders.html')

def addCusine(request):
    if request.method == 'POST':
        form = Cuisine_Form(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cuisine added successfully!')
            form = Cuisine_Form()
    else:
        form = Cuisine_Form()
    return render(request, 'adminapp/addCusine.html', {'form': form})

def userReview(request):
    return render(request, 'adminapp/userReview.html')

def revenue(request):
    return render(request, 'adminapp/revenue.html')
