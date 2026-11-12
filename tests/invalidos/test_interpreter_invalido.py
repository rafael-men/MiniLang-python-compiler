import pytest

from src.interpreter import ErroSemantico, TabelaSimbolos


def test_buscar_variavel_nao_definida():
    tabela = TabelaSimbolos()
    with pytest.raises(ErroSemantico) as erro:
        tabela.buscar("x", linha=3)
    assert "não definida" in erro.value.mensagem
    assert erro.value.linha == 3
