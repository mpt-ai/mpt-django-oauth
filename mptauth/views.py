from django.conf import settings
from django.contrib.auth import logout as logout_view
from django.http import HttpResponseRedirect
from . import utils

def logout(request):
    logout_view(request)
    _REDIRECT_BACKEND = getattr(settings, 'BASE_BACKEND_URL', None)
    _REDIRECT_FRONTEND = getattr(settings, 'BASE_FRONTEND_URL', None)
    _uri = getattr(settings, 'OAUTH_MPT_SERVER_BASEURL', None)
    _scheme = getattr(settings, 'OAUTH_MPT_SCHEME', None)
    if _uri is None:
        raise Exception("Please input `OAUTH_MPT_SERVER_BASEURL` in settings.py")
    callback_uri = request.GET.get('callback', None)
    REDIRECT_FRONTEND = _REDIRECT_FRONTEND if callback_uri == None else callback_uri
    REDIRECT_FRONTEND = utils.append_slash(url=REDIRECT_FRONTEND)
    if REDIRECT_FRONTEND is not None:
        return HttpResponseRedirect(f"{_scheme}://{_uri}/logout?next={REDIRECT_FRONTEND}")
    return HttpResponseRedirect(f"{_scheme}://{_uri}/logout?next={_REDIRECT_BACKEND}")
    