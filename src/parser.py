"""Parser descendente recursivo de expressões do MiniLang.

Gramática (EBNF, ver docs/gramatica.md):

    Programa      = { Comando } ;
    Comando       = AtribuicaoCmd | PrintCmd | Bloco | IfCmd | WhileCmd | ForCmd ;
    Bloco         = "{" { Comando } "}" ;
    Atribuicao    = ID "=" Expressao ;
    AtribuicaoCmd = Atribuicao ";" ;
    PrintCmd      = "print" "(" Expressao ")" ";" ;
    IfCmd         = "if" "(" Expressao ")" Bloco [ "else" Bloco ] ;
    WhileCmd      = "while" "(" Expressao ")" Bloco ;
    ForCmd        = "for" "(" Atribuicao ";" Expressao ";" Atribuicao ")" Bloco ;

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

    Parser(tokenizar(codigo)).parse_programa()    # programa completo
    Parser(tokenizar(codigo)).parse_expressao()   # só uma expressão

Ambos exigem `EOF` ao final. Os métodos por produção (`expressao`, `soma`,
`termo`, `fator`, `comando`, `bloco`, `atribuicao`, ...) NÃO exigem `EOF`
e continuam de onde a produção termina.

Convenção de `linha` nos nós da AST:
  - literais e variáveis: linha do seu token;
  - `BinOp`: linha do token do operador;
  - `Atribuicao`: linha do identificador (primeiro token);
  - `Print`, `If`, `While`, `For`: linha da palavra reservada;
  - `Bloco`: linha do `{`;
  - `Programa`: linha do primeiro token (a do `EOF` se o programa é vazio).
O `else` não tem nó próprio; `If.senao` é `None` quando ele não existe.

Erros léxicos (`LexerError`) não são capturados aqui: o parser só recebe
tokens já produzidos.
"""

from __future__ import annotations

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

    def _esperar(self, tipo: str, descricao: str) -> Token:
        """Consome um token do tipo dado ou lança ErroSintatico."""

        if self._atual().tipo != tipo:
            raise self._erro(descricao, self._atual())
        return self._consumir()

    # Interface pública

    def parse_programa(self) -> Programa:
        """Programa = { Comando } ;  Exige EOF ao final."""

        linha = self._atual().linha
        comandos: list[Comando] = []
        while self._atual().tipo != "EOF":
            comandos.append(self.comando())
        return Programa(comandos, linha=linha)

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

    # Comandos: uma função por produção

    def comando(self) -> Comando:
        """Comando = AtribuicaoCmd | PrintCmd | Bloco | IfCmd | WhileCmd | ForCmd ;


        O primeiro token decide a produção (LL(1))."""
        tipo = self._atual().tipo
        if tipo == "ID":
            return self.atribuicao_cmd()
        if tipo == "PRINT":
            return self.print_cmd()
        if tipo == "LBRACE":
            return self.bloco()
        if tipo == "IF":
            return self.if_cmd()
        if tipo == "WHILE":
            return self.while_cmd()
        if tipo == "FOR":
            return self.for_cmd()
        raise self._erro(
            "comando (identificador, 'print', 'if', 'while', 'for' ou '{')",
            self._atual(),
        )

    def bloco(self) -> Bloco:
        """Bloco = "{" { Comando } "}" ;"""

        abre = self._esperar("LBRACE", "'{'")
        comandos: list[Comando] = []
        while self._atual().tipo not in ("RBRACE", "EOF"):
            comandos.append(self.comando())
        self._esperar("RBRACE", "'}'")
        return Bloco(comandos, linha=abre.linha)

    def atribuicao(self) -> Atribuicao:
        """Atribuicao = ID "=" Expressao ;  (sem ';', usada também no for)"""

        nome = self._esperar("ID", "identificador")
        self._esperar("ASSIGN", "'='")
        return Atribuicao(nome.valor, self.expressao(), linha=nome.linha)

    def atribuicao_cmd(self) -> Atribuicao:
        """AtribuicaoCmd = Atribuicao ";" ;"""

        no = self.atribuicao()
        self._esperar("SEMICOLON", "';'")
        return no

    def print_cmd(self) -> Print:
        """PrintCmd = "print" "(" Expressao ")" ";" ;"""

        palavra = self._esperar("PRINT", "'print'")
        self._esperar("LPAREN", "'('")
        expr = self.expressao()
        self._esperar("RPAREN", "')'")
        self._esperar("SEMICOLON", "';'")
        return Print(expr, linha=palavra.linha)

    def if_cmd(self) -> If:
        """IfCmd = "if" "(" Expressao ")" Bloco [ "else" Bloco ] ;"""

        palavra = self._esperar("IF", "'if'")
        self._esperar("LPAREN", "'('")
        condicao = self.expressao()
        self._esperar("RPAREN", "')'")
        entao = self.bloco()
        senao = None
        if self._atual().tipo == "ELSE":
            self._consumir()
            senao = self.bloco()  # 'else if' não existe na gramática
        return If(condicao, entao, senao, linha=palavra.linha)

    def while_cmd(self) -> While:
        """WhileCmd = "while" "(" Expressao ")" Bloco ;"""

        palavra = self._esperar("WHILE", "'while'")
        self._esperar("LPAREN", "'('")
        condicao = self.expressao()
        self._esperar("RPAREN", "')'")
        corpo = self.bloco()
        return While(condicao, corpo, linha=palavra.linha)

    def for_cmd(self) -> For:
        """ForCmd = "for" "(" Atribuicao ";" Expressao ";" Atribuicao ")" Bloco ;

        As três cláusulas são obrigatórias."""

        palavra = self._esperar("FOR", "'for'")
        self._esperar("LPAREN", "'('")
        inicializacao = self.atribuicao()
        self._esperar("SEMICOLON", "';'")
        condicao = self.expressao()
        self._esperar("SEMICOLON", "';'")
        atualizacao = self.atribuicao()
        self._esperar("RPAREN", "')'")
        corpo = self.bloco()
        return For(inicializacao, condicao, atualizacao, corpo, linha=palavra.linha)
