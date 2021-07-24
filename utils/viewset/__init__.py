from rest_framework import viewsets

from django import http

from utils.serializers import EmptySerializer

class BaseView(viewsets.GenericViewSet):
    serializer_class = EmptySerializer

    def get_serializer_class(self):
        from django.core.exceptions import ImproperlyConfigured

        if not isinstance(self.serializer_classes, dict):
            raise ImproperlyConfigured("serializer_classes should be a dict mapping")

        if self.action in self.serializer_classes.keys():
            return self.serializer_classes[self.action]
        return super().get_serializer_class()

    def get_response(self, data, error_code):
        return http.JsonResponse(
            data={
                'data': data,
                'error_code': error_code
            }
        )

