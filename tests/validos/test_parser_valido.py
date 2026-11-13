"""Testes válidos do parser de expressões (usa o lexer real)."""

import pytest

from src.ast_nodes import BinOp, Booleano, Numero, Variavel
from src.lexer import tokenizar
from src.parser import Parser


def analisar(codigo):
    return Parser(tokenizar(codigo)).parse_expressao()


def test_numero_inteiro():
    arvore = analisar("42")
    assert arvore == Numero(42, linha=1)


def test_booleano_verdadeiro():
    arvore = analisar("true")
    assert isinstance(arvore, Booleano)
    assert arvore.valor is True


def test_booleano_falso():
    arvore = analisar("false")
    assert isinstance(arvore, Booleano)
    assert arvore.valor is False


def test_variavel():
    arvore = analisar("soma")
    assert isinstance(arvore, Variavel)
    assert arvore.nome == "soma"


@pytest.mark.parametrize("op", ["+", "-"])
def test_adicao_e_subtracao(op):
    arvore = analisar(f"a {op} 1")
    assert isinstance(arvore, BinOp)
    assert arvore.op == op
    assert arvore.esq == Variavel("a", linha=1)
    assert arvore.dir == Numero(1, linha=1)


@pytest.mark.parametrize("op", ["*", "/"])
def test_multiplicacao_e_divisao(op):
    arvore = analisar(f"6 {op} b")
    assert isinstance(arvore, BinOp)
    assert arvore.op == op
    assert arvore.esq == Numero(6, linha=1)
    assert arvore.dir == Variavel("b", linha=1)


@pytest.mark.parametrize("op", ["<", ">", "<=", ">="])
def test_comparacao_relacional(op):
    arvore = analisar(f"x {op} 10")
    assert isinstance(arvore, BinOp)
    assert arvore.op == op
    assert arvore.esq == Variavel("x", linha=1)
    assert arvore.dir == Numero(10, linha=1)


@pytest.mark.parametrize("op", ["==", "!="])
def test_igualdade_e_diferenca(op):
    arvore = analisar(f"x {op} y")
    assert isinstance(arvore, BinOp)
    assert arvore.op == op
    assert isinstance(arvore.esq, Variavel) and isinstance(arvore.dir, Variavel)


def test_precedencia_1_mais_2_vezes_3():
    arvore = analisar("1 + 2 * 3")
    assert arvore.op == "+"
    assert arvore.esq == Numero(1, linha=1)
    assert isinstance(arvore.dir, BinOp)
    assert arvore.dir.op == "*"
    assert arvore.dir.esq == Numero(2, linha=1)
    assert arvore.dir.dir == Numero(3, linha=1)


def test_agrupamento_com_parenteses():
    arvore = analisar("(1 + 2) * 3")
    assert arvore.op == "*"
    assert isinstance(arvore.esq, BinOp)
    assert arvore.esq.op == "+"
    assert arvore.esq.esq == Numero(1, linha=1)
    assert arvore.esq.dir == Numero(2, linha=1)
    assert arvore.dir == Numero(3, linha=1)


def test_parenteses_redundantes_nao_geram_no():
    assert analisar("((7))") == Numero(7, linha=1)


def test_associatividade_esquerda_subtracao():
    # a - b - c  ==  (a - b) - c
    arvore = analisar("a - b - c")
    assert arvore.op == "-"
    assert arvore.dir == Variavel("c", linha=1)
    assert isinstance(arvore.esq, BinOp)
    assert arvore.esq.op == "-"
    assert arvore.esq.esq == Variavel("a", linha=1)
    assert arvore.esq.dir == Variavel("b", linha=1)


def test_associatividade_esquerda_divisao():
    # 100 / 10 / 2  ==  (100 / 10) / 2
    arvore = analisar("100 / 10 / 2")
    assert arvore.op == "/"
    assert arvore.dir == Numero(2, linha=1)
    assert arvore.esq.op == "/"
    assert arvore.esq.esq == Numero(100, linha=1)
    assert arvore.esq.dir == Numero(10, linha=1)


def test_varios_niveis_de_precedencia():
    # a + b * 2 - 1 < (c + 1) * 3
    arvore = analisar("a + b * 2 - 1 < (c + 1) * 3")
    assert arvore.op == "<"

    esq = arvore.esq  # (a + (b * 2)) - 1
    assert esq.op == "-"
    assert esq.dir == Numero(1, linha=1)
    assert esq.esq.op == "+"
    assert esq.esq.esq == Variavel("a", linha=1)
    assert esq.esq.dir.op == "*"
    assert esq.esq.dir.esq == Variavel("b", linha=1)
    assert esq.esq.dir.dir == Numero(2, linha=1)

    dir_ = arvore.dir  # (c + 1) * 3
    assert dir_.op == "*"
    assert dir_.dir == Numero(3, linha=1)
    assert dir_.esq.op == "+"
    assert dir_.esq.esq == Variavel("c", linha=1)
    assert dir_.esq.dir == Numero(1, linha=1)


def test_comparacao_entre_parenteses_pode_ser_encadeada():
    arvore = analisar("(a < b) == (c < d)")
    assert arvore.op == "=="
    assert arvore.esq.op == "<"
    assert arvore.dir.op == "<"


def test_linha_do_operador_em_varias_linhas():
    arvore = analisar("1\n+\n2")
    assert arvore.linha == 2          # linha do operador
    assert arvore.esq.linha == 1
    assert arvore.dir.linha == 3


def test_funcoes_internas_nao_exigem_eof():
    # Reuso futuro pelo parser de comandos: a expressão para onde termina.
    parser = Parser(tokenizar("1 + 2 ;"))
    arvore = parser.expressao()
    assert arvore.op == "+"
    assert parser._atual().tipo == "SEMICOLON"
