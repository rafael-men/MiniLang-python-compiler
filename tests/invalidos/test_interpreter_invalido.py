"""Testes do interpretador com entradas inválidas (erros semânticos).

Resultado esperado: todos os casos abaixo devem lançar ErroSemantico
com uma mensagem que identifica o problema e a linha.

- Ler variável que nunca recebeu valor -> "variável 'x' não definida"
"""
import pytest

from src.interpreter import ErroSemantico, TabelaSimbolos


def test_buscar_variavel_nao_definida():
    tabela = TabelaSimbolos()
    with pytest.raises(ErroSemantico) as erro:
        tabela.buscar("x", linha=3)
    assert "não definida" in erro.value.mensagem
    assert erro.value.linha == 3
