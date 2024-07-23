from django.shortcuts import render, get_object_or_404, redirect
import json
from django.contrib.auth.decorators import login_required
from .forms import *
from .models import *
from accounts.models import CustomUser
from django.http import JsonResponse, HttpResponse
from datetime import datetime, timedelta, date
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.db.models import Count, Min
from django.db.models.signals import post_save, post_delete
from django.utils import timezone
from django.dispatch import receiver
from django.contrib import messages
from itertools import chain
from django.db import transaction
import re
import time
from django.core.mail import send_mail
from smtplib import SMTPAuthenticationError
import logging
from .tasks import enviar_emails_reserva, salvar_reserva, salvar_apartamento_task, salvar_casa_toda_task, salvar_casa_quarto_task, salvar_hotel_task, salvar_config_quarto_task, salvar_pousada_task


def index(request):
    parceiros = Parceiros.objects.filter(ativo=True)
    localidades = Localidades.objects.all()
    carrossel = [
        {'nome': 'Recife', 'imagem': 'https://c1.wallpaperflare.com/preview/476/1004/62/recife-ground-zero-pernambuco-marco.jpg'},
        {'nome': 'Olinda', 'imagem': 'https://img.freepik.com/fotos-premium/olinda-com-recife-ao-fundo-pernambuco-brasil_491130-1804.jpg'},
        {'nome': 'Tamandaré', 'imagem': 'https://t3.ftcdn.net/jpg/05/94/20/04/360_F_594200412_4FEAlobkbGtK0BC0vC2KAgQCVSS3Zz2J.jpg'},
        {'nome': 'Caruaru', 'imagem': 'https://s2-g1.glbimg.com/hO2RwCNTjS5lKElVIfMmSXF0h1A=/1200x/smart/filters:cover():strip_icc()/i.s3.glbimg.com/v1/AUTH_59edd422c0c84a879bd37670ae4f538a/internal_photos/bs/2021/y/t/SDykjeQI2Bv32dYWWKAg/indice.jpg'},
        {'nome': 'Gravatá', 'imagem': 'https://upload.wikimedia.org/wikipedia/commons/5/59/BRUNO_LIMA_IGREJA_MATRIZ_DE_SANTANA_GRAVAT%C3%81_PE.jpg'},
        {'nome': 'Garanhuns', 'imagem': 'https://viajeleve.net/v23/wp-content/uploads/2022/06/Relogio-das-Flores-Garanhuns-1170x780.jpg'}
    ]
    for cidade in carrossel:
        cidade['link'] = f"/{cidade['nome']}/destinos/" if cidade['nome'] in [localidade.localizacao for localidade in localidades] else '#'
    posts = Blog.objects.all()
    localidades_data = []
    min_prices = 0
    for localidade in localidades:
        min_price_apartamento = PropriedadeApartamento.objects.filter(cidade=localidade).aggregate(min_price=Min('valor_da_diaria'))['min_price'] or None
        min_price_casa_toda = PropriedadeCasaToda.objects.filter(cidade=localidade).aggregate(min_price=Min('valor_da_diaria'))['min_price'] or None
        min_price_casa_quarto = PropriedadeCasaQuarto.objects.filter(cidade=localidade).aggregate(min_price=Min('valor_da_diaria'))['min_price'] or None
        min_price_hotel = PropriedadeHotel.objects.filter(cidade=localidade).aggregate(min_price=Min('valor_da_diaria'))['min_price'] or None
        min_prices = [min_price_apartamento, min_price_casa_toda, min_price_casa_quarto, min_price_hotel]
        min_prices = [price for price in min_prices if price is not None]

        if not min_prices:
            min_price = 0
        else:
            min_price = min(min_prices)

        localidades_data.append({'localidade': localidade, 'min_price': min_price})


    propriedades_disponiveis = []
    if request.method == 'POST':
        checkin = request.POST.get('checkin')
        checkout = request.POST.get('checkout')
        adultos = int(request.POST.get('adultos'))
        criancas = int(request.POST.get('criancas'))
        permite_pet = request.POST.get('permite_pet')
        tipo_propriedad = request.POST.get('tipo_hospedagem')

        reservas_checkin = Reservas.objects.filter(data_inicio__gte=datetime.strptime(checkin, '%d/%m/%Y'))
        reservas_checkout = Reservas.objects.filter(data_fim__lte=datetime.strptime(checkout, '%d/%m/%Y'))
        
        for reserva in reservas_checkin:
            if reserva in reservas_checkout:
                propriedades_disponiveis.append(reserva.propriedade)
        if tipo_propriedad == 'apartamento':
            propriedades_disponiveis = [propriedade for propriedade in propriedades_disponiveis if propriedade.tipo_propriedade == 'apartamento']
        elif tipo_propriedad == 'casa':
            propriedades_disponiveis = [propriedade for propriedade in propriedades_disponiveis if propriedade.tipo_propriedade == 'casa']
        elif tipo_propriedad == 'quarto':
            propriedades_disponiveis = [propriedade for propriedade in propriedades_disponiveis if propriedade.tipo_propriedade == 'quarto']
        elif tipo_propriedad == 'hotel':
            propriedades_disponiveis = [propriedade for propriedade in propriedades_disponiveis if propriedade.tipo_propriedade == 'hotel']   
        elif tipo_propriedad == 'pousada':
            propriedades_disponiveis = [propriedade for propriedade in propriedades_disponiveis if propriedade.tipo_propriedade == 'pousada']
        if adultos > 0:
            propriedades_disponiveis = [propriedade for propriedade in propriedades_disponiveis if int(propriedade.qtd_hospedes) >= adultos]
        if criancas > 0:
            propriedades_disponiveis = [propriedade for propriedade in propriedades_disponiveis if propriedade.crianca_permissao == 'Sim']
        if permite_pet == 'Sim':
            propriedades_disponiveis = [propriedade for propriedade in propriedades_disponiveis if propriedade.aceita_pets == 'Sim']
        elif permite_pet == 'Não':
            propriedades_disponiveis = [propriedade for propriedade in propriedades_disponiveis if propriedade.aceita_pets == 'Não']

    return render(request, 'main/index.html', {'carrossel': carrossel, 'localidades': localidades, 'localidades_data': localidades_data, 'parceiros': parceiros, 'propriedades_disponiveis': propriedades_disponiveis, 'posts': posts})


def sobre(request):
    localidades = Localidades.objects.all()
    carrossel = [
        {'nome': 'Recife', 'imagem': 'https://c1.wallpaperflare.com/preview/476/1004/62/recife-ground-zero-pernambuco-marco.jpg'},
        {'nome': 'Olinda', 'imagem': 'https://img.freepik.com/fotos-premium/olinda-com-recife-ao-fundo-pernambuco-brasil_491130-1804.jpg'},
        {'nome': 'Tamandaré', 'imagem': 'https://t3.ftcdn.net/jpg/05/94/20/04/360_F_594200412_4FEAlobkbGtK0BC0vC2KAgQCVSS3Zz2J.jpg'},
        {'nome': 'Caruaru', 'imagem': 'https://s2-g1.glbimg.com/hO2RwCNTjS5lKElVIfMmSXF0h1A=/1200x/smart/filters:cover():strip_icc()/i.s3.glbimg.com/v1/AUTH_59edd422c0c84a879bd37670ae4f538a/internal_photos/bs/2021/y/t/SDykjeQI2Bv32dYWWKAg/indice.jpg'},
        {'nome': 'Gravatá', 'imagem': 'https://upload.wikimedia.org/wikipedia/commons/5/59/BRUNO_LIMA_IGREJA_MATRIZ_DE_SANTANA_GRAVAT%C3%81_PE.jpg'},
        {'nome': 'Garanhuns', 'imagem': 'https://viajeleve.net/v23/wp-content/uploads/2022/06/Relogio-das-Flores-Garanhuns-1170x780.jpg'}
    ]
    for cidade in carrossel:
        cidade['link'] = f"/{cidade['nome']}/destinos/" if cidade['nome'] in [localidade.localizacao for localidade in localidades] else '#'
    
    return render(request, 'main/sobre.html', {'carrossel': carrossel})

