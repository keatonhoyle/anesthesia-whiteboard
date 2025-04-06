from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth.models import User
import random

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        # Automatically connect the social account to an existing user or create a new user
        sociallogin.connect(request, sociallogin.user)

    def populate_user(self, request, sociallogin, data):
        user = super().populate_user(request, sociallogin, data)
        # Ensure the username is unique
        base_username = data.get('username') or data.get('email').split('@')[0]
        username = base_username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1
        user.username = username
        return user