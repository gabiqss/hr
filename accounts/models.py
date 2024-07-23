from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('O endereço de e-mail deve ser fornecido')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('data_nascimento', '2001-01-01')


        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser deve ter is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser deve ter is_superuser=True')

        return self.create_user(email, password, **extra_fields)
    
    def get_by_natural_key(self, username):
        return self.get(email=username)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    nome = models.CharField(max_length=100)
    sobrenome = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    telefone = models.CharField(max_length=15)
    data_nascimento = models.DateField()
    cpf = models.CharField(max_length=14)
    cnpj = models.CharField(max_length=18, null=True, blank=True)
    rua = models.CharField(max_length=255, null=True, blank=True)
    numero = models.CharField(max_length=10)
    complemento = models.CharField(max_length=255, null=True, blank=True)
    cep = models.CharField(max_length=10)
    cidade = models.CharField(max_length=255)
    uf = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_anfitriao = models.BooleanField(default=False)


    objects = CustomUserManager()
          
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nome']

    def __str__(self):
        return self.nome

