from django import forms
from .models import *
from django.utils import timezone


class EstadoSelect(forms.Select):
    def __init__(self, attrs=None):
        estados = [
            ('AC', 'Acre'),
            ('AL', 'Alagoas'),
            ('AP', 'Amapá'),
            ('AM', 'Amazonas'),
            ('BA', 'Bahia'),
            ('CE', 'Ceará'),
            ('DF', 'Distrito Federal'),
            ('ES', 'Espírito Santo'),
            ('GO', 'Goiás'),
            ('MA', 'Maranhão'),
            ('MT', 'Mato Grosso'),
            ('MS', 'Mato Grosso do Sul'),
            ('MG', 'Minas Gerais'),
            ('PA', 'Pará'),
            ('PB', 'Paraíba'),
            ('PR', 'Paraná'),
            ('PE', 'Pernambuco'),
            ('PI', 'Piauí'),
            ('RJ', 'Rio de Janeiro'),
            ('RN', 'Rio Grande do Norte'),
            ('RS', 'Rio Grande do Sul'),
            ('RO', 'Rondônia'),
            ('RR', 'Roraima'),
            ('SC', 'Santa Catarina'),
            ('SP', 'São Paulo'),
            ('SE', 'Sergipe'),
            ('TO', 'Tocantins')
        ]
        super().__init__(attrs, choices=estados)

class SelectSN(forms.Select):
    def __init__(self, attrs=None):
        simnao = [
            ('Sim', 'Sim'),
            ('Não', 'Não'),
        ]
        super().__init__(attrs, choices=simnao)

class SelectCobranca(forms.Select):
    def __init__(self, attrs=None):
        cobrança = [
            ('pix', 'PIX'),
            ('credito', 'Crédito'),
            ('debito', 'Débito'),
            ('dinheiro', 'Dinheiro'),
        ]
        super().__init__(attrs, choices=cobrança)

class LocalidadeForm(forms.ModelForm):
    class Meta:
        model = Localidades
        fields = '__all__'

class ReservaForm(forms.ModelForm):
    class Meta:
        model = Reservas
        fields = '__all__'
        widgets = {
            'quarto_hotel': forms.Select(attrs={'class': 'qty-pessoa'}),
        }

    def clean_data_inicio(self):
        data_inicio = self.cleaned_data['data_inicio']

        # Ajusta a data de início para o final do dia
        data_inicio_final_dia = timezone.make_aware(timezone.datetime.combine(data_inicio, timezone.datetime.max.time()))

        # Obtém a data e hora atuais
        agora = timezone.now()

        # Verifica se a data de início é no passado
        if data_inicio_final_dia <= agora:
            raise forms.ValidationError('A data de início deve ser posterior à data atual.')

        return data_inicio

    def clean_data_fim(self):
        data_fim = self.cleaned_data['data_fim']

        # Adicione sua lógica de validação aqui
        # Exemplo: Verifique se a data de fim é posterior à data de início
        data_inicio = self.cleaned_data.get('data_inicio')
        if data_inicio and data_fim <= data_inicio:
            raise forms.ValidationError('A data de fim deve ser posterior à data de início.')

        return data_fim

    def clean(self):
        cleaned_data = super().clean()
        numero_de_pessoas = cleaned_data.get('numero_de_pessoas')
        if numero_de_pessoas and numero_de_pessoas <= 0:
            raise forms.ValidationError('O número de pessoas deve ser maior que zero.')

        return cleaned_data
    def __init__(self, *args, **kwargs):
        propriedade_hotel = kwargs.pop('propriedade_hotel', None)
        super().__init__(*args, **kwargs)

        if propriedade_hotel:
            self.fields['quarto_hotel'].queryset = ConfigQuartoHotel.objects.filter(propriedade_hotel=propriedade_hotel)

class ParceirosForm(forms.ModelForm):
    cep = forms.CharField(widget=forms.TextInput(attrs={'minlength': '9', 'maxlength': '9', 'onkeyup': 'handleCEP(event)'}))

    class Meta:
        model = Parceiros
        fields = [
            'nome',
            'descricao',
            'sobre',
            'url',
            'logo',
            'ativo',
            'rua',
            'numero',
            'complemento',
            'cep',
            'cidade',
            'uf',
        ]

class FotosForm(forms.ModelForm):
    class Meta:
        model = Fotos
        fields = '__all__'
    
    campos_obrigatorios = [
        'foto1', 'foto2', 'foto3', 'foto4', 'foto5'
    ]

    def clean(self):
        cleaned_data = super().clean()
        # Verifica se algum campo obrigatório está vazio
        for campo in self.campos_obrigatorios:
            if not cleaned_data.get(campo):
                self.add_error(campo, 'Este campo é obrigatório.')
                self.required = True

        return cleaned_data

