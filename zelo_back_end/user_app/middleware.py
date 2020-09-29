from urllib import parse

from django.db import close_old_connections
from django.core.exceptions import ValidationError

from rest_framework_jwt.serializers import VerifyJSONWebTokenSerializer


class JWTAuthMiddleware:
    """
    Custom middleware that takes JWT token from the query string.
    """
    def __init__(self, inner):
        # Store the ASGI application we were passed
        self.inner = inner

    def __call__(self, scope):

        # Close old database connections to prevent usage of timed out connections
        close_old_connections()

        # Look up user from query string (you should also do things like
        # checking if it is a valid user ID, or if scope["user"] is already
        # populated).
        query_string = dict(parse.parse_qsl(scope['query_string'].decode('utf-8')))
        if 'token' not in query_string:
            raise ValidationError('Token required')
        serializer = VerifyJSONWebTokenSerializer({'token': query_string['token']})
        validated_data = serializer.validate({'token': query_string['token']})
        user = validated_data['user']

        # Return the inner application directly and let it run everything else
        return self.inner(dict(scope, user=user))
