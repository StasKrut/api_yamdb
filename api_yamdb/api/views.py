import random
import string

from rest_framework import viewsets, filters, status
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.tokens import default_token_generator
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from django.db import IntegrityError
from django.contrib.auth.hashers import make_password
from django.core.mail import EmailMessage

from review.models import User, Review
# Title
from .serializers import (
    MyTokenObtainPairSerializer,
    SendEmailSerializer,
    UsersSerializer,
    ReviewSerializer,
)
from .permissions import (
    IsAdminOrReadOnly,
    IsOwner,
    IsAuthorOrReadOnly
)


def generate_code():
    code_letters = string.ascii_uppercase
    code = ''.join(random.choice(code_letters) for i in range(9))
    return code


class SendEmailViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = SendEmailSerializer

    def perform_create(self, serializer):

        try:
            user = User.objects.create_user(
                email=self.request.data.get('email'),
                username=self.request.data.get('email').partition("@")[0],
            )
        except IntegrityError:
            User.objects.get(email=self.request.data.get('email')).delete()
            user = User.objects.create_user(
                email=self.request.data.get('email'),
                username=self.request.data.get('email').partition("@")[0],
            )
        confirmation_code = default_token_generator.make_token(user)
        user_email = user.email
        user.confirmation_code = confirmation_code
        user.password = make_password(confirmation_code)
        user.save()
        email = EmailMessage('Yamdb проверочный код: ', confirmation_code,
                             to=[user_email, ])
        email.send()


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UsersSerializer
    permission_classes = (IsAdminOrReadOnly, IsAuthenticated, IsOwner)
    filter_backends = [filters.SearchFilter]
    search_fields = ('username',)
    lookup_field = 'username'

    def perform_create(self, serializer):
        serializer.save()

    def get_queryset(self):
        user = self.request.user
        allow_all = user.is_superuser or user.is_staff
        if self.action == 'list' and not allow_all:
            raise PermissionDenied('ERROR: Access denied')
        return User.objects.all()

    @action(detail=False, methods=['GET', 'PATCH'], url_path='me',
            permission_classes=(IsOwner, IsAuthenticated,))
    def get_or_update_user(self, request):
        himself = User.objects.get(username=self.request.user)
        if request.method == 'GET':
            serializer = self.get_serializer(himself)
            return Response(serializer.data)
        if request.method == 'PATCH':
            serializer = self.get_serializer(himself, data=request.data,
                                             partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)


class ReviewViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthorOrReadOnly,)
    serializer_class = ReviewSerializer


def get_queryset(self):
    title_id = self.kwargs.get('title_id')
    new_queryset = Review.objects.filter(title=title_id)
    return new_queryset


"""
def perform_create(self, serializer):
    author = self.request.user
    text = self.request.data.get('text')
    title_id = self.kwargs.get('title_id')
    title = get_object_or_404(Title, id=title_id)
    reviews = Review.objects.filter(author=author, title=title)
    if reviews.count() > 0:
        # return True
    serializer.save(title=title, author=author, text=text)
"""


def create(self, request, *args, **kwargs):
    serializer = self.get_serializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    not_create_success = self.perform_create(serializer)
    headers = self.get_success_headers(serializer.data)

    if not_create_success:
        return Response(
            serializer.data,
            status=status.HTTP_400_BAD_REQUEST,
            headers=headers
        )
    else:
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )
