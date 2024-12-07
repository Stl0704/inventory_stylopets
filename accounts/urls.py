from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('registro/', views.registro, name='registro'),
    path('login/', views.inicio_sesion, name='inicio_sesion'),
    path('logout/', views.cerrar_sesion, name='cerrar_sesion'),
    path('index/', views.index, name='index'),
    path('password_reset/', views.RecuperacionPasswordView.as_view(),name='password_reset'),
    # Agrega las rutas para confirmación y finalización del password reset
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='accounts/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='accounts/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='accounts/password_reset_complete.html'), name='password_reset_complete'),
]
