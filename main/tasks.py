from __future__ import absolute_import, unicode_literals
from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.core.exceptions import ObjectDoesNotExist
from ast import literal_eval
from .models import Reservas, PropriedadeApartamento, PropriedadeCasaToda, PropriedadeCasaQuarto, PropriedadeHotel, ConfigQuartoHotel, Fotos
from django.core.files.base import ContentFile
from PIL import Image
import io
from project import settings

@shared_task
def enviar_emails_reserva(reserva_id):
    try:
        reserva = Reservas.objects.get(id=reserva_id)
        print('reserva_id: ', reserva_id)
        print(f"Valor de reserva.propriedade: {reserva.propriedade}")
        propriedade_lista = literal_eval(reserva.propriedade)

        # Verifique o tipo de propriedade e obtenha a instância correta
        tipo_propriedade = str(propriedade_lista[1])

        print(f"Tipo de propriedade após ajuste: {tipo_propriedade}")


        if tipo_propriedade == 'apartamento':
            propriedade = PropriedadeApartamento.objects.get(id=propriedade_lista[0])
        elif tipo_propriedade == 'casa':
            propriedade = PropriedadeCasaToda.objects.get(id=propriedade_lista[0])
        elif tipo_propriedade == 'quarto':
            propriedade = PropriedadeCasaQuarto.objects.get(id=propriedade_lista[0])
        elif tipo_propriedade == 'hotel':
            propriedade = PropriedadeHotel.objects.get(id=propriedade_lista[0])
        elif tipo_propriedade == 'pousada':
            propriedade = PropriedadeHotel.objects.get(id=propriedade_lista[0])
        else:
            raise ValueError(f'Tipo de propriedade inválido: {tipo_propriedade}')

        print(f"Tipo de reserva.propriedade: {type(reserva.propriedade)}")
        print(f"Tipo de reserva.propriedade: {reserva.propriedade}")
        info_propriedade = f"{propriedade.nome_da_rua}, {propriedade.numero_residencia}, {propriedade.cidade} - {propriedade.estado} {propriedade.codigo_postal}"
        info_anfitriao = f"E-mail: {propriedade.anfitriao.email}, telefone: {propriedade.anfitriao.telefone}"
        print(info_propriedade, info_anfitriao)
        subject_hospede = 'Reserva efetuada com sucesso - Hospeda Recife'
        message_hospede = f'''
        Olá {reserva.hospede}!

        Sua reserva foi efetuada com sucesso. Aqui estão os detalhes:

        - Hóspede: {reserva.hospede}
        - Propriedade: {propriedade.nome_da_propriedade}
        - Quarto: {reserva.quarto_hotel if reserva.quarto_hotel else 'Não houve necessidade de escolha de quarto nessa propriedade.'} 
        - Check-in: {reserva.data_inicio.strftime('%d/%m/%Y')}
        - Check-out: {reserva.data_fim.strftime('%d/%m/%Y')}
        - Número de Pessoas: {reserva.numero_de_pessoas}

        Mensagem ao anfitrião: {reserva.mensagem if reserva.mensagem else "Nenhuma mensagem adicional."}
        
        Anfitrião:
        {info_anfitriao}

        Endereço da propriedade:
        {info_propriedade}

        Agradecemos por escolher a Hospeda Recife. Se precisar de alguma assistência ou tiver perguntas adicionais, não hesite em nos contatar.

        Tenha uma ótima estadia!
        '''

        subject_propriedade = 'Nova reserva recebida - Hospeda Recife'
        message_propriedade = f'''
        Olá {propriedade.anfitriao.nome}!

        Você recebeu uma nova reserva para a sua propriedade. Aqui estão os detalhes:

        - Hóspede: {reserva.hospede}
        - Propriedade: {propriedade.nome_da_propriedade}
        - Quarto: {reserva.quarto_hotel if reserva.quarto_hotel else 'Não houve necessidade de escolha de quarto nessa propriedade.'} 
        - Check-in: {reserva.data_inicio.strftime('%d/%m/%Y')}
        - Check-out: {reserva.data_fim.strftime('%d/%m/%Y')}
        - Número de Pessoas: {reserva.numero_de_pessoas}

        Mensagem do hospede: {reserva.mensagem if reserva.mensagem else "Nenhuma mensagem adicional."}

        Endereço da propriedade:
        {info_propriedade}

        Entrar em contato com o hospede:
        E-mail: {reserva.hospede.email}
        Telefone: {reserva.hospede.telefone}
        '''

        print('mensagem hospede: ', message_hospede)
        print('mensagem anf: ', message_propriedade)

        from_email_hospede = 'mailtrap@hospedarecife.com'
        to_email_hospede = [reserva.hospede.email]

        from_email_propriedade = 'mailtrap@hospedarecife.com'
        to_email_propriedade = [propriedade.anfitriao.email]

        try:
            send_mail(subject_hospede, message_hospede, from_email_hospede, to_email_hospede, fail_silently=False)
            send_mail(subject_propriedade, message_propriedade, from_email_propriedade, to_email_propriedade, fail_silently=False)
            print('E-mails enviados com sucesso')
        except Exception as e:
            print(f"Erro ao enviar e-mails: {e}")

    except ObjectDoesNotExist:
        print(f"Reserva com ID {reserva_id} não encontrada.")

@shared_task
def salvar_reserva(reserva_id):
    reserva = Reservas.objects.get(id=reserva_id)
    reserva.save()
    print('sucesso.')

