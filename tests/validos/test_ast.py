"""Testes da AST do MiniLang (src/ast_nodes.py).

As árvores são montadas à mão, sem lexer nem parser, para verificar que os
nós expressam a estrutura prevista no contrato do plano de trabalho.
"""

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


def test_ast_precedencia_1_mais_2_vezes_3():
    """1 + 2 * 3: a multiplicação fica abaixo da soma, no lado direito."""
    arvore = BinOp(
        "+",
        Numero(1, linha=1),
        BinOp("*", Numero(2, linha=1), Numero(3, linha=1), linha=1),
        linha=1,
    )

    # Raiz: soma
    assert isinstance(arvore, BinOp)
    assert arvore.op == "+"

    # Esquerda da soma: Numero(1)
    assert isinstance(arvore.esq, Numero)
    assert arvore.esq.valor == 1

    # Direita da soma: multiplicação
    assert isinstance(arvore.dir, BinOp)
    assert arvore.dir.op == "*"

    # Operandos da multiplicação: Numero(2) e Numero(3)
    assert isinstance(arvore.dir.esq, Numero)
    assert arvore.dir.esq.valor == 2
    assert isinstance(arvore.dir.dir, Numero)
    assert arvore.dir.dir.valor == 3


def test_ast_for_completo_com_as_tres_clausulas():
    """for (i = 0; i < 5; i = i + 1) { print(i); }"""
    laco = For(
        inicializacao=Atribuicao("i", Numero(0, linha=1), linha=1),
        condicao=BinOp("<", Variavel("i", linha=1), Numero(5, linha=1), linha=1),
        atualizacao=Atribuicao(
            "i",
            BinOp("+", Variavel("i", linha=1), Numero(1, linha=1), linha=1),
            linha=1,
        ),
        corpo=Bloco([Print(Variavel("i", linha=2), linha=2)], linha=1),
        linha=1,
    )

    # Inicialização: atribuição i = 0
    assert isinstance(laco.inicializacao, Atribuicao)
    assert laco.inicializacao.nome == "i"
    assert isinstance(laco.inicializacao.expr, Numero)
    assert laco.inicializacao.expr.valor == 0

    # Condição: expressão i < 5
    assert isinstance(laco.condicao, BinOp)
    assert laco.condicao.op == "<"
    assert isinstance(laco.condicao.esq, Variavel)
    assert laco.condicao.esq.nome == "i"
    assert isinstance(laco.condicao.dir, Numero)
    assert laco.condicao.dir.valor == 5

    # Atualização: atribuição i = i + 1
    assert isinstance(laco.atualizacao, Atribuicao)
    assert laco.atualizacao.nome == "i"
    assert isinstance(laco.atualizacao.expr, BinOp)
    assert laco.atualizacao.expr.op == "+"

    # Corpo: bloco com um print(i)
    assert isinstance(laco.corpo, Bloco)
    assert len(laco.corpo.comandos) == 1
    assert isinstance(laco.corpo.comandos[0], Print)
    assert laco.corpo.comandos[0].expr.nome == "i"

    # As linhas informadas são recuperadas
    assert laco.linha == 1
    assert laco.inicializacao.linha == 1
    assert laco.condicao.linha == 1
    assert laco.atualizacao.linha == 1
    assert laco.corpo.comandos[0].linha == 2


def test_ast_while_guarda_condicao_e_corpo():
    laco = While(
        Booleano(True, linha=4),
        Bloco([Atribuicao("x", Numero(1, linha=5), linha=5)], linha=4),
        linha=4,
    )

    assert isinstance(laco.condicao, Booleano)
    assert laco.condicao.valor is True
    assert isinstance(laco.corpo, Bloco)
    assert len(laco.corpo.comandos) == 1
    assert laco.linha == 4


def test_ast_if_sem_else_tem_senao_none():
    sem_else = If(Booleano(True), Bloco())
    com_else = If(Booleano(False), Bloco(), Bloco())

    assert sem_else.senao is None
    assert isinstance(com_else.senao, Bloco)


def test_ast_listas_de_comandos_nao_sao_compartilhadas():
    p1, p2 = Programa(), Programa()
    p1.comandos.append(Print(Numero(1)))
    assert p2.comandos == []

    b1, b2 = Bloco(), Bloco()
    b1.comandos.append(Print(Numero(1)))
    assert b2.comandos == []


def test_ast_linha_tem_padrao_e_aceita_valor_explicito():
    assert Numero(1).linha == 0
    assert Numero(1, 7).linha == 7
    assert Numero(1, linha=7).linha == 7
