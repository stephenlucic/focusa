from django.contrib import admin
from django.urls import path, include
from focusaApp import views as app_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('focusaApp.urls')),
    path('kanban/', include('Kanban.urls')),
    path('perfil/', include('perfil.urls')),
    path('accounts/', include('usuario.urls')),
    path('calendario/', include('calendario.urls')),
]

handler404 = "focusaApp.views.error_404"
handler500 = "focusaApp.views.error_500"
handler403 = "focusaApp.views.error_403"
handler400 = "focusaApp.views.error_400"
