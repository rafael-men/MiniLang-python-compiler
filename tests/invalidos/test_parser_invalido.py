"""Testes inválidos do parser de expressões (usa o lexer real).

Resultado esperado: todas as entradas abaixo lançam ErroSintatico, com o
token encontrado e a posição (linha, coluna) indicados nos asserts.

Demonstração da Fase 4: 3 erros sintáticos (1 deles em laço), no fim do
arquivo (para rodar só eles: python -m pytest -v -k demonstracao_erro).
Todos passam pelo lexer sem erro léxico; quem falha é o parser, em ErroSintatico.

  1. "x = 10"  (atribuição sem ';')
     esperado ';', encontrado fim da entrada, linha 1, coluna 7
  2. "print(x;"  (print com parêntese não fechado)
     esperado ')', encontrado ';', linha 1, coluna 8
  3. for (i = 0; i < 10) { ... }  (laço for sem a cláusula de atualização)
     esperado ';', encontrado ')', linha 2, coluna 19
     Viola ForCmd = "for" "(" Atribuicao ";" Expressao ";" Atribuicao ")" Bloco
"""

import pytest

from src.lexer import LexerError, tokenizar
from src.parser import ErroSintatico, Parser


def analisar(codigo):
    return Parser(tokenizar(codigo)).parse_expressao()


def test_expressao_vazia():
    with pytest.raises(ErroSintatico) as erro:
        analisar("")
    assert erro.value.encontrado == "fim da entrada"
    assert (erro.value.linha, erro.value.coluna) == (1, 1)


def test_operador_sem_operando_a_esquerda():
    with pytest.raises(ErroSintatico) as erro:
        analisar("* 2")
    assert erro.value.encontrado == "'*'"
    assert (erro.value.linha, erro.value.coluna) == (1, 1)


def test_expressao_incompleta():
    with pytest.raises(ErroSintatico) as erro:
        analisar("1 +")
    assert erro.value.encontrado == "fim da entrada"
    assert (erro.value.linha, erro.value.coluna) == (1, 4)


def test_operador_seguido_de_operador():
    with pytest.raises(ErroSintatico) as erro:
        analisar("1 + * 2")
    assert erro.value.encontrado == "'*'"
    assert (erro.value.linha, erro.value.coluna) == (1, 5)


def test_parenteses_sem_fechamento():
    with pytest.raises(ErroSintatico) as erro:
        analisar("(1 + 2")
    assert erro.value.esperado == "')'"
    assert erro.value.encontrado == "fim da entrada"
    assert (erro.value.linha, erro.value.coluna) == (1, 7)


def test_parenteses_vazios():
    with pytest.raises(ErroSintatico) as erro:
        analisar("()")
    assert erro.value.encontrado == "')'"
    assert (erro.value.linha, erro.value.coluna) == (1, 2)


def test_token_inesperado_no_lugar_de_operando():
    with pytest.raises(ErroSintatico) as erro:
        analisar("x = (1 + ;")
    # '=' sobra depois de 'x' (expressão completa)
    assert erro.value.encontrado == "'='"
    assert (erro.value.linha, erro.value.coluna) == (1, 3)


def test_token_inesperado_dentro_da_expressao():
    with pytest.raises(ErroSintatico) as erro:
        analisar("(1 + ;")
    assert erro.value.encontrado == "';'"
    assert (erro.value.linha, erro.value.coluna) == (1, 6)


def test_comparacao_encadeada():
    with pytest.raises(ErroSintatico, match="comparação encadeada") as erro:
        analisar("a < b < c")
    assert erro.value.encontrado == "'<'"
    assert (erro.value.linha, erro.value.coluna) == (1, 7)


def test_comparacao_encadeada_mista():
    with pytest.raises(ErroSintatico, match="comparação encadeada"):
        analisar("a == b != c")


def test_tokens_extras_depois_da_expressao():
    with pytest.raises(ErroSintatico) as erro:
        analisar("1 + 2 3")
    assert erro.value.esperado == "fim da expressão"
    assert erro.value.encontrado == "'3'"
    assert (erro.value.linha, erro.value.coluna) == (1, 7)


