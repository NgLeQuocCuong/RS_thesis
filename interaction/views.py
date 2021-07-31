from rest_framework import permissions, decorators, exceptions, generics, filters
from . import serializer, models, filter as interaction_filter

# Create your views here.

def paginate_data(request, data):
    '''
    Function to handle pagination data.

    Params:

    data: array data.

    request: request object that contain paginate info

    page: page to show (Default is 1).

    page_size: Defaults is 10 (PAGE_SIZE=10).

    Return a JSON data:

    response_data = {
        "totalRows": total,
        "totalPages": total_pages,
        "currentPage": page_number,
        "content": content
    }
    '''

    page = int(request.data.get('page', 1))
    page_size = int(request.data.get('page_size', PAGE_SIZE))

    # Handle page_size = 'all'
    # page_size = 0 for get all
    if page_size == 0:
        page_size = len(data) + 1
    elif page_size < 0:
        raise ValueError(messages.NEGATIVE_PAGE_SIZE)
    elif page_size > PAGE_SIZE_MAX:
        raise ValueError(messages.OVER_PAGE_SIZE_MAX + PAGE_SIZE_MAX)

    paginator = Paginator(data, page_size)

    total_pages = paginator.num_pages

    if int(total_pages) < page:
        page_number = page
        content = []
    else:
        current_page = paginator.page(page)
        page_number = current_page.number
        content = current_page.object_list

    total = paginator.count

    response_data = {
        "totalRows": total,
        "totalPages": total_pages,
        "currentPage": page_number,
        "content": content,
        "pageSize": page_size
    }

    return response_data


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
                'data': paginate_data(request, data),
                'error_code': 0
            })
        except Exception as e:
            print(f"Exception while filtering: {e}")
        return JsonResponse({
            'data': None,
            'error_code': 0
        })

    @decorators.action(methods=['GET'], detail=False, url_path='get')
    def get_rate_of_user(self, request):
        user = request.user
        book = request.GET.get('uid', None)
        try:
            interaction = models.Interaction.objects.get(user=user, book__uid=book)
            return JsonResponse({
                'data': serializer.InteractionSerializer(interaction),
                'error_code': 0
            })
        except: 
            return JsonResponse({
                'data': None,
                'error_code': 500
            })

    @decorators.action(methods=['POST'], detail=False, url_path='rate')
    def get_rate_of_user(self, request):
        user = request.user
        book = request.POST.get('uid', None)
        rate = request.POST.get('rate', None)
        content = request.POST.get('content', '')
        header = request.POST.get('header', '')

        try:
            interaction = models.Interaction.objects.get(user=user, book__uid=book)
            interaction.rate = rate
            interaction.content = content
            interaction.header = header
            interaction.save() 
            return JsonResponse({
                'data': serializer.InteractionSerializer(interaction),
                'error_code': 0
            })
        except: 
            return JsonResponse({
                'data': None,
                'error_code': 500
            })