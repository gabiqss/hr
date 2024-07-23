from django.db import models
from django.contrib.auth.models import AbstractUser
from accounts.models import CustomUser
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from datetime import datetime

class Localidades(models.Model):
    localizacao = models.CharField(max_length=150)
    estado = models.CharField(max_length=150, blank=True, null=True)
    qty_hotel = models.IntegerField(blank=True, null=True)
    def __str__(self):
        return self.localizacao

class Parceiros(models.Model):
    CATEGORIA_CHOICES = [
        ('n/a', 'N/A'),
        ('restaurante', 'Restaurante'),
        ('supermercados', 'Supermercados'),
        ('farmacias', 'Farmácias'),
        ('hospitais', 'Hospitais'),
        ('turismo', 'Turismo'),
        # Adicione mais categorias conforme necessário
    ]
    nome = models.CharField(max_length=200)
    descricao = models.CharField(max_length=150)
    categoria = models.CharField(max_length=150, choices=CATEGORIA_CHOICES, default='')
    sobre = models.TextField(null=True)
    url = models.URLField()
    logo = models.ImageField(upload_to='parceiros/')
    ativo = models.BooleanField(default=True)
    rua = models.CharField(max_length=255)
    numero = models.CharField(max_length=10)
    complemento = models.CharField(max_length=255, null=True, blank=True)
    cep = models.CharField(max_length=10)
    cidade = models.CharField(max_length=255)
    uf = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.nome

