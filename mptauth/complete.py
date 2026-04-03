
from django.conf import settings
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import REDIRECT_FIELD_NAME
from social_core.actions import do_complete
from social_django.views import _do_login
from social_django.utils import psa
from social_core.utils import setting_name

from rest_framework_simplejwt.tokens import RefreshToken
from . import utils

NAMESPACE = getattr(settings, setting_name('URL_NAMESPACE'), None) or 'social'
_REDIRECT_FRONTEND = getattr(settings, 'BASE_FRONTEND_URL', None)
_COMPLETE_REDIRECT = getattr(settings, 'LOGIN_REDIRECT_URL', None)

@never_cache
@csrf_exempt
@psa('{0}:complete'.format(NAMESPACE))
def complete(request, backend, *args, **kwargs):
    data = request.GET
    callback = data.get('callback', None)
    REDIRECT_FRONTEND = _REDIRECT_FRONTEND if callback == None else callback
    REDIRECT_FRONTEND = utils.append_slash(REDIRECT_FRONTEND)
    if data.get('error', None) == "access_denied":
        if REDIRECT_FRONTEND is None:
            return redirect(_COMPLETE_REDIRECT)
        return HttpResponseRedirect(f"{REDIRECT_FRONTEND}?oauth_message=cancleauthen")

    """Authentication complete view"""
    try:
        _complete = do_complete(request.backend, _do_login, user=request.user,
                        redirect_name=REDIRECT_FIELD_NAME, request=request,
                        *args, **kwargs)
    except Exception as e:
        if settings.DEBUG: print(e)
        return HttpResponseRedirect(data.get('callback') or data.get('next') or "/")
    
    if REDIRECT_FRONTEND is None:
        return _complete
    
    user = request.user
    token = getToken(user)
    return HttpResponseRedirect(f"{REDIRECT_FRONTEND}callback/?token={token}")

def getToken(user):
    refresh = RefreshToken.for_user(user)
    '''
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }
    '''
    return str(refresh)