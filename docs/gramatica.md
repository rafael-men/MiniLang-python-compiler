# Especificação da Gramática - MiniLang

Este documento descreve a sintaxe formal, os tokens léxicos, a tabela de precedência e associatividade de operadores, bem como exemplos de programas válidos e inválidos na linguagem **MiniLang**.

## 1. Lexer (Analisador Léxico)

O analisador léxico da MiniLang é responsável por transformar o fluxo de caracteres de entrada em uma sequência de tokens tipados, registrando com precisão a **linha** e a **coluna** de cada token para fins de rastreamento e mensagens de erro.

### 1.1 Tabela de Tokens

| Tipo de Token | Padrão / Expressão Regular | Exemplo | Descrição |
| :--- | :--- | :--- | :--- |
| `IF` | `if` | `if` | Palavra reservada condicional |
| `ELSE` | `else` | `else` | Palavra reservada alternativa |
| `WHILE` | `while` | `while` | Palavra reservada de laço while |
| `FOR` | `for` | `for` | Palavra reservada de laço for |
| `PRINT` | `print` | `print` | Palavra reservada de comando de saída |
| `TRUE` | `true` | `true` | Literal booleano verdadeiro |
| `FALSE` | `false` | `false` | Literal booleano falso |
| `ID` | `[a-zA-Z_][a-zA-Z0-9_]*` | `total`, `x`, `_indice`, `fora` | Identificador de variável |
| `NUM` | `[0-9]+` | `0`, `42`, `100` | Literal numérico inteiro |
| `PLUS` | `+` | `+` | Operador aritmético de adição |
| `MINUS` | `-` | `-` | Operador aritmético de subtração |
| `STAR` | `*` | `*` | Operador aritmético de multiplicação |
| `SLASH` | `/` | `/` | Operador aritmético de divisão |
| `EQ` | `==` | `==` | Operador relacional de igualdade |
| `NEQ` | `!=` | `!=` | Operador relacional de diferença |
| `LT` | `<` | `<` | Operador relacional menor que |
| `LTE` | `<=` | `<=` | Operador relacional menor ou igual a |
| `GT` | `>` | `>` | Operador relacional maior que |
| `GTE` | `>=` | `>=` | Operador relacional maior ou igual a |
| `ASSIGN` | `=` | `=` | Operador de atribuição |
| `LPAREN` | `(` | `(` | Abre parênteses |
| `RPAREN` | `)` | `)` | Fecha parênteses |
| `LBRACE` | `{` | `{` | Abre chaves (início de bloco) |
| `RBRACE` | `}` | `}` | Fecha chaves (fim de bloco) |
| `SEMICOLON` | `;` | `;` | Ponto e vírgula delimitador |
| `EOF` | Fim da cadeia | - | Fim do arquivo de entrada |

> **Nota:** Comentários iniciados por `//` até o final da linha e caracteres de espaçamento (` `, `\t`, `\r`, `\n`) são ignorados pelo Lexer.

---

### 1.2 Tabela de Transições do Autômato Finito Determinístico (AFD)

O autômato léxico opera a partir do estado inicial $S_0$:

