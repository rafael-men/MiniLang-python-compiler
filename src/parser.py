"""Parser descendente recursivo de expressões do MiniLang.

Gramática (EBNF, ver docs/gramatica.md):

    Expressao = Soma [ OpRel Soma ] ;
    OpRel     = "==" | "!=" | "<" | "<=" | ">" | ">=" ;
    Soma      = Termo { ( "+" | "-" ) Termo } ;
    Termo     = Fator { ( "*" | "/" ) Fator } ;
    Fator     = NUM | "true" | "false" | ID | "(" Expressao ")" ;

Cada não terminal é um método. A precedência vem da profundidade das
chamadas (comparação < soma < termo < fator); a associatividade à esquerda
vem dos laços `while` que correspondem às repetições `{ ... }`; a
não associatividade das comparações vem do `[ ... ]` (no máximo uma).

Interface pública:

    Parser(tokenizar(codigo)).parse_expressao()

`parse_expressao()` lê uma expressão completa e exige `EOF` em seguida.
Os métodos `expressao`, `soma`, `termo` e `fator` NÃO exigem `EOF`: o futuro
parser de comandos (atribuição, print, if, while, for) poderá chamá-los
e continuar de onde a expressão terminou.

Convenção de `linha` nos nós da AST: literais e variáveis recebem a linha
do seu token; `BinOp` recebe a linha do token do operador.

Erros léxicos (`LexerError`) não são capturados aqui: o parser só recebe
tokens já produzidos.
"""

from __future__ import annotations

from src.ast_nodes import BinOp, Booleano, Expr, Numero, Variavel
from src.lexer import Token


class ErroSintatico(Exception):
    """Erro sintático com o que era esperado, o que foi encontrado e a posição."""

    def __init__(self, mensagem: str, linha: int, coluna: int,
                 esperado: str = "", encontrado: str = ""):
        self.mensagem = mensagem
        self.linha = linha
        self.coluna = coluna
        self.esperado = esperado
        self.encontrado = encontrado
        super().__init__(f"Erro sintático (linha {linha}, coluna {coluna}): {mensagem}")


_OPERADORES_RELACIONAIS = {"EQ", "NEQ", "LT", "LTE", "GT", "GTE"}
_OPERADORES_SOMA = {"PLUS", "MINUS"}
_OPERADORES_TERMO = {"STAR", "SLASH"}


def _descrever(token: Token) -> str:
    """Texto legível de um token para as mensagens de erro."""

    if token.tipo == "EOF":
        return "fim da entrada"
    return f"'{token.valor}'"


class Parser:
    def __init__(self, tokens: list[Token]):
        if not tokens or tokens[-1].tipo != "EOF":
            raise ValueError("a lista de tokens deve terminar com EOF")
        self.tokens = tokens
        self.pos = 0

    # Utilitários

    def _atual(self) -> Token:
        return self.tokens[self.pos]

    def _consumir(self) -> Token:
        token = self.tokens[self.pos]
        if token.tipo != "EOF":  # nunca passa do EOF
            self.pos += 1
        return token

    def _erro(self, esperado: str, token: Token) -> ErroSintatico:
        encontrado = _descrever(token)
        return ErroSintatico(
            f"esperado {esperado}, encontrado {encontrado}",
            token.linha, token.coluna, esperado, encontrado,
        )

    # Interface pública

    def parse_expressao(self) -> Expr:
        """Analisa uma expressão completa; o próximo token deve ser EOF."""

        arvore = self.expressao()
        if self._atual().tipo != "EOF":
            raise self._erro("fim da expressão", self._atual())
        return arvore

    # Uma função por produção

    def expressao(self) -> Expr:
        """Expressao = Soma [ OpRel Soma ] ;  (comparação não associativa)"""

        esq = self.soma()
        if self._atual().tipo in _OPERADORES_RELACIONAIS:
            op = self._consumir()
            dir = self.soma()
            if self._atual().tipo in _OPERADORES_RELACIONAIS:
                extra = self._atual()
                raise ErroSintatico(
                    f"comparação encadeada não permitida ({_descrever(extra)} "
                    f"após uma comparação); use parênteses",
                    extra.linha, extra.coluna,
                    "parênteses para agrupar a comparação", _descrever(extra),
                )
            return BinOp(op.valor, esq, dir, linha=op.linha)
        return esq

    def soma(self) -> Expr:
        """Soma = Termo { ( "+" | "-" ) Termo } ;  (associativa à esquerda)"""

        esq = self.termo()
        while self._atual().tipo in _OPERADORES_SOMA:
            op = self._consumir()
            esq = BinOp(op.valor, esq, self.termo(), linha=op.linha)
        return esq

    def termo(self) -> Expr:
        """Termo = Fator { ( "*" | "/" ) Fator } ;  (associativo à esquerda)"""

        esq = self.fator()
        while self._atual().tipo in _OPERADORES_TERMO:
            op = self._consumir()
            esq = BinOp(op.valor, esq, self.fator(), linha=op.linha)
        return esq

    def fator(self) -> Expr:
        """Fator = NUM | "true" | "false" | ID | "(" Expressao ")" ;"""

        token = self._atual()
        if token.tipo == "NUM":
            self._consumir()
            return Numero(token.valor, linha=token.linha)
        if token.tipo == "TRUE":
            self._consumir()
            return Booleano(True, linha=token.linha)
        if token.tipo == "FALSE":
            self._consumir()
            return Booleano(False, linha=token.linha)
        if token.tipo == "ID":
            self._consumir()
            return Variavel(token.valor, linha=token.linha)
        if token.tipo == "LPAREN":
            self._consumir()
            interna = self.expressao()
            if self._atual().tipo != "RPAREN":
                raise self._erro("')'", self._atual())
            self._consumir()
            return interna  # parênteses só agrupam; não geram nó
        raise self._erro("número, 'true', 'false', identificador ou '('", token)
