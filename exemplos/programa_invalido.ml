// MiniLang - Programa Inválido
// Demonstra erro sintático: laço for mal formado

acumulador = 0;

// ERRO DE SINTAXE:
// Na MiniLang, o for exige obrigatoriamente três cláusulas:
// for (inicializacao; condicao; atualizacao)
// No código abaixo, a cláusula de atualização foi omitida:
for (i = 0; i < 10) {
    acumulador = acumulador + i;
}

print(acumulador);