# Catálogo de Erros — MiniLang

Rascunho da seção "Catálogo de erros" do relatório (item f). Todas as mensagens abaixo foram copiadas da execução real do compilador (`python -m src.interpreter arquivo.ml`).

## Formato das mensagens

Cada fase do compilador lança a própria exceção, e a execução para no primeiro erro encontrado:

| Fase | Exceção | Formato | Posição |
| --- | --- | --- | --- |
| Análise léxica | `LexerError` (src/lexer.py) | `Erro léxico (linha L, coluna C): ...` | linha e coluna do caractere |
| Análise sintática | `ErroSintatico` (src/parser.py) | `Erro sintático (linha L, coluna C): esperado X, encontrado Y` | linha e coluna do token |
| Análise semântica | `ErroSemantico` (src/interpreter.py) | `Erro semântico (linha L): ...` | linha do operador ou do comando |
| Execução | `ErroLimiteIteracoes` (src/interpreter.py) | `Erro de execução (linha L): laço passou do limite de N iterações` | linha do laço |

## Erros léxicos

Um erro léxico ocorre quando uma sequência de caracteres não forma nenhum token do alfabeto da linguagem, ou seja, o AFD do lexer chega ao estado de erro.

| # | Mensagem | Causa | Exemplo |
| --- | --- | --- | --- |
| L1 | `Erro léxico (linha 1, coluna 7): símbolo inesperado '@'` | Caractere fora do alfabeto. Do estado inicial S0 não há transição para `@` | `x = 1 @ 2;` |
| L2 | `Erro léxico (linha 1, coluna 5): número mal formado (ex.: '1x')` | Uma letra logo depois de dígitos. No estado S_num, uma letra leva ao erro, porque `[0-9]+` não pode ser seguido de letra sem separador | `x = 1x;` |
| L3 | `Erro léxico (linha 1, coluna 7): símbolo inesperado '!'` | `!` só existe dentro de `!=`. No estado S_excl, qualquer caractere diferente de `=` leva ao erro | `if (x ! 1) { }` |
| L4 | `Erro léxico (linha 1, coluna 4): símbolo inesperado 'ç'` | Identificadores aceitam só `[a-zA-Z_][a-zA-Z0-9_]*`. Letras acentuadas estão fora do alfabeto | `preço = 10;` |

## Erros sintáticos

Um erro sintático ocorre quando a sequência de tokens é válida, mas não pode ser derivada pela gramática EBNF. O parser descendente recursivo detecta o erro no primeiro token que não pode iniciar nem continuar a produção em andamento.

| # | Mensagem | Causa | Exemplo | Produção violada |
| --- | --- | --- | --- | --- |
| S1 | `Erro sintático (linha 1, coluna 7): esperado ';', encontrado fim da entrada` | Atribuição sem `;` | `x = 10` | `AtribuicaoCmd = Atribuicao ";"` |
| S2 | `Erro sintático (linha 1, coluna 8): esperado ')', encontrado ';'` | `print` com parêntese não fechado | `print(x;` | `PrintCmd = "print" "(" Expressao ")" ";"` |
| **S3 (laço)** | `Erro sintático (linha 2, coluna 19): esperado ';', encontrado ')'` | `for` sem a cláusula de atualização | `for (i = 0; i < 10) { ... }` | `ForCmd = "for" "(" Atribuicao ";" Expressao ";" Atribuicao ")" Bloco` |
| **S4 (laço)** | `Erro sintático (linha 1, coluna 7): esperado '(', encontrado 'x'` | Condição do `while` sem parênteses | `while x < 5 { x = x + 1; }` | `WhileCmd = "while" "(" Expressao ")" Bloco` |
| S5 | `Erro sintático (linha 1, coluna 10): esperado número, 'true', 'false', identificador ou '(', encontrado ';'` | Expressão incompleta: depois de `+` falta um operando | `x = (1 + ;` | `Soma = Termo { ("+" \| "-") Termo }` |
| S6 | `Erro sintático (linha 1, coluna 12): comparação encadeada não permitida ('<' após uma comparação); use parênteses` | Duas comparações seguidas. As comparações não são associativas | `ok = 1 < 2 < 3;` | `Expressao = Soma [ OpRel Soma ]` |
| S7 | `Erro sintático (linha 1, coluna 22): esperado '}', encontrado fim da entrada` | Bloco aberto e não fechado | `if (true) { print(1);` | `Bloco = "{" { Comando } "}"` |
| S8 | `Erro sintático (linha 1, coluna 5): esperado número, 'true', 'false', identificador ou '(', encontrado '-'` | A MiniLang não tem menos unário | `x = -5;` | `Fator = NUM \| "true" \| "false" \| ID \| "(" Expressao ")"` |
| S9 | `Erro sintático (linha 1, coluna 1): esperado comando (identificador, 'print', 'if', 'while', 'for' ou '{'), encontrado 'else'` | `else` sem `if` antes | `else { print(1); }` | `Comando = AtribuicaoCmd \| PrintCmd \| Bloco \| IfCmd \| WhileCmd \| ForCmd` |

## Erros semânticos

Um erro semântico ocorre quando o programa está bem formado pela gramática, mas viola uma regra de significado da seção 4 de `docs/gramatica.md` (tipos, variáveis definidas, divisão por zero). O interpretador verifica essas regras durante a execução.

