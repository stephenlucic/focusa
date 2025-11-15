from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request, 'home.html')

def dashboard(request):
    series = [10, 41, 35, 51, 49, 62, 69, 91, 148]
    labels = ["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep"]

    data = {    
        'series': series,
        'labels': labels      
    }
    return render(request, 'dashboard.html', data)

def error_404(request, exception):
    return render(request, "errors/404.html", status=404)

def error_500(request):
    return render(request, "errors/500.html", status=500)

def error_403(request, exception):
    return render(request, "errors/403.html", status=403)

def error_400(request, exception):
    return render(request, "errors/400.html", status=400)