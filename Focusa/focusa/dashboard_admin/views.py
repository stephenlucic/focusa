from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User, Group
from django.db.models import Count, Max
from django.utils import timezone
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.http import HttpResponse
from django.template.loader import render_to_string
from datetime import timedelta
from .models import LoginLog
from weasyprint import HTML
import json

def is_admin(user):
    return user.groups.filter(name='Administrador').exists()

@login_required
# @user_passes_test(is_admin)
def dashboard_admin(request):
    if not request.user.groups.filter(name='Administrador').exists():
        messages.error(request, "No tienes permiso para acceder a esta página.")
        raise PermissionDenied
    
    # Total usuarios
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    
    # Por grupo
    admin_group = Group.objects.filter(name='Administrador').first()
    usuario_group = Group.objects.filter(name='Usuario').first()
    
    admins_count = admin_group.user_set.count() if admin_group else 0
    usuarios_count = usuario_group.user_set.count() if usuario_group else 0
    
    # Últimos 7 días - logins por día
    now = timezone.now()
    week_ago = now - timedelta(days=7)
    logins_per_day = (
        LoginLog.objects
        .filter(timestamp__gte=week_ago)
        .extra(select={'day': 'DATE(timestamp)'})
        .values('day')
        .annotate(count=Count('id'))
        .order_by('day')
    )

    # Convertir a lista y serializar correctamente para JSON
    logins_list = []
    for item in logins_per_day:
        logins_list.append({
            'day': str(item['day']),  # convertir fecha a string
            'count': item['count']
        })
    
    # Día con más conexiones (últimos 30 días)
    month_ago = now - timedelta(days=30)
    peak_day = (
        LoginLog.objects
        .filter(timestamp__gte=month_ago)
        .extra(select={'day': 'DATE(timestamp)'})
        .values('day')
        .annotate(count=Count('id'))
        .order_by('-count')
        .first()
    )
    
    # Últimas 10 conexiones
    recent_logins = LoginLog.objects.select_related('user').order_by('-timestamp')[:10]
    
    # Tabla de usuarios con última conexión
    usuarios_con_actividad = User.objects.annotate(
        ultimo_login=Max('login_logs__timestamp'),
        total_logins=Count('login_logs')
    ).select_related('perfil').prefetch_related('groups').order_by('-ultimo_login')
    
    # Calcular días de inactividad
    usuarios_info = []
    for user in usuarios_con_actividad:
        dias_inactivo = None
        if user.ultimo_login:
            dias_inactivo = (now - user.ultimo_login).days
        
        usuarios_info.append({
            'user': user,
            'ultimo_login': user.ultimo_login,
            'total_logins': user.total_logins,
            'dias_inactivo': dias_inactivo,
            'grupos': ', '.join([g.name for g in user.groups.all()]) or 'Sin grupo'
        })
    
    context = {
        'total_users': total_users,
        'active_users': active_users,
        'admins_count': admins_count,
        'usuarios_count': usuarios_count,
        'logins_per_day_json': json.dumps(logins_list),  # JSON serializado
        'peak_day': peak_day,
        'recent_logins': recent_logins,
        'usuarios_info': usuarios_info,
    }
    
    return render(request, 'dashboard_admin.html', context)


@login_required
def exportar_dashboard_pdf(request):
    if not request.user.groups.filter(name='Administrador').exists():
        raise PermissionDenied
    
    # Total usuarios
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    inactive_users = User.objects.filter(is_active=False).count()
    
    # Por grupo
    admin_group = Group.objects.filter(name='Administrador').first()
    usuario_group = Group.objects.filter(name='Usuario').first()
    
    admins_count = admin_group.user_set.count() if admin_group else 0
    usuarios_count = usuario_group.user_set.count() if usuario_group else 0
    
    # Estadísticas de logins
    now = timezone.now()
    month_ago = now - timedelta(days=30)
    
    # Día con más conexiones
    peak_day = (
        LoginLog.objects
        .filter(timestamp__gte=month_ago)
        .extra(select={'day': 'DATE(timestamp)'})
        .values('day')
        .annotate(count=Count('id'))
        .order_by('-count')
        .first()
    )
    
    # Logins últimos 7 días
    week_ago = now - timedelta(days=7)
    logins_per_day = (
        LoginLog.objects
        .filter(timestamp__gte=week_ago)
        .extra(select={'day': 'DATE(timestamp)'})
        .values('day')
        .annotate(count=Count('id'))
        .order_by('day')
    )
    
    # Usuarios con actividad
    usuarios_con_actividad = User.objects.annotate(
        ultimo_login=Max('login_logs__timestamp'),
        total_logins=Count('login_logs')
    ).select_related('perfil').prefetch_related('groups').order_by('-ultimo_login')
    
    # Calcular días de inactividad
    usuarios_info = []
    usuarios_inactivos_30 = 0
    usuarios_activos_7 = 0
    
    for user in usuarios_con_actividad:
        dias_inactivo = None
        if user.ultimo_login:
            dias_inactivo = (now - user.ultimo_login).days
            if dias_inactivo < 7:
                usuarios_activos_7 += 1
            elif dias_inactivo > 30:
                usuarios_inactivos_30 += 1
        
        usuarios_info.append({
            'user': user,
            'ultimo_login': user.ultimo_login,
            'total_logins': user.total_logins,
            'dias_inactivo': dias_inactivo,
            'grupos': ', '.join([g.name for g in user.groups.all()]) or 'Sin grupo'
        })
    
    context = {
        'total_users': total_users,
        'active_users': active_users,
        'inactive_users': inactive_users,
        'admins_count': admins_count,
        'usuarios_count': usuarios_count,
        'peak_day': peak_day,
        'logins_per_day': logins_per_day,
        'usuarios_info': usuarios_info[:20],  # Solo primeros 20 para el PDF
        'usuarios_inactivos_30': usuarios_inactivos_30,
        'usuarios_activos_7': usuarios_activos_7,
        'fecha_generacion': now,
        'generado_por': request.user.username,
    }
    
    # Renderizar template
    html_string = render_to_string('pdf/dashboard_admin_export.html', context)
    
    # Generar PDF
    html = HTML(string=html_string, base_url=request.build_absolute_uri())
    pdf = html.write_pdf()
    
    # Respuesta
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="dashboard_admin_{now.strftime("%Y%m%d_%H%M%S")}.pdf"'
    
    return response