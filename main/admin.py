from django.contrib import admin
from .models import Localidades, Parceiros, PropriedadeApartamento, PropriedadeCasaToda, PropriedadeCasaQuarto, PropriedadeHotel, ConfigQuartoHotel, Reservas, Fotos

# Criar classes ModelAdmin para cada modelo
class LocalidadesAdmin(admin.ModelAdmin):
    list_display = ['localizacao', 'estado', 'qty_hotel']

class ParceirosAdmin(admin.ModelAdmin):
    list_display = ['nome', 'descricao', 'ativo']

class PropriedadeApartamentoAdmin(admin.ModelAdmin):
    list_display = ['nome_da_propriedade', 'anfitriao', 'cidade', 'estado', 'valor_da_diaria']
    list_filter = ['cidade', 'estado']

class PropriedadeCasaTodaAdmin(admin.ModelAdmin):
    list_display = ['nome_da_propriedade', 'anfitriao', 'cidade', 'estado', 'valor_da_diaria']
    list_filter = ['cidade', 'estado']

class PropriedadeCasaQuartoAdmin(admin.ModelAdmin):
    list_display = ['nome_da_propriedade', 'anfitriao', 'cidade', 'estado', 'valor_da_diaria']
    list_filter = ['cidade', 'estado']

class PropriedadeHotelAdmin(admin.ModelAdmin):
    list_display = ['nome_da_propriedade', 'anfitriao', 'cidade', 'estado', 'valor_da_diaria', 'classificacao_por_estrelas']
    list_filter = ['cidade', 'estado']

class ConfigQuartoHotelAdmin(admin.ModelAdmin):
    list_display = ['propriedade_hotel', 'tipo_de_unidade', 'valor_da_diaria']

class ReservasAdmin(admin.ModelAdmin):
    list_display = ['hospede', 'propriedade', 'data_inicio', 'data_fim', 'numero_de_pessoas']
    list_filter = ['data_inicio', 'data_fim']

class FotosAdmin(admin.ModelAdmin):
    list_display = ['propriedade_apartamento', 'propriedade_casa_toda', 'propriedade_casa_quarto', 'propriedade_hotel']

admin.site.register(Localidades, LocalidadesAdmin)
admin.site.register(Parceiros, ParceirosAdmin)
admin.site.register(PropriedadeApartamento, PropriedadeApartamentoAdmin)
admin.site.register(PropriedadeCasaToda, PropriedadeCasaTodaAdmin)
admin.site.register(PropriedadeCasaQuarto, PropriedadeCasaQuartoAdmin)
admin.site.register(PropriedadeHotel, PropriedadeHotelAdmin)
admin.site.register(ConfigQuartoHotel, ConfigQuartoHotelAdmin)
admin.site.register(Reservas, ReservasAdmin)
admin.site.register(Fotos, FotosAdmin)
