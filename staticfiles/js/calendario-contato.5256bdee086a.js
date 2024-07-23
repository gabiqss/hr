console.log('Script is running');
$(document).ready(function() {
    var datasOcupadas;
    var quartoId = $('#contato_reserva_form').data('quarto-id'); 

    // Obter as datas ocupadas do backend
    $.ajax({
        url: '/obter_datas_ocupadas/' + quartoId + '/',  // Adicione o id_quarto aqui
        method: 'GET',
        success: function(response) {
            datasOcupadas = response.datas_ocupadas;
            console.log('Datas Ocupadas:', datasOcupadas);
            
            // Inicializar datepickers
            $('#checkin').datepicker({
                dateFormat: 'dd/mm/yy',
                startDate: '0d',
                minDate: '0', // Impede seleção de datas passadas
                beforeShowDay: function(date) {
                    var dateString = $.datepicker.formatDate('yy-mm-dd', date);
                    return [!datasOcupadas[dateString]];
                }
            });

            $('#checkout').datepicker({
                dateFormat: 'dd/mm/yy',
                startDate: '0d',
                minDate: '0', // Impede seleção de datas passadas
                beforeShowDay: function(date) {
                    var dateString = $.datepicker.formatDate('yy-mm-dd', date);
                    return [!datasOcupadas[dateString]];
                }
            });

            // Inicializar o calendário
            $('calendario').fullCalendar({
                header: {
                    left: 'prev,next today',
                    center: 'title',
                    right: 'month,agendaWeek,agendaDay'
                },
                locale: 'pt-br',  // Define o idioma como português
                events: function(start, end, timezone, callback) {
                    // Transformar datas ocupadas em um formato aceitável pelo FullCalendar
                    var eventos = [];
                    for (var data in datasOcupadas) {
                        eventos.push({
                            title: datasOcupadas[data],
                            start: data,
                            end: data,
                            allDay: true
                        });
                    }
                    callback(eventos);
                },
                eventRender: function(event, element) {
                    if (event.title == 'Ocupada') {
                        element.css('background-color', '#FF8888');
                    }
                }
            });
        }
    });
});