@shared_task
def salvar_apartamento_task(propriedade_data, fotos_data, user_id):
    try:
        propriedade_data['anfitriao_id'] = user_id  # Adicione esta linha

        propriedade = PropriedadeApartamento.objects.create(**propriedade_data)
        print(propriedade)
        fotos = Fotos.objects.create(propriedade_apartamento=propriedade)
        for i, foto_data in enumerate(fotos_data, start=1):
            # Convertendo bytes para um arquivo de imagem (neste exemplo, assumindo JPEG)
            image = Image.open(io.BytesIO(foto_data))
            filename = f'foto{i}.jpg'
            image_content = ContentFile(foto_data, name=filename)
            setattr(fotos, f'foto{i}', image_content)

        fotos.save()

        return True  

    except Exception as e:
        # Lidar com exceções, log ou retornar False, conforme necessário
        print(f"Erro ao salvar apartamento: {e}, id: {user_id}")
        return False
    
@shared_task
def salvar_casa_toda_task(propriedade_data, fotos_data, user_id):
    try:
        propriedade_data['anfitriao_id'] = user_id  # Adicione esta linha

        propriedade = PropriedadeCasaToda.objects.create(**propriedade_data)

        fotos = Fotos.objects.create(propriedade_casa_toda=propriedade)
        for i, foto_data in enumerate(fotos_data, start=1):
            # Convertendo bytes para um arquivo de imagem (neste exemplo, assumindo JPEG)
            image = Image.open(io.BytesIO(foto_data))
            filename = f'foto{i}.jpg'
            image_content = ContentFile(foto_data, name=filename)
            setattr(fotos, f'foto{i}', image_content)

        fotos.save()

        return True  

    except Exception as e:
        # Lidar com exceções, log ou retornar False, conforme necessário
        print(f"Erro ao salvar casa: {e}, id: {user_id}")
        return False
    
@shared_task
def salvar_casa_quarto_task(propriedade_data, fotos_data, user_id):
    try:
        propriedade_data['anfitriao_id'] = user_id  # Adicione esta linha

        propriedade = PropriedadeCasaQuarto.objects.create(**propriedade_data)

        fotos = Fotos.objects.create(propriedade_casa_quarto=propriedade)
        for i, foto_data in enumerate(fotos_data, start=1):
            # Convertendo bytes para um arquivo de imagem (neste exemplo, assumindo JPEG)
            image = Image.open(io.BytesIO(foto_data))
            filename = f'foto{i}.jpg'
            image_content = ContentFile(foto_data, name=filename)
            setattr(fotos, f'foto{i}', image_content)

        fotos.save()

        return True  

    except Exception as e:
        # Lidar com exceções, log ou retornar False, conforme necessário
        print(f"Erro ao salvar quarto: {e}, id: {user_id}")
        return False

@shared_task
def salvar_hotel_task(propriedade_data, fotos_data, user_id):
    try:
        propriedade_data['anfitriao_id'] = user_id  # Adicione esta linha

        propriedade = PropriedadeHotel.objects.create(**propriedade_data)

        fotos = Fotos.objects.create(propriedade_hotel=propriedade)
        for i, foto_data in enumerate(fotos_data, start=1):
            # Convertendo bytes para um arquivo de imagem (neste exemplo, assumindo JPEG)
            image = Image.open(io.BytesIO(foto_data))
            filename = f'foto{i}.jpg'
            image_content = ContentFile(foto_data, name=filename)
            setattr(fotos, f'foto{i}', image_content)

        fotos.save()

        return True  

    except Exception as e:
        # Lidar com exceções, log ou retornar False, conforme necessário
        print(f"Erro ao salvar hotel: {e}, id: {user_id}")
        return False
    
@shared_task
def salvar_pousada_task(propriedade_data, fotos_data, user_id):
    try:
        propriedade_data['anfitriao_id'] = user_id  # Adicione esta linha
        print(propriedade_data['tipo_propriedade'], propriedade_data['anfitriao_id'])
        propriedade = PropriedadeHotel.objects.create(**propriedade_data)

        fotos = Fotos.objects.create(propriedade_hotel=propriedade)
        for i, foto_data in enumerate(fotos_data, start=1):
            # Convertendo bytes para um arquivo de imagem (neste exemplo, assumindo JPEG)
            image = Image.open(io.BytesIO(foto_data))
            filename = f'foto{i}.jpg'
            image_content = ContentFile(foto_data, name=filename)
            setattr(fotos, f'foto{i}', image_content)

        fotos.save()

        return True  

    except Exception as e:
        # Lidar com exceções, log ou retornar False, conforme necessário
        print(f"Erro ao salvar pousada: {e}, id: {user_id}")
        return False

@shared_task
def salvar_config_quarto_task(propriedade_data, fotos_data, user_id, hotel_id):
    try:
        propriedade = ConfigQuartoHotel.objects.create(propriedade_hotel=hotel_id, **propriedade_data)

        fotos = Fotos.objects.create(config_quarto_hotel=propriedade)
        for i, foto_data in enumerate(fotos_data, start=1):
            # Convertendo bytes para um arquivo de imagem (neste exemplo, assumindo JPEG)
            image = Image.open(io.BytesIO(foto_data))
            filename = f'foto{i}.jpg'
            image_content = ContentFile(foto_data, name=filename)
            setattr(fotos, f'foto{i}', image_content)

        fotos.save()
        print(f"Config salva com sucesso, id: {user_id}")
        return True  

    except Exception as e:
        # Lidar com exceções, log ou retornar False, conforme necessário
        print(f"Erro ao salvar config: {e}, id: {user_id}")
        return False

