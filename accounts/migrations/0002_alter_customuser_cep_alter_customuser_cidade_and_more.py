# Generated by Django 4.2.5 on 2023-11-03 17:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='cep',
            field=models.CharField(max_length=10),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='cidade',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='cpf',
            field=models.CharField(max_length=14),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='data_nascimento',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='numero',
            field=models.CharField(max_length=10),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='sobrenome',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='telefone',
            field=models.CharField(max_length=15),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='uf',
            field=models.CharField(max_length=255),
        ),
    ]