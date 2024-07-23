import os
import django

# Configurar as configurações do Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")  # Substitua "seu_projeto" pelo nome real do seu projeto Django
django.setup()
from main.models import Localidades

cidades_turisticas_pe = [
    "Recife",
    "Olinda",
    "Porto de Galinhas",
    "Caruaru",
    "Garanhuns",
    "Fernando de Noronha",
    "Petrolina",
    "Gravatá",
    "Ipojuca",
    "Tamandaré",
]

# Preencher o banco de dados
for cidade in cidades_turisticas_pe:
    Localidades.objects.create(localizacao=cidade, estado="PE")