def test_parentese_fechando_sem_abrir():
    with pytest.raises(ErroSintatico) as erro:
        analisar("1 + 2)")
    assert erro.value.encontrado == "')'"
    assert (erro.value.linha, erro.value.coluna) == (1, 6)


def test_posicao_em_varias_linhas():
    with pytest.raises(ErroSintatico) as erro:
        analisar("1 +\n  * 2")
    assert (erro.value.linha, erro.value.coluna) == (2, 3)


def test_mensagem_legivel():
    with pytest.raises(ErroSintatico) as erro:
        analisar("1 +")
    texto = str(erro.value)
    assert "Erro sintático (linha 1, coluna 4)" in texto
    assert "esperado" in texto and "fim da entrada" in texto


def test_erro_lexico_nao_vira_erro_sintatico():
    # A distinção entre as fases é preservada: o erro vem do lexer.
    with pytest.raises(LexerError):
        analisar("1 + @")


def programa(codigo):
    return Parser(tokenizar(codigo)).parse_programa()


def erro_de(codigo):
    with pytest.raises(ErroSintatico) as erro:
        programa(codigo)
    return erro.value


def posicao(erro):
    return (erro.linha, erro.coluna)


def test_atribuicao_sem_ponto_e_virgula():
    erro = erro_de("x = 1")
    assert erro.esperado == "';'"
    assert erro.encontrado == "fim da entrada"
    assert posicao(erro) == (1, 6)


def test_atribuicao_sem_ponto_e_virgula_antes_de_outro_comando():
    erro = erro_de("x = 1\ny = 2;")
    assert erro.esperado == "';'"
    assert erro.encontrado == "'y'"
    assert posicao(erro) == (2, 1)


def test_atribuicao_sem_igual():
    erro = erro_de("x 1;")
    assert erro.esperado == "'='"
    assert erro.encontrado == "'1'"
    assert posicao(erro) == (1, 3)


def test_atribuicao_sem_expressao():
    erro = erro_de("x = ;")
    assert erro.encontrado == "';'"
    assert posicao(erro) == (1, 5)


def test_atribuicao_a_numero_e_comando_invalido():
    erro = erro_de("5 = x;")
    assert "comando" in erro.esperado
    assert erro.encontrado == "'5'"
    assert posicao(erro) == (1, 1)


def test_print_sem_parenteses():
    erro = erro_de("print x;")
    assert erro.esperado == "'('"
    assert erro.encontrado == "'x'"
    assert posicao(erro) == (1, 7)


def test_print_sem_fechar_parenteses():
    erro = erro_de("print(x;")
    assert erro.esperado == "')'"
    assert erro.encontrado == "';'"
    assert posicao(erro) == (1, 8)


def test_print_sem_ponto_e_virgula():
    erro = erro_de("print(x)")
    assert erro.esperado == "';'"
    assert erro.encontrado == "fim da entrada"


def test_print_vazio():
    erro = erro_de("print();")
    assert erro.encontrado == "')'"
    assert posicao(erro) == (1, 7)


def test_while_sem_parenteses_exemplo_5_da_gramatica():
    erro = erro_de(
        "contador = 0;\nwhile contador < 5 {\n contador = contador + 1;\n}"
    )
    assert erro.esperado == "'('"
    assert erro.encontrado == "'contador'"
    assert posicao(erro) == (2, 7)


def test_while_sem_chaves_no_corpo():
    erro = erro_de("while (x < 3) x = x + 1;")
    assert erro.esperado == "'{'"
    assert erro.encontrado == "'x'"
    assert posicao(erro) == (1, 15)


def test_while_sem_fechar_parenteses_da_condicao():
    erro = erro_de("while (x < 3 { }")
    assert erro.esperado == "')'"
    assert erro.encontrado == "'{'"


def test_if_sem_parenteses():
    erro = erro_de("if x > 0 { }")
    assert erro.esperado == "'('"
    assert erro.encontrado == "'x'"


def test_if_sem_bloco():
    erro = erro_de("if (x > 0) print(x);")
    assert erro.esperado == "'{'"
    assert erro.encontrado == "'print'"


def test_else_sem_bloco():
    erro = erro_de("if (x) { } else print(1);")
    assert erro.esperado == "'{'"
    assert erro.encontrado == "'print'"


