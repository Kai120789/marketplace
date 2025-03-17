# middleware.py

from django.utils.deprecation import MiddlewareMixin
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError
from django.http import JsonResponse
from django.shortcuts import redirect

class TokenExpirationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        access_token = request.COOKIES.get("access_token")

        if access_token:
            try:
                token = AccessToken(access_token)
            except TokenError:
                response = redirect("/shop/login/")
                response.delete_cookie("access_token")
                response.delete_cookie("refresh_token")
                return response

        return None