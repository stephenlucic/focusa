# perfil/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from focusaApp.models import Perfil

@login_required
def ver_perfil(request):
    perfil, _ = Perfil.objects.get_or_create(user=request.user)

    if request.method == "POST":
        # usuario
        u = request.user
        u.first_name = request.POST.get("first_name", u.first_name).strip()
        u.last_name  = request.POST.get("last_name", u.last_name).strip()
        new_email    = request.POST.get("email", u.email).strip()
        if new_email and new_email.lower() != (u.email or "").lower():
            if User.objects.filter(email__iexact=new_email).exclude(pk=u.pk).exists():
                messages.error(request, "Ese email ya está en uso.")
                return render(request, "perfil.html", {"perfil": perfil})
            u.email = new_email
        u.save()

        # campos de perfil
        perfil.telefono  = request.POST.get("telefono", perfil.telefono).strip()
        perfil.ocupacion = request.POST.get("ocupacion", perfil.ocupacion).strip()
        perfil.genero    = request.POST.get("genero", perfil.genero)
        perfil.pais      = request.POST.get("pais", perfil.pais).strip()

        # guardar avatar si viene archivo
        if 'avatar' in request.FILES:
            perfil.avatar = request.FILES['avatar']

        perfil.save()

        messages.success(request, "Perfil actualizado correctamente.")
        return redirect("perfil")

    return render(request, "perfil.html", {"perfil": perfil})
