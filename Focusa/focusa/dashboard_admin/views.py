from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User, Group
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from .models import LoginLog
import json

def is_admin(user):
    return user.groups.filter(name='Administrador').exists()

@login_required
@user_passes_test(is_admin)
def dashboard_admin(request):
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
    
    context = {
        'total_users': total_users,
        'active_users': active_users,
        'admins_count': admins_count,
        'usuarios_count': usuarios_count,
        'logins_per_day_json': json.dumps(logins_list),  # JSON serializado
        'peak_day': peak_day,
        'recent_logins': recent_logins,
    }
    
    return render(request, 'dashboard_admin.html', context)