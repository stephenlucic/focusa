from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.http import JsonResponse
from focusaApp.models import Perfil

def admin_usuarios(request):
    usuarios = User.objects.all()
    grupos = Group.objects.all()
    return render(request, "admin_usuarios.html", {"usuarios": usuarios, "grupos": grupos})

def editar_usuario(request, user_id):
    usuario = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        usuario.username = request.POST.get('username')
        usuario.email = request.POST.get('email')
        usuario.save()
        grupos = request.POST.getlist('grupos')
        usuario.groups.set(Group.objects.filter(id__in=grupos))
        return JsonResponse({'success': True, 'user': {
            'id': usuario.id,
            'username': usuario.username,
            'email': usuario.email,
            'groups': list(usuario.groups.values_list('name', flat=True))
        }})
    # GET: devolver JSON para modal
    grupos_html = ''.join([
        f'<div class="form-check"><input type="checkbox" name="grupos" value="{g.id}" {"checked" if g in usuario.groups.all() else ""} class="form-check-input"><label class="form-check-label">{g.name}</label></div>'
        for g in Group.objects.all()
    ])
    return JsonResponse({'id': usuario.id, 'username': usuario.username, 'email': usuario.email, 'grupos_html': grupos_html})

def eliminar_usuario(request, user_id):
    if request.method == 'POST':
        usuario = get_object_or_404(User, id=user_id)
        usuario.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'error': 'Método no permitido'}, status=405)

def toggle_usuario_activo(request, user_id):
    """Activa o desactiva un usuario"""
    if request.method == 'POST':
        usuario = get_object_or_404(User, id=user_id)
        usuario.is_active = not usuario.is_active
        usuario.save()
        return JsonResponse({
            'success': True, 
            'is_active': usuario.is_active,
            'user_id': usuario.id
        })
    return JsonResponse({'error': 'Método no permitido'}, status=405)

def crear_usuario(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        ocupacion = request.POST.get('ocupacion')
        telefono = request.POST.get('telefono')
        genero = request.POST.get('genero')
        pais = request.POST.get('pais')
        grupos = request.POST.getlist('grupos')

        # Validaciones
        if not all([username, email, first_name, last_name]):
            return JsonResponse({'success': False, 'error': 'Usuario, email, nombre y apellido son obligatorios.'})
        if password1 != password2:
            return JsonResponse({'success': False, 'error': 'Las contraseñas no coinciden.'})
        if len(password1) < 8:
            return JsonResponse({'success': False, 'error': 'La contraseña debe tener al menos 8 caracteres.'})
        if User.objects.filter(username=username).exists():
            return JsonResponse({'success': False, 'error': 'El usuario ya existe.'})
        if User.objects.filter(email=email).exists():
            return JsonResponse({'success': False, 'error': 'El email ya existe.'})

        user = User.objects.create_user(username=username, email=email, password=password1, first_name=first_name, last_name=last_name)
        perfil, _ = Perfil.objects.get_or_create(user=user)
        perfil.ocupacion = ocupacion
        perfil.telefono = telefono
        perfil.genero = genero
        perfil.pais = pais
        perfil.save()
        user.groups.set(Group.objects.filter(id__in=grupos))

        return JsonResponse({'success': True, 'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'groups': list(user.groups.values_list('name', flat=True))
        }})
    return JsonResponse({'error': 'Método no permitido'}, status=405)

