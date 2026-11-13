"""Testes válidos do parser de expressões (usa o lexer real)."""

import pytest

from src.ast_nodes import (
    Atribuicao,
    BinOp,
    Bloco,
    Booleano,
    For,
    If,
    Numero,
    Print,
    Programa,
    Variavel,
    While,
)
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


def programa(codigo):
    return Parser(tokenizar(codigo)).parse_programa()


def test_programa_vazio():
    assert programa("") == Programa([], linha=1)


def test_programa_so_com_comentario():
    # Programa vazio: linha do EOF (o comentário ocupa a linha 1, o EOF fica na 2)
    assert programa("// nada aqui\n") == Programa([], linha=2)


def test_atribuicao_simples():
    arvore = programa("x = 10;")
    assert arvore == Programa([Atribuicao("x", Numero(10, linha=1), linha=1)], linha=1)


def test_atribuicao_com_expressao():
    arvore = programa("y = 2 * (x + 5);")
    cmd = arvore.comandos[0]
    assert isinstance(cmd, Atribuicao)
    assert cmd.nome == "y"
    assert cmd.expr.op == "*"
    assert cmd.expr.esq == Numero(2, linha=1)
    assert cmd.expr.dir.op == "+"
    assert cmd.expr.dir.esq == Variavel("x", linha=1)
    assert cmd.expr.dir.dir == Numero(5, linha=1)


def test_atribuicao_de_booleano():
    cmd = programa("ok = x < 3;").comandos[0]
    assert cmd.nome == "ok"
    assert cmd.expr.op == "<"


def test_print():
    cmd = programa("print(x + 1);").comandos[0]
    assert isinstance(cmd, Print)
    assert cmd.expr == BinOp("+", Variavel("x", linha=1), Numero(1, linha=1), linha=1)
    assert cmd.linha == 1


def test_if_sem_else():
    cmd = programa("if (x > 0) { print(x); }").comandos[0]
    assert isinstance(cmd, If)
    assert cmd.condicao.op == ">"
    assert cmd.entao == Bloco([Print(Variavel("x", linha=1), linha=1)], linha=1)
    assert cmd.senao is None


def test_if_com_else():
    cmd = programa("if (x > 0) { print(x); } else { print(0); }").comandos[0]
    assert isinstance(cmd, If)
    assert cmd.entao.comandos == [Print(Variavel("x", linha=1), linha=1)]
    assert isinstance(cmd.senao, Bloco)
    assert cmd.senao.comandos == [Print(Numero(0, linha=1), linha=1)]


def test_bloco_com_varios_comandos():
    arvore = programa("{ a = 1; b = 2; print(a + b); }")
    bloco = arvore.comandos[0]
    assert isinstance(bloco, Bloco)
    assert [type(c) for c in bloco.comandos] == [Atribuicao, Atribuicao, Print]
    assert bloco.comandos[0].nome == "a"
    assert bloco.comandos[1].nome == "b"
    assert bloco.comandos[2].expr.op == "+"


def test_bloco_vazio():
    assert programa("{ }").comandos == [Bloco([], linha=1)]


def test_while():
    cmd = programa("while (x > 0) { x = x - 1; }").comandos[0]
    assert isinstance(cmd, While)
    assert cmd.condicao == BinOp(">", Variavel("x", linha=1), Numero(0, linha=1), linha=1)
    assert isinstance(cmd.corpo, Bloco)
    assert len(cmd.corpo.comandos) == 1
    atrib = cmd.corpo.comandos[0]
    assert atrib.nome == "x"
    assert atrib.expr.op == "-"


def test_for_completo_com_tres_clausulas():
    cmd = programa("for (i = 0; i < 5; i = i + 1) { soma = soma + i; }").comandos[0]
    assert isinstance(cmd, For)
    assert cmd.inicializacao == Atribuicao("i", Numero(0, linha=1), linha=1)
    assert cmd.condicao == BinOp("<", Variavel("i", linha=1), Numero(5, linha=1), linha=1)
    assert isinstance(cmd.atualizacao, Atribuicao)
    assert cmd.atualizacao.nome == "i"
    assert cmd.atualizacao.expr.op == "+"
    assert isinstance(cmd.corpo, Bloco)
    assert cmd.corpo.comandos[0].nome == "soma"


def test_comandos_aninhados():
    codigo = (
        "while (i < 3) {\n"
        "  if (i == 1) {\n"
        "    for (j = 0; j < 2; j = j + 1) { print(j); }\n"
        "  } else {\n"
        "    { print(i); }\n"
        "  }\n"
        "  i = i + 1;\n"
        "}"
    )
    laco = programa(codigo).comandos[0]
    assert isinstance(laco, While)
    assert [type(c) for c in laco.corpo.comandos] == [If, Atribuicao]

    cond = laco.corpo.comandos[0]
    assert isinstance(cond.entao.comandos[0], For)
    assert isinstance(cond.entao.comandos[0].corpo.comandos[0], Print)
    # else contém um bloco aninhado
    assert isinstance(cond.senao.comandos[0], Bloco)
    assert isinstance(cond.senao.comandos[0].comandos[0], Print)


def test_if_aninhado_sem_else_interno():
    # o else pertence ao if mais interno possível pela gramática (chaves obrigatórias)
    cmd = programa("if (a) { if (b) { x = 1; } } else { x = 2; }").comandos[0]
    assert cmd.senao is not None
    assert cmd.entao.comandos[0].senao is None


def test_programa_com_varios_comandos():
    codigo = (
        "x = 10;\n"
        "while (x > 0) { print(x); x = x - 1; }\n"
        "soma = 0;\n"
        "for (i = 0; i < 5; i = i + 1) { soma = soma + i; }\n"
        "if (soma > 20) { print(soma); } else { print(0); }\n"
    )
    arvore = programa(codigo)
    assert [type(c) for c in arvore.comandos] == [Atribuicao, While, Atribuicao, For, If]
    assert [c.linha for c in arvore.comandos] == [1, 2, 3, 4, 5]


def test_convencao_de_linha_dos_comandos():
    arvore = programa("// c\n\nx\n=\n1;\nprint(x);\n{\n}\nif (true)\n{ }")
    assert arvore.linha == 3
    atrib, imprime, bloco, cond = arvore.comandos
    assert atrib.linha == 3          # linha do identificador
    assert atrib.expr.linha == 5     # linha do literal
    assert imprime.linha == 6
    assert bloco.linha == 7          # linha do '{'
    assert cond.linha == 9           # linha do 'if'
    assert cond.entao.linha == 10


def test_exemplo_valido_do_repositorio():
    with open("exemplos/programa_valido.ml", encoding="utf-8") as f:
        arvore = programa(f.read())
    tipos = [type(c) for c in arvore.comandos]
    assert While in tipos and For in tipos
    laco_for = next(c for c in arvore.comandos if isinstance(c, For))
    assert laco_for.inicializacao.nome == "n"
    assert laco_for.condicao.op == "<="
    assert laco_for.atualizacao.nome == "n"


def test_expressoes_continuam_funcionando_pela_interface_antiga():
    assert analisar("1 + 2 * 3").op == "+"
