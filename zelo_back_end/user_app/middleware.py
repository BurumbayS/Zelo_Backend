from channels.db import database_sync_to_async
from urllib import parse
from django.contrib.auth.models import AnonymousUser
from rest_framework.authtoken.models import Token
from rest_framework_jwt.serializers import VerifyJSONWebTokenSerializer

@database_sync_to_async
def get_user(token):

    serializer = VerifyJSONWebTokenSerializer({'token': token})
    validated_data = serializer.validate({'token': token})
    user = validated_data['user']

    return user

class JWTAuthMiddleware:
    """
    Custom middleware (insecure) that takes user IDs from the query string.
    """

    def __init__(self, inner):
        # Store the ASGI application we were passed
        self.inner = inner

    def __call__(self, scope):
        return QueryAuthMiddlewareInstance(scope, self)

class QueryAuthMiddlewareInstance:
    """
    Inner class that is instantiated once per scope.
    """

    def __init__(self, scope, middleware):
        self.middleware = middleware
        self.scope = dict(scope)
        self.inner = self.middleware.inner

    async def __call__(self, receive, send):
        # Look up user from query string (you should also do things like
        # checking if it is a valid user ID, or if scope["user"] is already
        # populated).
        query_string = dict(parse.parse_qsl(self.scope['query_string'].decode('utf-8')))
        token = query_string['token']

        self.scope['user'] = await get_user(token)

        # Instantiate our inner application
        inner = self.inner(self.scope)

        return await inner(receive, send)
