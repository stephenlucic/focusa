import json
from datetime import date
from django.shortcuts import render

def dashboard(request):
    # Datos ficticios para los gráficos del template
    meses = ["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"]
    creadas = [40,32,38,50,46,55,62,58,60,65,70,68]
    completadas = [30,28,35,42,40,49,55,53,57,60,66,64]
    

    estados_labels = ["Por hacer","En proceso","En revisión","Completo"]
    estados_values = [18, 9, 6, 34]

    heatmap = [
        {"name": "Productividad", "data": [
            {"x": "Lun", "y": 22},
            {"x": "Mar", "y": 17},
            {"x": "Mié", "y": 19},
            {"x": "Jue", "y": 12},
            {"x": "Vie", "y": 16},
            {"x": "Sáb", "y": 11},
            {"x": "Dom", "y": 8},
        ]}
    ]
    

    resumen = {
        "tareas_creadas": 65,
        "tareas_completadas": 60,
        "productividad_pct": int(60/65*100),
        "dias_activos": 20
    }

    prioridades_labels = ["Ene","Feb","Mar","Abr","May"]
    pr_alta  = [8,7,6,9,10]
    pr_media = [12,11,13,14,13]
    pr_baja  = [6,5,7,6,8]


    # Tabla (fechas como objetos date para usar |date:"d/m/Y" en el template)
    tareas = [
        {
            "titulo": "Diseño interfaz usuario",
            "estado": "En proceso",
            "prioridad": "Alta",
            "fecha_creacion": date(2025, 11, 5),
            "fecha_limite": date(2025, 11, 18),
            "porcentaje": 60
        },
        {
            "titulo": "Configurar base de datos",
            "estado": "Por hacer",
            "prioridad": "Media",
            "fecha_creacion": date(2025, 11, 6),
            "fecha_limite": date(2025, 11, 20),
            "porcentaje": 0
        },
        {
            "titulo": "Desarrollar API REST",
            "estado": "Completo",
            "prioridad": "Alta",
            "fecha_creacion": date(2025, 11, 2),
            "fecha_limite": date(2025, 11, 14),
            "porcentaje": 100
        },
    ]

    ctx = {
        "meses_json": json.dumps(meses),
        "progreso_series_json": json.dumps([
            {"name": "Completadas", "data": completadas},
            {"name": "Creadas", "data": creadas}
        ]),
        "estados_labels_json": json.dumps(estados_labels),
        "estados_values_json": json.dumps(estados_values),
        "heatmap_json": json.dumps(heatmap),
        "resumen": resumen,
        "tareas": tareas,
        "prioridades_labels_json": json.dumps(prioridades_labels),
        "prioridades_series_json": json.dumps([
            {"name": "Alta", "data": pr_alta},
            {"name": "Media", "data": pr_media},
            {"name": "Baja", "data": pr_baja},
        ]),
    }

    return render(request, "dashboard.html", ctx)