from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User, Group
from Kanban.models import Tarea, Tag
from focusaApp.models import Perfil
import json

API_TOKEN = "blablax10"  # ideal: mover a settings

def check_token(request):
    auth = request.headers.get("Authorization", "")
    return auth == f"Bearer {API_TOKEN}"

# ========== TAREAS ==========
@csrf_exempt
def crear_tarea(request):
    if not check_token(request):
        return JsonResponse({"ok": False, "error": "No autorizado"}, status=401)

    if request.method != "POST":
        return JsonResponse({"ok": False, "error": "Método no permitido"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"ok": False, "error": "JSON inválido"}, status=400)

    username    = (data.get("username") or "").strip()
    titulo      = (data.get("titulo") or "").strip()
    descripcion = (data.get("descripcion") or "").strip()
    prioridad   = data.get("prioridad", "media")
    estado      = data.get("estado", "todo")
    fecha_desde = data.get("fecha_desde") or None
    fecha_hasta = data.get("fecha_hasta") or None
    tag_nombre  = (data.get("tag") or "").strip()

    if not username:
        return JsonResponse({"ok": False, "error": "username es obligatorio"}, status=400)
    if not titulo:
        return JsonResponse({"ok": False, "error": "titulo es obligatorio"}, status=400)

    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return JsonResponse({"ok": False, "error": "Usuario no encontrado"}, status=404)

    if prioridad not in dict(Tarea.PRIORIDAD_CHOICES):
        return JsonResponse({"ok": False, "error": "prioridad no válida"}, status=400)
    if estado not in dict(Tarea.ESTADO_CHOICES):
        return JsonResponse({"ok": False, "error": "estado no válido"}, status=400)

    tag = None
    if tag_nombre:
        tag, _ = Tag.objects.get_or_create(
            usuario=user,
            nombre=tag_nombre,
            defaults={"color": "#0d6efd"},
        )

    tarea = Tarea.objects.create(
        titulo=titulo,
        descripcion=descripcion,
        prioridad=prioridad,
        estado=estado,
        responsable=user,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        tag=tag,
    )

    return JsonResponse(
        {
            "ok": True,
            "tarea": {
                "id": tarea.id,
                "titulo": tarea.titulo,
                "descripcion": tarea.descripcion,
                "prioridad": tarea.prioridad,
                "estado": tarea.estado,
                "fecha_desde": str(tarea.fecha_desde) if tarea.fecha_desde else None,
                "fecha_hasta": str(tarea.fecha_hasta) if tarea.fecha_hasta else None,
                "tag": tarea.tag.nombre if tarea.tag else None,
                "responsable": tarea.responsable.username,
            },
        },
        status=201,
    )

@csrf_exempt
def editar_tarea(request, tarea_id):
    if not check_token(request):
        return JsonResponse({"ok": False, "error": "No autorizado"}, status=401)
    if request.method != "PUT" and request.method != "PATCH":
        return JsonResponse({"ok": False, "error": "Método no permitido"}, status=405)

    try:
        tarea = Tarea.objects.get(id=tarea_id)
    except Tarea.DoesNotExist:
        return JsonResponse({"ok": False, "error": "Tarea no encontrada"}, status=404)

    try:
        data = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"ok": False, "error": "JSON inválido"}, status=400)

    titulo      = data.get("titulo")
    descripcion = data.get("descripcion")
    prioridad   = data.get("prioridad")
    estado      = data.get("estado")
    fecha_desde = data.get("fecha_desde")
    fecha_hasta = data.get("fecha_hasta")
    tag_nombre  = data.get("tag")

    if titulo is not None:
        titulo = titulo.strip()
        if not titulo:
            return JsonResponse({"ok": False, "error": "titulo no puede ser vacío"}, status=400)
        tarea.titulo = titulo
    if descripcion is not None:
        tarea.descripcion = (descripcion or "").strip()
    if prioridad is not None:
        if prioridad not in dict(Tarea.PRIORIDAD_CHOICES):
            return JsonResponse({"ok": False, "error": "prioridad no válida"}, status=400)
        tarea.prioridad = prioridad
    if estado is not None:
        if estado not in dict(Tarea.ESTADO_CHOICES):
            return JsonResponse({"ok": False, "error": "estado no válido"}, status=400)
        tarea.estado = estado
    if fecha_desde is not None:
        tarea.fecha_desde = fecha_desde or None
    if fecha_hasta is not None:
        tarea.fecha_hasta = fecha_hasta or None
    if tag_nombre is not None:
        tag_nombre = (tag_nombre or "").strip()
        if tag_nombre:
            tag, _ = Tag.objects.get_or_create(
                usuario=tarea.responsable,
                nombre=tag_nombre,
                defaults={"color": "#0d6efd"},
            )
            tarea.tag = tag
        else:
            tarea.tag = None

    tarea.save()

    return JsonResponse({
        "ok": True,
        "tarea": {
            "id": tarea.id,
            "titulo": tarea.titulo,
            "descripcion": tarea.descripcion,
            "prioridad": tarea.prioridad,
            "estado": tarea.estado,
            "fecha_desde": str(tarea.fecha_desde) if tarea.fecha_desde else None,
            "fecha_hasta": str(tarea.fecha_hasta) if tarea.fecha_hasta else None,
            "tag": tarea.tag.nombre if tarea.tag else None,
            "responsable": tarea.responsable.username,
        },
    })

