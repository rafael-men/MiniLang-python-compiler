// MiniLang - Programa Válido
// Demonstra while, for (3 cláusulas), precedência e print


limite = 5;
total = 0;

// 1. Laço while: acumula somatório
i = 1;
while (i <= limite) {
    total = total + i;
    i = i + 1;
}

print(total);

// 2. Precedência de operadores: multiplicação antes da soma
resultado = total + 2 * 3;
print(resultado);

// 3. Laço for: cálculo do fatorial de 4
// Exige as três cláusulas: (inicialização; condição; atualização)
fatorial = 1;
for (n = 1; n <= 4; n = n + 1) {
    fatorial = fatorial * n;
}

print(fatorial);