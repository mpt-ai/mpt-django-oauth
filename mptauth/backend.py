import requests
from django.conf import settings
from social_core.backends.oauth import BaseOAuth2

class mptOAuth2(BaseOAuth2):
    name = 'mptauth'
    AUTH_SERVER = getattr(settings, 'OAUTH_MPT_SERVER_BASEURL', 'oauth.data.storemesh.com')
    _base = f'http://{AUTH_SERVER}'
    if getattr(settings, 'OAUTH_MPT_SCHEME', 'http') == "https":
        _base = f'https://{AUTH_SERVER}'
    AUTHORIZATION_URL = f'{_base}/o/authorize'
    ACCESS_TOKEN_URL = f'{_base}/o/token/'
    REFRESH_TOKEN_URL = f'{_base}/o/token/'
    USER_DATA_URL = f'{_base}/api/v1/account/me'
    
    _internal_host = getattr(settings, 'OAUTH_INTERNAL_IP', None)
    if _internal_host not in [None, "", " "]:
        ACCESS_TOKEN_URL = f'http://{_internal_host}/o/token/'
        REFRESH_TOKEN_URL = f'http://{_internal_host}/o/token/'
        USER_DATA_URL = f'http://{_internal_host}/api/v1/account/me'
        
    ACCESS_TOKEN_METHOD = 'POST'
    REVOKE_TOKEN_METHOD = 'GET'
    

    SCOPE_SEPARATOR = ' '
    EXTRA_DATA = [
        ('expires_in', 'expires_in'),
        ('refresh_token', 'refresh_token'),
        ('scope', 'scope'),
    ]

    def get_user_id(self, details, response):
        return details['username']

    def get_user_details(self, response):
        res = {
            'username': response.get('username'),
            'email': response.get('email'),
            'first_name': response.get('first_name'),
            'last_name': response.get('last_name'),
        }
        return res

    def user_data(self, access_token, *args, **kwargs):
        data = self._user_data(access_token)
        return data
                        
    def _user_data(self, access_token, path=None):
        headers = {
            'Authorization': 'Bearer {0}'.format(access_token)
        }
        extra_data = requests.get(self.USER_DATA_URL, headers=headers, verify=getattr(settings, 'SOCIAL_AUTH_VERIFY_SSL', False))
        user_profile = extra_data.json()
        return user_profile

    def auth_url(self):
        url = super().auth_url()
        callback = self.data.get('callback', None)
        next = self.data.get('next', None)
        if callback is not None:
            url += f"&callback={callback}"
        if next is not None:
            url += f"&next={next}"
        return url