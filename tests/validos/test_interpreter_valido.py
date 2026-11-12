from src.interpreter import TabelaSimbolos

def test_definir_e_buscar_inteiro():
    tabela = TabelaSimbolos()
    tabela.definir("x", 10)
    assert tabela.buscar("x") == 10


def test_definir_e_buscar_booleano():
    tabela = TabelaSimbolos()
    tabela.definir("ok", True)
    assert tabela.buscar("ok") is True


def test_atribuir_de_novo_atualiza_valor():
    tabela = TabelaSimbolos()
    tabela.definir("x", 1)
    tabela.definir("x", 2)
    assert tabela.buscar("x") == 2


def test_existe():
    tabela = TabelaSimbolos()
    assert not tabela.existe("x")
    tabela.definir("x", 0)
    assert tabela.existe("x")
