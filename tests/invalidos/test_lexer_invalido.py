"""Testes inválidos do lexer.

Demonstração da Fase 4 (executar apenas os três casos):
    python -m pytest -v tests/invalidos/test_lexer_invalido.py -k demonstracao_erro_lexico

Esperado:
  1. ``x = 1 @ 2;`` -> Erro léxico (linha 1, coluna 7): símbolo inesperado '@'
     Correção: ``x = 1 + 2;``
  2. ``x = 1x;`` -> Erro léxico (linha 1, coluna 5): número mal formado (ex.: '1x')
     Correção: ``x = 1;``
  3. ``if (x ! 1) { }`` -> Erro léxico (linha 1, coluna 7): símbolo inesperado '!'
     Correção: ``if (x != 1) { }``
"""

import pytest

from src.lexer import LexerError, tokenizar


def demonstrar_erro(codigo, mensagem, linha, coluna, corrigido):
    with pytest.raises(LexerError) as erro:
        tokenizar(codigo)

    assert erro.value.mensagem == mensagem
    assert (erro.value.linha, erro.value.coluna) == (linha, coluna)
    assert str(erro.value) == f"Erro léxico (linha {linha}, coluna {coluna}): {mensagem}"
    assert tokenizar(corrigido)[-1].tipo == "EOF"


def test_demonstracao_erro_lexico_caractere_fora_do_alfabeto():
    demonstrar_erro(
        "x = 1 @ 2;",
        "símbolo inesperado '@'",
        1,
        7,
        "x = 1 + 2;",
    )


def test_demonstracao_erro_lexico_numero_mal_formado():
    demonstrar_erro(
        "x = 1x;",
        "número mal formado (ex.: '1x')",
        1,
        5,
        "x = 1;",
    )


def test_demonstracao_erro_lexico_exclamacao_sem_igual():
    demonstrar_erro(
        "if (x ! 1) { }",
        "símbolo inesperado '!'",
        1,
        7,
        "if (x != 1) { }",
    )


@pytest.mark.parametrize("codigo", ["@", "$", "%", "&"])
def test_rejeita_simbolos_fora_do_alfabeto(codigo):
    with pytest.raises(LexerError):
        tokenizar(codigo)


def test_rejeita_numero_colado_em_identificador():
    with pytest.raises(LexerError, match="número mal formado") as erro:
        tokenizar("1x")
    assert (erro.value.linha, erro.value.coluna) == (1, 1)


def test_rejeita_exclamacao_sem_igual():
    with pytest.raises(LexerError) as erro:
        tokenizar("! ")
    assert (erro.value.linha, erro.value.coluna) == (1, 1)


def test_erro_lexico_indica_linha_e_coluna():
    with pytest.raises(LexerError) as erro:
        tokenizar("x = 1;\n @")
    assert (erro.value.linha, erro.value.coluna) == (2, 2)
