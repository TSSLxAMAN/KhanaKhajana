from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.
def homepage(request):
    return render(request, 'home/home.html')

def cuisine(request):
    return render(request, 'home/cuisine.html')

def aboutus(request):
    return render(request, 'home/aboutus.html')

def contact(request):
    return render(request, 'home/contact.html')

@login_required(login_url='/accounts/login')
def dashboard(request):
    return render(request, 'home/dashboard.html')

