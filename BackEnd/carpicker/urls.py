from django.urls import path
from . import views_auth

urlpatterns = [
    path('register/', views_auth.register),
    path('login/', views_auth.login_view),
    path('logout/', views_auth.logout_view),
]