@csrf_exempt
def eliminar_tarea_api(request, tarea_id):
    if not check_token(request):
        return JsonResponse({"ok": False, "error": "No autorizado"}, status=401)
    if request.method != "DELETE":
        return JsonResponse({"ok": False, "error": "Método no permitido"}, status=405)

    try:
        tarea = Tarea.objects.get(id=tarea_id)
    except Tarea.DoesNotExist:
        return JsonResponse({"ok": False, "error": "Tarea no encontrada"}, status=404)

    tarea.delete()
    return JsonResponse({"ok": True})

# NUEVO: listar tareas de un usuario
@csrf_exempt
def listar_tareas_usuario(request, username):
    if not check_token(request):
        return JsonResponse({"ok": False, "error": "No autorizado"}, status=401)

    if request.method != "GET":
        return JsonResponse({"ok": False, "error": "Método no permitido"}, status=405)

    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return JsonResponse({"ok": False, "error": "Usuario no encontrado"}, status=404)

    tareas = (
        Tarea.objects.filter(responsable=user)
        .select_related("tag")
        .order_by("estado", "prioridad", "id")
    )

    data = []
    for t in tareas:
        data.append(
            {
                "id": t.id,
                "titulo": t.titulo,
                "descripcion": t.descripcion,
                "prioridad": t.prioridad,
                "estado": t.estado,
                "fecha_desde": str(t.fecha_desde) if t.fecha_desde else None,
                "fecha_hasta": str(t.fecha_hasta) if t.fecha_hasta else None,
                "tag": t.tag.nombre if t.tag else None,
            }
        )

    return JsonResponse({"ok": True, "usuario": user.username, "tareas": data})

# ========== TAGS ==========
@csrf_exempt
def crear_tag(request):
    if not check_token(request):
        return JsonResponse({"ok": False, "error": "No autorizado"}, status=401)

    if request.method != "POST":
        return JsonResponse({"ok": False, "error": "Método no permitido"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"ok": False, "error": "JSON inválido"}, status=400)

    username = (data.get("username") or "").strip()
    nombre   = (data.get("nombre") or "").strip()
    color    = (data.get("color") or "#0d6efd").strip()

    if not username:
        return JsonResponse({"ok": False, "error": "username es obligatorio"}, status=400)
    if not nombre:
        return JsonResponse({"ok": False, "error": "nombre es obligatorio"}, status=400)

    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return JsonResponse({"ok": False, "error": "Usuario no encontrado"}, status=404)

    tag, created = Tag.objects.get_or_create(
        usuario=user,
        nombre=nombre,
        defaults={"color": color},
    )

    if not created and color and tag.color != color:
        tag.color = color
        tag.save(update_fields=["color"])

    return JsonResponse(
        {
            "ok": True,
            "created": created,
            "tag": {
                "id": tag.id,
                "nombre": tag.nombre,
                "color": tag.color,
                "usuario": tag.usuario.username,
            },
        },
        status=201 if created else 200,
    )

