document.addEventListener('DOMContentLoaded', function () {
    // Seleciona TODOS os botões que têm a classe .toggle-saldo-btn
    const toggleButtons = document.querySelectorAll('.toggle-saldo-btn');
    
    // Se não encontrar nenhum botão, o script para por aqui.
    if (toggleButtons.length === 0) return;

    // 1. Define a URL correta do backend diretamente no script.
    // Isso resolve o erro 'undefined'.
    const url = '/toggle-card-visibility';
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    // Adiciona um 'ouvinte' de clique para cada um dos botões encontrados
    toggleButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Pega as informações do botão que foi clicado
            const cardName = this.dataset.cardName;
            const cardValue = this.dataset.cardValue;

            // Encontra os elementos de valor e ícone correspondentes pelo ID
            const valorElement = document.getElementById(`${cardName}-valor`);
            const iconElement = document.getElementById(`${cardName}-icon`);

            if (!valorElement || !iconElement) {
                console.error(`Elementos para o card '${cardName}' não foram encontrados.`);
                return;
            }

            // Inverte a visibilidade no frontend INSTANTANEAMENTE
            const isCurrentlyVisible = !iconElement.classList.contains('bi-eye');

            if (isCurrentlyVisible) {
                valorElement.textContent = 'R$ ••••••';
                iconElement.classList.remove('bi-eye-slash');
                iconElement.classList.add('bi-eye');
            } else {
                valorElement.textContent = cardValue;
                iconElement.classList.remove('bi-eye');
                iconElement.classList.add('bi-eye-slash');
            }

            // 2. Envia a mudança para o backend em segundo plano usando a URL correta
            fetch(url, { 
                method: 'POST', 
                headers: { 
                    'Content-Type': 'application/json', 
                    'X-CSRFToken': csrfToken 
                },
                body: JSON.stringify({ card: cardName })
            })
            .then(response => {
                if (!response.ok) {
                    // Se o backend retornar um erro, loga no console do navegador
                    console.error('Falha ao salvar a preferência de visibilidade no servidor.');
                }
            })
            .catch(error => console.error('Erro de comunicação com o servidor:', error));
        });
    });
});