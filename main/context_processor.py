from django.conf import settings
from user.models import Profile
from news.models import New
from django.contrib.auth.forms import AuthenticationForm

def base(request):
    '''
    This is a context processor that adds some vars to the base template
    '''
    if request.method == 'POST' and request.POST.has_key('id_username'):
        login_form = AuthenticationForm(request.POST)
        login_form.is_valid()
    else:
        login_form = AuthenticationForm()
    return {
        'SITE_NAME': settings.SITE_NAME,
        'MEDIA_URL': settings.MEDIA_URL,
        'user': request.user,
        'front_news': New.objects.filter(hidden=False).order_by("-publish_date")[:3],
        'session': request.session,
        'login_form': login_form
    }