def lugares(request):
    localidades = Localidades.objects.all()
    propriedade = list(PropriedadeApartamento.objects.all()) + list(PropriedadeCasaToda.objects.all()) + list(PropriedadeCasaQuarto.objects.all()) + list(PropriedadeHotel.objects.all())
    carrossel = [
        {'nome': 'Recife', 'imagem': 'https://c1.wallpaperflare.com/preview/476/1004/62/recife-ground-zero-pernambuco-marco.jpg'},
        {'nome': 'Olinda', 'imagem': 'https://img.freepik.com/fotos-premium/olinda-com-recife-ao-fundo-pernambuco-brasil_491130-1804.jpg'},
        {'nome': 'Tamandaré', 'imagem': 'https://t3.ftcdn.net/jpg/05/94/20/04/360_F_594200412_4FEAlobkbGtK0BC0vC2KAgQCVSS3Zz2J.jpg'},
        {'nome': 'Caruaru', 'imagem': 'https://s2-g1.glbimg.com/hO2RwCNTjS5lKElVIfMmSXF0h1A=/1200x/smart/filters:cover():strip_icc()/i.s3.glbimg.com/v1/AUTH_59edd422c0c84a879bd37670ae4f538a/internal_photos/bs/2021/y/t/SDykjeQI2Bv32dYWWKAg/indice.jpg'},
        {'nome': 'Gravatá', 'imagem': 'https://upload.wikimedia.org/wikipedia/commons/5/59/BRUNO_LIMA_IGREJA_MATRIZ_DE_SANTANA_GRAVAT%C3%81_PE.jpg'},
        {'nome': 'Garanhuns', 'imagem': 'https://viajeleve.net/v23/wp-content/uploads/2022/06/Relogio-das-Flores-Garanhuns-1170x780.jpg'}
    ]
    for cidade in carrossel:
        cidade['link'] = f"/{cidade['nome']}/destinos/" if cidade['nome'] in [localidade.localizacao for localidade in localidades] else '#'
    
    query = request.GET.get('q')
    if query:
        # Se uma consulta foi fornecida, filtre as localidades com base na consulta
        localidades = localidades.filter(Q(localizacao__icontains=query) | Q(estado__icontains=query))
        propriedade = propriedade.filter(Q(nome_da_propriedade__icontains=query))

    return render(request, 'main/lugares.html', {'localidades': localidades, 'query': query, 'carrossel': carrossel})

def indicacoes(request):
    parceiros = Parceiros.objects.filter(ativo=True)
    localidades = Localidades.objects.all()
    carrossel = [
        {'nome': 'Recife', 'imagem': 'https://c1.wallpaperflare.com/preview/476/1004/62/recife-ground-zero-pernambuco-marco.jpg'},
        {'nome': 'Olinda', 'imagem': 'https://img.freepik.com/fotos-premium/olinda-com-recife-ao-fundo-pernambuco-brasil_491130-1804.jpg'},
        {'nome': 'Tamandaré', 'imagem': 'https://t3.ftcdn.net/jpg/05/94/20/04/360_F_594200412_4FEAlobkbGtK0BC0vC2KAgQCVSS3Zz2J.jpg'},
        {'nome': 'Caruaru', 'imagem': 'https://s2-g1.glbimg.com/hO2RwCNTjS5lKElVIfMmSXF0h1A=/1200x/smart/filters:cover():strip_icc()/i.s3.glbimg.com/v1/AUTH_59edd422c0c84a879bd37670ae4f538a/internal_photos/bs/2021/y/t/SDykjeQI2Bv32dYWWKAg/indice.jpg'},
        {'nome': 'Gravatá', 'imagem': 'https://upload.wikimedia.org/wikipedia/commons/5/59/BRUNO_LIMA_IGREJA_MATRIZ_DE_SANTANA_GRAVAT%C3%81_PE.jpg'},
        {'nome': 'Garanhuns', 'imagem': 'https://viajeleve.net/v23/wp-content/uploads/2022/06/Relogio-das-Flores-Garanhuns-1170x780.jpg'}
    ]
    for cidade in carrossel:
        cidade['link'] = f"/{cidade['nome']}/destinos/" if cidade['nome'] in [localidade.localizacao for localidade in localidades] else '#'
    
    query = request.GET.get('q')
    if query:
        # Se uma consulta foi fornecida, filtre as localidades com base na consulta
        parceiros = parceiros.filter(Q(nome__icontains=query) | Q(descricao__icontains=query) | Q(categoria__icontains=query) | Q(cidade__icontains=query))
    return render(request, 'main/indicacoes.html', {'parceiros': parceiros, 'query': query, 'carrossel': carrossel})



def destinos(request, localizacao):
    localidade = get_object_or_404(Localidades, localizacao=localizacao)
    propriedades_apartamento = PropriedadeApartamento.objects.filter(cidade=localidade).annotate(min_price=Min('valor_da_diaria'))
    propriedades_casa_toda = PropriedadeCasaToda.objects.filter(cidade=localidade).annotate(min_price=Min('valor_da_diaria'))
    propriedades_casa_quarto = PropriedadeCasaQuarto.objects.filter(cidade=localidade).annotate(min_price=Min('valor_da_diaria'))
    propriedades_hotel = PropriedadeHotel.objects.filter(cidade=localidade).annotate(min_price=Min('valor_da_diaria'))
    parceiros = Parceiros.objects.filter(cidade=localidade)

    checkin = request.GET.get('checkin')
    checkout = request.GET.get('checkout')
    adultos = int(request.GET.get('adultos', 1))
    criancas = int(request.GET.get('criancas', 0))
    permite_pet = request.GET.get('permite_pet')
    tipo_propriedade = request.GET.get('tipo_hospedagem')
    print(checkin, checkout, adultos, criancas, permite_pet, tipo_propriedade)
    

    if checkin and checkout:
    # Filtra as propriedades com base nos filtros
        propriedades_apartamento = [prop for prop in propriedades_apartamento if prop.atende_filtro(checkin, checkout, adultos, criancas, permite_pet, tipo_propriedade)]
        propriedades_casa_toda = [prop for prop in propriedades_casa_toda if prop.atende_filtro(checkin, checkout, adultos, criancas, permite_pet, tipo_propriedade)]
        propriedades_casa_quarto = [prop for prop in propriedades_casa_quarto if prop.atende_filtro(checkin, checkout, adultos, criancas, permite_pet, tipo_propriedade)]
        propriedades_hotel = [prop for prop in propriedades_hotel if prop.atende_filtro(checkin, checkout, adultos, criancas, permite_pet, tipo_propriedade)]


    propriedades = list(propriedades_apartamento) + list(propriedades_casa_toda) + list(propriedades_casa_quarto) + list(propriedades_hotel)
    fotos = Fotos.objects.filter(
        Q(propriedade_apartamento__cidade=localidade) |
        Q(propriedade_casa_toda__cidade=localidade) |
        Q(propriedade_casa_quarto__cidade=localidade) |
        Q(propriedade_hotel__cidade=localidade) |
        Q()
    )
    prop_apartamento = []
    prop_casa_toda = []
    prop_casa_quarto = []
    prop_hotel = []
    
    for i in fotos:
        if i.propriedade_apartamento:
            prop_apartamento.append(i.propriedade_apartamento.id)
        if i.propriedade_casa_toda:
            prop_casa_toda.append(i.propriedade_casa_toda.id)
        if i.propriedade_casa_quarto:
            prop_casa_quarto.append(i.propriedade_casa_quarto.id)
        if i.propriedade_hotel:
            prop_hotel.append(i.propriedade_hotel.id)
    
    print('prop_apartamento', prop_apartamento)
    print('prop_casa_toda', prop_casa_toda)
    print('prop_casa_quarto', prop_casa_quarto)
    print('prop_hotel', prop_hotel)
    
    fotos_por_propriedade = {
        'apartamento': fotos.filter(propriedade_apartamento__isnull=False),
        'casa_toda': fotos.filter(propriedade_casa_toda__isnull=False),
        'casa_quarto': fotos.filter(propriedade_casa_quarto__isnull=False),
        'hotel': fotos.filter(propriedade_hotel__isnull=False),
    }
    localidades = Localidades.objects.all()
    carrossel = [
        {'nome': 'Recife', 'imagem': 'https://c1.wallpaperflare.com/preview/476/1004/62/recife-ground-zero-pernambuco-marco.jpg'},
        {'nome': 'Olinda', 'imagem': 'https://img.freepik.com/fotos-premium/olinda-com-recife-ao-fundo-pernambuco-brasil_491130-1804.jpg'},
        {'nome': 'Tamandaré', 'imagem': 'https://t3.ftcdn.net/jpg/05/94/20/04/360_F_594200412_4FEAlobkbGtK0BC0vC2KAgQCVSS3Zz2J.jpg'},
        {'nome': 'Caruaru', 'imagem': 'https://s2-g1.glbimg.com/hO2RwCNTjS5lKElVIfMmSXF0h1A=/1200x/smart/filters:cover():strip_icc()/i.s3.glbimg.com/v1/AUTH_59edd422c0c84a879bd37670ae4f538a/internal_photos/bs/2021/y/t/SDykjeQI2Bv32dYWWKAg/indice.jpg'},
        {'nome': 'Gravatá', 'imagem': 'https://upload.wikimedia.org/wikipedia/commons/5/59/BRUNO_LIMA_IGREJA_MATRIZ_DE_SANTANA_GRAVAT%C3%81_PE.jpg'},
        {'nome': 'Garanhuns', 'imagem': 'https://viajeleve.net/v23/wp-content/uploads/2022/06/Relogio-das-Flores-Garanhuns-1170x780.jpg'}
    ]
    for cidade in carrossel:
        cidade['link'] = f"/{cidade['nome']}/destinos/" if cidade['nome'] in [localidade.localizacao for localidade in localidades] else '#'
    
    
    return render(request, 'main/destinos.html', {'localidade': localidade, 'propriedades': propriedades, 'parceiros': parceiros, 'fotos_por_propriedade': fotos_por_propriedade, 'carrossel': carrossel, 'prop_apartamento': prop_apartamento, 'prop_casa_toda': prop_casa_toda, 'prop_casa_quarto': prop_casa_quarto, 'prop_hotel': prop_hotel})