# NUEVO: listar tags de un usuario
@csrf_exempt
def listar_tags_usuario(request, username):
    if not check_token(request):
        return JsonResponse({"ok": False, "error": "No autorizado"}, status=401)

    if request.method != "GET":
        return JsonResponse({"ok": False, "error": "Método no permitido"}, status=405)

    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return JsonResponse({"ok": False, "error": "Usuario no encontrado"}, status=404)

    tags = Tag.objects.filter(usuario=user).order_by("nombre")

    data = [
        {"id": tag.id, "nombre": tag.nombre, "color": tag.color}
        for tag in tags
    ]

    return JsonResponse({"ok": True, "usuario": user.username, "tags": data})

@csrf_exempt
def editar_tag(request, tag_id):
    if not check_token(request):
        return JsonResponse({"ok": False, "error": "No autorizado"}, status=401)
    if request.method != "PUT" and request.method != "PATCH":
        return JsonResponse({"ok": False, "error": "Método no permitido"}, status=405)

    try:
        tag = Tag.objects.get(id=tag_id)
    except Tag.DoesNotExist:
        return JsonResponse({"ok": False, "error": "Tag no encontrado"}, status=404)

    try:
        data = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"ok": False, "error": "JSON inválido"}, status=400)

    nombre = data.get("nombre")
    color  = data.get("color")

    if nombre is not None:
        nombre = nombre.strip()
        if not nombre:
            return JsonResponse({"ok": False, "error": "nombre no puede ser vacío"}, status=400)
        tag.nombre = nombre
    if color is not None:
        tag.color = color.strip() or tag.color

    tag.save()

    return JsonResponse({
        "ok": True,
        "tag": {
            "id": tag.id,
            "nombre": tag.nombre,
            "color": tag.color,
            "usuario": tag.usuario.username,
        },
    })

@csrf_exempt
def eliminar_tag_api(request, tag_id):
    if not check_token(request):
        return JsonResponse({"ok": False, "error": "No autorizado"}, status=401)
    if request.method != "DELETE":
        return JsonResponse({"ok": False, "error": "Método no permitido"}, status=405)

    try:
        tag = Tag.objects.get(id=tag_id)
    except Tag.DoesNotExist:
        return JsonResponse({"ok": False, "error": "Tag no encontrado"}, status=404)

    tag.delete()
    return JsonResponse({"ok": True})

# ========== USUARIOS ==========

@csrf_exempt
def crear_usuario(request):
    if not check_token(request):
        return JsonResponse({"ok": False, "error": "No autorizado"}, status=401)

    if request.method != "POST":
        return JsonResponse({"ok": False, "error": "Método no permitido"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"ok": False, "error": "JSON inválido"}, status=400)

    username   = (data.get("username") or "").strip()
    email      = (data.get("email") or "").strip()
    first_name = (data.get("first_name") or "").strip()
    last_name  = (data.get("last_name") or "").strip()
    password   = data.get("password") or ""
    ocupacion  = (data.get("ocupacion") or "").strip()
    telefono   = (data.get("telefono") or "").strip()
    genero     = (data.get("genero") or "").strip()
    pais       = (data.get("pais") or "").strip()
    # grupos puede venir como lista de nombres o IDs
    grupos_nombres = data.get("grupos") or []   # ej: ["Administrador", "Usuario"]

    if not username or not email or not first_name or not last_name or not password:
        return JsonResponse(
            {"ok": False, "error": "username, email, first_name, last_name y password son obligatorios"},
            status=400,
        )

    if User.objects.filter(username=username).exists():
        return JsonResponse({"ok": False, "error": "El username ya existe"}, status=400)
    if User.objects.filter(email=email).exists():
        return JsonResponse({"ok": False, "error": "El email ya existe"}, status=400)

    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
    )

    # Perfil
    perfil, _ = Perfil.objects.get_or_create(user=user)
    perfil.ocupacion = ocupacion
    perfil.telefono = telefono
    perfil.genero = genero
    perfil.pais = pais
    perfil.save()

    # Grupos: si no se envía nada, asignar por defecto "Usuario" (si existe)
    grupos_qs = Group.objects.none()
    if grupos_nombres:
        grupos_qs = Group.objects.filter(name__in=grupos_nombres)

    if not grupos_qs.exists():
        grupo_usuario = Group.objects.filter(name="Usuario").first()
        if grupo_usuario:
            grupos_qs = Group.objects.filter(id=grupo_usuario.id)

    user.groups.set(grupos_qs)

    return JsonResponse(
        {
            "ok": True,
            "usuario": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "ocupacion": perfil.ocupacion,
                "telefono": perfil.telefono,
                "genero": perfil.genero,
                "pais": perfil.pais,
                "grupos": list(user.groups.values_list("name", flat=True)),
            },
        },
        status=201,
    )

