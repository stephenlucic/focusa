from django.http import JsonResponse
from django.shortcuts import render
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from Kanban.models import Tarea  # ajusta si el nombre del app cambia

@login_required
def calendario(request):
    # Si el calendario pide eventos (?events=1), devolvemos JSON
    if request.GET.get("events") == "1":
        user = request.user
        tareas = (Tarea.objects
                  .filter(responsable=user)
                  .exclude(fecha_desde__isnull=True))

        estado_clase = {
            "todo": "fc-task-todo",
            "progress": "fc-task-progress",
            "review": "fc-task-review",
            "done": "fc-task-done",
        }
        prioridad_clase = {
            "alta": "fc-prioridad-alta",
            "media": "fc-prioridad-media",
            "baja": "fc-prioridad-baja",
        }

        events = []
        for t in tareas:
            start = t.fecha_desde
            end = t.fecha_hasta
            if end:
                end = end + timedelta(days=1)

            ev = {
                "id": t.id,
                "title": t.titulo,
                "start": start.strftime("%Y-%m-%d"),
                "allDay": True,
                "className": [prioridad_clase.get(t.prioridad, "fc-task-default")],
            }
            if end:
                ev["end"] = end.strftime("%Y-%m-%d")

            ev["extendedProps"] = {
                "prioridad": t.prioridad,
                "estado": t.estado,
            }

            events.append(ev)

        return JsonResponse(events, safe=False)

    # Renderizamos directamente calendario.html
    return render(request, "calendario.html")
