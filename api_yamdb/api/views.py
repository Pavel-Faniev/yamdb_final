import uuid


from django.contrib.auth import get_user_model
from django.core.mail import EmailMessage
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, status, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenViewBase
from reviews.models import Category, Comment, Genre, Review, Title

from api_yamdb.settings import FROM_EMAIL

from .filters import TitleFilter
from .permissions import (IsAdminOrReadOnly, IsAdminOrSuperUser,
                          IsAuthorOrAdminOrModeratorOrReadOnly)
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, OwnProfileSerializer,
                          ReviewSerializer, TitleBaseSerializer,
                          TitlePostSerializer, TokenWithoutPasswordSerializer,
                          UserMainSerializer, UserRegisterSerializer)

User = get_user_model()


class ViewsUtilityMethods():
    """Повторяющиеся / служебные методы"""

    def generate_confirmation_code():
        """генерирует случайный код подтверждения"""

        # генерирует случайный ключ UUID
        confirmation_code = uuid.uuid4()
        return confirmation_code

    def confirmation_code_send(confirmation_code: str, to_email: str):
        """Отправляет код подтверждения на почту"""

        email = EmailMessage(
            'Ваш ключ подтверждения',
            (f'Для вас был сгенерирован ключ подтверждения'
             f' {confirmation_code}'),
            FROM_EMAIL,
            [to_email]
        )
        email.send()


class UpdateRetrieveViewSet(mixins.UpdateModelMixin, mixins.RetrieveModelMixin,
                            viewsets.GenericViewSet):
    """Базовый класс для Viewset.
    Позволяет обновлять объект и просматривать объект"""
    pass


class CreateViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """Базовый класс для Viewset.
    Позволяет Создавать новый объект"""
    pass


class MyProfileViewSet(UpdateRetrieveViewSet):
    """
    Viewset for User Model, "own account" only.
    Используется для url /users/me/
    """
    serializer_class = OwnProfileSerializer
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()

    def get_object(self):
        return self.request.user


class UserViewSet(viewsets.ModelViewSet):
    """
    Viewset for User Model.
    Используется для url /users/
    """
    queryset = User.objects.all()
    serializer_class = UserMainSerializer
    permission_classes = [IsAdminOrSuperUser]
    pagination_class = PageNumberPagination
    lookup_field = 'username'

    def perform_create(self, serializer, *args, **kwargs):
        """
        Create new User.
        """
        serializer.save(
            confirmation_code=ViewsUtilityMethods.generate_confirmation_code()
        )


class RegistrationViewSet(CreateViewSet):
    """Viewset используется для страницы Sign-up."""

    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer, *args, **kwargs):
        """
        Create new User. Здесь мы генерируем новый Confirmation Code,
        записываем в юзера и высылаем его на почту.
        """
        # Генерируем confirmation_code
        confirmation_code = ViewsUtilityMethods.generate_confirmation_code()
        # Отправляем Confirmation code
        ViewsUtilityMethods.confirmation_code_send(
            confirmation_code,
            serializer.validated_data['email']
        )
        # Сохраняем confirmation code
        serializer.save(
            confirmation_code=confirmation_code
        )

    def create(self, request, *args, **kwargs):
        """
        По факту, пришлось сделать этот кусок только для того,
        чтобы выдавать 200 ошибку, а не 201, как это делает
        стандартный код при создании записи
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
            headers=headers
        )


class TokenObtainPairWithoutPassword(TokenViewBase):
    """View для получения токена без пароля"""

    serializer_class = TokenWithoutPasswordSerializer


class CreateListDeleteViewSet(mixins.CreateModelMixin,
                              mixins.ListModelMixin,
                              mixins.DestroyModelMixin,
                              viewsets.GenericViewSet):
    pass


class GenreViewSet(CreateListDeleteViewSet):
    """Viewset для работы с жанрами произведений."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class CategoryViewSet(CreateListDeleteViewSet):
    """Viewset для работы с категориями произведений."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    """Viewset для работы с произведениями."""

    queryset = Title.objects.annotate(rating=Avg('reviews__score'))
    serializer_class = TitlePostSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = TitleFilter
    pagination_class = PageNumberPagination
    permission_classes = (IsAdminOrReadOnly,)

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return TitlePostSerializer
        return TitleBaseSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """Viewset для работы с отзывами на произведения."""

    permission_classes = [IsAuthorOrAdminOrModeratorOrReadOnly]
    serializer_class = ReviewSerializer

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        return Review.objects.filter(title_id=title_id)

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            title=get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # сначала проверяем, что этот автор еще
        # не оставлял отзыв о данном произведении
        # если такое было, то выдаем ошибку
        author = self.request.user,
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        existing_review = Review.objects.filter(
            author=author[0],
            title=title.pk,
        )
        if existing_review:
            return Response(data={'message': 'Вы уже оставили отзыв'},
                            status=status.HTTP_400_BAD_REQUEST)
        # дальше все происходит только тогда, когда
        # мы уже убедились, что автор другого отзыва на это
        # произведение не оставлял
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )


class CommentViewSet(viewsets.ModelViewSet):
    """Viewset для работы с комментариями к произведениям."""

    permission_classes = [IsAuthorOrAdminOrModeratorOrReadOnly]
    serializer_class = CommentSerializer

    def get_queryset(self):
        review_id = self.kwargs.get('review_id')
        return Comment.objects.filter(review_id=review_id)

    def perform_create(self, serializer):
        serializer.is_valid(raise_exception=True)
        # если выше ошибка, дальше не пойдет
        serializer.save(
            author=self.request.user,
            review=get_object_or_404(
                Review,
                pk=self.kwargs.get('review_id'))
        )
