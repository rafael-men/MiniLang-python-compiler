# Diário de Bordo — MiniLang

Registro semanal do desenvolvimento do compilador-intérprete MiniLang.

**Integrantes:** Rafael Menezes Gonçalves · Richard de Souza Santos · Wilia Francisco da Silva

**Como usar:** cada integrante preenche a própria parte da semana. Toda vez que usar IA generativa, registre na tabela "Uso de IA" no mesmo dia, enquanto ainda lembra o que pediu e o que mudou.

---

## Template da semana (copiar para cada nova semana)

```markdown
## Semana N — dd/mm a dd/mm

### Objetivo da semana
O que o grupo planejou entregar nesta semana.

### Atividades por integrante
| Data | Integrante | Atividade | Arquivos | Commit |
| --- | --- | --- | --- | --- |
| dd/mm | Nome | O que foi feito | caminho/arquivo | hash |

### Uso de IA
| Data | Integrante | Ferramenta / modelo | Para que foi usada | Resultado | O que foi corrigido e por quê |
| --- | --- | --- | --- | --- | --- |
| dd/mm | Nome | ex.: Claude Opus 5.5 | pedido feito à IA | Aceito / Reescrito / Descartado | conceito teórico envolvido na correção |

### Decisões tomadas
- Decisão e justificativa.

### Dificuldades e como foram resolvidas
- Problema → solução.

### Próximos passos
- [ ] Tarefa — responsável — prazo
```

---

## Semana 1 — 11/11 a 15/11

### Objetivo da semana
Montar a estrutura do repositório, dividir o trabalho, combinar as interfaces entre as fases (tokens, nós da AST, erros) e entregar a gramática, a AST e o início do lexer, do parser e do interpretador.