def sucesso(request):
    return render(request, 'main/sucesso.html')

# criador de localidades com base nas propriedades
@receiver(post_save, sender=[PropriedadeCasaToda, PropriedadeApartamento, PropriedadeCasaQuarto, PropriedadeHotel])
def salvar_localidade(sender, instance, created, **kwargs):
    if created:
        localidade, created = Localidades.objects.get_or_create(
            localizacao=instance.cidade,
            estado=instance.estado
        )
        instance.localidade = localidade
        instance.save()

def index_login(request):
    localidades = Localidades.objects.all()
    carrossel = [
        {'nome': 'Recife', 'imagem': 'https://c1.wallpaperflare.com/preview/476/1004/62/recife-ground-zero-pernambuco-marco.jpg'},
        {'nome': 'Olinda', 'imagem': 'https://img.freepik.com/fotos-premium/olinda-com-recife-ao-fundo-pernambuco-brasil_491130-1804.jpg'},
        {'nome': 'Tamandaré', 'imagem': 'https://t3.ftcdn.net/jpg/05/94/20/04/360_F_594200412_4FEAlobkbGtK0BC0vC2KAgQCVSS3Zz2J.jpg'},
        {'nome': 'Caruaru', 'imagem': 'https://s2-g1.glbimg.com/hO2RwCNTjS5lKElVIfMmSXF0h1A=/1200x/smart/filters:cover():strip_icc()/i.s3.glbimg.com/v1/AUTH_59edd422c0c84a879bd37670ae4f538a/internal_photos/bs/2021/y/t/SDykjeQI2Bv32dYWWKAg/indice.jpg'},
        {'nome': 'Gravatá', 'imagem': 'https://upload.wikimedia.org/wikipedia/commons/5/59/BRUNO_LIMA_IGREJA_MATRIZ_DE_SANTANA_GRAVAT%C3%81_PE.jpg'},
        {'nome': 'Garanhuns', 'imagem': 'https://viajeleve.net/v23/wp-content/uploads/2022/06/Relogio-das-Flores-Garanhuns-1170x780.jpg'}
    ]
    for cidade in carrossel:
        cidade['link'] = f"/{cidade['nome']}/destinos/" if cidade['nome'] in [localidade.localizacao for localidade in localidades] else '#'
    
    return render(request, 'main/index_login.html', {'carrossel': carrossel})



@login_required
def reserva(request, id_propriedade, tipo_propriedade):
    if request.user.is_anfitriao:
        return redirect('/anfitriao')
    localidades = Localidades.objects.all()
    carrossel = [
        {'nome': 'Recife', 'imagem': 'https://c1.wallpaperflare.com/preview/476/1004/62/recife-ground-zero-pernambuco-marco.jpg'},
        {'nome': 'Olinda', 'imagem': 'https://img.freepik.com/fotos-premium/olinda-com-recife-ao-fundo-pernambuco-brasil_491130-1804.jpg'},
        {'nome': 'Tamandaré', 'imagem': 'https://t3.ftcdn.net/jpg/05/94/20/04/360_F_594200412_4FEAlobkbGtK0BC0vC2KAgQCVSS3Zz2J.jpg'},
        {'nome': 'Caruaru', 'imagem': 'https://s2-g1.glbimg.com/hO2RwCNTjS5lKElVIfMmSXF0h1A=/1200x/smart/filters:cover():strip_icc()/i.s3.glbimg.com/v1/AUTH_59edd422c0c84a879bd37670ae4f538a/internal_photos/bs/2021/y/t/SDykjeQI2Bv32dYWWKAg/indice.jpg'},
        {'nome': 'Gravatá', 'imagem': 'https://upload.wikimedia.org/wikipedia/commons/5/59/BRUNO_LIMA_IGREJA_MATRIZ_DE_SANTANA_GRAVAT%C3%81_PE.jpg'},
        {'nome': 'Garanhuns', 'imagem': 'https://viajeleve.net/v23/wp-content/uploads/2022/06/Relogio-das-Flores-Garanhuns-1170x780.jpg'}
    ]
    for cidade in carrossel:
        cidade['link'] = f"/{cidade['nome']}/destinos/" if cidade['nome'] in [localidade.localizacao for localidade in localidades] else '#'
    
    datas_reservadas_propriedade = []
    for reserva in Reservas.objects.filter(propriedade=[id_propriedade, tipo_propriedade]):
        datas_reservadas_propriedade.append({
            'data_comeco': reserva.data_inicio.strftime('%Y-%m-%d'),
            'data_final': reserva.data_fim.strftime('%Y-%m-%d'),
        })
    datas_reservadas_json = json.dumps(datas_reservadas_propriedade)
    prop_model = None
    quarto_hotel = None
    propriedade = None
    if tipo_propriedade == 'apartamento':
        prop_model = PropriedadeApartamento
        quarto_hotel = []
    elif tipo_propriedade == 'casa':
        prop_model = PropriedadeCasaToda
        quarto_hotel = []
    elif tipo_propriedade == 'quarto':
        prop_model = PropriedadeCasaQuarto
        quarto_hotel = []
    elif tipo_propriedade == 'hotel':
        prop_model = PropriedadeHotel
        quarto_hotel = ConfigQuartoHotel.objects.filter(propriedade_hotel=id_propriedade)
    elif tipo_propriedade == 'pousada':
        prop_model = PropriedadeHotel
        quarto_hotel = ConfigQuartoHotel.objects.filter(propriedade_hotel=id_propriedade)

    if prop_model is not None:
        propriedade = get_object_or_404(prop_model, id=id_propriedade)
        qtd_hospedes = propriedade.qtd_hospedes if propriedade.tipo_propriedade != 'hotel' or propriedade.tipo_propriedade != 'pousada' else None
        
        checkin = request.GET.get('checkin')
        checkout = request.GET.get('checkout')
        if checkin and checkout:
            checkin_formatted = datetime.strptime(checkin, "%d/%m/%Y").strftime("%Y-%m-%d")
            checkout_formatted = datetime.strptime(checkout, "%d/%m/%Y").strftime("%Y-%m-%d")
        else:
            checkin_formatted = None
            checkout_formatted = None
        
        fotos = Fotos.objects.filter(
            Q(propriedade_apartamento=id_propriedade) if tipo_propriedade == 'apartamento' else
            Q(propriedade_casa_toda=id_propriedade) if tipo_propriedade == 'casa' else
            Q(propriedade_casa_quarto=id_propriedade) if tipo_propriedade == 'quarto' else
            Q(propriedade_hotel=id_propriedade) if tipo_propriedade == 'hotel' or tipo_propriedade == 'pousada' else
            Q()
        )
        
        if request.method == 'POST':
            form = ReservaForm(request.POST)
            if form.is_valid():
                hospede = request.user
                mensagem = form.cleaned_data['mensagem']
                data_inicio = form.cleaned_data['data_inicio']
                data_fim = form.cleaned_data['data_fim']
                numero_de_pessoas = form.cleaned_data['numero_de_pessoas']
                quarto_hotel = form.cleaned_data['quarto_hotel']
                with transaction.atomic():

                    reserva = Reservas(
                        hospede=hospede,
                        mensagem=mensagem,
                        propriedade=[id_propriedade, tipo_propriedade],
                        propriedade_apartamento=propriedade if tipo_propriedade == 'apartamento' else None,
                        propriedade_casa_toda=propriedade if tipo_propriedade == 'casa' else None,
                        propriedade_casa_quarto=propriedade if tipo_propriedade == 'quarto' else None,
                        propriedade_hotel=propriedade if tipo_propriedade == 'hotel' or tipo_propriedade == 'pousada' else None,
                        quarto_hotel=quarto_hotel,
                        data_inicio=data_inicio,
                        data_fim=data_fim,
                        numero_de_pessoas=numero_de_pessoas
                    )

                    reserva.save()
                    enviar_emails_reserva.delay(reserva.id)
                    messages.success(request, 'Reserva efetuada com sucesso!')
                    time.sleep(1.5)
                    return redirect('suas_reservas')

        else:
            form = ReservaForm(initial={'data_inicio': checkin, 'data_fim': checkout})

        return render(request, 'main/reserva.html', {'propriedade': propriedade, 'tipo_propriedade': tipo_propriedade, 'form': form, 'qtd_hospedes': qtd_hospedes, 'datas_reservadas_propriedade': datas_reservadas_propriedade, 'datas_reservadas_json': datas_reservadas_json, 'checkin': checkin_formatted, 'checkout': checkout_formatted, 'fotos': fotos, 'quarto_hotel': quarto_hotel, 'capacidade_maxima': [quarto.quntos_hospedes_podem_ficar_neste_quarto for quarto in quarto_hotel], 'carrossel': carrossel
})
    else:
        return HttpResponse('Tipo de propriedade inválido')

