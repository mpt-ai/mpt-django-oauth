import os
import requests
from io import BytesIO

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in
from django.core.files.images import ImageFile

# Using getattr with a default is cleaner
SSL_VERIFY = getattr(settings, 'SOCIAL_AUTH_VERIFY_SSL', False)


class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=300)
    last_name = models.CharField(max_length=300)
    email = models.EmailField()
    image = models.ImageField(upload_to='mptauth-image', blank=True, null=True)
    role = models.JSONField(default=list) 
    permission = models.JSONField(default=list)
    
    def __str__(self) -> str:
        return self.user.username


class AccessLog(models.Model):
    actor = models.CharField(max_length=255)
    action = models.CharField(max_length=20)
    resource = models.TextField()
    status = models.PositiveSmallIntegerField()
    origin = models.TextField()
    response_time = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)


def logged_in_handle(sender, user, request, **kwargs):
    if settings.DEBUG: 
        print("logged_in_handle triggered")
        
    if not user.is_authenticated:
        return

    # 1. Base user data
    user_data = {
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
        'role': [],
        'permission': []
    }

    # 2. Check for social auth provider using .last() directly
    prov = user.social_auth.filter(provider='mptauth').last()

    if prov:
        data = prov.extra_data
        headers = {"Authorization": f"Bearer {data.get('access_token', '')}"}
        
        _internal_ip = getattr(settings, 'OAUTH_INTERNAL_IP', None)
        _url = f"http://{_internal_ip}" if _internal_ip and _internal_ip.strip() else f"https://{settings.OAUTH_MPT_SERVER_BASEURL}"
        
        try:
            # Add a timeout! A hanging external API shouldn't crash the login process.
            response = requests.get(f"{_url}/api/v1/account/me/", headers=headers, verify=SSL_VERIFY, timeout=5)
            response.raise_for_status() # Raises an error for bad HTTP responses (4xx, 5xx)
            api = response.json()
        except (requests.RequestException, ValueError) as e:
            if settings.DEBUG: 
                print(f"logged_in_handle API error: {e}")
            api = None

        if api:
            profile_url = api.get('profile_url')
            
            # Fetch image safely with its own timeout
            if profile_url:
                try:
                    img_resp = requests.get(profile_url, timeout=5)
                    if img_resp.status_code == 200:
                        user_data['image'] = ImageFile(BytesIO(img_resp.content), name=f"{user.username}.png")
                except requests.RequestException as e:
                    if settings.DEBUG: 
                        print(f"logged_in_handle image fetch error: {e}")

            # Update role/permission defaults
            user_data['role'] = api.get('role', [])
            user_data['permission'] = api.get('permission', [])
            
            # Update and save the core User model efficiently
            user.is_staff = api.get('is_staff', False)
            user.is_superuser = api.get('is_superuser', False)
            user.save(update_fields=['is_staff', 'is_superuser'])

    # 3. Create or Update the Account model
    account, created = Account.objects.get_or_create(user=user, defaults=user_data)
    
    if not created:
        # If updating, properly delete the old image using Django's Storage API
        if 'image' in user_data and user_data['image'] and account.image:
            account.image.storage.delete(account.image.name)
            
        # Update attributes cleanly (avoids the list comprehension side-effect anti-pattern)
        for k, v in user_data.items():
            setattr(account, k, v)
        account.save()

user_logged_in.connect(logged_in_handle)