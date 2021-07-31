from . import serializers as user_serializers
from utils import viewset, http_code

from utils.services import user as user_services, email as email_services

from rest_framework import permissions, decorators, exceptions

from django.urls import reverse
from .models import User

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


class AuthViewSet(viewset.BaseView):
    permission_classes = [permissions.AllowAny, ]
    serializer_classes = {
        'register': user_serializers.RegisterSerializer,
        'active': user_serializers.ActiveSerializer,
        'login': user_serializers.LoginSerializer,
        'change_password': user_serializers.ChangePasswordSerializer,
        'forgot_password': user_serializers.ForgotPasswordSerializer,
        'reset_password': user_serializers.ResetPasswordSerializer,
    }

    @decorators.action(methods=['GET'], url_path='list', detail=False)
    def list_user(self, request):
        try:
            users = User.objects.all()
            data = user_serializers.UserSerializer(users, many=True).data
            return self.get_response(
                data = data, 
                error_code=http_code.HttpSuccess
            )
        except:
            return self.get_response(
                data = None, 
                error_code=500
            )

    @decorators.action(methods=['GET', ], detail=False)
    def infor(self, request):
        try:
            user = request.user
            return self.get_response(
                data = {
                    'name': user.name,
                    'is_admin': user.is_admin,
                    'uid': user.uid
                }, 
                error_code=http_code.HttpSuccess
            )
        except:
            return self.get_response(
                data = None, 
                error_code=500
            )

    @decorators.action(methods=['POST', ], detail=False)
    def register(self, request):
        """
            A api to register a new user on the system

            :param request: email & password

            @do:
                -> Check valid email and password, If error, return response with status code 400 (error.status_code)
                -> Create new user on the system, and send an email to active account
                -> Return None, with error code is 0.
        """
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            user = user_services.create_user_account(**serializer.validated_data)
            try:
                from django.contrib.sites.shortcuts import get_current_site

                email_services.active_email_sender(domain=get_current_site(request),email=user.email)
            except Exception as e:
                print(e)
                raise e

            return self.get_response(
                data=None,
                error_code=http_code.HttpSuccess
            )
        except exceptions.ValidationError as e:
            return self.get_response(data=e.detail, error_code=e.status_code)

    @decorators.action(methods=['GET', ], detail=False)
    def active(self, request):
        serializer = self.get_serializer(data=request.GET)
        try:
            serializer.is_valid(raise_exception=True)
            is_active = user_services.active_user_account(serializer.validated_data['token'])
            if is_active:
                return self.get_response(data=None, error_code=http_code.HttpSuccess)
            return self.get_response(data={'User':['Cannot active account']}, error_code=http_code.HttpSomethingWentWrong)
        except exceptions.ValidationError as e:
            return self.get_response(
                data=e.detail,
                error_code=e.status_code
            )

    @decorators.action(methods=['POST', ], detail=False)
    def login(self, request):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            user = user_services.get_and_authenticate_user(**serializer.validated_data)
            data = user_serializers.AuthSerializer(user).data
            return self.get_response(
                data = data,
                error_code=http_code.HttpSuccess
            )
        except exceptions.ValidationError as e:
            return self.get_response(
                data = e.detail,
                error_code=e.status_code
            )

    @decorators.action(methods=['GET', ],detail=False, permission_classes=[permissions.IsAuthenticated, ])
    def logout(self, request):
        data, is_complete = user_services.logout_user_account(request.GET)
        if is_complete:
            print("yes")
            return self.get_response(data=None, error_code=http_code.HttpSuccess)
        return self.get_response(data=data, error_code=http_code.HttpSomethingWentWrong)

    @decorators.action(methods=['POST', ], detail=False, permission_classes=[permissions.IsAuthenticated, ])
    def change_password(self, request):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            user = user_services.get_and_authenticate_user(email=request.user.email, password= serializer.validated_data['current_password'])
            user_services.change_user_password(user, serializer.validated_data['new_password'])
            return self.get_response(data=None, error_code=http_code.HttpSuccess)
        except exceptions.ValidationError as e:
            return self.get_response(
                data = e.detail,
                error_code=e.status_code
            )

    @decorators.action(methods=['GET', ], detail=False)
    def forgot_password(self, request):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            from django.contrib.sites.shortcuts import get_current_site

            email_services.forgot_password_email_sender(domain=get_current_site(request), **serializer.validated_data)
            return self.get_response(data=None, error_code=http_code.HttpSuccess)
        except exceptions.ValidationError as e:
            return self.get_response(
                data = e.detail,
                error_code=e.status_code
            )

    @decorators.action(methods=['POST', ], detail=False)
    def reset_password(self, request):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            user_services.reset_user_password(**serializer.validated_data)
            return self.get_response(data=None, error_code=http_code.HttpSuccess)
        except exceptions.ValidationError as e:
            return self.get_response(
                data = e.detail,
                error_code=e.status_code
            )