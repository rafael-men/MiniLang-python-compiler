import pytest

from src.interpreter import executar_codigo


def rodar(codigo, max_iteracoes=10_000):
    saida = []
    interp = executar_codigo(codigo, max_iteracoes, saida.append)
    return saida, interp


# while

def test_while_nao_executa_com_condicao_falsa_na_entrada():
    saida, _ = rodar("x = 10; while (x < 5) { print(x); x = x + 1; }")
    assert saida == []


def test_while_executa_uma_vez():
    saida, _ = rodar("x = 4; while (x < 5) { print(x); x = x + 1; }")
    assert saida == ["4"]


def test_while_executa_n_vezes():
    saida, interp = rodar("x = 0; while (x < 5) { print(x); x = x + 1; }")
    assert saida == ["0", "1", "2", "3", "4"]
    assert interp.tabela.buscar("x") == 5


def test_while_decrescente():
    saida, _ = rodar("x = 3; while (x > 0) { print(x); x = x - 1; }")
    assert saida == ["3", "2", "1"]


# for

def test_for_nao_executa_com_condicao_falsa_na_entrada():
    saida, interp = rodar("for (i = 10; i < 5; i = i + 1) { print(i); }")
    assert saida == []
    # a inicialização roda mesmo que o corpo não execute
    assert interp.tabela.buscar("i") == 10


def test_for_executa_uma_vez():
    saida, _ = rodar("for (i = 0; i < 1; i = i + 1) { print(i); }")
    assert saida == ["0"]


def test_for_executa_n_vezes():
    saida, interp = rodar("soma = 0; for (i = 0; i < 5; i = i + 1) { soma = soma + i; }")
    assert interp.tabela.buscar("soma") == 10
    assert interp.tabela.buscar("i") == 5  # escopo único: i continua existindo


@pytest.mark.parametrize("atualizacao, esperado", [
    ("i = i + 2", ["0", "2", "4", "6", "8"]),
    ("i = i * 2 + 1", ["0", "1", "3", "7"]),
])
def test_for_com_atualizacao_que_altera_a_variavel_de_controle(atualizacao, esperado):
    saida, _ = rodar(f"for (i = 0; i < 10; {atualizacao}) {{ print(i); }}")
    assert saida == esperado


def test_for_decrescente():
    saida, _ = rodar("for (i = 3; i > 0; i = i - 1) { print(i); }")
    assert saida == ["3", "2", "1"]


def test_for_ordem_inicializacao_condicao_corpo_atualizacao():
    # o corpo vê o valor antes da atualização; a atualização roda depois do corpo
    saida, interp = rodar("for (i = 0; i < 2; i = i + 1) { print(i); i = i + 10; }")
    assert saida == ["0"]
    assert interp.tabela.buscar("i") == 11


def test_lacos_aninhados():
    saida, _ = rodar(
        "for (i = 1; i <= 2; i = i + 1) {"
        "  j = 1;"
        "  while (j <= 2) { print(i * 10 + j); j = j + 1; }"
        "}"
    )
    assert saida == ["11", "12", "21", "22"]


# limite de iterações (borda)

def test_laco_exatamente_no_limite_e_permitido():
    saida, _ = rodar("x = 0; while (x < 5) { x = x + 1; }", max_iteracoes=5)
    assert saida == []


def test_for_exatamente_no_limite_e_permitido():
    saida, _ = rodar("for (i = 0; i < 5; i = i + 1) { print(i); }", max_iteracoes=5)
    assert len(saida) == 5
