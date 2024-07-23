from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name = 'home'),
    path('sobre', views.sobre, name = 'sobre'),
    path('perfil/', views.perfil, name = 'perfil'),
    path('localidades/', views.lugares, name='localidades'),
    path('indicacoes/', views.indicacoes, name='indicacoes'),
    path('<str:localizacao>/destinos/', views.destinos, name='destinos'),
    path('sucesso/', views.sucesso, name='sucesso'),
    path('login_init/', views.index_login, name='login_index'), 
    path('anfitriao/', views.anfitriao_page, name='anfitriao'),
    path('suas_reservas/', views.suas_reservas, name='suas_reservas'),
    path('salvar_casa/', views.salvar_casa, name='salvar_casa'),
    path('salvar_apartamento/', views.salvar_apartamento, name='salvar_apartamento'),
    path('salvar_casa_quarto/', views.salvar_casa_quarto, name='salvar_casa_quarto'),
    path('salvar_hotel/', views.salvar_hotel, name='salvar_hotel'),
    path('salvar_pousada/', views.salvar_pousada, name='salvar_pousada'),
    path('salvar_config_quarto/<int:id_propriedade>/', views.salvar_config_quarto, name='salvar_config_quarto'),
    path('reserva/<str:tipo_propriedade>/<int:id_propriedade>/', views.reserva, name="reserva"),
    path('excluir_reserva/<int:reserva_id>/', views.excluir_reserva, name='excluir_reserva'),
    path('atualizar_propriedade/<str:tipo_propriedade>/<int:id_propriedade>/', views.atualizar_propriedade, name='atualizar_propriedade'),
    path('excluir_propriedade/<str:tipo_propriedade>/<int:id_propriedade>/', views.excluir_propriedade, name='excluir_propriedade'),
    path('reset_password/', auth_views.PasswordResetView.as_view(), name='reset_password'),
    path('reset_password/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('excluir_quarto/<int:id_quarto>/', views.excluir_quarto, name='excluir_quarto'),
    path('atualizar_quarto/<int:id_propriedade>/<int:id_quarto>/', views.atualizar_quarto, name='atualizar_quarto'),
    path('blog_hospeda/', views.blog_page, name='blog'),
    path('blog_hospeda/atualizar/<int:id_post>/', views.atualizar_post, name='atualizar_post'),
    path('blog_hospeda/excluir/<int:id_post>/', views.excluir_post, name='excluir_post'),
    path('blog_hospeda/post/<int:id_post>/', views.post, name='post'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)