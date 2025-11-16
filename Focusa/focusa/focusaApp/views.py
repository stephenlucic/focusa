from django.conf import settings
from django.contrib.auth import login
from django.shortcuts import redirect, render
from django.views.generic import CreateView
from .forms import SignUpForm
from .models import Perfil
from django.contrib.auth.models import Group

# Create your views here.

class SignUpView(CreateView):
    template_name = "registration/registrar.html"
    form_class = SignUpForm

    def dispatch(self, request, *args, **kwargs):
        # Si ya está autenticado, no permitir entrar al registrar
        if request.user.is_authenticated:
            return redirect(getattr(settings, "LOGIN_REDIRECT_URL", "/"))
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.save()
        Perfil.objects.get_or_create(user=user)  # seguro si ya existe
        usuario_group, _ = Group.objects.get_or_create(name="Usuario")
        user.groups.add(usuario_group)
        login(self.request, user)
        return redirect(getattr(settings, "LOGIN_REDIRECT_URL", "/"))

    def form_invalid(self, form):
        print("Signup errors:", form.errors.as_json())
        return super().form_invalid(form)

def error_404(request, exception):
    return render(request, "errors/404.html", status=404)

def error_500(request):
    return render(request, "errors/500.html", status=500)

def error_403(request, exception):
    return render(request, "errors/403.html", status=403)

def error_400(request, exception):
    return render(request, "errors/400.html", status=400)