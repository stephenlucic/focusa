from django.http import JsonResponse
from django.shortcuts import render
from datetime import datetime, timedelta

def calendario(request):
    # Si el calendario pide eventos (?events=1), devolvemos JSON
    if request.GET.get("events") == "1":
        today = datetime.now()
        data = [
            {
                "title": "Diseño de la interfaz",
                "start": (today + timedelta(days=1)).strftime("%Y-%m-%d"),
                "allDay": True,
                "className": ["fc-event-azul"]
            },
            {
                "title": "Configuración base de datos",
                "start": (today + timedelta(days=3)).strftime("%Y-%m-%d"),
                "allDay": True,
                "className": ["fc-event-verde"]
            },
            {
                "title": "Desarrollar API REST",
                "start": (today + timedelta(days=0)).strftime("%Y-%m-%d"),
                "allDay": True,
                "className": ["fc-event-amarillo"]
            },
        ]
        return JsonResponse(data, safe=False)

    # Renderizamos directamente calendario.html
    return render(request, "calendario.html")
