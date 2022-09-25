from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from reviews.models import Category, Comment, Genre, Review, Title

User = get_user_model()


class SerializerUtilityMethods():
    """Класс для повторяющихся функций"""
    def validate_username(username):
        """Проверяет корректность поля username"""

        if username == 'me':
            raise serializers.ValidationError(
                "Username me использовать не разрешено"
            )
        if len(username) < 3:
            raise serializers.ValidationError(
                "Username не должно быть короче 3х символов"
            )
        return username


class TokenWithoutPasswordSerializer(TokenObtainPairSerializer):
    """
    Сериализатор нужен, чтобы выдавать пользователю токен
    по паре логин / confirmation_code
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['confirmation_code'] = serializers.CharField()
        self.fields['password'].required = False

    def validate(self, attrs):
        # заполнение пробелом нужно, чтобы не было ошибки, т.к. проверяется,
        # что поле пароль хоть чем-то заполнено
        attrs.update({'password': ''})
        if attrs['confirmation_code'] == '':
            raise serializers.ValidationError('Введите код подтверждения')
        auth_user = get_object_or_404(
            User,
            username=self.initial_data['username']
        )
        if not auth_user:
            raise serializers.ValidationError('Введены неверные данные')
        # проверяем, правильный ли указан confirmation_code
        if auth_user.confirmation_code != attrs['confirmation_code']:
            raise serializers.ValidationError('Введены неверные данные')
        return super().validate(attrs)


class UserRegisterSerializer(serializers.ModelSerializer):
    """Serializer для регистрации нового пользователя
    Используется только в /sign-up/
    """
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    class Meta:
        model = User
        fields = (
            'username', 'email',
        )
        required_fields = ('username', 'email')

    def validate_username(self, value):
        return SerializerUtilityMethods.validate_username(value)


class UserMainSerializer(serializers.ModelSerializer):
    """Serializer для просмотра, создания и изменения пользователя
    Используется только админом для url /users/
    """
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name',
            'last_name', 'bio', 'role',
        )
        required_fields = ('username', 'email')

    def validate_username(self, value):
        return SerializerUtilityMethods.validate_username(value)


class OwnProfileSerializer(serializers.ModelSerializer):
    """Serializer для просмотра и изменения собственной учетной записи."""

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role',
        )
        read_only_fields = ('username', 'email', 'role', )


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для категории"""

    class Meta:
        model = Category
        fields = ("name", "slug",)


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для жанров."""

    class Meta:
        model = Genre
        fields = ("name", "slug",)


class TitleBaseSerializer(serializers.ModelSerializer):
    """Сериализатор произведений для чтения."""

    genre = GenreSerializer(read_only=True, many=True)
    category = CategorySerializer(read_only=True)
    rating = serializers.IntegerField(required=False,
                                      read_only=True)

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'rating', 'description', 'genre',
                  'category')
        read_only_fields = ['rating']


class TitlePostSerializer(serializers.ModelSerializer):
    """Сериализатор произведений для записи."""

    genre = serializers.SlugRelatedField(many=True, slug_field='slug',
                                         queryset=Genre.objects.all())
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description', 'genre', 'category')

    def validate_year(self, value):
        """Валидация года выпуска произведения"""

        year = timezone.now().year
        if 0 < value > year:
            raise serializers.ValidationError('Неправильный год!')
        return value


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор отзывов."""

    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        model = Review
        fields = ('id', 'author', 'title', 'text', 'score', 'pub_date')
        read_only_fields = ('author', 'title')
        required_fields = ('title', 'text', 'score')


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор комментариев."""

    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        model = Comment
        fields = ('id', 'author', 'review', 'text', 'pub_date')
        read_only_fields = ('author', 'review')
        required_fields = ('text', )
