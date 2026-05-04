# Validação de String

**Descrição**: Escreva uma função que determina se uma string termina com 'A' e começa com 'B'.

- **Lógica**: [validacao_string.py](validacao_string.py) (Implementações via `startswith`/`endswith` e via `indexação`)
- **Testes**: [test_validacao_string.py](test_validacao_string.py)

### Interface

![Exercício 1 - Validação de String](../../docs/screenshots/ex001.png)

---

## Análise de Design e Arquitetura

### Decisões de Design

#### 1. **Duas Implementações Comparativas**

A solução fornece duas abordagens distintas:

- **`verificar_com_metodos_string()`**: Usa métodos nativos `startswith()` e `endswith()`
  - **Vantagem**: Legibilidade superior, intenção clara, interface pythônica
  - **Ideal para**: Código production onde readability vale mais que micro-otimizações

- **`verificar_com_indexacao()`**: Acessa direto via índices `texto[0]` e `texto[-1]`
  - **Vantagem**: Demonstra conhecimento de indexação Python e operações em O(1)
  - **Ideal para**: Educacional, entrevistas técnicas, comparações de performance

#### 2. **Validação de Tipos Robusta**

```python
if not isinstance(texto, str):
    if texto is None:
        return False
    raise TypeError(f"Esperado str, recebido {type(texto).__name__!r}")
```

**Por que**: 
- Diferencia `None` (retorna `False`) de tipos inválidos (exceção)
- `isinstance()` é preferido sobre `type()` para permitir subclasses de `str`
- Falha rápido com mensagem clara em caso de erro

#### 3. **Constantes Imutáveis**

```python
CARACTERE_INICIAL: Final[str] = "B"
CARACTERE_FINAL: Final[str] = "A"
```

**Por que**:
- Usa `Final` do módulo `typing` para enforce imutabilidade em type-check
- Facilita manutenção: mudar critérios exige uma única edição
- Melhora legibilidade do código principal

#### 4. **Tratamento de Strings Vazias**

```python
if not texto:
    return False
```

**Por que**: Uma string vazia não começa com 'B' nem termina com 'A'

### Performance

| Abordagem | Complexidade de Tempo | Complexidade de Espaço | Notas |
|-----------|----------------------|----------------------|-------|
| `startswith`/`endswith` | **O(1)** | O(1) | Otimizadas em C, rápidas para caractere único |
| Indexação direta | **O(1)** | O(1) | Acesso direto, sem overhead de função |

**Benchmark esperado** (para strings grandes):
- Ambas são equivalentes em prática (~nanosegundos)
- Indexação pode ser ligeiramente mais rápida por evitar chamadas de função
- Diferença insignificante para uso em production

### Cobertura de Testes

O test suite cobre:

1. **Casos válidos**: `"BA"`, `"BOLA"`, `"BANANA"`, `"B A"`, `"B123A"` 
2. **Caracteres especiais**: tabs, newlines, pontuação, emojis, null bytes
3. **Casos inválidos**: maiúsculas invertidas, posição errada, homóglifos (ΒA vs BA)
4. **Strings longas**: até 10k caracteres
5. **Subclasses de `str`**: valida `isinstance()` dispatch
6. **Tipos incorretos**: None, int, list, dict, float
7. **Strings vazias e caracteres únicos**

**Estratégia**: Validação por equivalência — ambas as implementações são testadas em paralelo para garantir comportamento idêntico.

### Arquitetura

```
validacao_string.py
├── Constantes (CARACTERE_INICIAL, CARACTERE_FINAL)
├── verificar_com_metodos_string()
│   ├── Type guard (isinstance)
│   ├── Empty check
│   └── Verificação via startswith/endswith
└── verificar_com_indexacao()
    ├── Type guard (isinstance)
    ├── Empty check
    └── Verificação via indexação
```

**Padrão**: Ambas funções seguem o mesmo fluxo de validação, garantindo simetria e facilitando comparações.

### Lições de Engenharia

✓ **Type safety**: Validação explícita vs. EAFP (Easier to Ask for Forgiveness than Permission)  
✓ **Constantes**: Facilita manutenção e testes  
✓ **Testes comparativos**: Garante equivalência entre implementações  
✓ **Documentação de edge cases**: Unicode, emojis, homóglifos demonstram profundidade
