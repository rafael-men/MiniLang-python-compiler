from __future__ import annotations

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
