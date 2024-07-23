from __future__ import absolute_import, unicode_literals
from celery import shared_task
from django.shortcuts import redirect
from django.contrib.auth import login, authenticate, logout, get_user_model
from .models import CustomUser
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from project import settings

@shared_task
def register_user_task(user_data):
    User = get_user_model()
    user = User.objects.create_user(
        email=user_data.get('email'),
        password=user_data.get('password1'),
        nome=user_data.get('nome'),
        sobrenome=user_data.get('sobrenome'),
        telefone=user_data.get('telefone'),
        data_nascimento=user_data.get('data_nascimento'),
        cpf=user_data.get('cpf'),
        cnpj=user_data.get('cnpj'),
        rua=user_data.get('rua'),
        numero=user_data.get('numero'),
        complemento=user_data.get('complemento'),
        cep=user_data.get('cep'),
        cidade=user_data.get('cidade'),
        uf=user_data.get('uf'),
        is_active=True,
        is_staff=False,
        is_anfitriao=False,
        # Adicione outros campos conforme necessário
    )
    send_confirmation_email(user_data.get('email'))
    
    return {'email': user_data.get('email'), 'password': user_data.get('password1')}


@shared_task
def register_anfitriao_task(anfitriao_data):
    User = get_user_model()
    anfitriao = User.objects.create_user(
        email=anfitriao_data.get('email'),
        password=anfitriao_data.get('password1'),
        nome=anfitriao_data.get('nome'),
        sobrenome=anfitriao_data.get('sobrenome'),
        telefone=anfitriao_data.get('telefone'),
        data_nascimento=anfitriao_data.get('data_nascimento'),
        cpf=anfitriao_data.get('cpf'),
        cnpj=anfitriao_data.get('cnpj'),
        rua=anfitriao_data.get('rua'),
        numero=anfitriao_data.get('numero'),
        complemento=anfitriao_data.get('complemento'),
        cep=anfitriao_data.get('cep'),
        cidade=anfitriao_data.get('cidade'),
        uf=anfitriao_data.get('uf'),
        is_active=True,
        is_staff=False,
        is_anfitriao=True,  # Defina como True para indicar que é um anfitrião
        # Adicione outros campos conforme necessário
    )
    send_confirmation_email(anfitriao_data.get('email'))
    # Retorne informações relevantes para autenticação
    return {'email': anfitriao_data.get('email'), 'password': anfitriao_data.get('password1')}

def send_confirmation_email(email):
    subject = 'Confirmação de Cadastro - Hospeda Recife'
    message = 'Olá! Agradecemos por se cadastrar na Hospeda Recife!'
    from_email = 'mailtrap@hospedarecife.com'  # Substitua pelo seu endereço de e-mail
    if settings.EMAIL_HOST == 'sandbox.smtp.mailtrap.io':
        from_email = 'projetos@proglogic.com.br'
    recipient_list = [email]


    # Enviar o e-mail
    send_mail(subject, message, from_email, recipient_list)