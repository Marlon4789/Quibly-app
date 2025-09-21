from django.urls import path, include # type: ignore
from .views import profile_login, home_login, exit, register, login_view
from login.views import CustomPasswordResetView, CustomPasswordResetDoneView, CustomPasswordResetConfirmView, CustomPasswordResetCompleteView
from login.views import delete_account, account_deleted

urlpatterns = [
     path('home_login', home_login, name='home_login'),
     path('profile/', profile_login, name='profile'),
     path('logout/', exit, name='exit'),
     path('register/', register, name='register'),
     path('login/', login_view, name='login'),

     # URLs de autenticación de Django
    path('accounts/', include('django.contrib.auth.urls')),

    # Resetear contraseña
    path('password_reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),

    # eliminar cuenta
    path('delete_account/', delete_account, name='delete_account'),
    path('account_deleted/', account_deleted, name='account_deleted'),  
]
