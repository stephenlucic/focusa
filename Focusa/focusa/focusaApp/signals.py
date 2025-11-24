from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver

@receiver(user_logged_in)
def set_user_session_flags(sender, user, request, **kwargs):
    request.session['is_admin'] = user.groups.filter(name='Administrador').exists()
    request.session['is_usuario'] = user.groups.filter(name='Usuario').exists()

@receiver(user_logged_out)
def clear_user_session_flags(sender, user, request, **kwargs):
    request.session.pop('is_admin', None)
    request.session.pop('is_usuario', None)