| # | Mensagem | Causa | Exemplo | Regra violada |
| --- | --- | --- | --- | --- |
| E1 | `Erro semântico (linha 1): variável 'y' não definida` | Leitura de variável que nunca recebeu valor | `print(y);` | 4.3: uma variável só pode ser lida depois de atribuída |
| E2 | `Erro semântico (linha 1): divisão por zero` | Divisor igual a zero | `x = 10 / 0;` | 4.2: dividir por zero é erro |
| E3 | `Erro semântico (linha 1): operador '+' exige dois inteiros, recebeu booleano e inteiro` | Aritmética com booleano | `x = true + 1;` | 4.1: `+ - * /` só com inteiros |
| E4 | `Erro semântico (linha 1): operador '<' exige dois inteiros, recebeu inteiro e booleano` | Comparação de ordem com booleano | `ok = 1 < true;` | 4.1: `< <= > >=` só com inteiros |
| E5 | `Erro semântico (linha 1): operador '==' compara valores de tipos diferentes: inteiro e booleano` | Igualdade entre tipos diferentes | `ok = 1 == true;` | 4.1: `==` e `!=` só entre tipos iguais |
| **E6 (laço)** | `Erro semântico (linha 2): condição do 'while' deve ser booleana, recebeu inteiro` | Condição de laço inteira | `x = 5; while (x) { x = x - 1; }` | 4.1: condição de `while` deve ser booleana |
| **E7 (laço)** | `Erro semântico (linha 1): condição do 'for' deve ser booleana, recebeu inteiro` | Condição do `for` inteira | `for (i = 0; i; i = i + 1) { }` | 4.1: condição de `for` deve ser booleana |
| E8 | `Erro semântico (linha 1): condição do 'if' deve ser booleana, recebeu inteiro` | Condição do `if` inteira | `if (1) { print(1); }` | 4.1: condição de `if` deve ser booleana |
| **E9 (laço)** | `Erro semântico (linha 1): variável 'k' não definida` | Variável de controle do `while` nunca inicializada | `while (k < 10) { k = k + 1; }` | 4.3 |
| **E10 (laço)** | `Erro semântico (linha 1): variável 'j' não definida` | Condição do `for` usa variável diferente da inicializada | `for (i = 0; j < 10; i = i + 1) { }` | 4.3 |

## Erro de execução

| # | Mensagem | Causa | Exemplo |
| --- | --- | --- | --- |
| X1 | `Erro de execução (linha 1): laço passou do limite de 10000 iterações` | Laço que não termina. Não é um erro da linguagem: é a proteção do interpretador para não travar | `while (true) { }` |

## Como demonstrar com execução

| Categoria | Arquivo de teste | Comando |
| --- | --- | --- |
| Léxicos | tests/invalidos/test_lexer_invalido.py | `python -m pytest tests/invalidos/test_lexer_invalido.py -v -k demonstracao_erro_lexico` |
| Sintáticos | tests/invalidos/test_parser_invalido.py | `python -m pytest tests/invalidos/test_parser_invalido.py -v -k demonstracao_erro` |
| Semânticos | tests/invalidos/test_interpreter_invalido.py | `python -m pytest tests/invalidos/test_interpreter_invalido.py -v` |
| Laço infinito | tests/invalidos/test_laco_infinito.py | `python -m pytest tests/invalidos/test_laco_infinito.py -v` |

Pela linha de comando: `python -m src.interpreter exemplos/programa_invalido.ml` mostra o erro S3.

## Estratégia de diagnóstico e justificativa

**Estratégia adotada:** o compilador **para no primeiro erro** e não tenta recuperar. A mensagem traz a fase (léxico, sintático ou semântico), a linha e, nas fases léxica e sintática, a coluna. Os erros sintáticos dizem também **o que era esperado e o que foi encontrado**.

**Por que parar no primeiro erro:**

1. **Público-alvo.** A MiniLang serve para ensinar compiladores a iniciantes. Um erro por vez, com a causa exata, é mais didático do que uma lista longa em que só o primeiro item é real.
2. **Evitar erros em cascata.** A alternativa clássica é a recuperação em modo pânico: descartar tokens até um token de sincronização, como `;` ou `}`, e continuar. Ela costuma gerar erros falsos. Em `x = (1 + ;`, o parser sincronizaria no `;`, mas o `(` aberto faria os comandos seguintes parecerem errados também. Para um iniciante, esses falsos erros confundem mais do que ajudam.
3. **O interpretador não tem como continuar.** Os erros semânticos são detectados durante a execução. Depois de uma divisão por zero ou de uma variável não definida, não existe valor correto para seguir executando. Inventar um valor (por exemplo, 0) produziria uma saída enganosa.
4. **Programas pequenos.** Os programas MiniLang têm poucas linhas, e corrigir e rodar de novo é imediato. O custo de ver um erro por vez é baixo.
5. **O parser fica simples e verificável.** Cada função do parser descendente recursivo só precisa lançar `ErroSintatico` quando o token atual não serve. Não há conjuntos de sincronização para projetar e testar, e cada erro tem posição exata, verificada nos testes.

**O que foi priorizado no lugar da recuperação:** a qualidade de **uma** mensagem. Linha e coluna exatas, "esperado X, encontrado Y" no parser e, no interpretador, os tipos recebidos (`recebeu booleano e inteiro`), para o aluno saber o que corrigir sem precisar adivinhar.

## Limitação conhecida

As verificações semânticas são **dinâmicas**: acontecem quando o comando executa. Por isso, um erro semântico em um trecho que nunca executa não é detectado:

```
if (false) { print(true + 1); }
print(0);
```

Esse programa roda e imprime `0`, embora `true + 1` viole a regra 4.1. Detectar esse erro exigiria uma **análise semântica estática** (verificação de tipos sobre a AST, antes da execução), que não foi implementada. Pelo enunciado, as verificações semânticas exigidas (variável não definida, divisão por zero, tipo incompatível e condição não booleana em laço) são todas detectadas quando o trecho executa. A divisão por zero, em geral, só pode ser detectada na execução, porque o divisor pode depender de valores calculados.
