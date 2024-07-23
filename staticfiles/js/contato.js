
document.getElementById('contato_reserva_form').addEventListener('submit', function(event) {
    event.preventDefault();
    var quartoId = this.dataset.quartoId;
    var url = `/contato/${quartoId}/`;
    var nome = document.getElementById('nome').value;
    var sobrenome = document.getElementById('sobrenome').value;
    var email = document.getElementById('email').value;
    var telefone = document.getElementById('telefone').value;
    var endereco = document.getElementById('endereco').value;
    var mensagem = document.getElementById('mensagem').value;
    var checkin = document.getElementById('checkin').value;
    var checkout = document.getElementById('checkout').value;

    var formData = new FormData();
    formData.append('nome', nome);
    formData.append('sobrenome', sobrenome);
    formData.append('email', email);
    formData.append('telefone', telefone);
    formData.append('endereco', endereco);
    formData.append('mensagem', mensagem);
    formData.append('checkin', checkin);
    formData.append('checkout', checkout);

    // Adicione esta linha para enviar o id_quarto corretamente
    formData.append('id_quarto', quartoId); 
    console.log(quartoId)
    // Enviar a requisição
    fetch(url, {
        method: 'POST',
        body: formData
    }).then(function(response) {
        return response.json();
    }).then(function(data) {
        // Verificar a resposta
        if (data.success) {
            // Redirecionar para a página de sucesso após 5 segundos
            setTimeout(function() {
                window.location.href = '/sucesso/';
            }, 5000); // 5000 milissegundos = 5 segundos
        } else {
            // Tratar o caso em que houve um erro ao salvar os dados (opcional)
        }
    });
});

