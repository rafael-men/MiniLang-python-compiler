from __future__ import annotations

import sys
from typing import Callable

from src.ast_nodes import (
    Atribuicao,
    BinOp,
    Bloco,
    Booleano,
    Comando,
    Expr,
    For,
    If,
    Numero,
    Print,
    Programa,
    Variavel,
    While,
)
from src.lexer import LexerError, tokenizar
from src.parser import ErroSintatico, Parser


class ErroSemantico(Exception):

    def __init__(self, mensagem: str, linha: int = 0, coluna: int = 0):
        self.mensagem = mensagem
        self.linha = linha
        self.coluna = coluna
        super().__init__(f"Erro semântico (linha {linha}): {mensagem}")


class ErroLimiteIteracoes(Exception):
    # Não é erro da linguagem: é a proteção do interpretador contra laço
    # infinito (o problema da parada é indecidível, então usamos um limite).

    def __init__(self, limite: int, linha: int = 0):
        self.limite = limite
        self.linha = linha
        self.mensagem = f"laço passou do limite de {limite} iterações"
        super().__init__(f"Erro de execução (linha {linha}): {self.mensagem}")


class TabelaSimbolos:


    def __init__(self):
        self._valores: dict[str, int | bool] = {}

    def definir(self, nome: str, valor: int | bool) -> None:
        self._valores[nome] = valor

    def buscar(self, nome: str, linha: int = 0) -> int | bool:
        if nome not in self._valores:
            raise ErroSemantico(f"variável '{nome}' não definida", linha)
        return self._valores[nome]

    def existe(self, nome: str) -> bool:
        return nome in self._valores


_ARITMETICOS = {"+", "-", "*", "/"}
_RELACIONAIS = {"<", "<=", ">", ">="}
_IGUALDADE = {"==", "!="}


def _tipo(valor: int | bool) -> str:
    # bool é subclasse de int no Python (True + 1 == 2), por isso o
    # booleano é testado primeiro e nunca se usa isinstance(valor, int).
    return "booleano" if isinstance(valor, bool) else "inteiro"


def _dividir(a: int, b: int, linha: int) -> int:
    if b == 0:
        raise ErroSemantico("divisão por zero", linha)
    # Divisão inteira truncada em direção a zero (-7 / 2 = -3).
    # O // do Python arredonda para baixo (-7 // 2 = -4), por isso não serve.
    quociente = abs(a) // abs(b)
    return quociente if (a < 0) == (b < 0) else -quociente


def _formatar(valor: int | bool) -> str:
    if isinstance(valor, bool):
        return "true" if valor else "false"
    return str(valor)


class Interpretador:

    def __init__(self, max_iteracoes: int = 10_000,
                 escrever: Callable[[str], None] = print):
        self.tabela = TabelaSimbolos()
        self.max_iteracoes = max_iteracoes
        self.escrever = escrever

    # Comandos

    def executar_programa(self, programa: Programa) -> None:
        for comando in programa.comandos:
            self.executar(comando)

    def executar(self, comando: Comando) -> None:
        if isinstance(comando, Atribuicao):
            self.tabela.definir(comando.nome, self.avaliar(comando.expr))
        elif isinstance(comando, Print):
            self.escrever(_formatar(self.avaliar(comando.expr)))
        elif isinstance(comando, Bloco):
            for interno in comando.comandos:
                self.executar(interno)
        elif isinstance(comando, If):
            if self._condicao(comando.condicao, "if", comando.linha):
                self.executar(comando.entao)
            elif comando.senao is not None:
                self.executar(comando.senao)
        elif isinstance(comando, While):
            self._executar_while(comando)
        elif isinstance(comando, For):
            self._executar_for(comando)
        else:
            raise TypeError(f"comando desconhecido: {type(comando).__name__}")

    def _condicao(self, expr: Expr, comando: str, linha: int) -> bool:
        valor = self.avaliar(expr)
        if not isinstance(valor, bool):
            raise ErroSemantico(
                f"condição do '{comando}' deve ser booleana, recebeu {_tipo(valor)}",
                linha,
            )
        return valor

    def _contar_iteracao(self, iteracoes: int, linha: int) -> int:
        iteracoes += 1
        if iteracoes > self.max_iteracoes:
            raise ErroLimiteIteracoes(self.max_iteracoes, linha)
        return iteracoes

    def _executar_while(self, comando: While) -> None:
        iteracoes = 0
        while self._condicao(comando.condicao, "while", comando.linha):
            iteracoes = self._contar_iteracao(iteracoes, comando.linha)
            self.executar(comando.corpo)

    def _executar_for(self, comando: For) -> None:
        # inicialização; testa condição; corpo; atualização; repete
        self.executar(comando.inicializacao)
        iteracoes = 0
        while self._condicao(comando.condicao, "for", comando.linha):
            iteracoes = self._contar_iteracao(iteracoes, comando.linha)
            self.executar(comando.corpo)
            self.executar(comando.atualizacao)

    # Expressões

    def avaliar(self, expr: Expr) -> int | bool:
        if isinstance(expr, Numero):
            return expr.valor
        if isinstance(expr, Booleano):
            return expr.valor
        if isinstance(expr, Variavel):
            return self.tabela.buscar(expr.nome, expr.linha)
        if isinstance(expr, BinOp):
            return self._avaliar_binop(expr)
        raise TypeError(f"nó de expressão desconhecido: {type(expr).__name__}")

    def _avaliar_binop(self, expr: BinOp) -> int | bool:
        esq = self.avaliar(expr.esq)
        dir = self.avaliar(expr.dir)
        op = expr.op

        if op in _ARITMETICOS or op in _RELACIONAIS:
            if _tipo(esq) != "inteiro" or _tipo(dir) != "inteiro":
                raise ErroSemantico(
                    f"operador '{op}' exige dois inteiros, "
                    f"recebeu {_tipo(esq)} e {_tipo(dir)}",
                    expr.linha,
                )
            if op == "+":
                return esq + dir
            if op == "-":
                return esq - dir
            if op == "*":
                return esq * dir
            if op == "/":
                return _dividir(esq, dir, expr.linha)
            if op == "<":
                return esq < dir
            if op == "<=":
                return esq <= dir
            if op == ">":
                return esq > dir
            return esq >= dir

        if op in _IGUALDADE:
            if _tipo(esq) != _tipo(dir):
                raise ErroSemantico(
                    f"operador '{op}' compara valores de tipos diferentes: "
                    f"{_tipo(esq)} e {_tipo(dir)}",
                    expr.linha,
                )
            return esq == dir if op == "==" else esq != dir

        raise ErroSemantico(f"operador desconhecido '{op}'", expr.linha)


# Pipeline completo: lexer -> parser -> interpretador

def executar_codigo(codigo: str, max_iteracoes: int = 10_000,
                    escrever: Callable[[str], None] = print) -> Interpretador:
    programa = Parser(tokenizar(codigo)).parse_programa()
    interp = Interpretador(max_iteracoes, escrever)
    interp.executar_programa(programa)
    return interp


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print("uso: python -m src.interpreter arquivo.ml", file=sys.stderr)
        return 2
    try:
        with open(argv[0], encoding="utf-8") as arquivo:
            codigo = arquivo.read()
    except OSError as erro:
        print(f"não foi possível abrir '{argv[0]}': {erro.strerror}", file=sys.stderr)
        return 2
    try:
        executar_codigo(codigo)
    except (LexerError, ErroSintatico, ErroSemantico, ErroLimiteIteracoes) as erro:
        print(erro, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
