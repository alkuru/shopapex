from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import web_views

router = DefaultRouter()
router.register(r'profiles', views.UserProfileViewSet)
router.register(r'actions', views.UserActionViewSet)
router.register(r'favorites', views.UserFavoriteViewSet)
router.register(r'sessions', views.UserSessionViewSet)

app_name = 'accounts'

urlpatterns = [
    # Web URLs
    path('login/', web_views.login_page, name='login_page'),
    path('register/', web_views.register_page, name='register_page'),
    path('logout/', web_views.logout_page, name='logout_page'),
    path('profile/', web_views.profile_page, name='profile_page'),
    path('garage/', web_views.garage_page, name='garage_page'),
    path('garage/add/', web_views.add_vehicle_to_garage, name='add_vehicle_to_garage'),
    path('garage/remove/<int:vehicle_id>/', web_views.remove_vehicle_from_garage, name='remove_vehicle_from_garage'),

    # API URLs
    path('api/', include(router.urls)),

    # Auth URLs
    path('api/register/', views.register, name='register'),
    path('api/login/', views.login_view, name='login'),
    path('api/logout/', views.logout_view, name='logout'),
    path('api/change-password/', views.change_password, name='change_password'),
]