| Estado Atual | Caractere de Entrada | Próximo Estado | Ação / Token Produzido |
| :--- | :--- | :--- | :--- |
| **$S_0$ (Inicial)** | Espaço, `\t`, `\r` | $S_0$ | Ignora caractere, avança coluna |
| **$S_0$** | `\n` | $S_0$ | Ignora, incrementa linha e reseta coluna = 1 |
| **$S_0$** | `/` | $S_{\text{barra}}$ | Espia próximo caractere |
| **$S_0$** | `=` | $S_{\text{igual}}$ | Espia próximo caractere |
| **$S_0$** | `!` | $S_{\text{excl}}$ | Espia próximo caractere |
| **$S_0$** | `<` | $S_{\text{menor}}$ | Espia próximo caractere |
| **$S_0$** | `>` | $S_{\text{maior}}$ | Espia próximo caractere |
| **$S_0$** | `+`, `-`, `*`, `(`, `)`, `{`, `}`, `;` | $S_0$ | Retorna token do operador/delimitador simples |
| **$S_0$** | `[0-9]` | $S_{\text{num}}$ | Acumula dígitos numéricos |
| **$S_0$** | `[a-zA-Z_]` | $S_{\text{id}}$ | Acumula caracteres alfanuméricos |
| **$S_0$** | Outro símbolo (`@`, `$`, etc.) | $S_{\text{erro}}$ | Lança `LexerError` (símbolo fora do alfabeto) |
| **$S_{\text{barra}}$** | `/` | $S_{\text{coment}}$ | Transiciona para estado de comentário |
| **$S_{\text{barra}}$** | Outro | $S_0$ | Retorna token `SLASH` (`/`) |
| **$S_{\text{coment}}$** | `\n` ou `EOF` | $S_0$ | Fim do comentário, volta a $S_0$ |
| **$S_{\text{coment}}$** | Qualquer caractere $\neq$ `\n` | $S_{\text{coment}}$ | Consome caractere do comentário |
| **$S_{\text{igual}}$** | `=` | $S_0$ | Retorna token `EQ` (`==`) |
| **$S_{\text{igual}}$** | Outro | $S_0$ | Retorna token `ASSIGN` (`=`) |
| **$S_{\text{excl}}$** | `=` | $S_0$ | Retorna token `NEQ` (`!=`) |
| **$S_{\text{excl}}$** | Outro | $S_{\text{erro}}$ | Lança `LexerError` (`!` sem `=`) |
| **$S_{\text{menor}}$** | `=` | $S_0$ | Retorna token `LTE` (`<=`) |
| **$S_{\text{menor}}$** | Outro | $S_0$ | Retorna token `LT` (`<`) |
| **$S_{\text{maior}}$** | `=` | $S_0$ | Retorna token `GTE` (`>=`) |
| **$S_{\text{maior}}$** | Outro | $S_0$ | Retorna token `GT` (`>`) |
| **$S_{\text{num}}$** | `[0-9]` | $S_{\text{num}}$ | Continua acumulando dígitos |
| **$S_{\text{num}}$** | `[a-zA-Z_]` | $S_{\text{erro}}$ | Lança `LexerError` (ex: `1x` mal formado) |
| **$S_{\text{num}}$** | Outro delimitador/espaço | $S_0$ | Retorna token `NUM` com o valor numérico |
| **$S_{\text{id}}$** | `[a-zA-Z0-9_]` | $S_{\text{id}}$ | Continua acumulando caracteres |
| **$S_{\text{id}}$** | Outro delimitador/espaço | $S_0$ | Consulta tabela de palavras reservadas; retorna token correspondente ou `ID` |


---

## 2. Gramática EBNF

A gramática formal da linguagem está expressa em bloco EBNF abaixo. Note que cada nível de precedência das expressões aritméticas e lógicas possui sua própria produção sintática.

```ebnf
(* ======================================================== *)
(* Estrutura do Programa e Comandos                         *)
(* ======================================================== *)
Programa       = { Comando } ;
Comando        = AtribuicaoCmd
               | PrintCmd
               | Bloco
               | IfCmd
               | WhileCmd
               | ForCmd ;
Bloco          = "{" { Comando } "}" ;
Atribuicao     = ID "=" Expressao ;
AtribuicaoCmd  = Atribuicao ";" ;
PrintCmd       = "print" "(" Expressao ")" ";" ;
IfCmd          = "if" "(" Expressao ")" Bloco [ "else" Bloco ] ;
WhileCmd       = "while" "(" Expressao ")" Bloco ;
(* Laço for: as três cláusulas são estritamente obrigatórias *)
ForCmd         = "for" "(" Atribuicao ";" Expressao ";" Atribuicao ")" Bloco ;
(* ======================================================== *)
(* Expressões Estruturadas por Níveis de Precedência        *)
(* ======================================================== *)
(* Nível 1: Comparações relacionais (menor precedência) *)
Expressao      = Soma [ OpRel Soma ] ;
OpRel          = "==" | "!=" | "<" | "<=" | ">" | ">=" ;
(* Nível 2: Soma e Subtração *)
Soma           = Termo { ( "+" | "-" ) Termo } ;
(* Nível 3: Multiplicação e Divisão *)
Termo          = Fator { ( "*" | "/" ) Fator } ;
(* Nível 4: Fatores / Termos primários (maior precedência) *)
Fator          = NUM
               | "true"
               | "false"
               | ID
               | "(" Expressao ")" ;
```

---

## 3. Tabela de Precedência e Associatividade

A tabela abaixo define a prioridade de avaliação e o sentido de agrupamento dos operadores quando não há parênteses explícitos:
| Precedência | Operadores | Descrição | Associatividade | Exemplo / Interpretação |
| :---: | :---: | :---: | :---: | :---: |
| **4 (Mais alta)** | `( )` | Parênteses (Agrupamento) | Não aplicável | `(a + b) * c` |
| **3** | `*`, `/` | Multiplicação e Divisão inteira | **Esquerda** | `a / b * c` $\equiv$ `(a / b) * c` |
| **2** | `+`, `-` | Adição e Subtração | **Esquerda** | `a - b - c` $\equiv$ `(a - b) - c` |
| **1 (Mais baixa)** | `==`, `!=`, `<`, `<=`, `>`, `>=` | Comparações relacionais | Não associativo | `a + 1 < b * 2` |

