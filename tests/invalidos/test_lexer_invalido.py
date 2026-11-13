import pytest

from src.lexer import LexerError, tokenizar


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
