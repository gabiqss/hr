# Generated by Django 4.2.5 on 2023-11-17 19:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_remove_propriedadeapartamento_link_wpp_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='reservas',
            name='quarto_hotel',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='main.configquartohotel'),
        ),
    ]
