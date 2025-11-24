from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Tarea, Tag
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods

@login_required
def kanban(request):
    if request.method == "POST":
        action = request.POST.get("action")

        # 1) Crear TAG
        if action == "create_tag":
            nombre = request.POST.get("name", "").strip()
            color = request.POST.get("color", "#0d6efd").strip() or "#0d6efd"
            if nombre:
                Tag.objects.create(nombre=nombre, color=color)
            return redirect("kanban")

        # 2) Crear TAREA
        titulo = request.POST.get("title", "").strip()
        descripcion = request.POST.get("description", "").strip()
        prioridad = request.POST.get("priority", "media")
        estado = request.POST.get("status", "todo")
        fecha_desde = request.POST.get("start_date") or None
        fecha_hasta = request.POST.get("end_date") or None
        tag_id = request.POST.get("tag") or None

        tag = None
        if tag_id:
            try:
                tag = Tag.objects.get(id=tag_id)
            except Tag.DoesNotExist:
                tag = None

        if titulo:
            Tarea.objects.create(
                titulo=titulo,
                descripcion=descripcion,
                prioridad=prioridad,
                estado=estado,
                responsable=request.user,
                fecha_desde=fecha_desde,
                fecha_hasta=fecha_hasta,
                tag=tag,
            )
        return redirect("kanban")

    tareas = Tarea.objects.filter(responsable=request.user).order_by("fecha_creacion")
    tags = Tag.objects.all().order_by("nombre")
    contexto = {
        "tareas_todo": tareas.filter(estado="todo"),
        "tareas_progress": tareas.filter(estado="progress"),
        "tareas_review": tareas.filter(estado="review"),
        "tareas_done": tareas.filter(estado="done"),
        "tags": tags,
    }
    return render(request, "kanban.html", contexto)

@require_POST
@login_required
def actualizar_estado_tarea(request):
    tarea_id = request.POST.get("id")
    nuevo_estado = request.POST.get("estado")

    if not tarea_id or not nuevo_estado:
        return JsonResponse({"ok": False, "error": "Datos inválidos"}, status=400)

    try:
        tarea = Tarea.objects.get(id=tarea_id, responsable=request.user)
    except Tarea.DoesNotExist:
        return JsonResponse({"ok": False, "error": "Tarea no encontrada"}, status=404)

    if nuevo_estado not in dict(Tarea.ESTADO_CHOICES).keys():
        return JsonResponse({"ok": False, "error": "Estado no válido"}, status=400)

    tarea.estado = nuevo_estado
    tarea.save(update_fields=["estado"])

    return JsonResponse({"ok": True})

@require_http_methods(["GET", "POST"])
@login_required
def tarea_detalle_actualizar(request, pk):
    tarea = get_object_or_404(Tarea, pk=pk, responsable=request.user)

    if request.method == "POST":
        titulo = request.POST.get("title", "").strip()
        descripcion = request.POST.get("description", "").strip()
        prioridad = request.POST.get("priority", "media")
        estado = request.POST.get("status", "todo")
        fecha_desde = request.POST.get("start_date") or None
        fecha_hasta = request.POST.get("end_date") or None
        tag_id = request.POST.get("tag") or None

        tag = None
        if tag_id:
            try:
                tag = Tag.objects.get(id=tag_id)
            except Tag.DoesNotExist:
                tag = None

        if not titulo:
            return JsonResponse({"ok": False, "error": "El título es obligatorio"}, status=400)

        tarea.titulo = titulo
        tarea.descripcion = descripcion
        tarea.prioridad = prioridad
        tarea.estado = estado
        tarea.fecha_desde = fecha_desde
        tarea.fecha_hasta = fecha_hasta
        tarea.tag = tag
        tarea.save()

        return JsonResponse({"ok": True})

    # GET: devolver datos para rellenar la modal
    data = {
        "id": tarea.id,
        "titulo": tarea.titulo,
        "descripcion": tarea.descripcion,
        "prioridad": tarea.prioridad,
        "estado": tarea.estado,
        "fecha_desde": tarea.fecha_desde.isoformat() if tarea.fecha_desde else "",
        "fecha_hasta": tarea.fecha_hasta.isoformat() if tarea.fecha_hasta else "",
        "tag_id": tarea.tag_id,
    }
    return JsonResponse({"ok": True, "tarea": data})

@require_POST
@login_required
def eliminar_tarea(request, pk):
    tarea = get_object_or_404(Tarea, pk=pk, responsable=request.user)
    tarea.delete()
    return JsonResponse({"ok": True})

@require_POST
@login_required
def eliminar_tag(request, pk):
    tag = get_object_or_404(Tag, pk=pk)
    tag.delete()
    return JsonResponse({"ok": True})

@require_POST
@login_required
def actualizar_tag(request, pk):
    tag = get_object_or_404(Tag, pk=pk)
    nombre = request.POST.get('nombre', '').strip()
    color = request.POST.get('color', '#0d6efd').strip() or '#0d6efd'
    if not nombre:
        return JsonResponse({"ok": False, "error": "El nombre es obligatorio"}, status=400)
    tag.nombre = nombre
    tag.color = color
    tag.save(update_fields=['nombre', 'color'])
    return JsonResponse({"ok": True, "id": tag.id, "nombre": tag.nombre, "color": tag.color})

@require_POST
@login_required
def crear_tag(request):
    nombre = request.POST.get("nombre","").strip()
    color = request.POST.get("color","#0d6efd").strip() or "#0d6efd"
    if not nombre:
        return JsonResponse({"ok": False, "error": "Nombre requerido"}, status=400)
    tag = Tag.objects.create(nombre=nombre, color=color)
    return JsonResponse({"ok": True, "id": tag.id, "nombre": tag.nombre, "color": tag.color})
