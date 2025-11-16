import json
from django.shortcuts import render

def dashboard(request):
    # 1. Progreso mensual (creadas vs completadas)
    meses = ["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"]
    creadas = [40,32,38,50,46,55,62,58,60,65,70,68]
    completadas = [30,28,35,42,40,49,55,53,57,60,66,64]

    # Distribución estados (por hacer, en proceso, revisión, completo)
    estados_labels = ["Por hacer","En proceso","En revisión","Completo"]
    estados_values = [18, 9, 6, 34]

    # Productividad por día (heatmap: lunes alto, jueves bajo)
    productividad_dias = [
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

    # Progreso proyectos (porcentaje completado)
    proyectos = ["Website", "Mobile App", "API", "Data ETL", "UX Rediseño"]
    progreso = [75, 42, 88, 55, 63]  # %
    pendientes = [25, 58, 12, 45, 37]

    # Resumen mes
    resumen = {
        "tareas_creadas": 65,
        "tareas_completadas": 60,
        "productividad_pct": int(60/65*100),
        "dias_activos": 20
    }

    # Tareas por prioridad (apiladas)
    prioridades_labels = ["Ene","Feb","Mar","Abr","May"]
    pr_alta   = [8,7,6,9,10]
    pr_media  = [12,11,13,14,13]
    pr_baja   = [6,5,7,6,8]

    ctx = {
        "meses_json": json.dumps(meses),
        "progreso_series_json": json.dumps([
            {"name": "Completadas", "data": completadas},
            {"name": "Creadas", "data": creadas}
        ]),
        "estados_labels_json": json.dumps(estados_labels),
        "estados_values_json": json.dumps(estados_values),
        "heatmap_json": json.dumps(productividad_dias),
        "proyectos_labels_json": json.dumps(proyectos),
        "proyectos_completadas_json": json.dumps(progreso),
        "proyectos_pendientes_json": json.dumps(pendientes),
        "resumen": resumen,
        "prioridades_labels_json": json.dumps(prioridades_labels),
        "prioridades_series_json": json.dumps([
            {"name": "Alta", "data": pr_alta},
            {"name": "Media", "data": pr_media},
            {"name": "Baja", "data": pr_baja},
        ])
    }
    tareas = [
    {
        "titulo": "Diseño interfaz usuario",
        "estado": "En proceso",
        "prioridad": "Alta",
        "fecha_creacion": "2025-11-05",
        "fecha_limite": "2025-11-18",
        "porcentaje": 60
    },
    {
        "titulo": "Configurar base de datos",
        "estado": "Por hacer",
        "prioridad": "Media",
        "fecha_creacion": "2025-11-06",
        "fecha_limite": "2025-11-20",
        "porcentaje": 0
    },
    {
        "titulo": "Desarrollar API REST",
        "estado": "Completo",
        "prioridad": "Alta",
        "fecha_creacion": "2025-11-02",
        "fecha_limite": "2025-11-14",
        "porcentaje": 100
    },
] 
    ctx["tareas"] = tareas
    return render(request, "dashboard.html", ctx)