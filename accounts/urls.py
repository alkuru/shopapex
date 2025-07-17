from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'profiles', views.UserProfileViewSet)
router.register(r'actions', views.UserActionViewSet)
router.register(r'favorites', views.UserFavoriteViewSet)
router.register(r'sessions', views.UserSessionViewSet)

app_name = 'accounts'

urlpatterns = [
    # API URLs
    path('api/', include(router.urls)),
    
    # Auth URLs
    path('api/register/', views.register, name='register'),
    path('api/login/', views.login_view, name='login'),
    path('api/logout/', views.logout_view, name='logout'),
    path('api/change-password/', views.change_password, name='change_password'),
]
