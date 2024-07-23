from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from .forms import CustomUserCreationForm, CustomAuthenticationForm, AnfitriaoCreationForm, AnfitriaoLoginForm
import requests
from django.contrib import messages
from .tasks import register_user_task, register_anfitriao_task, send_confirmation_email
from main.models import Localidades

def consultar_cnpj(cnpj):
    url = f'https://www.receitaws.com.br/v1/cnpj/{cnpj}'
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        return data
    else:
        return None

def register(request):
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
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user_data = form.cleaned_data
            auth_info = register_user_task.delay(user_data).get()
            # Autenticar o usuário recém-criado
            user = authenticate(email=auth_info['email'], password=auth_info['password'])

            if user is not None:
                # Fazer login se a autenticação for bem-sucedida
                login(request, user)
                # Redirecionar para a página desejada após o login
                messages.success(request, 'Cadastro efetuado.')

                return redirect('/')  # Altere para a URL desejada
            else:
                # Lógica para lidar com a falha na autenticação, se necessário
                pass
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form, 'carrossel': carrossel})

def user_login(request):
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
    
    mensagem = ""
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(email=email, password=password)

        if user is not None and not user.is_anfitriao:  # Verifica se não é anfitrião
            login(request, user)

            return redirect('/')
        else:
            mensagem = "Algo deu errado. Por favor, tente novamente."
    return render(request, 'accounts/login.html', {'mensagem': mensagem, 'carrossel': carrossel})

def user_logout(request):
    logout(request)
    return redirect('/')  # Redirecione para a página de login após o logout

def register_anfitriao(request):
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
    
    if request.method == 'POST':
        form = AnfitriaoCreationForm(request.POST)
        if form.is_valid():
            cnpj = form.cleaned_data.get('cnpj')
            endereco_data = consultar_cnpj(cnpj)
            print(endereco_data)
            if endereco_data and len(cnpj) >= 16:
                form.cleaned_data['rua'] = endereco_data.get('logradouro') or form.cleaned_data['rua']
                form.cleaned_data['numero'] = endereco_data.get('numero') or form.cleaned_data['numero']
                form.cleaned_data['complemento'] = endereco_data.get('complemento') or form.cleaned_data['complemento']
                form.cleaned_data['cep'] = endereco_data.get('cep') or form.cleaned_data['cep']
                form.cleaned_data['cidade'] = endereco_data.get('municipio') or form.cleaned_data['cidade']
                form.cleaned_data['uf'] = endereco_data.get('uf') or form.cleaned_data['uf']
            anfitriao_data = form.cleaned_data
            auth_info = register_anfitriao_task.delay(anfitriao_data).get()

            # Autenticar o anfitrião recém-criado
            user = authenticate(email=auth_info['email'], password=auth_info['password'])

            if user is not None:
                # Fazer login se a autenticação for bem-sucedida
                login(request, user)
                # Redirecionar para a página desejada após o login
                messages.success(request, 'Cadastro efetuado.')

                return redirect('/anfitriao/')  # Altere para a URL desejada
            else:
                # Lógica para lidar com a falha na autenticação, se necessário
                pass
    else:
        form = AnfitriaoCreationForm()
    return render(request, 'accounts/register_anfitriao.html', {'form': form, 'localidades': localidades, 'carrossel': carrossel})

def login_anfitriao(request):
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
    
    mensagem = ""
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(email=email, password=password)
            
        if user is not None and user.is_anfitriao:
            login(request, user)
            return redirect('/anfitriao/') 
        else:
            mensagem = "Algo deu errado. Por favor, tente novamente."

    return render(request, 'accounts/login_anfitriao.html', {'mensagem': mensagem, 'carrossel': carrossel})

