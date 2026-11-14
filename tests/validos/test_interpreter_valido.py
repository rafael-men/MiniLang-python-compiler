from pathlib import Path

import pytest

from src.ast_nodes import BinOp, Booleano, Numero, Variavel
from src.interpreter import Interpretador, TabelaSimbolos, executar_codigo, main
from src.lexer import tokenizar
from src.parser import Parser

EXEMPLOS = Path(__file__).resolve().parents[2] / "exemplos"


def rodar(codigo):
    saida = []
    interp = executar_codigo(codigo, escrever=saida.append)
    return saida, interp


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


# Comandos

def test_atribuicao_e_reatribuicao():
    _, interp = rodar("x = 1; x = x + 1; ok = x == 2;")
    assert interp.tabela.buscar("x") == 2
    assert interp.tabela.buscar("ok") is True


def test_variavel_pode_mudar_de_tipo():
    _, interp = rodar("x = 1; x = true;")
    assert interp.tabela.buscar("x") is True


def test_print_de_inteiro_e_booleano():
    saida, _ = rodar("print(1 + 1); print(2 > 1); print(false);")
    assert saida == ["2", "true", "false"]


@pytest.mark.parametrize("x, esperado", [(5, ["1"]), (0, ["0"])])
def test_if_else(x, esperado):
    saida, _ = rodar(f"x = {x}; if (x > 0) {{ print(1); }} else {{ print(0); }}")
    assert saida == esperado


def test_if_sem_else_com_condicao_falsa_nao_faz_nada():
    saida, _ = rodar("if (1 > 2) { print(1); }")
    assert saida == []


def test_bloco_solto():
    saida, _ = rodar("{ x = 3; { print(x); } }")
    assert saida == ["3"]


def test_programa_vazio():
    saida, _ = rodar("// só comentário\n")
    assert saida == []


# Ponta a ponta: arquivos de exemplo

def test_programa_valido_de_exemplo():
    codigo = (EXEMPLOS / "programa_valido.ml").read_text(encoding="utf-8")
    saida, _ = rodar(codigo)
    assert saida == ["15", "21", "24"]


def test_exemplo_do_enunciado():
    codigo = """
    x = 10;
    y = 2 * (x + 5);
    while (x > 0) {
        print(x);
        x = x - 1;
    }
    soma = 0;
    for (i = 0; i < 5; i = i + 1) {
        soma = soma + i;
    }
    if (soma > 20) {
        print(soma);
    } else {
        print(0);
    }
    """
    saida, interp = rodar(codigo)
    assert saida == ["10", "9", "8", "7", "6", "5", "4", "3", "2", "1", "0"]
    assert interp.tabela.buscar("y") == 30


def test_linha_de_comando_com_programa_valido(capsys):
    assert main([str(EXEMPLOS / "programa_valido.ml")]) == 0
    assert capsys.readouterr().out.split() == ["15", "21", "24"]
