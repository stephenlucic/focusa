from django.http import JsonResponse
from django.shortcuts import render
from datetime import datetime, timedelta

def calendario(request):
    # Si el calendario pide eventos (?events=1), devolvemos JSON
    if request.GET.get("events") == "1":
        today = datetime.now()
        data = [
            {
                "title": "Diseño Interfaz Usuario",
                "start": (today + timedelta(days=1)).strftime("%Y-%m-%d"),
                "allDay": True,
            },
            {
                "title": "Configuración base de datos",
                "start": (today + timedelta(days=3)).strftime("%Y-%m-%d"),
                "allDay": True,
            },
            {
                "title": "Desarrollar API REST",
                "start": (today + timedelta(days=0)).strftime("%Y-%m-%d"),
                "allDay": True,
            },
        ]
        return JsonResponse(data, safe=False)

    # Renderizamos directamente calendario.html (sin subcarpeta)
    return render(request, "calendario.html")
