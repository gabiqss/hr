from django import template
from django.template.defaultfilters import stringfilter
from django.utils.html import escape
import requests

register = template.Library()

@register.filter(name='get_random_image')
@stringfilter
def get_random_image(cidade, estado):
    termo_busca = f'{cidade} {estado}'
    response = requests.get(f'https://source.unsplash.com/800x600/?{escape(termo_busca)}')
    print(termo_busca)
    if response.status_code == 200:
        return response.url
    else:
        return 'static/images/seta-em-loop.png'
