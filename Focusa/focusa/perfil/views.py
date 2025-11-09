# perfil/views.py
from django.shortcuts import render, redirect
from django.contrib import messages

def ver_perfil_publico(request):
    # intenta cargar perfil ficticio desde sesión; si no existe, muestra datos por defecto
    perfil = request.session.get("perfil_ficticio", {
        "first_name": "Juan",
        "last_name": "Pérez",
        "email": "juanperez@gmail.com",
        "mobile": "+56 9 1234 5678",
        "gender": "Masculino",
        "tax_country": "Chile",
    })
    return render(request, "perfil.html", {"perfil": perfil})

def editar_perfil_ficticio(request):
    # Datos ficticios por defecto
    defaults = {
        "first_name": "Juan",
        "last_name": "Pérez",
        "email": "juan.perez@ejemplo.com",
        "mobile": "+56 9 1234 5678",
        "gender": "male",
        "tax_country": "Chile",
    }
    
    # Obtener datos de la sesión o usar defaults
    perfil = request.session.get("perfil_ficticio", defaults)
    


    return render(request, "perfil/perfil.html", {
        "perfil": perfil,
        "is_ficticio": True
    })