---


## 4. Regras Semânticas

As regras abaixo definem os tipos e os resultados das expressões MiniLang. Uma violação durante a análise ou execução deve produzir um erro semântico, com a linha correspondente quando disponível.

### 4.1 Tipos e operações

- Os únicos tipos de valor são **inteiro** e **booleano**. Literais `NUM` são inteiros; `true` e `false` são booleanos. Uma variável recebe o tipo do valor atribuído a ela.
- Os operadores aritméticos `+`, `-`, `*` e `/` aceitam somente operandos inteiros e produzem um inteiro. Usá-los com booleanos é erro semântico; por exemplo, `true + 1` é inválido.
- Os operadores relacionais `<`, `<=`, `>` e `>=` aceitam somente operandos inteiros e produzem um booleano.
- Os operadores `==` e `!=` aceitam operandos de tipos iguais e produzem um booleano. Comparar inteiro com booleano é erro semântico; por exemplo, `1 == true` é inválido.
- A condição de `if`, `while` e `for` deve produzir um booleano. Um inteiro usado como condição é erro semântico.
- `print` aceita expressões inteiras ou booleanas.

### 4.2 Divisão inteira e divisão por zero

- `/` realiza divisão inteira, descartando a parte fracionária em direção a zero: `7 / 2` resulta em `3` e `-7 / 2` resulta em `-3`.
- Dividir por zero é erro semântico durante a execução.

### 4.3 Variáveis

- Uma variável só pode ser lida depois de receber um valor por atribuição. Ler uma variável ainda não definida é erro semântico.
- Atribuições podem atualizar o valor de uma variável; o novo valor pode ser inteiro ou booleano.

## 5. Exemplos Comentados

### Exemplo 1: Programa Válido

Demonstra atribuição, operações aritméticas com precedência e os laços `while` e `for`.


```c
x = 10;
soma = 0;
while (x > 0) {
    soma = soma + x;
    x = x - 1;
}
for (i = 0; i < 5; i = i + 1) {
    print(soma + i * 2);
}
```
* **Status**: **Válido**.
* **Análise**: Segue todas as regras léxicas, sintáticas e semânticas. O laço `for` possui as 3 cláusulas obrigatórias e a expressão `soma + i * 2` agrupa primeiro a multiplicação.


---


### Exemplo 2: Inválido Léxico (Caractere Desconhecido)


```c
x = 10;
y = x @ 5;
print(y);
```

* **Status**: **Inválido (Erro Léxico)**.
* **Regra Violada**: O símbolo `@` não pertence ao alfabeto de caracteres válidos da MiniLang (não é operador aritmético, relacional nem delimitador). O analisador léxico deve emitir erro de token inesperado.

---


### Exemplo 3: Inválido Sintático (Laço `for` com Cláusula Faltando)


```c
soma = 0;
for (i = 0; i < 10) {
    soma = soma + i;
}
print(soma);
```

* **Status**: **Inválido (Erro Sintático)**.
* **Regra Violada**: A produção `ForCmd = "for" "(" Atribuicao ";" Expressao ";" Atribuicao ")" Bloco ;` exige obrigatoriamente 3 cláusulas separadas por dois `;`. No exemplo acima, foi omitida a terceira cláusula (atualização) e o segundo ponto e vírgula, resultando em erro sintático no token `)`.


---


### Exemplo 4: Inválido Semântico (Variável Não Declarada/Inicializada)


```c
total = 10;
print(total + valor_desconhecido);
```
* **Status**: **Inválido (Erro Semântico)**.
* **Regra Violada**: O identificador `valor_desconhecido` é referenciado na expressão sem ter sido atribuído previamente no escopo. A análise semântica/interpretador não permite leitura de variáveis não inicializadas.
---


### Exemplo 5: Inválido Sintático (Laço `while` sem Parênteses Obrigatórios)


```c
contador = 0;
while contador < 5 {
    contador = contador + 1;
}
```
* **Status**: **Inválido (Erro Sintático)**.
* **Regra Violada**: A produção `WhileCmd = "while" "(" Expressao ")" Bloco ;` exige que a expressão de teste esteja obrigatoriamente entre parênteses `(` e `)`. O analisador sintático espera `(` imediatamente após o `while`.