# função apenas de definição
def obter_nome_tipo_propriedade(propriedade):
    if isinstance(propriedade, PropriedadeApartamento):
        return 'Apartamento'
    elif isinstance(propriedade, PropriedadeCasaToda):
        return 'Casa Toda'
    elif isinstance(propriedade, PropriedadeHotel):
        return 'Hotel'
    elif isinstance(propriedade, PropriedadeCasaQuarto):
        return 'Casa Quarto'
    pass
    return 'Tipo Desconhecido' 

@login_required
def anfitriao_page(request):
    localidades = Localidades.objects.all()
    carrossel = [
        {'nome': 'Recife', 'imagem': 'https://c1.wallpaperflare.com/preview/476/1004/62/recife-ground-zero-pernambuco-marco.jpg'},
        {'nome': 'Olinda', 'imagem': 'https://img.freepik.com/fotos-premium/olinda-com-recife-ao-fundo-pernambuco-brasil_491130-1804.jpg'},
        {'nome': 'Tamandaré', 'imagem': 'https://t3.ftcdn.net/jpg/05/94/20/04/360_F_594200412_4FEAlobkbGtK0BC0vC2KAgQCVSS3Zz2J.jpg'},
        {'nome': 'Caruaru', 'imagem': 'https://s2-g1.glbimg.com/hO2RwCNTjS5lKElVIfMmSXF0h1A=/1200x/smart/filters:cover():strip_icc()/i.s3.glbimg.com/v1/AUTH_59edd422c0c84a879bd37670ae4f538a/internal_photos/bs/2021/y/t/SDykjeQI2Bv32dYWWKAg/indice.jpg'},
        {'nome': 'Gravatá', 'imagem': 'https://upload.wikimedia.org/wikipedia/commons/5/59/BRUNO_LIMA_IGREJA_MATRIZ_DE_SANTANA_GRAVAT%C3%81_PE.jpg'},
        {'nome': 'Garanhuns', 'imagem': 'https://viajeleve.net/v23/wp-content/uploads/2022/06/Relogio-das-Flores-Garanhuns-1170x780.jpg'}
    ]
    for cidade in carrossel:
        cidade['link'] = f"/{cidade['nome']}/destinos/" if cidade['nome'] in [localidade.localizacao for localidade in localidades] else '#'
    
    if not request.user.is_anfitriao:
        return redirect('/')
    propriedades_apartamento = PropriedadeApartamento.objects.filter(anfitriao=request.user)
    propriedades_casa_toda = PropriedadeCasaToda.objects.filter(anfitriao=request.user)
    propriedades_casa_quarto = PropriedadeCasaQuarto.objects.filter(anfitriao=request.user)
    propriedades_hotel = PropriedadeHotel.objects.filter(anfitriao=request.user)
    propriedades_hotel_ids = [propriedade.id for propriedade in propriedades_hotel]

    print(propriedades_hotel_ids)

    quarto_hotel = ConfigQuartoHotel.objects.all
    print(quarto_hotel)

    propriedades = list(propriedades_apartamento) + list(propriedades_casa_toda) + list(propriedades_casa_quarto) + list(propriedades_hotel)

    datas_reservadas = []
    for propriedade in propriedades:
        reservas = Reservas.objects.filter(propriedade=[propriedade.id, propriedade.tipo_propriedade])
        for reserva in reservas:
            reserva_id = reserva.id
            hospede_nome = reserva.hospede # Aqui estamos pegando o nome do hóspede diretamente
            quantidade_dias = (reserva.data_fim - reserva.data_inicio).days
                # Converte o valor_da_diaria para um número de ponto flutuante
            valor_diaria = float(propriedade.valor_da_diaria)
            
                # Calcula o valor total multiplicado pela quantidade de diárias
            valor_total = valor_diaria * quantidade_dias
            whatsapp_numero = re.sub(r'\D', '', hospede_nome.telefone)
            whatsapp = "https://api.whatsapp.com/send?phone=55" + whatsapp_numero
            
            
            datas_reservadas.append({
                'id_propriedade': propriedade.id,
                'tipo_propriedade': propriedade.tipo_propriedade,
                'start': reserva.data_inicio.strftime('%d/%m/%Y'),
                'end': reserva.data_fim.strftime('%d/%m/%Y'),
                'hospede_nome': hospede_nome,  # Adicionamos o nome do hóspede aqui
                'reserva_id': reserva_id,
                'valor_total': "{:.2f}".format(valor_total),
                'whatsapp': whatsapp
            })
    
    
    if request.user.is_authenticated and request.user.is_anfitriao:
        return render(request, 'main/anfitriao.html', {'propriedades': propriedades, 'datas_reservadas': datas_reservadas, 'carrossel': carrossel, 'localidades': localidades, 'quarto_hotel': quarto_hotel})
    else:
        return redirect('/')


@login_required
def suas_reservas(request):
    localidades = Localidades.objects.all()
    carrossel = [
        {'nome': 'Recife', 'imagem': 'https://c1.wallpaperflare.com/preview/476/1004/62/recife-ground-zero-pernambuco-marco.jpg'},
        {'nome': 'Olinda', 'imagem': 'https://img.freepik.com/fotos-premium/olinda-com-recife-ao-fundo-pernambuco-brasil_491130-1804.jpg'},
        {'nome': 'Tamandaré', 'imagem': 'https://t3.ftcdn.net/jpg/05/94/20/04/360_F_594200412_4FEAlobkbGtK0BC0vC2KAgQCVSS3Zz2J.jpg'},
        {'nome': 'Caruaru', 'imagem': 'https://s2-g1.glbimg.com/hO2RwCNTjS5lKElVIfMmSXF0h1A=/1200x/smart/filters:cover():strip_icc()/i.s3.glbimg.com/v1/AUTH_59edd422c0c84a879bd37670ae4f538a/internal_photos/bs/2021/y/t/SDykjeQI2Bv32dYWWKAg/indice.jpg'},
        {'nome': 'Gravatá', 'imagem': 'https://upload.wikimedia.org/wikipedia/commons/5/59/BRUNO_LIMA_IGREJA_MATRIZ_DE_SANTANA_GRAVAT%C3%81_PE.jpg'},
        {'nome': 'Garanhuns', 'imagem': 'https://viajeleve.net/v23/wp-content/uploads/2022/06/Relogio-das-Flores-Garanhuns-1170x780.jpg'}
    ]
    for cidade in carrossel:
        cidade['link'] = f"/{cidade['nome']}/destinos/" if cidade['nome'] in [localidade.localizacao for localidade in localidades] else '#'
    
    if request.user.is_anfitriao:
        return redirect('/anfitriao')

    if request.user.is_authenticated:
        # Pega todas as reservas associadas ao usuário
        reservas = Reservas.objects.filter(hospede=request.user)

        # Inicializa a lista de informações de reservas
        reservas_info = []

        # Itera sobre as reservas
        for reserva in reservas:
            propriedade = None
            tipo_propriedade = None

            # Verifica o tipo específico de propriedade associada a esta reserva
            if reserva.propriedade_apartamento:
                propriedade = reserva.propriedade_apartamento
                tipo_propriedade = 'apartamento'
            elif reserva.propriedade_casa_toda:
                propriedade = reserva.propriedade_casa_toda
                tipo_propriedade = 'casa'
            elif reserva.propriedade_casa_quarto:
                propriedade = reserva.propriedade_casa_quarto
                tipo_propriedade = 'casa_quarto'
            elif reserva.propriedade_hotel:
                propriedade = reserva.propriedade_hotel
                tipo_propriedade = 'hotel'

            if propriedade:
                reserva_id = reserva.id
                # Calcula a quantidade de dias entre as datas de início e fim
                quantidade_dias = (reserva.data_fim - reserva.data_inicio).days
                # Converte o valor_da_diaria para um número de ponto flutuante
                
                valor_diaria = float(propriedade.valor_da_diaria)
                # Calcula o valor total multiplicado pela quantidade de diárias
                valor_total = valor_diaria * quantidade_dias
                whatsapp_numero = re.sub(r'\D', '', propriedade.telefone)
                whatsapp = "https://api.whatsapp.com/send?phone=55" + whatsapp_numero
                print(whatsapp)
                reservas_info.append({
                    'propriedade': propriedade,
                    'reserva': reserva,
                    'start': reserva.data_inicio.strftime('%d/%m/%Y'),
                    'end': reserva.data_fim.strftime('%d/%m/%Y'),
                    'reserva_id': reserva_id,
                    'tipo_propriedade': tipo_propriedade,
                    'diarias': quantidade_dias,
                    'valor_total': "{:.2f}".format(valor_total),
                    'whatsapp': whatsapp
                })
        return render(request, 'main/suas_reservas.html', {'reservas_info': reservas_info, 'carrossel': carrossel})

    return redirect('login')  # Redireciona para a página de login se o usuário não estiver autenticado



