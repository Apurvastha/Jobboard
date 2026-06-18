from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from django.core.cache import cache
from drf_spectacular.extensions import OpenApiAuthenticationExtension


class RedisRevokedJWTAuthentication(JWTAuthentication):
    """
    Extends JWTauth to check Redis for revoked access token.
    Adds ~0.1ms per person request(Redis in-memory lookup)
    """

    def get_validated_token(self, raw_token):
        # first validate signature mathematically
        token = super().get_validated_token(raw_token)

        # then check the Redis revocation store (fast, in-memory)
        jti = token['jti']
        if cache.get(f'revoked_token:{jti}'):
            raise InvalidToken('Token has been revoked. Please log in again.')
        return token

class RedisRevokedJWTAuthenticationScheme(OpenApiAuthenticationExtension):
    """
    Tells drf-spectacular that RedisRevokedJWTAuthentication
    uses Bearer JWT — same as standard JWTAuthentication.
    Without this, Swagger UI has no Authorize button.
    """
    target_class = 'accounts.authentication.RedisRevokedJWTAuthentication'
    name = 'bearerAuth'

    def get_security_definition(self, auto_schema):
        return {
            'type': 'http',
            'scheme': 'bearer',
            'bearerFormat': 'JWT',
        }