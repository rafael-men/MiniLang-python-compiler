"""Testes inválidos do parser de expressões (usa o lexer real).

Resultado esperado: todas as entradas abaixo lançam ErroSintatico, com o
token encontrado e a posição (linha, coluna) indicados nos asserts.
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
