from __future__ import annotations

from src.ast_nodes import BinOp, Booleano, Expr, Numero, Variavel

class ErroSemantico(Exception):

    def __init__(self, mensagem: str, linha: int = 0, coluna: int = 0):
        self.mensagem = mensagem
        self.linha = linha
        self.coluna = coluna
        super().__init__(f"Erro semântico (linha {linha}): {mensagem}")


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


class Interpretador:

    def __init__(self):
        self.tabela = TabelaSimbolos()

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
