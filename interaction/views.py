from rest_framework import permissions, decorators, exceptions, generics, filters
from . import serializer, models, filter as interaction_filter

# Create your views here.

class GetInteractionOfProduct(generics.ListAPIView):
    queryset = models.Interaction.objects.all()
    permission_classes = (permissions.AllowAny, )
    serializer_class = serializer.InteractionSerializer
    filter_backends = [filters.SearchFilter, interaction_filter.InteractionFilter]
    search_fields = ['uid']

    def list(self, request):
        from django.http import JsonResponse
        try: 
            data = super().list(request).data

            return JsonResponse({
                'data': data,
                'error_code': 0
            })
        except Exception as e:
            print(f"Exception while filtering: {e}")
        return JsonResponse({
            'data': None,
            'error_code': 0
        })

# class InteractionProduct(generics.)