from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import Cuisine_Form
from .models import *
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.shortcuts import get_object_or_404

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
def pendingOrders(request):
    return render(request, 'adminapp/pendingOrders.html')

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
