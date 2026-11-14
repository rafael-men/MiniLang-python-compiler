import pytest

from src.ast_nodes import BinOp, Booleano, Numero, Variavel
from src.interpreter import Interpretador, TabelaSimbolos
from src.lexer import tokenizar
from src.parser import Parser


def avaliar_codigo(codigo, variaveis=None):
    interp = Interpretador()
    for nome, valor in (variaveis or {}).items():
        interp.tabela.definir(nome, valor)
    return interp.avaliar(Parser(tokenizar(codigo)).parse_expressao())


def test_definir_e_buscar_inteiro():
    tabela = TabelaSimbolos()
    tabela.definir("x", 10)
    assert tabela.buscar("x") == 10


def test_definir_e_buscar_booleano():
    tabela = TabelaSimbolos()
    tabela.definir("ok", True)
    assert tabela.buscar("ok") is True


def test_atribuir_de_novo_atualiza_valor():
    tabela = TabelaSimbolos()
    tabela.definir("x", 1)
    tabela.definir("x", 2)
    assert tabela.buscar("x") == 2


def test_existe():
    tabela = TabelaSimbolos()
    assert not tabela.existe("x")
    tabela.definir("x", 0)
    assert tabela.existe("x")


# Expressões com AST montada à mão

def test_literais():
    interp = Interpretador()
    assert interp.avaliar(Numero(42)) == 42
    assert interp.avaliar(Booleano(True)) is True
    assert interp.avaliar(Booleano(False)) is False


def test_variavel():
    interp = Interpretador()
    interp.tabela.definir("x", 10)
    assert interp.avaliar(Variavel("x")) == 10


def test_ast_de_1_mais_2_vezes_3():
    # 1 + 2 * 3: a multiplicação fica mais abaixo na árvore
    arvore = BinOp("+", Numero(1), BinOp("*", Numero(2), Numero(3)))
    assert Interpretador().avaliar(arvore) == 7


def test_ast_de_1_mais_2_entre_parenteses_vezes_3():
    # (1 + 2) * 3: a soma fica mais abaixo na árvore
    arvore = BinOp("*", BinOp("+", Numero(1), Numero(2)), Numero(3))
    assert Interpretador().avaliar(arvore) == 9


# Expressões vindas do lexer e do parser

@pytest.mark.parametrize("codigo, esperado", [
    ("1 + 2 * 3", 7),
    ("(1 + 2) * 3", 9),
    ("10 - 2 - 3", 5),      # associatividade à esquerda: (10 - 2) - 3
    ("100 / 10 / 2", 5),    # (100 / 10) / 2
    ("7 / 2", 3),
    ("0 - 7 / 2", -3),
    ("(0 - 7) / 2", -3),    # truncamento em direção a zero
    ("(0 - 7) / (0 - 2)", 3),
    ("7 / (0 - 2)", -3),
])
def test_aritmetica(codigo, esperado):
    assert avaliar_codigo(codigo) == esperado


@pytest.mark.parametrize("codigo, esperado", [
    ("1 < 2", True),
    ("2 < 1", False),
    ("2 <= 2", True),
    ("3 > 2", True),
    ("2 >= 3", False),
    ("1 + 1 == 2", True),
    ("1 != 1", False),
    ("true == true", True),
    ("true != false", True),
    ("(1 < 2) == true", True),
])
def test_comparacoes(codigo, esperado):
    assert avaliar_codigo(codigo) is esperado


def test_expressao_com_variaveis():
    assert avaliar_codigo("soma + i * 2", {"soma": 10, "i": 3}) == 16
