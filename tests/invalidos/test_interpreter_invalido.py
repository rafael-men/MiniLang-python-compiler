"""Testes do interpretador com entradas inválidas (erros semânticos).

Resultado esperado: todos os casos abaixo devem lançar ErroSemantico
com uma mensagem que identifica o problema e a linha.

- Ler variável que nunca recebeu valor -> "variável 'x' não definida"
- Divisão por zero -> "divisão por zero"
- Aritmética ou comparação (<, <=, >, >=) com booleano -> "operador '+' exige dois inteiros"
- == ou != entre inteiro e booleano -> "compara valores de tipos diferentes"
- Condição não booleana em if, while ou for -> "condição do 'while' deve ser booleana"
- Variável de controle de laço não definida -> "variável 'k' não definida"
- Pela linha de comando, programa_invalido.ml (for sem atualização) e
  erros léxicos/semânticos são mostrados e o código de saída é 1
"""
from pathlib import Path

import pytest

from src.ast_nodes import BinOp, Numero, Variavel
from src.interpreter import ErroSemantico, Interpretador, TabelaSimbolos, executar_codigo, main
from src.lexer import tokenizar
from src.parser import Parser

EXEMPLOS = Path(__file__).resolve().parents[2] / "exemplos"


def rodar(codigo):
    return executar_codigo(codigo, escrever=lambda _: None)


def avaliar_codigo(codigo):
    return Interpretador().avaliar(Parser(tokenizar(codigo)).parse_expressao())


def test_buscar_variavel_nao_definida():
    tabela = TabelaSimbolos()
    with pytest.raises(ErroSemantico) as erro:
        tabela.buscar("x", linha=3)
    assert "não definida" in erro.value.mensagem
    assert erro.value.linha == 3


def test_variavel_nao_definida_em_expressao():
    with pytest.raises(ErroSemantico) as erro:
        Interpretador().avaliar(BinOp("+", Numero(1), Variavel("y", linha=4), linha=4))
    assert "variável 'y' não definida" in erro.value.mensagem
    assert erro.value.linha == 4


@pytest.mark.parametrize("codigo", ["1 / 0", "5 / (2 - 2)"])
def test_divisao_por_zero(codigo):
    with pytest.raises(ErroSemantico, match="divisão por zero"):
        avaliar_codigo(codigo)


@pytest.mark.parametrize("codigo", [
    "true + 1",
    "1 - false",
    "true * true",
    "8 / true",
    "1 < true",
    "false >= 0",
])
def test_operador_exige_inteiros(codigo):
    with pytest.raises(ErroSemantico, match="exige dois inteiros"):
        avaliar_codigo(codigo)


@pytest.mark.parametrize("codigo", ["1 == true", "false != 0"])
def test_igualdade_entre_tipos_diferentes(codigo):
    with pytest.raises(ErroSemantico, match="tipos diferentes"):
        avaliar_codigo(codigo)


def test_erro_indica_linha_do_operador():
    with pytest.raises(ErroSemantico) as erro:
        avaliar_codigo("1 +\n\n true")
    assert erro.value.linha == 1


# Erros semânticos em comandos e laços

@pytest.mark.parametrize("codigo, comando", [
    ("if (1) { print(1); }", "if"),
    ("x = 5; while (x) { x = x - 1; }", "while"),
    ("for (i = 0; i; i = i + 1) { }", "for"),
    ("for (i = 0; i + 1; i = i + 1) { }", "for"),
])
def test_condicao_nao_booleana(codigo, comando):
    with pytest.raises(ErroSemantico, match=f"condição do '{comando}' deve ser booleana"):
        rodar(codigo)


def test_condicao_nao_booleana_indica_linha_do_comando():
    with pytest.raises(ErroSemantico) as erro:
        rodar("x = 1;\n\nwhile (x) { }")
    assert erro.value.linha == 3


@pytest.mark.parametrize("codigo, nome", [
    ("while (k < 10) { k = k + 1; }", "k"),
    ("for (i = 0; j < 10; i = i + 1) { }", "j"),
    ("for (i = 0; i < 10; i = n + 1) { }", "n"),
])
def test_variavel_de_controle_nao_definida(codigo, nome):
    with pytest.raises(ErroSemantico, match=f"variável '{nome}' não definida"):
        rodar(codigo)


def test_erro_dentro_do_laco_interrompe_a_execucao():
    saida = []
    with pytest.raises(ErroSemantico, match="divisão por zero"):
        executar_codigo("for (i = 2; i >= 0; i = i - 1) { print(10 / i); }",
                        escrever=saida.append)
    assert saida == ["5", "10"]


# Linha de comando

def test_linha_de_comando_programa_invalido(capsys):
    assert main([str(EXEMPLOS / "programa_invalido.ml")]) == 1
    erro = capsys.readouterr().err
    assert "Erro sintático (linha 10, coluna 19)" in erro


@pytest.mark.parametrize("codigo, mensagem", [
    ("x = 1 @ 2;", "Erro léxico"),
    ("print(true + 1);", "Erro semântico"),
])
def test_linha_de_comando_mostra_erro(tmp_path, capsys, codigo, mensagem):
    arquivo = tmp_path / "erro.ml"
    arquivo.write_text(codigo, encoding="utf-8")
    assert main([str(arquivo)]) == 1
    assert mensagem in capsys.readouterr().err


def test_linha_de_comando_arquivo_inexistente(capsys):
    assert main(["nao_existe.ml"]) == 2
    assert "não foi possível abrir" in capsys.readouterr().err
