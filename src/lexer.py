from __future__ import annotations
from dataclasses import dataclass


class LexerError(Exception):
    # Erro léxico com a posição do caractere que causou o problema.

    def __init__(self, mensagem: str, linha: int, coluna: int):
        self.mensagem = mensagem
        self.linha = linha
        self.coluna = coluna
        super().__init__(f"Erro léxico (linha {linha}, coluna {coluna}): {mensagem}")


@dataclass(frozen=True)
class Token:
    tipo: str
    valor: str | int | None
    linha: int
    coluna: int


_PALAVRAS_RESERVADAS = {
    "if": "IF",
    "else": "ELSE",
    "while": "WHILE",
    "for": "FOR",
    "print": "PRINT",
    "true": "TRUE",
    "false": "FALSE",
}

_OPERADORES_DUPLOS = {"==": "EQ", "!=": "NEQ", "<=": "LTE", ">=": "GTE"}
_TOKENS_SIMPLES = {
    "+": "PLUS",
    "-": "MINUS",
    "*": "STAR",
    "/": "SLASH",
    "<": "LT",
    ">": "GT",
    "=": "ASSIGN",
    "(": "LPAREN",
    ")": "RPAREN",
    "{": "LBRACE",
    "}": "RBRACE",
    ";": "SEMICOLON",
}


class Lexer:
    def __init__(self, codigo: str):
        self.codigo = codigo
        self.indice = 0
        self.linha = 1
        self.coluna = 1

    def _atual(self) -> str:
        return self.codigo[self.indice] if self.indice < len(self.codigo) else ""

    def _avancar(self) -> str:
        caractere = self._atual()
        if caractere:
            self.indice += 1
            if caractere == "\n":
                self.linha += 1
                self.coluna = 1
            else:
                self.coluna += 1
        return caractere

    @staticmethod
    def _inicio_identificador(caractere: str) -> bool:
        return caractere == "_" or "a" <= caractere <= "z" or "A" <= caractere <= "Z"

    @classmethod
    def _parte_identificador(cls, caractere: str) -> bool:
        return cls._inicio_identificador(caractere) or "0" <= caractere <= "9"

    def tokenizar(self) -> list[Token]:
        tokens: list[Token] = []
        while self._atual():
            caractere = self._atual()

            if caractere in " \t\r\n":
                self._avancar()
                continue

            if caractere == "/" and self.codigo[self.indice:self.indice + 2] == "//":
                while self._atual() and self._atual() != "\n":
                    self._avancar()
                continue

            inicio_linha, inicio_coluna = self.linha, self.coluna

            if self._inicio_identificador(caractere):
                inicio = self.indice
                while self._parte_identificador(self._atual()):
                    self._avancar()
                lexema = self.codigo[inicio:self.indice]
                tipo = _PALAVRAS_RESERVADAS.get(lexema, "ID")
                tokens.append(Token(tipo, lexema, inicio_linha, inicio_coluna))
                continue

            if "0" <= caractere <= "9":
                inicio = self.indice
                while "0" <= self._atual() <= "9":
                    self._avancar()
                if self._inicio_identificador(self._atual()):
                    raise LexerError("número mal formado (ex.: '1x')", inicio_linha, inicio_coluna)
                tokens.append(Token("NUM", int(self.codigo[inicio:self.indice]), inicio_linha, inicio_coluna))
                continue

            par = self.codigo[self.indice:self.indice + 2]
            if par in _OPERADORES_DUPLOS:
                self._avancar()
                self._avancar()
                tokens.append(Token(_OPERADORES_DUPLOS[par], par, inicio_linha, inicio_coluna))
                continue

            if caractere in _TOKENS_SIMPLES:
                self._avancar()
                tokens.append(Token(_TOKENS_SIMPLES[caractere], caractere, inicio_linha, inicio_coluna))
                continue

            raise LexerError(f"símbolo inesperado {caractere!r}", inicio_linha, inicio_coluna)

        tokens.append(Token("EOF", None, self.linha, self.coluna))
        return tokens


def tokenizar(codigo: str) -> list[Token]:
    return Lexer(codigo).tokenizar()
