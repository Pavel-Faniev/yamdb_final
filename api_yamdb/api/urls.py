from django.urls import include, path
from rest_framework import routers

from .views import (CategoryViewSet, CommentViewSet, GenreViewSet,
                    MyProfileViewSet, RegistrationViewSet, ReviewViewSet,
                    TitleViewSet, TokenObtainPairWithoutPassword, UserViewSet)

app_name = 'api'
router = routers.DefaultRouter()

router.register('users', UserViewSet)
router.register('categories', CategoryViewSet, basename='categories')
router.register('genres', GenreViewSet, basename='genres')
router.register('titles', TitleViewSet, basename='titles')
router.register(r'titles/(?P<title_id>\d+)/reviews',
                ReviewViewSet, basename='reviews')
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet, basename='comments'
)

urlpatterns = [
    path(
        'users/me/',
        MyProfileViewSet.as_view({'get': 'retrieve', 'patch': 'update'}),
        name='own_account'
    ),
    path('', include(router.urls)),
    path(
        'auth/signup/',
        RegistrationViewSet.as_view({'post': 'create'}),
        name='signup'
    ),
    path(
        'auth/token/',
        TokenObtainPairWithoutPassword.as_view(),
        name='token_obtain_pair'
    ),
]
