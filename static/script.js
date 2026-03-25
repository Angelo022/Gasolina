document.addEventListener('DOMContentLoaded', function() {
    // Definindo a data e a hora atuais
    const today = new Date();

    // Verifica se os elementos existem antes de acessar
    const dataInput = document.getElementById('data');
    const horaInput = document.getElementById('horaInput');
    if (dataInput && horaInput) {
        dataInput.value = today.toISOString().split('T')[0]; // Data no formato YYYY-MM-DD
        horaInput.value = today.toTimeString().split(' ')[0].substring(0, 5); // Hora no formato HH:MM

        // Atualiza a hora a cada minuto
        setInterval(() => {
            const now = new Date();
            horaInput.value = now.toTimeString().split(' ')[0].substring(0, 5); // Atualiza a hora
        }, 60000); // 60000 ms = 1 minuto
    }

    // Lógica para habilitar/desabilitar o campo de Número de Controle
    const tipoAbastecimentoSelect = document.getElementById('tipoAbastecimentoSelect');
    const numeroControleInput = document.getElementById('numeroControleInput');
    if (tipoAbastecimentoSelect && numeroControleInput) {
        tipoAbastecimentoSelect.addEventListener('change', function() {
            if (this.value === 'externo') {
                numeroControleInput.disabled = true; // Desabilita o campo
                numeroControleInput.value = ''; // Limpa o campo
            } else {
                numeroControleInput.disabled = false; // Habilita o campo
            }
        });
    }

    // Lista de motoristas para autocomplete
    const motoristas = [
        "ADEMILSON FRANCISCO DAMACENO",
        "ADRIANO ARMELIN",
        "ALTAIR ROBERTO DA SILVA",
        "ANA PAULA VIEIRA",
        "ANGELINO APARECIDO ALVES",
        "ARLISON DA SILVA SOUZA",
        "ANTONIO CEZAR TELES DOS SANTOS",
        "BENEDITO LEOPOLDO ALVES",
        "CARLOS ROBERTO MERISSE",
        "CARLA ISABEL SANTOS VENCESLAU",
        "CLAUDIA SIMONE DA CRUZ",
        "CLAUDIOMAR SILVA NOVAIS",
        "DANYLO PEGORARO MARCELO",
        "DHEMERSON HIAGO S. CASTRO",
        "DIVANILSON LOPES DA SILVA",
        "ERIWELTON MARTINS DE SOUZA PAIXÃO",
        "EDSONIA DE BARROS RODRIGUES",
        "ELAINE APARECIDA MACHADO DOS SANTOS",
        "FABIANO SOUZA DE FRANCA",
        "FABIO SOUZA LIMA",
        "FABIO ROGÉRIO DE QUEIROZ",
        "FRANCISCO CARLOS B ALMEIDA",
        "GERALDO MARCELINO DE FREITAS",
        "GERALDO SOARES DE OLIVEIRA",
        "GERSON DOS REIS",
        "GERFESSON LIMA SANTOS",
        "GILMAR JOSÉ DE SOUZA",
        "GILMAR VIEIRA DOS SANTOS",
        "GILMAR CLEMENTE DO NASCIMENTO",
        "GILVANIR PEREIRA ROCHA",
        "GENILDO DOMINGOS",
        "IVAN PEREIRA DA SILVA",
        "IVANILDO RODRIGUES LINS",
        "JAQUELINE SOUZA NASCIMENTO",
        "JHONATAN ALVES DA SILVA",
        "JOAO BATISTA DE OLIVEIRA",
        "JOAO BAPTISTA",
        "JORGE DOS SANTOS",
        "JORGE RODRIGUES DE SOUZA",
        "JOSE APARECIDO CORDEIRO",
        "JOSE CORREIA DOS SANTOS",
        "JOSE GERALDO M. DA SILVA",
        "JOSE LOURENÇO PEREIRA",
        "JOSE RAIMUNDO NASCIMENTO",
        "JOSE SILVESTRE DA SILVA",
        "JERRY ADRIANO DA SILVA",
        "JOSE APARECIDO DE LIMA VIEIRA",
        "JOSE CARLOS COSTA",
        "JOSE FRANCISCO DOS SANTOS JUNIOR",
        "JOSE GILDO SOARES GOMES",
        "JULIANO DA ROCHA",
        "JULIANO ALVES",
        "JULIO CESAR",
        "KATIA C DE OLIVEIRA SILVA",
        "KELIANO DE LIRA LIMA",
        "KELLY ARAUJO ROCHA",
        "LUIS FERNANDO DA SILVA CARDOSO",
        "LUIS CARLOS BARBATE",
        "MAILTON T. DE OLIVEIRA",
        "MARIA DO CARMO SILVA FERREIRA",
        "MARCELO ROQUE DE GOES",
        "MARCO AURELIO VIEIRA",
        "MARCOS GOMES DA SILVA",
        "MARCO ANTONIO DA SILVA",
        "MARINALDO JOSE DA SILVA",
        "MAURINDO ALVES DE OLIVEIRA",
        "MAURO SERGIO BARBOSA",
        "MICHAEL FILIPE BATISTA LEITE",
        "MIRIAN GISELI BIASOLI VIEIRA",
        "NELSON APARECIDO DA SILVA",
        "ODAIR MULLER DE OLIVEIRA",
        "OSMAR SOARES BISPO",
        "PAULO CESAR MARCELLO",
        "PAULO DE SOUZA SANTOS",
        "PAULO CESAR LIMA DA SILVA",
        "PAULO ROBERTO DA SILVA",
        "PEDRO DOS SANTOS LOPES",
        "PEDRO PEREIRA DA SILVA",
        "PAULO RENATO TODÃO",
        "RAIMUNDO BATISTA SOARES",
        "ROBSON AP. MENEGHESSO",
        "RUAN CARLOS RODRIGUES",
        "REGIANI MARLI PAULO MORI",
        "ROSANGELA RODRIGUES PINTO DA SILVA",
        "SEBASTIÃO TRIUNFO FILHO",
        "SILVIO LUIZ",
        "TANIA CRISTINA B. DA SILVA",
        "VALDEY OLIMPIO",
        "VALDIR DA SILVA BARIANI",
        "VALDEMIR SANTOS DE SANTANA",
        "VANDERLEY F. DA SILVA",
        "VILSON PEREIRA DA COSTA",
        "VLADIMIR ARAUJO",
        "WAGNER APARECIDO PRETE",
        "WALMIR JOSE ROSSI",
        "WELLINGTON PEREIRA DA SILVA",
        "WESLEI ALVES DA SILVA"
    ];

    // Lista de números de ônibus para autocomplete
    const numerosOnibus = [
        "101E","102E","103E","104","107","108","109","110","111E","112","113","114","115","116","117","118",
        "200","201","202","203","300E","301E","302E","303E","304E","305E","306E","307E","308E","700","701",
        "801","802","1000","1001","1100","1200","1600","1700","1800","1900","2200","2400","2600","2700",
        "2800","2900","4000","4100","4200","4300","4400","4600","6400","6500","6600","6700","7001","7002",
        "7003","7004","8100","8200","8300","8400","8500","8600","8700","8900","9000","9100","9200","9300",
        "9400","9500","9600","9900","1300","1400","2000","2001","2002","2003","2300","3000E","3100","3200",
        "3300","3400","3512","3600E","3700E","3800E","3900E","4700","4800","4900","5000","5100","5200",
        "5300E","5412","5512","5800","5900","6000","6100","6800E","6900E","7000E","7100E","7200E","7300",
        "7400E","7500E","7600E","7700","7800","7900","8000","8800E","9700"
    ];

    // Função para criar autocomplete para um input e lista de opções
    function setupAutocomplete(inputElement, optionsList) {
        let autocompleteContainer = inputElement.parentNode.querySelector('.autocomplete-items');
        if (!autocompleteContainer) {
            autocompleteContainer = document.createElement('div');
            autocompleteContainer.setAttribute('class', 'autocomplete-items');
            inputElement.parentNode.appendChild(autocompleteContainer);
        }

        inputElement.addEventListener('input', function() {
            const val = this.value.toUpperCase();
            autocompleteContainer.innerHTML = '';
            if (!val) {
                return false;
            }
            const filtered = optionsList.filter(item => item.toUpperCase().startsWith(val));
            filtered.forEach(function(item) {
                const itemDiv = document.createElement('div');
                itemDiv.innerHTML = "<strong>" + item.substr(0, val.length) + "</strong>";
                itemDiv.innerHTML += item.substr(val.length);
                itemDiv.addEventListener('click', function() {
                    inputElement.value = item;
                    autocompleteContainer.innerHTML = '';
                });
                autocompleteContainer.appendChild(itemDiv);
            });
        });

        document.addEventListener('click', function(e) {
            if (e.target !== inputElement) {
                autocompleteContainer.innerHTML = '';
            }
        });
    }

    // Configura autocomplete para motorista
    const motoristaInput = document.getElementById('motoristaInput');
    if (motoristaInput) {
        setupAutocomplete(motoristaInput, motoristas);
    }

    // Configura autocomplete para número do ônibus
    const numeroOnibusInput = document.getElementById('numeroOnibusInput');
    if (numeroOnibusInput) {
        setupAutocomplete(numeroOnibusInput, numerosOnibus);
    }

    // Função para enviar dados do abastecimento
    const submitGastoBtn = document.getElementById('submitGasto');
    if (submitGastoBtn) {
        submitGastoBtn.addEventListener('click', function() {
            const numeroOnibusInput = document.getElementById('numeroOnibusInput');
            const litrosInput = document.getElementById('litrosInput');
            const motoristaInput = document.getElementById('motoristaInput');
            const numeroControleInput = document.getElementById('numeroControleInput');
            const quemAbasteceuInput = document.getElementById('quemAbasteceuInput');
            const quilometragemInput = document.getElementById('quilometragemInput');
            const horaInput = document.getElementById('horaInput');
            const dataInput = document.getElementById('data');
            const tipoFrotaSelect = document.getElementById('tipoFrotaSelect');
            const tipoAbastecimentoSelect = document.getElementById('tipoAbastecimentoSelect');

            if (!numeroOnibusInput || !litrosInput || !motoristaInput || !numeroControleInput || !quemAbasteceuInput || !quilometragemInput || !horaInput || !dataInput || !tipoFrotaSelect || !tipoAbastecimentoSelect) {
                console.error('Um ou mais elementos do formulário não foram encontrados.');
                return;
            }

            const data = {
                numeroOnibus: numeroOnibusInput.value,
                litros: litrosInput.value,
                motorista: motoristaInput.value,
                numeroControle: numeroControleInput.value,
                quemAbasteceu: quemAbasteceuInput.value,
                quilometragem: quilometragemInput.value,
                hora: horaInput.value,
                data: dataInput.value,
                tipoDeFrota: tipoFrotaSelect.value,
                tipoAbastecimento: tipoAbastecimentoSelect.value
            };

            fetch('/api/gastos', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Erro na resposta do servidor');
                }
                return response.json();
            })
            .then(data => {
                const messageElement = document.getElementById('message');
                if (messageElement) {
                    messageElement.innerText = "Abastecimento adicionado com sucesso";
                }
                // Limpar formulário
                if (numeroOnibusInput) numeroOnibusInput.value = '';
                if (litrosInput) litrosInput.value = '';
                if (motoristaInput) motoristaInput.value = '';
                if (numeroControleInput) numeroControleInput.value = '';
                if (quemAbasteceuInput) quemAbasteceuInput.value = '';
                if (quilometragemInput) quilometragemInput.value = '';
                if (horaInput) horaInput.value = '';
                if (dataInput) dataInput.value = new Date().toISOString().split('T')[0];
                if (tipoFrotaSelect) tipoFrotaSelect.selectedIndex = 0;
                if (tipoAbastecimentoSelect) tipoAbastecimentoSelect.selectedIndex = 0;
            })
            .catch(error => {
                console.error('Error:', error);
            });
        });
    }

    // Função para reabastecer combustível
    const submitReabastecerBtn = document.getElementById('submitReabastecer');
    if (submitReabastecerBtn) {
        submitReabastecerBtn.addEventListener('click', function() {
            const litrosReabastecerInput = document.getElementById('litrosReabastecerInput');
            if (!litrosReabastecerInput) {
                console.error('Elemento litrosReabastecerInput não encontrado.');
                return;
            }
            const litrosReabastecer = litrosReabastecerInput.value;

            fetch('/api/reabastecer', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ litros: litrosReabastecer })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Erro na resposta do servidor');
                }
                return response.json();
            })
            .then(data => {
                document.getElementById('message').innerText = "Reabastecimento realizado com sucesso. Nova quantidade: " + data.nova_quantidade;
                litrosReabastecerInput.value = '';
                atualizarQuantidadeDisponivel();
            })
            .catch(error => {
                console.error('Error:', error);
            });
        });
    }

    // Função para obter e exibir a quantidade de combustível disponível
    function atualizarQuantidadeDisponivel() {
        fetch('/api/combustivel/disponivel')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Erro ao obter dados do servidor');
                }
                return response.json();
            })
            .then(data => {
                const quantidadeDisponivelSpan = document.getElementById('quantidadeDisponivel');
                if (quantidadeDisponivelSpan) {
                    quantidadeDisponivelSpan.innerText = data.quantidade;
                }
            })
            .catch(error => {
                console.error('Erro ao obter quantidade disponível:', error);
                const quantidadeDisponivelSpan = document.getElementById('quantidadeDisponivel');
                if (quantidadeDisponivelSpan) {
                    quantidadeDisponivelSpan.innerText = 'Erro ao obter dados';
                }
            });
    }

    // Chama a função ao carregar a página
    atualizarQuantidadeDisponivel();
});

