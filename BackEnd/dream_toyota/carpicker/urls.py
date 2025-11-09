# carpicker/urls.py
from django.urls import path
# from . import views_auth  # import your authentication views
from . import views       # (optional) import your car-matching views if you have them

urlpatterns = [
    # 🔐 Authentication endpoints
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # 🚘 (optional) Car recommendation endpoint
    # e.g. POST /api/get_car/
    # path('get_car/', views.get_car, name='get_car'),
]