@login_required
def salvar_apartamento(request):
    localidades = Localidades.objects.all()
    carrossel = [
        {'nome': 'Recife', 'imagem': 'https://c1.wallpaperflare.com/preview/476/1004/62/recife-ground-zero-pernambuco-marco.jpg'},
        {'nome': 'Olinda', 'imagem': 'https://img.freepik.com/fotos-premium/olinda-com-recife-ao-fundo-pernambuco-brasil_491130-1804.jpg'},
        {'nome': 'Tamandaré', 'imagem': 'https://t3.ftcdn.net/jpg/05/94/20/04/360_F_594200412_4FEAlobkbGtK0BC0vC2KAgQCVSS3Zz2J.jpg'},
        {'nome': 'Caruaru', 'imagem': 'https://s2-g1.glbimg.com/hO2RwCNTjS5lKElVIfMmSXF0h1A=/1200x/smart/filters:cover():strip_icc()/i.s3.glbimg.com/v1/AUTH_59edd422c0c84a879bd37670ae4f538a/internal_photos/bs/2021/y/t/SDykjeQI2Bv32dYWWKAg/indice.jpg'},
        {'nome': 'Gravatá', 'imagem': 'https://upload.wikimedia.org/wikipedia/commons/5/59/BRUNO_LIMA_IGREJA_MATRIZ_DE_SANTANA_GRAVAT%C3%81_PE.jpg'},
        {'nome': 'Garanhuns', 'imagem': 'https://viajeleve.net/v23/wp-content/uploads/2022/06/Relogio-das-Flores-Garanhuns-1170x780.jpg'}
    ]
    for cidade in carrossel:
        cidade['link'] = f"/{cidade['nome']}/destinos/" if cidade['nome'] in [localidade.localizacao for localidade in localidades] else '#'
    
    if not request.user.is_anfitriao:
        return redirect('/')
    if request.method == 'POST':
        form = PropriedadeApartamentoForm(request.POST, request.FILES)
        fotos_form = FotosForm(request.POST, request.FILES)
        print('form 1', form.errors)
        print('form 2', fotos_form.errors)
        if form.is_valid() and fotos_form.is_valid():
            propriedade_data = form.cleaned_data
            user_id = request.user.id
            print(propriedade_data)
            print(user_id)

            # Convertendo os arquivos em bytes
            fotos_data = [foto.read() for foto in request.FILES.values()]
            print(fotos_data)
            # Substitua o salvamento direto pela chamada da tarefa do Celery
            salvar_apartamento_task.delay(propriedade_data, fotos_data, user_id)
            messages.success(request, 'Apartamento cadastrado com sucesso!')
            time.sleep(1.5)
            return redirect('anfitriao')
        else:
            print('chegou')
    else:
        form = PropriedadeApartamentoForm()
        fotos_form = FotosForm()

    return render(request, 'main/salvar_apartamento.html', {'form': form, 'fotos_form': fotos_form, 'carrossel': carrossel})

@login_required
def salvar_casa(request):
    localidades = Localidades.objects.all()
    carrossel = [
        {'nome': 'Recife', 'imagem': 'https://c1.wallpaperflare.com/preview/476/1004/62/recife-ground-zero-pernambuco-marco.jpg'},
        {'nome': 'Olinda', 'imagem': 'https://img.freepik.com/fotos-premium/olinda-com-recife-ao-fundo-pernambuco-brasil_491130-1804.jpg'},
        {'nome': 'Tamandaré', 'imagem': 'https://t3.ftcdn.net/jpg/05/94/20/04/360_F_594200412_4FEAlobkbGtK0BC0vC2KAgQCVSS3Zz2J.jpg'},
        {'nome': 'Caruaru', 'imagem': 'https://s2-g1.glbimg.com/hO2RwCNTjS5lKElVIfMmSXF0h1A=/1200x/smart/filters:cover():strip_icc()/i.s3.glbimg.com/v1/AUTH_59edd422c0c84a879bd37670ae4f538a/internal_photos/bs/2021/y/t/SDykjeQI2Bv32dYWWKAg/indice.jpg'},
        {'nome': 'Gravatá', 'imagem': 'https://upload.wikimedia.org/wikipedia/commons/5/59/BRUNO_LIMA_IGREJA_MATRIZ_DE_SANTANA_GRAVAT%C3%81_PE.jpg'},
        {'nome': 'Garanhuns', 'imagem': 'https://viajeleve.net/v23/wp-content/uploads/2022/06/Relogio-das-Flores-Garanhuns-1170x780.jpg'}
    ]
    for cidade in carrossel:
        cidade['link'] = f"/{cidade['nome']}/destinos/" if cidade['nome'] in [localidade.localizacao for localidade in localidades] else '#'
    
    if not request.user.is_anfitriao:
        return redirect('/')
    if request.method == 'POST':
        form = PropriedadeCasaTodaForm(request.POST, request.FILES)
        fotos_form = FotosForm(request.POST, request.FILES)
        if form.is_valid() and fotos_form.is_valid():
            propriedade_data = form.cleaned_data
            user_id = request.user.id

            # Convertendo os arquivos em bytes
            fotos_data = [foto.read() for foto in request.FILES.values()]

            # Substitua o salvamento direto pela chamada da tarefa do Celery
            salvar_casa_toda_task.delay(propriedade_data, fotos_data, user_id)
            messages.success(request, 'Casa cadastrada com sucesso!')
            time.sleep(1.5)
            return redirect('/anfitriao/')
    else:
        form = PropriedadeCasaTodaForm()
        fotos_form = FotosForm()

    return render(request, 'main/salvar_casa.html', {'form': form, 'fotos_form': fotos_form, 'carrossel': carrossel})

@login_required
def salvar_casa_quarto(request):
    localidades = Localidades.objects.all()
    carrossel = [
        {'nome': 'Recife', 'imagem': 'https://c1.wallpaperflare.com/preview/476/1004/62/recife-ground-zero-pernambuco-marco.jpg'},
        {'nome': 'Olinda', 'imagem': 'https://img.freepik.com/fotos-premium/olinda-com-recife-ao-fundo-pernambuco-brasil_491130-1804.jpg'},
        {'nome': 'Tamandaré', 'imagem': 'https://t3.ftcdn.net/jpg/05/94/20/04/360_F_594200412_4FEAlobkbGtK0BC0vC2KAgQCVSS3Zz2J.jpg'},
        {'nome': 'Caruaru', 'imagem': 'https://s2-g1.glbimg.com/hO2RwCNTjS5lKElVIfMmSXF0h1A=/1200x/smart/filters:cover():strip_icc()/i.s3.glbimg.com/v1/AUTH_59edd422c0c84a879bd37670ae4f538a/internal_photos/bs/2021/y/t/SDykjeQI2Bv32dYWWKAg/indice.jpg'},
        {'nome': 'Gravatá', 'imagem': 'https://upload.wikimedia.org/wikipedia/commons/5/59/BRUNO_LIMA_IGREJA_MATRIZ_DE_SANTANA_GRAVAT%C3%81_PE.jpg'},
        {'nome': 'Garanhuns', 'imagem': 'https://viajeleve.net/v23/wp-content/uploads/2022/06/Relogio-das-Flores-Garanhuns-1170x780.jpg'}
    ]
    for cidade in carrossel:
        cidade['link'] = f"/{cidade['nome']}/destinos/" if cidade['nome'] in [localidade.localizacao for localidade in localidades] else '#'
    
    if not request.user.is_anfitriao:
        return redirect('/')
    if request.method == 'POST':
        form = PropriedadeCasaQuartoForm(request.POST, request.FILES)
        fotos_form = FotosForm(request.POST, request.FILES)
        if form.is_valid() and fotos_form.is_valid():
            propriedade_data = form.cleaned_data
            user_id = request.user.id
            print(user_id)

            # Convertendo os arquivos em bytes
            fotos_data = [foto.read() for foto in request.FILES.values()]

            # Substitua o salvamento direto pela chamada da tarefa do Celery
            salvar_casa_quarto_task.delay(propriedade_data, fotos_data, user_id)
            messages.success(request, 'Quarto cadastrado com sucesso!')
            time.sleep(1.5)
            return redirect('/anfitriao/')
    else:
        form = PropriedadeCasaQuartoForm()
        fotos_form = FotosForm()

    return render(request, 'main/salvar_casa_quarto.html', {'form': form, 'fotos_form': fotos_form, 'carrossel': carrossel})

