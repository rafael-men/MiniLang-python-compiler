from src.lexer import Lexer, tokenizar


def test_palavras_reservadas_e_identificadores_parecidos():
    tokens = tokenizar("if else while whilex for print true false fora")
    assert [token.tipo for token in tokens] == [
        "IF", "ELSE", "WHILE", "ID", "FOR", "PRINT", "TRUE", "FALSE", "ID", "EOF"
    ]
    assert tokens[3].valor == "whilex"
    assert tokens[8].valor == "fora"


def test_numero_identificador_operadores_e_delimitadores():
    tokens = tokenizar("_x2 = 42 + 3 * 2 / 1;")
    assert [(token.tipo, token.valor) for token in tokens] == [
        ("ID", "_x2"), ("ASSIGN", "="), ("NUM", 42), ("PLUS", "+"),
        ("NUM", 3), ("STAR", "*"), ("NUM", 2), ("SLASH", "/"),
        ("NUM", 1), ("SEMICOLON", ";"), ("EOF", None),
    ]


def test_operadores_de_um_e_dois_caracteres():
    tokens = tokenizar("+ - * / < <= > >= = == != ( ) { } ;")
    assert [token.tipo for token in tokens] == [
        "PLUS", "MINUS", "STAR", "SLASH", "LT", "LTE", "GT", "GTE",
        "ASSIGN", "EQ", "NEQ", "LPAREN", "RPAREN", "LBRACE", "RBRACE",
        "SEMICOLON", "EOF",
    ]


def test_comentarios_sao_ignorados_e_linhas_colunas_sao_preservadas():
    tokens = Lexer("x=1; // comentário ignorado\nprint(x);").tokenizar()
    assert [(token.tipo, token.linha, token.coluna) for token in tokens] == [
        ("ID", 1, 1), ("ASSIGN", 1, 2), ("NUM", 1, 3), ("SEMICOLON", 1, 4),
        ("PRINT", 2, 1), ("LPAREN", 2, 6), ("ID", 2, 7), ("RPAREN", 2, 8),
        ("SEMICOLON", 2, 9), ("EOF", 2, 10),
    ]


def test_barra_sem_comentario_e_comentario_no_fim_do_arquivo():
    assert [token.tipo for token in tokenizar("8/2 // fim")] == ["NUM", "SLASH", "NUM", "EOF"]
