"""Testes do interpretador com entradas inválidas (erros semânticos).

Resultado esperado: todos os casos abaixo devem lançar ErroSemantico
com uma mensagem que identifica o problema e a linha.

- Ler variável que nunca recebeu valor -> "variável 'x' não definida"
- Divisão por zero -> "divisão por zero"
- Aritmética ou comparação (<, <=, >, >=) com booleano -> "operador '+' exige dois inteiros"
- == ou != entre inteiro e booleano -> "compara valores de tipos diferentes"
"""
import pytest

from src.ast_nodes import BinOp, Numero, Variavel
from src.interpreter import ErroSemantico, Interpretador, TabelaSimbolos
from src.lexer import tokenizar
from src.parser import Parser


def avaliar_codigo(codigo):
    return Interpretador().avaliar(Parser(tokenizar(codigo)).parse_expressao())


def test_buscar_variavel_nao_definida():
    tabela = TabelaSimbolos()
    with pytest.raises(ErroSemantico) as erro:
        tabela.buscar("x", linha=3)
    assert "não definida" in erro.value.mensagem
    assert erro.value.linha == 3


def test_variavel_nao_definida_em_expressao():
    with pytest.raises(ErroSemantico) as erro:
        Interpretador().avaliar(BinOp("+", Numero(1), Variavel("y", linha=4), linha=4))
    assert "variável 'y' não definida" in erro.value.mensagem
    assert erro.value.linha == 4


@pytest.mark.parametrize("codigo", ["1 / 0", "5 / (2 - 2)"])
def test_divisao_por_zero(codigo):
    with pytest.raises(ErroSemantico, match="divisão por zero"):
        avaliar_codigo(codigo)


@pytest.mark.parametrize("codigo", [
    "true + 1",
    "1 - false",
    "true * true",
    "8 / true",
    "1 < true",
    "false >= 0",
])
def test_operador_exige_inteiros(codigo):
    with pytest.raises(ErroSemantico, match="exige dois inteiros"):
        avaliar_codigo(codigo)


@pytest.mark.parametrize("codigo", ["1 == true", "false != 0"])
def test_igualdade_entre_tipos_diferentes(codigo):
    with pytest.raises(ErroSemantico, match="tipos diferentes"):
        avaliar_codigo(codigo)


def test_erro_indica_linha_do_operador():
    with pytest.raises(ErroSemantico) as erro:
        avaliar_codigo("1 +\n\n true")
    assert erro.value.linha == 1
