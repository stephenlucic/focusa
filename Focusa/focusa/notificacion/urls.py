from django.urls import path
from .views import *
from django.contrib.auth.decorators import login_required

urlpatterns = [
    # Define your URL patterns here
    path('', login_required(notificaciones_vista), name='notificaciones'),
    path('notificaciones/count/', login_required(notificaciones_count), name='notificaciones_count'),
    path('eliminar/<int:pk>/', login_required(eliminar_notificacion), name='eliminar_notificacion'),
    path('eliminar-todas/', login_required(eliminar_todas_notificaciones), name='eliminar_todas_notificaciones'),

]