class PropriedadeApartamentoForm(forms.ModelForm):
    cidade = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    tipo_de_cobranca = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,  # Use CheckboxSelectMultiple para múltiplas escolhas
        choices=[
            ('pix', 'PIX'),
            ('credito', 'Crédito'),
            ('debito', 'Débito'),
            ('dinheiro', 'Dinheiro'),
        ]
    )
    local_de_dormir = forms.CharField(
    max_length=255,
    widget=forms.TextInput(attrs={'placeholder': '1 Cama de Casal, 1 Cama de Solteiro...'})
)

    bebidas_alcoolicas = forms.CharField(widget=SelectSN)
    qtd_banheiros = forms.CharField(widget=forms.NumberInput(attrs={'type': 'number'}))
    estado = forms.CharField(widget=EstadoSelect)
    crianca_permissao = forms.CharField(widget=SelectSN)
    oferece_bercos = forms.CharField(widget=SelectSN)
    serve_cafe_da_manha = forms.CharField(widget=SelectSN)
    tem_estacionamento = forms.CharField(widget=SelectSN)
    permitido_fumar = forms.CharField(widget=SelectSN)
    aceita_pets = forms.CharField(widget=SelectSN)
    festas_eventos_permitidos = forms.CharField(widget=SelectSN)
    codigo_postal = forms.CharField(widget=forms.TextInput(attrs={'minlength': '9', 'maxlength': '9', 'onkeyup': 'handleCEP(event)'}))
    email = forms.EmailField()
    telefone = forms.CharField(widget=forms.TextInput(attrs={'minlength': '15','maxlength': '15', 'onkeyup': 'handlePhone(event)'}))
    def __init__(self, *args, **kwargs):
        super(PropriedadeApartamentoForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'e-mail'
            field.required = False
    class Meta:
        model = PropriedadeApartamento
        exclude = ['anfitriao', 'latitude', 'longitude', 'email_cliente', 'tipo_documento_cliente', 'nome_do_cliente', 'data_nascimento_cliente', 'cpf_cliente', 'check_in', 'check_out', 'endereco_da_propriedade', 'tipo_propriedade']

    campos_obrigatorios = [
        'nome_da_propriedade',
        'pais_regiao',
        'nome_da_rua',
        'numero_residencia',
        'codigo_postal',
        'cidade',
        'estado',
        'local_de_dormir',
        'qtd_hospedes',
        'qtd_banheiros',
        'crianca_permissao',
        'oferece_bercos',
        'tamanho_da_propriedade',
        'tamanho_unidade',
        'o_que_pode_usar_na_propriedade',
        'serve_cafe_da_manha',
        'tem_estacionamento',
        'idiomas',
        'permitido_fumar',
        'bebidas_alcoolicas',
        'aceita_pets',
        'festas_eventos_permitidos',
        'tipo_de_cobranca',
        'valor_da_diaria',
        'email',
        'telefone',
    ]

    def clean(self):
        cleaned_data = super().clean()
        # Verifica se algum campo obrigatório está vazio
        for campo in self.campos_obrigatorios:
            self.required = True
            if not cleaned_data.get(campo):
                self.add_error(campo, 'Este campo é obrigatório.')
                
        return cleaned_data


class PropriedadeCasaTodaForm(forms.ModelForm):
    cidade = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    tipo_de_cobranca = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,  # Use CheckboxSelectMultiple para múltiplas escolhas
        choices=[
            ('pix', 'PIX'),
            ('credito', 'Crédito'),
            ('debito', 'Débito'),
            ('dinheiro', 'Dinheiro'),
        ]
    )
    local_de_dormir = forms.CharField(
    max_length=255,
    widget=forms.TextInput(attrs={'placeholder': '1 Cama de Casal, 1 Cama de Solteiro...'})
)
    bebidas_alcoolicas = forms.CharField(widget=SelectSN)
    estado = forms.CharField(widget=EstadoSelect)
    crianca_permissao = forms.CharField(widget=SelectSN)
    oferece_bercos = forms.CharField(widget=SelectSN)
    serve_cafe_da_manha = forms.CharField(widget=SelectSN)
    tem_estacionamento = forms.CharField(widget=SelectSN)
    permitido_fumar = forms.CharField(widget=SelectSN)
    aceita_pets = forms.CharField(widget=SelectSN)
    festas_eventos_permitidos = forms.CharField(widget=SelectSN)
    codigo_postal = forms.CharField(widget=forms.TextInput(attrs={'minlength': '9', 'maxlength': '9', 'onkeyup': 'handleCEP(event)'}))
    email = forms.EmailField()
    telefone = forms.CharField(widget=forms.TextInput(attrs={'minlength': '15','maxlength': '15', 'onkeyup': 'handlePhone(event)'}))
    def __init__(self, *args, **kwargs):
        super(PropriedadeCasaTodaForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'e-mail'
            field.required = False
    class Meta:
        model = PropriedadeCasaToda
        exclude = ['anfitriao', 'email_cliente', 'tipo_documento_cliente', 'nome_do_cliente', 'data_nascimento_cliente', 'cpf_cliente', 'check_in', 'check_out', 'endereco_da_propriedade', 'tipo_propriedade', 'latitude', 'longitude']

    campos_obrigatorios = [
        'nome_da_propriedade',
        'pais_regiao',
        'nome_da_rua',
        'numero_residencia',
        'codigo_postal',
        'cidade',
        'estado',
        'local_de_dormir',
        'qtd_hospedes',
        'qtd_banheiros',
        'crianca_permissao',
        'oferece_bercos',
        'tamanho_da_propriedade',
        'tamanho_unidade',
        'o_que_pode_usar_na_propriedade',
        'serve_cafe_da_manha',
        'tem_estacionamento',
        'idiomas',
        'permitido_fumar',
        'bebidas_alcoolicas',
        'aceita_pets',
        'festas_eventos_permitidos',
        'tipo_de_cobranca',
        'valor_da_diaria',
        'email',
        'telefone',
    ]

    def clean(self):
        cleaned_data = super().clean()
        # Verifica se algum campo obrigatório está vazio
        for campo in self.campos_obrigatorios:
            self.required = True
            if not cleaned_data.get(campo):
                self.add_error(campo, 'Este campo é obrigatório.')
                
        return cleaned_data

class PropriedadeCasaQuartoForm(forms.ModelForm):
    cidade = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    tipo_de_cobranca = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,  # Use CheckboxSelectMultiple para múltiplas escolhas
        choices=[
            ('pix', 'PIX'),
            ('credito', 'Crédito'),
            ('debito', 'Débito'),
            ('dinheiro', 'Dinheiro'),
        ]
    )
    local_de_dormir = forms.CharField(
    max_length=255,
    widget=forms.TextInput(attrs={'placeholder': '1 Cama de Casal, 1 Cama de Solteiro...'})
)
    bebidas_alcoolicas = forms.CharField(widget=SelectSN)
    estado = forms.CharField(widget=EstadoSelect)
    crianca_permissao = forms.CharField(widget=SelectSN)
    oferece_bercos = forms.CharField(widget=SelectSN)
    serve_cafe_da_manha = forms.CharField(widget=SelectSN)
    tem_estacionamento = forms.CharField(widget=SelectSN)
    permitido_fumar = forms.CharField(widget=SelectSN)
    aceita_pets = forms.CharField(widget=SelectSN)
    festas_eventos_permitidos = forms.CharField(widget=SelectSN)
    codigo_postal = forms.CharField(widget=forms.TextInput(attrs={'minlength': '9', 'maxlength': '9', 'onkeyup': 'handleCEP(event)'}))
    email = forms.EmailField()
    telefone = forms.CharField(widget=forms.TextInput(attrs={'minlength': '15','maxlength': '15', 'onkeyup': 'handlePhone(event)'}))
    def __init__(self, *args, **kwargs):
        super(PropriedadeCasaQuartoForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'e-mail'
            field.required = False
            
    class Meta:
        model = PropriedadeCasaQuarto
        exclude = ['anfitriao', 'latitude', 'longitude', 'email_cliente', 'tipo_documento_cliente', 'nome_do_cliente', 'data_nascimento_cliente', 'cpf_cliente', 'check_in', 'check_out', 'endereco_da_propriedade', 'tipo_propriedade']

    campos_obrigatorios = [
        'nome_da_propriedade',
        'pais_regiao',
        'nome_da_rua',
        'numero_residencia',
        'codigo_postal',
        'cidade',
        'estado',
        'local_de_dormir',
        'qtd_hospedes',
        'qtd_banheiros',
        'crianca_permissao',
        'oferece_bercos',
        'tamanho_da_propriedade',
        'tamanho_unidade',
        'o_que_pode_usar_na_propriedade',
        'serve_cafe_da_manha',
        'tem_estacionamento',
        'idiomas',
        'permitido_fumar',
        'bebidas_alcoolicas',
        'aceita_pets',
        'festas_eventos_permitidos',
        'tipo_de_cobranca',
        'valor_da_diaria',
        'email',
        'telefone',
    ]

    def clean(self):
        cleaned_data = super().clean()
        # Verifica se algum campo obrigatório está vazio
        for campo in self.campos_obrigatorios:
            self.required = True
            if not cleaned_data.get(campo):
                self.add_error(campo, 'Este campo é obrigatório.')
                
        return cleaned_data

class PropriedadeHotelForm(forms.ModelForm):
    cidade = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    tipo_de_cobranca = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,  # Use CheckboxSelectMultiple para múltiplas escolhas
        choices=[
            ('pix', 'PIX'),
            ('credito', 'Crédito'),
            ('debito', 'Débito'),
            ('dinheiro', 'Dinheiro'),
        ]
    )
    local_de_dormir = forms.CharField(
    max_length=255,
    widget=forms.TextInput(attrs={'placeholder': '1 Cama de Casal, 1 Cama de Solteiro...'})
)
    bebidas_alcoolicas = forms.CharField(widget=SelectSN)
    estado = forms.CharField(widget=EstadoSelect)
    crianca_permissao = forms.CharField(widget=SelectSN)
    oferece_bercos = forms.CharField(widget=SelectSN)
    serve_cafe_da_manha = forms.CharField(widget=SelectSN)
    tem_estacionamento = forms.CharField(widget=SelectSN)
    permitido_fumar = forms.CharField(widget=SelectSN)
    aceita_pets = forms.CharField(widget=SelectSN)
    festas_eventos_permitidos = forms.CharField(widget=SelectSN)
    codigo_postal = forms.CharField(widget=forms.TextInput(attrs={'minlength': '9', 'maxlength': '9', 'onkeyup': 'handleCEP(event)'}))
    email = forms.EmailField()
    telefone = forms.CharField(widget=forms.TextInput(attrs={'minlength': '15','maxlength': '15', 'onkeyup': 'handlePhone(event)'}))
    def __init__(self, *args, **kwargs):
        super(PropriedadeHotelForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'e-mail'
            field.required = False
    class Meta:
        model = PropriedadeHotel
        exclude = ['anfitriao', 'classificacao_por_estrelas', 'empresa_faz_gestao_de_propriedades_ou_faz_parte_de_um_grupo_rede', 'nome_empresa_ou_grupo_rede', 'email_cliente', 'tipo_documento_cliente', 'nome_do_cliente', 'data_nascimento_cliente', 'cpf_cliente', 'check_in', 'check_out', 'endereco_da_propriedade', 'latitude', 'longitude', 'grupo_rede']

    campos_obrigatorios = [
        'nome_da_propriedade',
        'pais_regiao',
        'nome_da_rua',
        'numero_residencia',
        'codigo_postal',
        'cidade',
        'estado',
        'local_de_dormir',
        'qtd_hospedes',
        'qtd_banheiros',
        'crianca_permissao',
        'oferece_bercos',
        'tamanho_da_propriedade',
        'tamanho_unidade',
        'o_que_pode_usar_na_propriedade',
        'serve_cafe_da_manha',
        'tem_estacionamento',
        'idiomas',
        'permitido_fumar',
        'bebidas_alcoolicas',
        'aceita_pets',
        'festas_eventos_permitidos',
        'tipo_de_cobranca',
        'valor_da_diaria',
        'email',
        'telefone',
    ]

    def clean(self):
        cleaned_data = super().clean()
        # Verifica se algum campo obrigatório está vazio
        for campo in self.campos_obrigatorios:
            self.required = True
            if not cleaned_data.get(campo):
                self.add_error(campo, 'Este campo é obrigatório.')
                
        return cleaned_data

class ConfigQuartoHotelForm(forms.ModelForm):
    class Meta:
        model = ConfigQuartoHotel
        fields = [
            'propriedade_hotel',
            'tipo_de_unidade',
            'qual_a_quantidade_de_quartos_deste_tipo_que_você_tem',
            'quais_camas_estao_disponiveis_neste_quarto',
            'quntos_hospedes_podem_ficar_neste_quarto',
            'tamanho_do_quarto',
            'tamanho_unidade',
            'permitido_fumar',
            'banheiro_privativo',
            'quais_itens_do_banheiro_esta_disponivel',
            'comodidades_gerais',
            'area_externa_e_vista',
            'comidas_e_bebidas',
            'nome_do_quarto',
            'valor_da_diaria',
        ]

    def __init__(self, *args, **kwargs):
        super(ConfigQuartoHotelForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'e-mail'

    def clean(self):
        cleaned_data = super().clean()
        # Verifica se algum campo obrigatório está vazio
        for campo in self.fields:
            self.required = False
            if not cleaned_data.get(campo):
                self.add_error(campo, 'Este campo é obrigatório.')
                
        return cleaned_data
    
class BlogForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = ['imagem', 'titulo', 'conteudo']

    imagem = forms.ImageField(widget=forms.ClearableFileInput(attrs={'class': 'form-control-file', 'onchange': 'previewImage(this)'}), required=False)
    titulo = forms.CharField(widget=forms.TextInput(attrs={'class': 'titulo', 'placeholder': 'Título'}))
    conteudo = forms.CharField(widget=forms.Textarea(attrs={'class': 'conteudo', 'placeholder': 'Conteúdo'}))