# Generated by Django 4.2.5 on 2023-11-17 19:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_reservas_quarto_hotel'),
    ]

    operations = [
        migrations.AlterField(
            model_name='configquartohotel',
            name='foto',
            field=models.ImageField(blank=True, null=True, upload_to='propriedades/'),
        ),
    ]