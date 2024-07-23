    localidade = Localidade.objects.get(id_loc=id_loc)
    print(f'Localidade: {localidade}')  # Adicione este print statement
    hoteis = Hotel.objects.filter(id_loc=id_loc).annotate(min_price=Min('quarto__preco'))
    print(f'Hoteis: {hoteis}')  # Adicione este print statement
    return render(request, 'main/hotel.html', {'localidade': localidade, 'hoteis': hoteis})