def test_else_if_nao_existe_na_gramatica():
    erro = erro_de("if (a) { } else if (b) { }")
    assert erro.esperado == "'{'"
    assert erro.encontrado == "'if'"


def test_else_sem_if():
    erro = erro_de("else { }")
    assert "comando" in erro.esperado
    assert erro.encontrado == "'else'"


def test_bloco_sem_fechamento():
    erro = erro_de("{ x = 1;")
    assert erro.esperado == "'}'"
    assert erro.encontrado == "fim da entrada"
    assert posicao(erro) == (1, 9)


def test_bloco_de_laco_sem_fechamento_em_outra_linha():
    erro = erro_de("while (true) {\n  x = 1;\n")
    assert erro.esperado == "'}'"
    assert erro.encontrado == "fim da entrada"
    assert posicao(erro) == (3, 1)


def test_chave_de_fechamento_sobrando():
    erro = erro_de("x = 1; }")
    assert "comando" in erro.esperado
    assert erro.encontrado == "'}'"
    assert posicao(erro) == (1, 8)


def test_for_sem_clausula_de_atualizacao_exemplo_3_da_gramatica():
    erro = erro_de("soma = 0;\nfor (i = 0; i < 10) {\n soma = soma + i;\n}")
    assert erro.esperado == "';'"
    assert erro.encontrado == "')'"
    assert posicao(erro) == (2, 19)


def test_for_com_atualizacao_vazia():
    erro = erro_de("for (i = 0; i < 10; ) { }")
    assert erro.esperado == "identificador"
    assert erro.encontrado == "')'"


def test_for_com_inicializacao_vazia():
    erro = erro_de("for (; i < 10; i = i + 1) { }")
    assert erro.esperado == "identificador"
    assert erro.encontrado == "';'"
    assert posicao(erro) == (1, 6)


def test_for_com_condicao_vazia():
    erro = erro_de("for (i = 0; ; i = i + 1) { }")
    assert erro.encontrado == "';'"
    assert posicao(erro) == (1, 13)


def test_for_apenas_com_inicializacao():
    erro = erro_de("for (i = 0) { }")
    assert erro.esperado == "';'"
    assert erro.encontrado == "')'"


def test_for_com_inicializacao_que_nao_e_atribuicao():
    erro = erro_de("for (i < 0; i < 3; i = i + 1) { }")
    assert erro.esperado == "'='"
    assert erro.encontrado == "'<'"


def test_for_com_atualizacao_terminada_em_ponto_e_virgula():
    erro = erro_de("for (i = 0; i < 3; i = i + 1;) { }")
    assert erro.esperado == "')'"
    assert erro.encontrado == "';'"


def test_for_sem_bloco():
    erro = erro_de("for (i = 0; i < 3; i = i + 1) print(i);")
    assert erro.esperado == "'{'"
    assert erro.encontrado == "'print'"


def test_for_sem_parenteses():
    erro = erro_de("for i = 0; i < 3; i = i + 1 { }")
    assert erro.esperado == "'('"
    assert erro.encontrado == "'i'"


def test_erro_em_comando_aninhado_mantem_a_linha_correta():
    codigo = "while (a) {\n  if (b) {\n    print(1)\n  }\n}"
    erro = erro_de(codigo)
    assert erro.esperado == "';'"
    assert erro.encontrado == "'}'"
    assert posicao(erro) == (4, 3)


def test_erro_de_expressao_dentro_de_comando():
    erro = erro_de("x = 1;\ny = (1 + ;")
    assert erro.encontrado == "';'"
    assert posicao(erro) == (2, 10)


def test_comparacao_encadeada_dentro_de_if():
    erro = erro_de("if (a < b < c) { }")
    assert "comparação encadeada" in erro.mensagem
    assert posicao(erro) == (1, 11)


def test_conteudo_extra_depois_de_programa_valido():
    erro = erro_de("x = 1; )")
    assert "comando" in erro.esperado
    assert erro.encontrado == "')'"
    assert posicao(erro) == (1, 8)


def test_expressao_solta_nao_e_comando():
    erro = erro_de("1 + 2;")
    assert "comando" in erro.esperado
    assert erro.encontrado == "'1'"