### Atividades por integrante
| Data | Integrante | Atividade | Arquivos | Commit |
| --- | --- | --- | --- | --- |
| 11/11 | Rafael | Criação do repositório | README.md, .gitignore | f5343c8 |
| 11/11 | Wilia | Estrutura de pastas e arquivos conforme o enunciado | docs/, exemplos/, src/, tests/ | d5e3127, aca688f |
| 11/11 | Wilia | Plano de trabalho com divisão de tarefas e cronograma até 20/11 | (documento interno do grupo) | — |
| 12/11 | Richard | Rascunho dos nós da AST (expressões e comandos, incluindo While e For) | src/ast_nodes.py | d0a23bb |
| 12/11 | Rafael | pytest adicionado e funcionando | requirements.txt | 9e30085 |
| 12/11 | Rafael | Tabela de tokens, tabela de transições do AFD, EBNF, tabela de precedência e 5 exemplos comentados; programas de exemplo válido e inválido | docs/gramatica.md, exemplos/*.ml | d3b0ee6 |
| 12/11 | Wilia | Diário de bordo com template semanal | docs/diario_de_bordo.md | |
| 12/11 | Rafael | Inclusão das regras semânticas de tipos, condições, `print`, divisão inteira, divisão por zero e variáveis | docs/gramatica.md, docs/diario_de_bordo.md | — |
| 12/11 | Richard | Testes permanentes da AST (precedência de `1 + 2 * 3`, `For` com as três cláusulas, `While`, `If` sem `else`, listas independentes e `linha`). Rafael implementou o lexer e a interface de `Token` foi confirmada, o que permitiu iniciar o parser de expressões (ver Semana 1, 13/11) | tests/validos/test_ast.py, docs/diario_de_bordo.md | 8da8196 |
| 13/11 | Richard | Parser descendente recursivo de expressões (`expressao`, `soma`, `termo`, `fator`), `ErroSintatico` e testes válidos e inválidos com o lexer real | src/parser.py, tests/validos/test_parser_valido.py, tests/invalidos/test_parser_invalido.py | 4624f89 |
| 13/11 | Richard | Parser de comandos e de programa completo: `parse_programa`, `comando`, `bloco`, `atribuicao`, `atribuicao_cmd`, `print_cmd`, `if_cmd`, `while_cmd` e `for_cmd` (as três cláusulas do `for` obrigatórias), reutilizando as funções de expressão; testes válidos e inválidos dos comandos | src/parser.py, tests/validos/test_parser_valido.py, tests/invalidos/test_parser_invalido.py | a32491a |
| 12/11 | Wilia | Tabela de símbolos (`definir`, `buscar`, `existe`) e `ErroSemantico`, com testes | src/interpreter.py, tests/validos/test_interpreter_valido.py, tests/invalidos/test_interpreter_invalido.py | ed9b9c1, c1a647c |
| 13/11 | Wilia | Avaliação de expressões (`Numero`, `Booleano`, `Variavel`, `BinOp`) seguindo as regras semânticas da gramática: aritmética e relacionais só com inteiros, `==`/`!=` só entre tipos iguais, divisão inteira truncada em direção a zero e erro de divisão por zero; testes com AST montada à mão e com o lexer e o parser reais | src/interpreter.py, tests/validos/test_interpreter_valido.py, tests/invalidos/test_interpreter_invalido.py | |

### Uso de IA
| Data | Integrante | Ferramenta / modelo | Para que foi usada | Resultado | O que foi corrigido e por quê |
| --- | --- | --- | --- | --- | --- |
| 11/11 | Wilia | Claude Code (Claude Opus 5.5) | Montar o plano de trabalho com divisão entre os três integrantes | Reescrito | Ajustes feitos pelo grupo: datas, formato das tabelas e ordem de dependência entre as fases |
| 12/11 | Wilia | Claude Code (Claude Opus 5.5) | Conferir as entregas de Rafael e Richard contra o enunciado e o plano | Aceito | Apontou falta das regras de tipo na gramática e nomes de tokens diferentes do combinado |
| 12/11 | Rafael | Codex (GPT-6 Luna) | Analisar a lacuna de regras semânticas indicada e ajudar a especificar as regras na gramática | Aceito | A divisão inteira foi definida com truncamento em direção a zero (`-7 / 2` resulta em `-3`); a especificação foi revisada e registrada pelo integrante |
| 12/11 | Richard | Claude Sonnet 5.5 | Tarefa 01: gerar a implementação inicial das dataclasses dos nós da AST (11 nós, campo `linha`), seguindo o contrato do plano de trabalho | Aceito | Nenhuma correção de código. Pontos de integração levantados para o grupo: tratamento de `If.senao` (`None` quando não há `else`), valor padrão do campo `linha` e a interface que o interpretador espera da AST |
| 12/11 | Richard | ChatGPT (GPT-6) | Tarefa 01: revisar a implementação da AST, conferir a conformidade com o contrato, analisar os resultados apresentados e orientar a validação | Aceito | Implementação aceita após a revisão, sem necessidade de alterações no código. A revisão apontou os mesmos pontos de integração (`If.senao`, `linha`, interface esperada pelo interpretador) para discussão com Rafael e Wilia |
| 12/11 | Richard | Claude Sonnet 5.5 | Fase 2: (a) escrever os testes permanentes da AST; (b) conferir se existia interface concreta de tokens para iniciar o parser de expressões; (c) registrar o uso de IA neste diário. Arquivos alterados: `tests/validos/test_ast.py` e `docs/diario_de_bordo.md` | Testes: aceito. Parser: não implementado (bloqueado) | Nenhuma correção nos testes gerados. Foram rodados com `python -m pytest`: 6 testes da AST passam e, em uma cópia temporária, três defeitos introduzidos de propósito (`senao` com padrão errado, lista de comandos compartilhada, `For` com atualização que não é atribuição) foram detectados. Conceito aplicado nos testes: a precedência fica na estrutura da árvore, com a operação de maior precedência mais abaixo. O parser não foi escrito porque o repositório não define o formato dos objetos `Token` (`src/lexer.py` está vazio); a IA parou em vez de inventar essa interface |
| 13/11 | Richard | Claude Sonnet 5.5 | Implementar o parser descendente recursivo de expressões, os testes válidos e inválidos e o diagnóstico sintático (`ErroSintatico`), usando o lexer real de Rafael. Arquivos alterados: `src/parser.py`, `tests/validos/test_parser_valido.py`, `tests/invalidos/test_parser_invalido.py` e `docs/diario_de_bordo.md` | Aceito, pendente de revisão e commit por Richard | Nenhuma correção de código foi necessária depois da primeira execução: `python -m pytest -q` passou com 61 testes (23 anteriores + 38 novos). Conceitos aplicados: uma função por produção da EBNF (análise descendente recursiva), precedência dada pela profundidade das chamadas, associatividade à esquerda pelo laço que implementa `{ ... }`, comparação não associativa pelo `[ ... ]` (no máximo um operador relacional, o segundo gera erro). Pontos que Richard deve conferir na revisão: a convenção de `linha` (operador em `BinOp`, token nos literais) e o `ErroSintatico` incluir `esperado` e `encontrado` além de linha e coluna. Os erros léxicos não são capturados pelo parser |
| 13/11 | Richard | Claude Sonnet 5.5 | Implementar o parser de comandos e de programa completo (atribuição, `print`, `if`/`else`, bloco, `while`, `for`) a partir de `docs/gramatica.md`, sem duplicar a lógica de expressões, e escrever os testes válidos e inválidos correspondentes. Arquivos alterados: `src/parser.py`, `tests/validos/test_parser_valido.py`, `tests/invalidos/test_parser_invalido.py` e `docs/diario_de_bordo.md` | Código: aceito, pendente de revisão e commit por Richard. Testes: reescritos em 4 expectativas | O parser não precisou de correção. Na primeira execução 4 testes falharam por erro nas expectativas escritas pela IA, e não por defeito do parser: três posições de coluna/linha contadas errado (o `)` do `for` incompleto está na coluna 19, o segundo `<` do `if` na coluna 11, o `for` de `exemplos/programa_invalido.ml` na linha 10) e um programa só com comentário, cujo `Programa.linha` é a do `EOF` (linha 2) pela convenção documentada. As posições foram recontadas à mão a partir dos tokens, e não copiadas da saída. Resultado: `python -m pytest -q` passou com 117 testes (61 anteriores + 56 novos). Conceitos aplicados: uma função por produção, escolha da produção de `Comando` pelo primeiro token (LL(1)), `{ Comando }` e `[ else Bloco ]` como laço e `if` opcional, `Atribuicao` sem `;` reutilizada nas cláusulas do `for`, e `EOF` exigido ao final de `parse_programa`. Revisão por Richard: pendente |
| 12/11 | Wilia | Wilia | Implementar a tabela de símbolos e o `ErroSemantico` com testes | Reescrito | Remover os docstrings que só repetiam o que o código já diz e manteve o comentário obrigatório no topo de `tests/invalidos/test_interpreter_invalido.py` (item f) |
| 13/11 | Wilia | Claude Code (Claude Opus 5.5) | Implementar a avaliação de expressões seguindo as regras semânticas da gramática, com testes válidos e inválidos | Aceito | Dois pontos conferidos: (1) `bool` é subclasse de `int` no Python (`True + 1 == 2`), então a checagem de tipo testa o booleano primeiro e não usa `isinstance(v, int)`; sem isso `true + 1` passaria sem erro; (2) o `//` do Python arredonda para baixo (`-7 // 2 == -4`), mas a gramática define truncamento em direção a zero (`-3`), então a divisão é feita sobre os valores absolutos e o sinal é aplicado depois. Conceito: verificação de tipos na análise semântica, que não pode herdar as conversões implícitas da linguagem hospedeira |

### Decisões tomadas
- **Divisão por fase do compilador:** Rafael fica com gramática e lexer, Richard com AST e parser, Wilia com interpretador e testes de laço. Assim cada um é dono de uma fase inteira (código, testes e seção do relatório).
- **Contratos entre as fases:** combinar o formato dos tokens e os nós da AST antes de programar, para os três trabalharem em paralelo. O interpretador é testado com ASTs montadas à mão até o parser ficar pronto.
- **Técnica de análise sintática:** descendente recursiva, com uma produção da EBNF por nível de precedência (comparação → soma → multiplicação → fator).
- **Laço for:** as três cláusulas são obrigatórias, então na AST nenhuma delas é opcional.
- **Comparações não associativas:** `Expressao = Soma [ OpRel Soma ]`, então `a < b < c` é erro sintático.

### Dificuldades e como foram resolvidas
- **Nomes de tokens diferentes entre o plano e a gramática** (`NEQ`/`LTE`/`GTE`/`SEMICOLON` em vez de `NE`/`LE`/`GE`/`SEMI`) → o grupo adota os nomes da gramática do Rafael.
- **Nome da exceção léxica** (`LexerError` na gramática e `ErroLexico` no combinado) → a definir.
