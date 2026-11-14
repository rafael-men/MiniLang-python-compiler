"""Testes de laço infinito com limite de iterações.

Resultado esperado: todos os casos abaixo lançam ErroLimiteIteracoes
("laço passou do limite de N iterações") em vez de travar a suíte.
- while (true) { } -> limite atingido
- while cuja variável nunca muda -> limite atingido
- for cuja atualização não altera a variável de controle -> limite atingido
- laço que passa do limite por uma iteração -> limite atingido
- pela linha de comando, o erro aparece e o código de saída é 1
"""
import pytest

from src.interpreter import ErroLimiteIteracoes, executar_codigo, main


def rodar(codigo, max_iteracoes=100):
    return executar_codigo(codigo, max_iteracoes, lambda _: None)


def test_while_true():
    with pytest.raises(ErroLimiteIteracoes) as erro:
        rodar("while (true) { }")
    assert erro.value.limite == 100
    assert erro.value.linha == 1


def test_while_com_variavel_que_nunca_muda():
    with pytest.raises(ErroLimiteIteracoes):
        rodar("x = 0;\nwhile (x < 10) {\n  print(x);\n}")


def test_for_com_atualizacao_que_nao_avanca():
    with pytest.raises(ErroLimiteIteracoes) as erro:
        rodar("\n\nfor (i = 0; i < 10; i = i) { }")
    assert erro.value.linha == 3


def test_passa_do_limite_por_uma_iteracao():
    with pytest.raises(ErroLimiteIteracoes):
        rodar("x = 0; while (x < 6) { x = x + 1; }", max_iteracoes=5)


def test_limite_padrao_e_10000():
    with pytest.raises(ErroLimiteIteracoes) as erro:
        executar_codigo("while (true) { }", escrever=lambda _: None)
    assert erro.value.limite == 10_000


def test_linha_de_comando_mostra_erro(tmp_path, capsys):
    arquivo = tmp_path / "infinito.ml"
    arquivo.write_text("while (true) { }", encoding="utf-8")
    assert main([str(arquivo)]) == 1
    assert "limite de 10000 iterações" in capsys.readouterr().err
