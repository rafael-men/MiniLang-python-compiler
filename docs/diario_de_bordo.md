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

### Uso de IA
| Data | Integrante | Ferramenta / modelo | Para que foi usada | Resultado | O que foi corrigido e por quê |
| --- | --- | --- | --- | --- | --- |
| 11/11 | Wilia | Claude Code (Claude Opus 5.5) | Montar o plano de trabalho com divisão entre os três integrantes | Reescrito | Ajustes feitos pelo grupo: datas, formato das tabelas e ordem de dependência entre as fases |
| 12/11 | Wilia | Claude Code (Claude Opus 5.5) | Conferir as entregas de Rafael e Richard contra o enunciado e o plano | Aceito | Apontou falta das regras de tipo na gramática e nomes de tokens diferentes do combinado |
| | Rafael | | | | |
| | Richard | | | | |

### Decisões tomadas
- **Divisão por fase do compilador:** Rafael fica com gramática e lexer, Richard com AST e parser, Wilia com interpretador e testes de laço. Assim cada um é dono de uma fase inteira (código, testes e seção do relatório).
- **Contratos entre as fases:** combinar o formato dos tokens e os nós da AST antes de programar, para os três trabalharem em paralelo. O interpretador é testado com ASTs montadas à mão até o parser ficar pronto.
- **Técnica de análise sintática:** descendente recursiva, com uma produção da EBNF por nível de precedência (comparação → soma → multiplicação → fator).
- **Laço for:** as três cláusulas são obrigatórias, então na AST nenhuma delas é opcional.
- **Comparações não associativas:** `Expressao = Soma [ OpRel Soma ]`, então `a < b < c` é erro sintático.

### Dificuldades e como foram resolvidas
- **Nomes de tokens diferentes entre o plano e a gramática** (`NEQ`/`LTE`/`GTE`/`SEMICOLON` em vez de `NE`/`LE`/`GE`/`SEMI`) → o grupo adota os nomes da gramática do Rafael.
- **Nome da exceção léxica** (`LexerError` na gramática e `ErroLexico` no combinado) → a definir.

