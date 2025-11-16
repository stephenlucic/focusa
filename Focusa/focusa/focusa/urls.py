from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LoginView
from focusaApp import views as app_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # Login que redirige si ya estás logeado
    path(
        'accounts/login/',
        LoginView.as_view(
            template_name='registration/login.html',
            redirect_authenticated_user=True
        ),
        name='login'
    ),

    # Resto de vistas de auth
    path('accounts/', include('django.contrib.auth.urls')),

    path('', include('home.urls')),
    path('focusa/', include('focusaApp.urls')),
    path('kanban/', include('Kanban.urls')),
    path('perfil/', include('perfil.urls')),
    path('calendario/', include('calendario.urls')),
]

handler404 = "focusaApp.views.error_404"
handler500 = "focusaApp.views.error_500"
handler403 = "focusaApp.views.error_403"
handler400 = "focusaApp.views.error_400"

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