@login_required
def salvar_hotel(request):
    localidades = Localidades.objects.all()
    carrossel = [
        {'nome': 'Recife', 'imagem': 'https://c1.wallpaperflare.com/preview/476/1004/62/recife-ground-zero-pernambuco-marco.jpg'},
        {'nome': 'Olinda', 'imagem': 'https://img.freepik.com/fotos-premium/olinda-com-recife-ao-fundo-pernambuco-brasil_491130-1804.jpg'},
        {'nome': 'Tamandaré', 'imagem': 'https://t3.ftcdn.net/jpg/05/94/20/04/360_F_594200412_4FEAlobkbGtK0BC0vC2KAgQCVSS3Zz2J.jpg'},
        {'nome': 'Caruaru', 'imagem': 'https://s2-g1.glbimg.com/hO2RwCNTjS5lKElVIfMmSXF0h1A=/1200x/smart/filters:cover():strip_icc()/i.s3.glbimg.com/v1/AUTH_59edd422c0c84a879bd37670ae4f538a/internal_photos/bs/2021/y/t/SDykjeQI2Bv32dYWWKAg/indice.jpg'},
        {'nome': 'Gravatá', 'imagem': 'https://upload.wikimedia.org/wikipedia/commons/5/59/BRUNO_LIMA_IGREJA_MATRIZ_DE_SANTANA_GRAVAT%C3%81_PE.jpg'},
        {'nome': 'Garanhuns', 'imagem': 'https://viajeleve.net/v23/wp-content/uploads/2022/06/Relogio-das-Flores-Garanhuns-1170x780.jpg'}
    ]
    for cidade in carrossel:
        cidade['link'] = f"/{cidade['nome']}/destinos/" if cidade['nome'] in [localidade.localizacao for localidade in localidades] else '#'
    
    if not request.user.is_anfitriao:
        return redirect('/')
    if request.method == 'POST':
        form = PropriedadeHotelForm(request.POST, request.FILES)
        fotos_form = FotosForm(request.POST, request.FILES)
        if form.is_valid() and fotos_form.is_valid():
            propriedade_data = form.cleaned_data
            user_id = request.user.id

            # Convertendo os arquivos em bytes
            fotos_data = [foto.read() for foto in request.FILES.values()]

            # Substitua o salvamento direto pela chamada da tarefa do Celery
            salvar_hotel_task.delay(propriedade_data, fotos_data, user_id)
            messages.success(request, 'Hotel cadastrado com sucesso!')
            time.sleep(1.5)
            return redirect('/anfitriao/')
    else:
        form = PropriedadeHotelForm()
        fotos_form = FotosForm()
    
    return render(request, 'main/salvar_hotel.html', {'form': form, 'fotos_form': fotos_form, 'carrossel': carrossel})

@login_required
def salvar_pousada(request):
    localidades = Localidades.objects.all()
    carrossel = [
        {'nome': 'Recife', 'imagem': 'https://c1.wallpaperflare.com/preview/476/1004/62/recife-ground-zero-pernambuco-marco.jpg'},
        {'nome': 'Olinda', 'imagem': 'https://img.freepik.com/fotos-premium/olinda-com-recife-ao-fundo-pernambuco-brasil_491130-1804.jpg'},
        {'nome': 'Tamandaré', 'imagem': 'https://t3.ftcdn.net/jpg/05/94/20/04/360_F_594200412_4FEAlobkbGtK0BC0vC2KAgQCVSS3Zz2J.jpg'},
        {'nome': 'Caruaru', 'imagem': 'https://s2-g1.glbimg.com/hO2RwCNTjS5lKElVIfMmSXF0h1A=/1200x/smart/filters:cover():strip_icc()/i.s3.glbimg.com/v1/AUTH_59edd422c0c84a879bd37670ae4f538a/internal_photos/bs/2021/y/t/SDykjeQI2Bv32dYWWKAg/indice.jpg'},
        {'nome': 'Gravatá', 'imagem': 'https://upload.wikimedia.org/wikipedia/commons/5/59/BRUNO_LIMA_IGREJA_MATRIZ_DE_SANTANA_GRAVAT%C3%81_PE.jpg'},
        {'nome': 'Garanhuns', 'imagem': 'https://viajeleve.net/v23/wp-content/uploads/2022/06/Relogio-das-Flores-Garanhuns-1170x780.jpg'}
    ]
    for cidade in carrossel:
        cidade['link'] = f"/{cidade['nome']}/destinos/" if cidade['nome'] in [localidade.localizacao for localidade in localidades] else '#'
    
    if not request.user.is_anfitriao:
        return redirect('/')
    if request.method == 'POST':
        form = PropriedadeHotelForm(request.POST, request.FILES)
        print(form.errors)
        fotos_form = FotosForm(request.POST, request.FILES)
        print(fotos_form.errors)
        if form.is_valid() and fotos_form.is_valid():
            print(form.is_valid())
            propriedade_data = form.cleaned_data
            user_id = request.user.id

            # Convertendo os arquivos em bytes
            fotos_data = [foto.read() for foto in request.FILES.values()]
            print(form.errors)
            print(fotos_form.errors)

            # Substitua o salvamento direto pela chamada da tarefa do Celery
            salvar_pousada_task.delay(propriedade_data, fotos_data, user_id)
            messages.success(request, 'Pousada cadastrada com sucesso!')
            time.sleep(1.5)
            return redirect('/anfitriao/')
    else:
        form = PropriedadeHotelForm()
        fotos_form = FotosForm()
        print(form.errors)
        print(fotos_form.errors)
    
    return render(request, 'main/salvar_pousada.html', {'form': form, 'fotos_form': fotos_form, 'carrossel': carrossel})

@login_required
def salvar_config_quarto(request, id_propriedade):
    localidades = Localidades.objects.all()
    carrossel = [
        {'nome': 'Recife', 'imagem': 'https://c1.wallpaperflare.com/preview/476/1004/62/recife-ground-zero-pernambuco-marco.jpg'},
        {'nome': 'Olinda', 'imagem': 'https://img.freepik.com/fotos-premium/olinda-com-recife-ao-fundo-pernambuco-brasil_491130-1804.jpg'},
        {'nome': 'Tamandaré', 'imagem': 'https://t3.ftcdn.net/jpg/05/94/20/04/360_F_594200412_4FEAlobkbGtK0BC0vC2KAgQCVSS3Zz2J.jpg'},
        {'nome': 'Caruaru', 'imagem': 'https://s2-g1.glbimg.com/hO2RwCNTjS5lKElVIfMmSXF0h1A=/1200x/smart/filters:cover():strip_icc()/i.s3.glbimg.com/v1/AUTH_59edd422c0c84a879bd37670ae4f538a/internal_photos/bs/2021/y/t/SDykjeQI2Bv32dYWWKAg/indice.jpg'},
        {'nome': 'Gravatá', 'imagem': 'https://upload.wikimedia.org/wikipedia/commons/5/59/BRUNO_LIMA_IGREJA_MATRIZ_DE_SANTANA_GRAVAT%C3%81_PE.jpg'},
        {'nome': 'Garanhuns', 'imagem': 'https://viajeleve.net/v23/wp-content/uploads/2022/06/Relogio-das-Flores-Garanhuns-1170x780.jpg'}
    ]
    for cidade in carrossel:
        cidade['link'] = f"/{cidade['nome']}/destinos/" if cidade['nome'] in [localidade.localizacao for localidade in localidades] else '#'
    
    hotel = get_object_or_404(PropriedadeHotel, id=id_propriedade)
    if request.method == 'POST':
        form = ConfigQuartoHotelForm(request.POST, request.FILES)
        fotos_form = FotosForm(request.POST, request.FILES)
        if form.is_valid() and fotos_form.is_valid():
            config = form.save(commit=False)
            config.save()
            fotos = Fotos.objects.create(
                config_quarto_hotel=config,
                foto1=request.FILES.get('foto1'),
                foto2=request.FILES.get('foto2'),
                foto3=request.FILES.get('foto3'),
                foto4=request.FILES.get('foto4'),
                foto5=request.FILES.get('foto5'),
                foto6=request.FILES.get('foto6'),
                foto7=request.FILES.get('foto7'),
                foto8=request.FILES.get('foto8'),
                foto9=request.FILES.get('foto9'),
                foto10=request.FILES.get('foto10'),
            )
            messages.success(request, 'Quarto cadastrado com sucesso!')
            time.sleep(1.5)
            return redirect('/anfitriao/')  # Redirecionar para uma página de sucesso
            
    else:
        form = ConfigQuartoHotelForm()
        fotos_form = FotosForm()
    print(form.errors)
    print(fotos_form.errors)
        
    return render(request, 'main/config-quartos.html', {'form': form, 'hotel': hotel.id, 'fotos_form': fotos_form, 'carrossel': carrossel}) 

