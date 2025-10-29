from django.shortcuts import render

# Create your views here.
def kanban(request):
    return render(request, 'kanban.html')
