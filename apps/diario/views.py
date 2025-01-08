from django.shortcuts import render

def home(request):
    return render(request, 'home.html')

def escrever(request):
    if request.method == "GET":
        return render(request, 'escrever.html')