def atualizar_propriedade(request, id_propriedade, tipo_propriedade):
    localidades = Localidades.objects.all()
    carrossel = [
        {'nome': 'Recife', 'imagem': 'https://c1.wallpaperflare.com/preview/476/1004/62/recife-ground-zero-pernambuco-marco.jpg'},
        {'nome': 'Olinda', 'imagem': 'https://img.freepik.com/fotos-premium/olinda-com-recife-ao-fundo-pernambuco-brasil_491130-1804.jpg'},
        {'nome': 'Tamandaré', 'imagem': 'https://t3.ftcdn.net/jpg/05/94/20/04/360_F_594200412_4FEAlobkbGtK0BC0vC2KAgQCVSS3Zz2J.jpg'},
        {'nome': 'Caruaru', 'imagem': 'https://s2-g1.glbimg.com/hO2RwCNTjS5lKElVIfMmSXF0h1A=/1200x/smart/filters:cover():strip_icc()/i.s3.glbimg.com/v1/AUTH_59edd422c0c84a879bd37670ae4f538a/internal_photos/bs/2021/y/t/SDykjeQI2Bv32dYWWKAg/indice.jpg'},
        {'nome': 'Gravatá', 'imagem': 'https://upload.wikimedia.org/wikipedia/commons/5/59/BRUNO_LIMA_IGREJA_MATRIZ_DE_SANTANA_GRAVAT%C3%81_PE.jpg'},
        {'nome': 'Garanhuns', 'imagem': 'https://viajeleve.net/v23/wp-content/uploads/2022/06/Relogio-das-Flores-Garanhuns-1170x780.jpg'}
    ]
    for cidade in carrossel:
        cidade['link'] = f"/{cidade['nome']}/destinos/" if cidade['nome'] in [localidade.localizacao for localidade in localidades] else '#'
    
    tipo_form_map = {
        'apartamento': PropriedadeApartamentoForm,
        'casa': PropriedadeCasaTodaForm,
        'quarto': PropriedadeCasaQuartoForm,
        'hotel': PropriedadeHotelForm,
        'pousada': PropriedadeHotelForm
    }

    form_class = tipo_form_map.get(tipo_propriedade)

    if form_class is None:
        return HttpResponse('Tipo de propriedade inválido')

    prop_model = None
    if tipo_propriedade == 'apartamento':
        prop_model = PropriedadeApartamento
    elif tipo_propriedade == 'casa':
        prop_model = PropriedadeCasaToda
    elif tipo_propriedade == 'quarto':
        prop_model = PropriedadeCasaQuarto
    elif tipo_propriedade == 'hotel' or tipo_propriedade == 'pousada':
        prop_model = PropriedadeHotel

    if prop_model is not None:
        propriedade = get_object_or_404(prop_model, id=id_propriedade)

        fotos_instance = None
        if tipo_propriedade == 'apartamento':
            fotos_instance = Fotos.objects.filter(propriedade_apartamento=propriedade).first()
            fotos_form = FotosForm(request.POST, request.FILES, instance=fotos_instance)
        elif tipo_propriedade == 'casa':
            fotos_instance = Fotos.objects.filter(propriedade_casa_toda=propriedade).first()
            fotos_form = FotosForm(request.POST, request.FILES, instance=fotos_instance)
        elif tipo_propriedade == 'quarto':
            fotos_instance = Fotos.objects.filter(propriedade_casa_quarto=propriedade).first()
            fotos_form = FotosForm(request.POST, request.FILES, instance=fotos_instance)
        elif tipo_propriedade == 'hotel' or tipo_propriedade == 'pousada':
            fotos_instance = Fotos.objects.filter(propriedade_hotel=propriedade).first()
            fotos_form = FotosForm(request.POST, request.FILES, instance=fotos_instance)
        else:
            fotos_form = None

        if request.method == 'POST':
            form = form_class(request.POST, instance=propriedade)

            if form.is_valid():
                propriedade = form.save(commit=False)
                propriedade.anfitriao = request.user
                propriedade.save()

                if tipo_propriedade in {'apartamento', 'casa', 'quarto', 'hotel', 'pousada'}:
                    if fotos_form.is_valid():
                        fotos_form.instance = propriedade
                        fotos_form.save()
                        print("Fotos form saved successfully")
                    else:
                        print("Fotos form is not valid. Errors:", fotos_form.errors)

                form.save_m2m()
                messages.success(request, 'Atualização feita com sucesso!')
                time.sleep(1.5)
                return redirect('/anfitriao', tipo_propriedade=tipo_propriedade, id_propriedade=id_propriedade)
            else:
                print("Main form is not valid. Errors:", form.errors)

        else:
            form = form_class(instance=propriedade)

        return render(request, 'main/atualizar_propriedade.html', {'form': form, 'fotos_form': fotos_form, 'propriedade': propriedade, 'carrossel': carrossel})

    return HttpResponse('Tipo de propriedade inválido')


def excluir_propriedade(request, tipo_propriedade, id_propriedade):
    tipo_model_map = {
        'apartamento': PropriedadeApartamento,
        'casa': PropriedadeCasaToda,
        'quarto': PropriedadeCasaQuarto,
        'hotel': PropriedadeHotel,
        'pousada': PropriedadeHotel,
    }

    prop_model = tipo_model_map.get(tipo_propriedade)

    if prop_model is not None:
        propriedade = get_object_or_404(prop_model, id=id_propriedade)
        propriedade.delete()
        messages.success(request, 'Propriedade excluída!')
        return redirect('/anfitriao')  # Redirecionar para a lista de propriedades ou outra página

    return HttpResponse('Tipo de propriedade inválido')



def excluir_reserva(request, reserva_id):
    if request.method == 'POST':
        reserva = get_object_or_404(Reservas, id=reserva_id)
        reserva.delete()
        messages.success(request, 'Reserva excluída!')
    return redirect('anfitriao')

def perfil(request):
    localidades = Localidades.objects.all()
    carrossel = [
        {'nome': 'Recife', 'imagem': 'https://c1.wallpaperflare.com/preview/476/1004/62/recife-ground-zero-pernambuco-marco.jpg'},
        {'nome': 'Olinda', 'imagem': 'https://img.freepik.com/fotos-premium/olinda-com-recife-ao-fundo-pernambuco-brasil_491130-1804.jpg'},
        {'nome': 'Tamandaré', 'imagem': 'https://t3.ftcdn.net/jpg/05/94/20/04/360_F_594200412_4FEAlobkbGtK0BC0vC2KAgQCVSS3Zz2J.jpg'},
        {'nome': 'Caruaru', 'imagem': 'https://s2-g1.glbimg.com/hO2RwCNTjS5lKElVIfMmSXF0h1A=/1200x/smart/filters:cover():strip_icc()/i.s3.glbimg.com/v1/AUTH_59edd422c0c84a879bd37670ae4f538a/internal_photos/bs/2021/y/t/SDykjeQI2Bv32dYWWKAg/indice.jpg'},
        {'nome': 'Gravatá', 'imagem': 'https://upload.wikimedia.org/wikipedia/commons/5/59/BRUNO_LIMA_IGREJA_MATRIZ_DE_SANTANA_GRAVAT%C3%81_PE.jpg'},
        {'nome': 'Garanhuns', 'imagem': 'https://viajeleve.net/v23/wp-content/uploads/2022/06/Relogio-das-Flores-Garanhuns-1170x780.jpg'}
    ]
    for cidade in carrossel:
        cidade['link'] = f"/{cidade['nome']}/destinos/" if cidade['nome'] in [localidade.localizacao for localidade in localidades] else '#'
    
    profile = request.user
    return render(request, 'main/perfil.html', {'profile': profile, 'carrossel': carrossel})

