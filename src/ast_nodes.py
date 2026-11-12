"""Nós da AST (árvore sintática abstrata) do MiniLang."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Union


# Expressões: produzem um valor


@dataclass
class Numero:
    """Literal inteiro, ex.: 42."""

    valor: int
    linha: int = 0


@dataclass
class Booleano:
    """Literal booleano: true ou false."""

    valor: bool
    linha: int = 0


@dataclass
class Variavel:
    """Uso de uma variável dentro de uma expressão, ex.: x."""

    nome: str
    linha: int = 0


@dataclass
class BinOp:
    """Operação binária, ex.: a + b, x < 10.

    `op` é o texto do operador: "+", "-", "*", "/",
    "<", ">", "<=", ">=", "==", "!=".
    """

    op: str
    esq: Expr
    dir: Expr
    linha: int = 0

# Comandos: executam uma ação

@dataclass
class Atribuicao:
    """Atribuição, ex.: x = 10;"""

    nome: str
    expr: Expr
    linha: int = 0


@dataclass
class Print:
    """Impressão, ex.: print(x + 1);"""

    expr: Expr
    linha: int = 0


@dataclass
class Bloco:
    """Sequência de comandos entre chaves, ex.: { ... }"""

    comandos: list[Comando] = field(default_factory=list)
    linha: int = 0


@dataclass
class If:
    """Condicional. `senao` é None quando não há else."""

    condicao: Expr
    entao: Bloco
    senao: Optional[Bloco] = None
    linha: int = 0


@dataclass
class While:
    """Laço while (condicao) { corpo }"""

    condicao: Expr
    corpo: Bloco
    linha: int = 0


@dataclass
class For:
    """Laço for (inicializacao; condicao; atualizacao) { corpo }

    As três cláusulas são obrigatórias na MiniLang, por isso nenhuma
    é Optional. Inicialização e atualização são atribuições.
    """

    inicializacao: Atribuicao
    condicao: Expr
    atualizacao: Atribuicao
    corpo: Bloco
    linha: int = 0


@dataclass
class Programa:
    """Raiz da AST: a lista de comandos do programa inteiro."""

    comandos: list[Comando] = field(default_factory=list)
    linha: int = 0

# Apelidos de tipo (só para documentar o que cada campo aceita)

Expr = Union[Numero, Booleano, Variavel, BinOp]
Comando = Union[Atribuicao, Print, Bloco, If, While, For]