@csrf_exempt
def listar_usuarios(request):
    if not check_token(request):
        return JsonResponse({"ok": False, "error": "No autorizado"}, status=401)

    if request.method != "GET":
        return JsonResponse({"ok": False, "error": "Método no permitido"}, status=405)

    usuarios = (
        User.objects.all()
        .select_related("perfil")
        .prefetch_related("groups")
        .order_by("id")
    )

    data = []
    for u in usuarios:
        perfil = getattr(u, "perfil", None)
        data.append(
            {
                "id": u.id,
                "username": u.username,
                "email": u.email,
                "first_name": u.first_name,
                "last_name": u.last_name,
                "ocupacion": getattr(perfil, "ocupacion", ""),
                "telefono": getattr(perfil, "telefono", ""),
                "genero": getattr(perfil, "genero", ""),
                "pais": getattr(perfil, "pais", ""),
                "grupos": list(u.groups.values_list("name", flat=True)),
            }
        )

    return JsonResponse({"ok": True, "usuarios": data})

@csrf_exempt
def editar_usuario_api(request, user_id):
    if not check_token(request):
        return JsonResponse({"ok": False, "error": "No autorizado"}, status=401)
    if request.method != "PUT" and request.method != "PATCH":
        return JsonResponse({"ok": False, "error": "Método no permitido"}, status=405)

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return JsonResponse({"ok": False, "error": "Usuario no encontrado"}, status=404)

    try:
        data = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"ok": False, "error": "JSON inválido"}, status=400)

    username   = data.get("username")
    email      = data.get("email")
    first_name = data.get("first_name")
    last_name  = data.get("last_name")
    password   = data.get("password")
    ocupacion  = data.get("ocupacion")
    telefono   = data.get("telefono")
    genero     = data.get("genero")
    pais       = data.get("pais")
    grupos_nombres = data.get("grupos")  # lista opcional

    if username is not None:
        username = username.strip()
        if not username:
            return JsonResponse({"ok": False, "error": "username no puede ser vacío"}, status=400)
        if User.objects.exclude(id=user.id).filter(username=username).exists():
            return JsonResponse({"ok": False, "error": "El username ya existe"}, status=400)
        user.username = username

    if email is not None:
        email = email.strip()
        if not email:
            return JsonResponse({"ok": False, "error": "email no puede ser vacío"}, status=400)
        if User.objects.exclude(id=user.id).filter(email=email).exists():
            return JsonResponse({"ok": False, "error": "El email ya existe"}, status=400)
        user.email = email

    if first_name is not None:
        user.first_name = first_name.strip()
    if last_name is not None:
        user.last_name = last_name.strip()
    if password:
        user.set_password(password)

    user.save()

    perfil, _ = Perfil.objects.get_or_create(user=user)
    if ocupacion is not None:
        perfil.ocupacion = (ocupacion or "").strip()
    if telefono is not None:
        perfil.telefono = (telefono or "").strip()
    if genero is not None:
        perfil.genero = (genero or "").strip()
    if pais is not None:
        perfil.pais = (pais or "").strip()
    perfil.save()

    if grupos_nombres is not None:
        grupos_qs = Group.objects.filter(name__in=grupos_nombres) if grupos_nombres else Group.objects.none()
        if not grupos_qs.exists():
            grupo_usuario = Group.objects.filter(name="Usuario").first()
            if grupo_usuario:
                grupos_qs = Group.objects.filter(id=grupo_usuario.id)
        user.groups.set(grupos_qs)

    return JsonResponse({
        "ok": True,
        "usuario": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "ocupacion": perfil.ocupacion,
            "telefono": perfil.telefono,
            "genero": perfil.genero,
            "pais": perfil.pais,
            "grupos": list(user.groups.values_list("name", flat=True)),
        },
    })

@csrf_exempt
def eliminar_usuario_api(request, user_id):
    if not check_token(request):
        return JsonResponse({"ok": False, "error": "No autorizado"}, status=401)
    if request.method != "DELETE":
        return JsonResponse({"ok": False, "error": "Método no permitido"}, status=405)

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return JsonResponse({"ok": False, "error": "Usuario no encontrado"}, status=404)

    user.delete()
    return JsonResponse({"ok": True})