def test_palavra_reservada_nao_pode_ser_alvo_de_atribuicao():
    erro = erro_de("while = 1;")
    assert erro.esperado == "'('"
    assert erro.encontrado == "'='"


def test_programa_com_erro_lexico_continua_sendo_erro_lexico():
    with pytest.raises(LexerError):
        programa("x = 10;\ny = x @ 5;")


def test_erro_de_comando_tem_todos_os_atributos():
    erro = erro_de("print(x)")
    assert erro.mensagem
    assert erro.esperado and erro.encontrado
    assert (erro.linha, erro.coluna) == (1, 9)
    assert str(erro).startswith("Erro sintático (linha 1, coluna 9)")


def test_exemplo_invalido_do_repositorio():
    with open("exemplos/programa_invalido.ml", encoding="utf-8") as f:
        erro = erro_de(f.read())
    assert erro.esperado == "';'"
    assert erro.encontrado == "')'"
    assert erro.linha == 10


def demonstrar_erro_sintatico(codigo):
    """Tokeniza e analisa `codigo`, e devolve o ErroSintatico lançado.

    A tokenização fica fora do pytest.raises: se a entrada tivesse erro léxico,
    o teste falharia com LexerError e não contaria como erro sintático.
    """

    tokens = tokenizar(codigo)
    with pytest.raises(ErroSintatico) as erro:
        Parser(tokens).parse_programa()
    return erro.value


def test_demonstracao_erro_1_atribuicao_sem_ponto_e_virgula():
    """AtribuicaoCmd = Atribuicao ";" : falta o ';' e a entrada acaba."""

    erro = demonstrar_erro_sintatico("x = 10")

    assert erro.mensagem == "esperado ';', encontrado fim da entrada"
    assert erro.esperado == "';'"
    assert erro.encontrado == "fim da entrada"
    # "x = 10" tem 6 caracteres, então o fim da entrada está na coluna 7
    assert (erro.linha, erro.coluna) == (1, 7)
    assert str(erro) == (
        "Erro sintático (linha 1, coluna 7): esperado ';', encontrado fim da entrada"
    )

    # Corrigido (com o ';'), o programa é aceito
    assert len(Parser(tokenizar("x = 10;")).parse_programa().comandos) == 1


def test_demonstracao_erro_2_print_com_parentese_nao_fechado():
    """PrintCmd = "print" "(" Expressao ")" ";" : o ')' foi trocado por ';'."""

    erro = demonstrar_erro_sintatico("print(x;")

    assert erro.mensagem == "esperado ')', encontrado ';'"
    assert erro.esperado == "')'"
    assert erro.encontrado == "';'"
    # print(x;  ->  ';' é o 8º caractere
    assert (erro.linha, erro.coluna) == (1, 8)
    assert str(erro) == (
        "Erro sintático (linha 1, coluna 8): esperado ')', encontrado ';'"
    )

    # Corrigido (com o ')'), o programa é aceito
    assert len(Parser(tokenizar("print(x);")).parse_programa().comandos) == 1


def test_demonstracao_erro_3_for_sem_clausula_de_atualizacao():
    """
    ForCmd = "for" "(" Atribuicao ";" Expressao ";" Atribuicao ")" Bloco
    As três cláusulas são obrigatórias. Aqui faltam o 2º ';' e a atualização:
    depois da condição `i < 10` o parser pede ';' e encontra ')'.
    """

    codigo = (
        "soma = 0;\n"
        "for (i = 0; i < 10) {\n"
        "    soma = soma + i;\n"
        "}"
    )
    erro = demonstrar_erro_sintatico(codigo)

    assert erro.mensagem == "esperado ';', encontrado ')'"
    assert erro.esperado == "';'"
    assert erro.encontrado == "')'"
    # O erro está na linha do `for` (2), não na da atribuição anterior (1).
    # for (i = 0; i < 10) ->  ')' é o 19º caractere
    assert (erro.linha, erro.coluna) == (2, 19)
    assert str(erro) == (
        "Erro sintático (linha 2, coluna 19): esperado ';', encontrado ')'"
    )

    # Com as três cláusulas, o mesmo laço é aceito
    corrigido = codigo.replace("i < 10)", "i < 10; i = i + 1)")
    assert len(Parser(tokenizar(corrigido)).parse_programa().comandos) == 2
