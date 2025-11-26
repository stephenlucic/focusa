import json
from datetime import datetime, timedelta
from calendar import month_abbr
from django.shortcuts import render
from django.db import connection
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from Kanban.models import Tarea  # ajusta import si el app label es distinto

def fetch_tareas_por_hacer(user_id):
    with connection.cursor() as cursor:
        cursor.callproc('sp_tareas_por_hacer', [user_id])
        rows = cursor.fetchall()
    cols = ['id','titulo','prioridad','estado','fecha_desde','fecha_hasta','fecha_creacion']
    return [dict(zip(cols, r)) for r in rows]

def contar_tareas_por_hacer(user_id):
    with connection.cursor() as cursor:
        cursor.callproc('sp_contar_tareas_por_hacer', [user_id])
        row = cursor.fetchone()
    return row[0] if row else 0

def _counts_by_estado(user):
    qs = (Tarea.objects
          .filter(responsable=user)
          .values('estado')
          .annotate(total=Count('id')))
    mapa = {'todo':'Por hacer','progress':'En proceso','review':'En revisión','done':'Completo'}
    etiquetas, valores = [], []
    for e in ['todo','progress','review','done']:
        registro = next((r for r in qs if r['estado']==e), None)
        etiquetas.append(mapa[e])
        valores.append(registro['total'] if registro else 0)
    return etiquetas, valores

def _counts_by_prioridad(user):
    qs = (Tarea.objects
          .filter(responsable=user)
          .values('prioridad')
          .annotate(total=Count('id')))
    orden = ['alta','media','baja']
    etiquetas, valores = [], []
    for p in orden:
        registro = next((r for r in qs if r['prioridad']==p), None)
        etiquetas.append(p.capitalize())
        valores.append(registro['total'] if registro else 0)
    return etiquetas, valores

def _monthly_progress(user):
    hoy = datetime.today().date()
    meses, creadas, completadas = [], [], []
    for i in range(11, -1, -1):
        m_ref = (hoy.replace(day=1) - timedelta(days=30*i))
        year, month = m_ref.year, m_ref.month
        inicio = datetime(year, month, 1)
        fin = datetime(year + (1 if month == 12 else 0),
                       (1 if month == 12 else month + 1), 1)

        creadas.append(
            Tarea.objects.filter(responsable=user,
                                 fecha_creacion__gte=inicio,
                                 fecha_creacion__lt=fin).count()
        )
        # completadas usando fecha_hasta (DateField)
        completadas.append(
            Tarea.objects.filter(responsable=user,
                                 estado='done',
                                 fecha_hasta__gte=inicio.date(),
                                 fecha_hasta__lt=fin.date()).count()
        )
        meses.append(month_abbr[month])
    return meses, creadas, completadas

def _weekly_productivity(user):
    hoy = timezone.now().date()
    inicio_semana_actual = hoy - timedelta(days=hoy.weekday())  # lunes
    semanas = []
    series_map = {'creadas': [], 'todo': [], 'progress': [], 'review': [], 'done': []}

    for i in range(3, -1, -1):
        ini = inicio_semana_actual - timedelta(days=7*i)
        fin = ini + timedelta(days=7)  # siguiente lunes

        semanas.append(f"Sem {ini.isocalendar().week}")

        # creadas en la semana
        series_map['creadas'].append(
            Tarea.objects.filter(responsable=user,
                                 fecha_creacion__date__gte=ini,
                                 fecha_creacion__date__lt=fin).count()
        )

        # completadas (fecha_hasta es DateField)
        series_map['done'].append(
            Tarea.objects.filter(responsable=user,
                                 estado='done',
                                 fecha_hasta__gte=ini,
                                 fecha_hasta__lt=fin).count()
        )

        # snapshot de estados (creadas antes del fin y actualmente en ese estado)
        for est in ['todo','progress','review']:
            series_map[est].append(
                Tarea.objects.filter(responsable=user,
                                     estado=est,
                                     fecha_creacion__date__lte=fin - timedelta(days=1)).count()
            )

    series = [
        {"name": "Creadas", "data": series_map['creadas']},
        {"name": "Por hacer", "data": series_map['todo']},
        {"name": "En proceso", "data": series_map['progress']},
        {"name": "En revisión", "data": series_map['review']},
        {"name": "Completadas", "data": series_map['done']},
    ]
    return semanas, series

def contar_tareas_pendientes(user_id):
    """Cuenta todas las tareas que NO están completadas (estado != 'done')"""
    with connection.cursor() as cursor:
        cursor.callproc('sp_contar_tareas_pendientes', [user_id])
        row = cursor.fetchone()
    return row[0] if row else 0

@login_required
def dashboard(request):
    user = request.user

    # Tareas por hacer (SP)
    tareas_por_hacer = fetch_tareas_por_hacer(user.id)
    total_por_hacer = contar_tareas_por_hacer(user.id)

    # Tareas pendientes (cualquier estado excepto 'done')
    total_pendientes = contar_tareas_pendientes(user.id)

    # Tabla completa (ejemplo: últimas 50 tareas del usuario)
    tareas_qs = (Tarea.objects
                 .filter(responsable=user)
                 .order_by('-fecha_creacion')[:50])

    # Convertir a lista dict para el template (incluye porcentaje aproximado)
    porcentaje_map = {'todo':0,'progress':50,'review':80,'done':100}
    tareas = []
    for t in tareas_qs:
        tareas.append({
            "titulo": t.titulo,
            "estado": {'todo':'Por hacer','progress':'En proceso','review':'En revisión','done':'Completo'}[t.estado],
            "prioridad": t.prioridad.capitalize(),
            "fecha_creacion": t.fecha_creacion,
            "fecha_limite": getattr(t, 'fecha_hasta', None),
            "porcentaje": porcentaje_map.get(t.estado, 0)
        })

    # Estados
    estados_labels, estados_values = _counts_by_estado(user)

    # Prioridades (para pie)
    prioridades_labels, prioridades_values = _counts_by_prioridad(user)
    prioridades_series = [{"name": lbl, "data":[val]} for lbl, val in zip(prioridades_labels, prioridades_values)]

    # Progreso mensual
    meses, creadas, completadas = _monthly_progress(user)
    progreso_series = [
        {"name":"Completadas","data":completadas},
        {"name":"Creadas","data":creadas}
    ]

    # Productividad semanal
    productividad_labels, productividad_series = _weekly_productivity(user)

    # Resumen
    tareas_completadas = Tarea.objects.filter(responsable=user, estado='done').count()
    total_creadas = Tarea.objects.filter(responsable=user).count()
    productividad_pct = round((tareas_completadas / total_creadas)*100, 1) if total_creadas else 0

    resumen = {
        "tareas_creadas": total_creadas,        # <-- total de tareas creadas
        "tareas_pendientes": total_pendientes,  # <-- todas las tareas sin completar
        "tareas_por_hacer": total_por_hacer,    # <-- solo estado 'todo'
        "tareas_completadas": tareas_completadas,
        "productividad_pct": productividad_pct,
        "dias_activos": 0
    }

    ctx = {
        "meses_json": json.dumps(meses),
        "progreso_series_json": json.dumps(progreso_series),
        "estados_labels_json": json.dumps(estados_labels),
        "estados_values_json": json.dumps(estados_values),
        "productividad_labels_json": json.dumps(productividad_labels),
        "productividad_series_json": json.dumps(productividad_series),
        "resumen": resumen,
        "tareas": tareas,
        "prioridades_labels_json": json.dumps(prioridades_labels),
        "prioridades_series_json": json.dumps(prioridades_series),
    }
    return render(request, "dashboard.html", ctx)