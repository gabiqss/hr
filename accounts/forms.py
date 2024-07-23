from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser
from django.contrib.auth import authenticate
from django.utils import timezone
from dateutil.relativedelta import relativedelta

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

class CustomUserCreationForm(UserCreationForm):
    data_nascimento = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    uf = forms.CharField(widget=EstadoSelect)
    class CPFFormWidget(forms.TextInput):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.attrs.update({
                'minlength': '14',
                'maxlength': '14',
                'onkeyup': 'handleCPF(event)'
            })
    cpf = forms.CharField(widget=CPFFormWidget)
    telefone = forms.CharField(widget=forms.TextInput(attrs={'minlength': '15','maxlength': '15', 'onkeyup': 'handlePhone(event)'}))
    # No seu formulário Django, adicione o seguinte campo
    cep = forms.CharField(widget=forms.TextInput(attrs={'minlength': '9', 'maxlength': '9', 'onkeyup': 'handleCEP(event)'}))
    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'e-mail'
    class Meta:
        model = CustomUser
        fields = ['email', 'nome', 'sobrenome', 'data_nascimento', 'cpf', 'telefone', 'rua', 'numero', 'complemento', 'cep', 'cidade', 'uf', 'password1', 'password2']

    def clean_data_nascimento(self):
        data_nascimento = self.cleaned_data.get('data_nascimento')
        idade_minima = timezone.now().date() - relativedelta(years=18)
        if data_nascimento >= idade_minima:
            raise forms.ValidationError("Você deve ter pelo menos 18 anos para se cadastrar.")
        return data_nascimento

class AnfitriaoCreationForm(UserCreationForm):
    # No seu formulário Django, adicione o seguinte campo
    cep = forms.CharField(widget=forms.TextInput(attrs={'minlength': '9', 'maxlength': '9', 'onkeyup': 'handleCEP(event)'}))

    data_nascimento = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    uf = forms.CharField(widget=EstadoSelect)
    telefone = forms.CharField(widget=forms.TextInput(attrs={'minlength': '15','maxlength': '15', 'onkeyup': 'handlePhone(event)'}))
    class CPFFormWidget(forms.TextInput):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.attrs.update({
                'minlength': '14',
                'maxlength': '14',
                'onkeyup': 'handleCPF(event)'
            })
    class CNPJFormWidget(forms.TextInput):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.attrs.update({
                'minlength': '18',
                'maxlength': '18',
                'onkeyup': 'handleCNPJ(event)'
            })
    cpf = forms.CharField(widget=CPFFormWidget)
    cnpj = forms.CharField(widget=CNPJFormWidget)

    def __init__(self, *args, **kwargs):
        super(AnfitriaoCreationForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'e-mail'
    class Meta:
        model = CustomUser
        fields = ['email', 'nome', 'sobrenome', 'data_nascimento', 'cpf', 'cnpj', 'telefone', 'rua', 'numero', 'complemento', 'cep', 'cidade', 'uf', 'password1', 'password2']

    def clean_data_nascimento(self):
        data_nascimento = self.cleaned_data.get('data_nascimento')
        idade_minima = timezone.now().date() - relativedelta(years=18)
        if data_nascimento >= idade_minima:
            raise forms.ValidationError("Você deve ter pelo menos 18 anos para se cadastrar.")
        return data_nascimento

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_anfitriao = True
        if commit:
            user.save()
        return user

class AnfitriaoLoginForm(AuthenticationForm):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    def __init__(self, *args, **kwargs):
        super(AnfitriaoLoginForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'e-mail'
    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        if not authenticate(email=email, password=password):
            raise forms.ValidationError("Email e/ou senha inválidos.")

        return cleaned_data

class CustomAuthenticationForm(AuthenticationForm):
    class Meta:
        model = CustomUser
        fields = ['email', 'password']
    def __init__(self, *args, **kwargs):
        super(CustomAuthenticationForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'e-mail'
    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        if not authenticate(email=email, password=password):
            raise forms.ValidationError("Email e/ou senha inválidos.")

        return cleaned_data



