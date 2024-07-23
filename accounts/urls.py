from django.urls import path
from .views import register, user_login, user_logout, register_anfitriao, login_anfitriao  # Certifique-se de incluir user_logout aqui

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),  # Use user_logout ao invés de views.user_logout
    path('register_anfitriao/', register_anfitriao, name='register_anfitriao'),
    path('login_anfitriao/', login_anfitriao, name='login_anfitriao')
]
