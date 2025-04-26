from django.shortcuts import render

# Create your views here.
def homepage(request):
    return render(request, 'home/home.html')

def cuisine(request):
    return render(request, 'home/cuisine.html')

def aboutus(request):
    return render(request, 'home/aboutus.html')

def contact(request):
    return render(request, 'home/contact.html')

def login(request):
    return render(request, 'home/login.html')