from django.urls import path, include

from rest_framework.routers import DefaultRouter

from .views import UserProfileViewSet, complete_registration

router = DefaultRouter()
router.register('users', UserProfileViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('registration/', complete_registration, name='verification-url'),
]