def excluir_quarto(request, id_quarto):
    quarto = get_object_or_404(ConfigQuartoHotel,pk=id_quarto)
    quarto.delete()
    messages.success(request, 'Quarto excluído!')
    return redirect('/anfitriao')  # Redirecionar para a lista de propriedades ou outra página~

def atualizar_quarto(request, id_quarto, id_propriedade):
    quarto = get_object_or_404(ConfigQuartoHotel,pk=id_quarto)
    hotel = get_object_or_404(PropriedadeHotel, id=id_propriedade)
    if request.method == 'POST':
        form = ConfigQuartoHotelForm(request.POST, instance=quarto)
        fotos_form = FotosForm(request.POST, request.FILES)

        if form.is_valid() and fotos_form.is_valid():
            form.save()

            # Atualizar fotos do quarto
            fotos, created = Fotos.objects.get_or_create(config_quarto_hotel=quarto)
            fotos.foto1 = request.FILES.get('foto1')
            fotos.foto2 = request.FILES.get('foto2')
            fotos.foto3 = request.FILES.get('foto3')
            fotos.foto4 = request.FILES.get('foto4')
            fotos.foto5 = request.FILES.get('foto5')
            fotos.foto6 = request.FILES.get('foto6')
            fotos.foto7 = request.FILES.get('foto7')
            fotos.foto8 = request.FILES.get('foto8')
            fotos.foto9 = request.FILES.get('foto9')
            fotos.foto10 = request.FILES.get('foto10')
            fotos.save()
            messages.success(request, 'Quarto atualizado!')
            return redirect('/anfitriao/')  # Redirecionar para uma página de sucesso
    else:
        form = ConfigQuartoHotelForm(instance=quarto)
        fotos_form = FotosForm()

    return render(request, 'main/atualizar_quarto.html', {'form': form, 'fotos_form': fotos_form, 'quarto': quarto, 'hotel': hotel.id})


def blog_page(request):
    localidades = Localidades.objects.all()
    carrossel = [
    {'nome': 'Recife', 'imagem': 'https://c1.wallpaperflare.com/preview/476/1004/62/recife-ground-zero-pernambuco-marco.jpg'},
    {'nome': 'Olinda', 'imagem': 'https://img.freepik.com/fotos-premium/olinda-com-recife-ao-fundo-pernambuco-brasil_491130-1804.jpg'},
    {'nome': 'Tamandaré', 'imagem': 'https://t3.ftcdn.net/jpg/05/94/20/04/360_F_594200412_4FEAlobkbGtK0BC0vC2KAgQCVSS3Zz2J.jpg'},
    {'nome': 'Caruaru', 'imagem': 'https://s2-g1.glbimg.com/hO2RwCNTjS5lKElVIfMmSXF0h1A=/1200x/smart/filters:cover():strip_icc()/i.s3.glbimg.com/v1/AUTH_59edd422c0c84a879bd37670ae4f538a/internal_photos/bs/2021/y/t/SDykjeQI2Bv32dYWWKAg/indice.jpg'},
    {'nome': 'Gravatá', 'imagem': 'https://upload.wikimedia.org/wikipedia/commons/5/59/BRUNO_LIMA_IGREJA_MATRIZ_DE_SANTANA_GRAVAT%C3%81_PE.jpg'},
    {'nome': 'Garanhuns', 'imagem': 'https://viajeleve.net/v23/wp-content/uploads/2022/06/Relogio-das-Flores-Garanhuns-1170x780.jpg'}
    ]
    for cidade in carrossel:
        cidade['link'] = f"/{cidade['nome']}/destinos/" if cidade['nome'] in [localidade.localizacao for localidade in localidades] else '#'
    
    posts = Blog.objects.all()
    if request.method == 'POST':
        form = BlogForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Publicação feita!')
            return redirect('blog')
    else:
        form = BlogForm()
    return render(request, 'main/blog.html', {'posts': posts, 'form': form, 'carrossel': carrossel})

def excluir_post(request, id_post):
    post = get_object_or_404(Blog,pk=id_post)
    post.delete()
    messages.success(request, 'Post excluído!')
    return redirect('blog')  # Redirecionar para a lista de propriedades ou outra página

def atualizar_post(request, id_post):
    localidades = Localidades.objects.all()
    carrossel = [
    {'nome': 'Recife', 'imagem': 'https://c1.wallpaperflare.com/preview/476/1004/62/recife-ground-zero-pernambuco-marco.jpg'},
    {'nome': 'Olinda', 'imagem': 'https://img.freepik.com/fotos-premium/olinda-com-recife-ao-fundo-pernambuco-brasil_491130-1804.jpg'},
    {'nome': 'Tamandaré', 'imagem': 'https://t3.ftcdn.net/jpg/05/94/20/04/360_F_594200412_4FEAlobkbGtK0BC0vC2KAgQCVSS3Zz2J.jpg'},
    {'nome': 'Caruaru', 'imagem': 'https://s2-g1.glbimg.com/hO2RwCNTjS5lKElVIfMmSXF0h1A=/1200x/smart/filters:cover():strip_icc()/i.s3.glbimg.com/v1/AUTH_59edd422c0c84a879bd37670ae4f538a/internal_photos/bs/2021/y/t/SDykjeQI2Bv32dYWWKAg/indice.jpg'},
    {'nome': 'Gravatá', 'imagem': 'https://upload.wikimedia.org/wikipedia/commons/5/59/BRUNO_LIMA_IGREJA_MATRIZ_DE_SANTANA_GRAVAT%C3%81_PE.jpg'},
    {'nome': 'Garanhuns', 'imagem': 'https://viajeleve.net/v23/wp-content/uploads/2022/06/Relogio-das-Flores-Garanhuns-1170x780.jpg'}
    ]
    for cidade in carrossel:
        cidade['link'] = f"/{cidade['nome']}/destinos/" if cidade['nome'] in [localidade.localizacao for localidade in localidades] else '#'

    post = get_object_or_404(Blog,pk=id_post)
    if request.method == 'POST':
        form = BlogForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Post atualizado!')
            return redirect('blog')
    else:
        form = BlogForm(instance=post)
    return render(request, 'main/atualizar_post.html', {'form_atualizar': form, 'post_atualizar': post})

def post(request, id_post):
    localidades = Localidades.objects.all()
    carrossel = [
    {'nome': 'Recife', 'imagem': 'https://c1.wallpaperflare.com/preview/476/1004/62/recife-ground-zero-pernambuco-marco.jpg'},
    {'nome': 'Olinda', 'imagem': 'https://img.freepik.com/fotos-premium/olinda-com-recife-ao-fundo-pernambuco-brasil_491130-1804.jpg'},
    {'nome': 'Tamandaré', 'imagem': 'https://t3.ftcdn.net/jpg/05/94/20/04/360_F_594200412_4FEAlobkbGtK0BC0vC2KAgQCVSS3Zz2J.jpg'},
    {'nome': 'Caruaru', 'imagem': 'https://s2-g1.glbimg.com/hO2RwCNTjS5lKElVIfMmSXF0h1A=/1200x/smart/filters:cover():strip_icc()/i.s3.glbimg.com/v1/AUTH_59edd422c0c84a879bd37670ae4f538a/internal_photos/bs/2021/y/t/SDykjeQI2Bv32dYWWKAg/indice.jpg'},
    {'nome': 'Gravatá', 'imagem': 'https://upload.wikimedia.org/wikipedia/commons/5/59/BRUNO_LIMA_IGREJA_MATRIZ_DE_SANTANA_GRAVAT%C3%81_PE.jpg'},
    {'nome': 'Garanhuns', 'imagem': 'https://viajeleve.net/v23/wp-content/uploads/2022/06/Relogio-das-Flores-Garanhuns-1170x780.jpg'}
    ]
    for cidade in carrossel:
        cidade['link'] = f"/{cidade['nome']}/destinos/" if cidade['nome'] in [localidade.localizacao for localidade in localidades] else '#'    
    post = get_object_or_404(Blog,pk=id_post)
    return render(request, 'main/post.html', {'post': post, 'carrossel': carrossel})