class Propriedade(models.Model):
    nome_da_propriedade = models.CharField(max_length=255, blank=True)
    pais_regiao = models.CharField(max_length=255, blank=True)
    nome_da_rua = models.CharField(max_length=255, blank=True)
    numero_residencia = models.CharField(max_length=10, blank=True)
    codigo_postal = models.CharField(max_length=10, blank=True)
    cidade = models.CharField(max_length=255, blank=True)
    estado = models.CharField(max_length=255, blank=True)
    anfitriao = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    local_de_dormir = models.CharField(max_length=255, blank=True)
    qtd_hospedes = models.CharField(max_length=10, blank=True)
    qtd_banheiros = models.CharField(max_length=10, blank=True)
    crianca_permissao = models.CharField(max_length=255, blank=True)
    oferece_bercos = models.CharField(max_length=255, blank=True)
    tamanho_da_propriedade = models.CharField(max_length=10, blank=True)
    tamanho_unidade = models.CharField(max_length=10, blank=True)
    o_que_pode_usar_na_propriedade = models.CharField(max_length=255, blank=True)
    serve_cafe_da_manha = models.CharField(max_length=10, blank=True)
    tem_estacionamento = models.CharField(max_length=10, blank=True)
    idiomas = models.CharField(max_length=255, blank=True)
    permitido_fumar = models.CharField(max_length=10, blank=True)
    bebidas_alcoolicas = models.CharField(max_length=10, default='Sim', blank=True)
    aceita_pets = models.CharField(max_length=10, blank=True)
    festas_eventos_permitidos = models.CharField(max_length=10, blank=True)
    tipo_de_cobranca = models.CharField(max_length=255, blank=True)
    valor_da_diaria = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    email = models.EmailField(blank=True)
    telefone = models.CharField(max_length=15, blank=True)
    atende_filtro = models.BooleanField(null=True, default=False)

    class Meta:
        abstract = True
        
    def atende_filtro(self, checkin, checkout, adultos, criancas, permite_pet, tipo_propriedade):
        # Converter as datas para o formato 'YYYY-MM-DD' mantendo como objeto de data
        checkin = datetime.strptime(checkin, '%d/%m/%Y').date()
        checkout = datetime.strptime(checkout, '%d/%m/%Y').date()
               
        if int(adultos) + int(criancas) > int(self.qtd_hospedes):
            return False
        
        if int(criancas) >= 1 and self.crianca_permissao == "Não":
            return False
            
        if permite_pet == "Sim" and self.aceita_pets == "Não":
            return False
        
        if isinstance(self, PropriedadeApartamento):
            reservas_apartamento = Reservas.objects.filter(propriedade_apartamento=self)
            for reserva in reservas_apartamento:
                if checkin >= reserva.data_inicio and checkout <= reserva.data_fim:
                    return False

        if isinstance(self, PropriedadeCasaToda):
            reservas_casa_toda = Reservas.objects.filter(propriedade_casa_toda=self)
            for reserva in reservas_casa_toda:
                if checkin >= reserva.data_inicio and checkout <= reserva.data_fim:
                    return False
                
        if isinstance(self, PropriedadeCasaQuarto):
            reservas_casa_quarto = Reservas.objects.filter(propriedade_casa_quarto=self)
            for reserva in reservas_casa_quarto:
                if checkin >= reserva.data_inicio and checkout <= reserva.data_fim:
                    return False

        if isinstance(self, PropriedadeHotel):
            reservas_hotel = Reservas.objects.filter(propriedade_hotel=self)
            for reserva in reservas_hotel:
                if checkin >= reserva.data_inicio and checkout <= reserva.data_fim:
                    return False
                
        if isinstance(self, PropriedadeApartamento) and tipo_propriedade != 'apartamento':
            return False
        elif isinstance(self, PropriedadeCasaToda) and tipo_propriedade != 'casa':
            return False
        elif isinstance(self, PropriedadeCasaQuarto) and tipo_propriedade != 'quarto':
            return False
        elif isinstance(self, PropriedadeHotel) and self.tipo_propriedade == 'hotel' and tipo_propriedade != 'hotel':
            return False
        elif isinstance(self, PropriedadeHotel) and self.tipo_propriedade == 'pousada' and tipo_propriedade != 'pousada':
            return False

        return True


    def save(self, *args, **kwargs):
        created = not self.pk
        super(Propriedade, self).save(*args, **kwargs)

        if created:
            self.atualizar_quantidade_localidade()

    def delete(self, *args, **kwargs):
        cidade_propriedade = self.cidade

        super(Propriedade, self).delete(*args, **kwargs)
        
        self.atualizar_quantidade_localidade()

    def atualizar_quantidade_localidade(self):
        tipos_de_propriedade = [PropriedadeCasaToda, PropriedadeApartamento, PropriedadeCasaQuarto, PropriedadeHotel]
        total_de_propriedades = sum(tipo.objects.filter(cidade=self.cidade).count() for tipo in tipos_de_propriedade)

        localidade, created = Localidades.objects.get_or_create(
            localizacao=self.cidade,
            estado=self.estado
        )

        localidade.qty_hotel = total_de_propriedades
        localidade.save()
        
class PropriedadeApartamento(Propriedade):
    tipo_propriedade = models.CharField(default='apartamento', max_length=255)

class PropriedadeCasaToda(Propriedade):
    tipo_propriedade = models.CharField(default='casa', max_length=255)

class PropriedadeCasaQuarto(Propriedade):
    tipo_propriedade = models.CharField(default='quarto', max_length=255)

class PropriedadeHotel(Propriedade):
    tipo_propriedade = models.CharField(default='hotel', max_length=255)
    classificacao_por_estrelas = models.IntegerField(null=True)
    grupo_rede = models.CharField(null=True, max_length=10)
    nome_empresa_ou_grupo_rede = models.CharField(null=True, max_length=255)

    def __str__(self):
        return self.tipo_propriedade

