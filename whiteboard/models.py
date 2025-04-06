from allauth.socialaccount.models import SocialAccount
from django.db import models

class CustomSocialAccount(SocialAccount):
    class Meta:
        proxy = True

    def __str__(self):
        return str(self.user.username) + " (" + str(self.provider) + ")"