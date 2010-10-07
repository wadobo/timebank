from django.conf import settings

def base(request):
    '''
    This is a context processor that adds some vars to the base template
    '''
    return {
        'SITE_NAME': settings.SITE_NAME,
        'MEDIA_URL': settings.MEDIA_URL
    }