class ConfigQuartoHotel(models.Model):
    config_quarto_hotel_id = models.AutoField(primary_key=True)
    propriedade_hotel = models.ForeignKey(PropriedadeHotel, on_delete=models.CASCADE, null=True, blank=True)
    tipo_de_unidade = models.CharField(max_length=255, blank=True)
    qual_a_quantidade_de_quartos_deste_tipo_que_você_tem = models.IntegerField(blank=True)
    quais_camas_estao_disponiveis_neste_quarto = models.CharField(max_length=255, blank=True)
    quntos_hospedes_podem_ficar_neste_quarto = models.IntegerField(blank=True)
    tamanho_do_quarto = models.CharField(max_length=10, blank=True)
    tamanho_unidade = models.CharField(max_length=10, blank=True)
    permitido_fumar = models.CharField(max_length=10, blank=True)
    banheiro_privativo = models.CharField(max_length=10, blank=True)
    quais_itens_do_banheiro_esta_disponivel = models.CharField(max_length=255, blank=True)
    comodidades_gerais = models.CharField(max_length=255, blank=True)
    area_externa_e_vista = models.CharField(max_length=255, blank=True)
    comidas_e_bebidas = models.CharField(max_length=255, blank=True)
    nome_do_quarto = models.CharField(max_length=255, blank=True)
    valor_da_diaria = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    foto = models.ImageField(upload_to='propriedades/', blank=True, null=True)
    atende_filtro = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.nome_do_quarto} - R$ {self.valor_da_diaria} - até {self.quntos_hospedes_podem_ficar_neste_quarto} pessoas"
    

class Reservas(models.Model):
    hospede = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    propriedade = models.TextField(default=None)
    propriedade_apartamento = models.ForeignKey(PropriedadeApartamento, on_delete=models.CASCADE, null=True, blank=True)
    propriedade_casa_toda = models.ForeignKey(PropriedadeCasaToda, on_delete=models.CASCADE, null=True, blank=True)
    propriedade_casa_quarto = models.ForeignKey(PropriedadeCasaQuarto, on_delete=models.CASCADE, null=True, blank=True)
    propriedade_hotel = models.ForeignKey(PropriedadeHotel, on_delete=models.CASCADE, null=True, blank=True)
    mensagem = models.TextField(blank=True, null=True)
    data_inicio = models.DateField()
    data_fim = models.DateField()
    numero_de_pessoas = models.IntegerField()
    quarto_hotel = models.ForeignKey(ConfigQuartoHotel, on_delete=models.CASCADE, null=True, blank=True)
    def __str__(self):
        return self.hospede
    
class Fotos(models.Model):
    config_quarto_hotel = models.ForeignKey(ConfigQuartoHotel, on_delete=models.CASCADE, null=True, blank=True)
    parceiro = models.ForeignKey(Parceiros, on_delete=models.CASCADE, null=True, blank=True)
    propriedade_apartamento = models.ForeignKey(PropriedadeApartamento, on_delete=models.CASCADE, null=True, blank=True)
    propriedade_casa_toda = models.ForeignKey(PropriedadeCasaToda, on_delete=models.CASCADE, null=True, blank=True)
    propriedade_casa_quarto = models.ForeignKey(PropriedadeCasaQuarto, on_delete=models.CASCADE, null=True, blank=True)
    propriedade_hotel = models.ForeignKey(PropriedadeHotel, on_delete=models.CASCADE, null=True, blank=True)
    foto1 = models.ImageField(upload_to='fotos/')
    foto2 = models.ImageField(upload_to='fotos/')
    foto3 = models.ImageField(upload_to='fotos/')
    foto4 = models.ImageField(upload_to='fotos/')
    foto5 = models.ImageField(upload_to='fotos/')
    foto6 = models.ImageField(null=True, blank=True, upload_to='fotos/')
    foto7 = models.ImageField(null=True, blank=True, upload_to='fotos/')
    foto8 = models.ImageField(null=True, blank=True, upload_to='fotos/')
    foto9 = models.ImageField(null=True, blank=True, upload_to='fotos/')
    foto10 = models.ImageField(null=True, blank=True, upload_to='fotos/')

class Blog(models.Model):
    imagem = models.ImageField(upload_to='blog/', null=True, blank=True)
    titulo = models.CharField(max_length=128, null=True, blank=True)
    conteudo = models.TextField(max_length=1024)
    data_publicacao = models.DateField(auto_now=True)