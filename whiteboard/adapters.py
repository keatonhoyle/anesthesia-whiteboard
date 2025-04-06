from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        # Automatically connect the social account to an existing user or create a new user
        sociallogin.connect(request, sociallogin.user)