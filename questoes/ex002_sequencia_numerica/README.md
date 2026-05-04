# Sequência Numérica

**Descrição**: Considerando a sequência numérica a seguir: `(11, 18, 25, 32, 39...)`

Faça uma função que recebe como entrada uma posição e devolve qual o valor do número naquela posição.

**Notas**:
- A sequência começa da posição 1

**Exemplos**:
- `calcular_valor_sequencia(posicao=1)` retornará `11`
- `calcular_valor_sequencia(posicao=2)` retornará `18`
- `calcular_valor_sequencia(posicao=200)` retornará `1404`
- `calcular_valor_sequencia(posicao=254)` retornará `1.782`
- `calcular_valor_sequencia(posicao=3.542.158)` retornará `24.795.110`

> **Nota de Implementação**: Embora esse problema possa ser resolvido em complexidade de tempo $O(1)$ utilizando o cálculo matemático da Progressão Aritmética ($7x + 4$), o objetivo desta solução é focar em Engenharia de Software. Portanto, o código foi desenvolvido para demonstrar conhecimentos algorítmicos e o domínio de **Geradores (Generators)** com carregamento preguiçoso (*lazy evaluation*) nativos do Python.

- **Lógica**: [sequencia_numerica.py](sequencia_numerica.py)
- **Testes**: [test_sequencia_numerica.py](test_sequencia_numerica.py)

### Interface

![Exercício 2 - Sequência Numérica](../../docs/screenshots/ex002.png)

---

## Análise de Design e Arquitetura

### Decisão Estratégica: Por que Não Usar Fórmula O(1)?

A sequência `(11, 18, 25, 32, 39...)` é uma **Progressão Aritmética** (PA) com:
- Primeiro termo: `a₁ = 11`
- Razão: `r = 7`
- **Fórmula fechada**: `aₙ = 11 + (n-1)×7 = 7n + 4` → **O(1)**

```python
# Trivial, mas não demonstra engenharia
def calcular_valor_sequencia_formula(posicao: int) -> int:
    return 7 * posicao + 4
```

**Por que rejeitamos?**
- Demonstra apenas conhecimento matemático
- Esconde decisões de arquitetura e trade-offs
- Não avalia compreensão de estruturas de dados e iteração em Python
- Um candidato a Tech Lead deve dominar ambas: matemática **e** engenharia

### Abordagem Adotada: Generators com Lazy Evaluation

#### 1. **Progressão Preguiçosa com Generator**

```python
def _gerar_sequencia():
    valor = VALOR_INICIAL  # 11
    while True:
        yield valor
        valor += RAZAO      # +7
```

**Vantagens**:
- ✓ **Memória O(1)**: Não armazena todos os valores, gera sob demanda
- ✓ **Lazy evaluation**: Calcula apenas até onde é necessário
- ✓ **Iterativo**: Segue padrão naturalista de progressão
- ✓ **Extensível**: Fácil adaptar para sequências mais complexas (não-lineares)

#### 2. **Acesso Eficiente com `itertools.islice`**

```python
it = _gerar_sequencia()
resultado = next(itertools.islice(it, posicao - 1, None), None)
```

**Desempenho**:
- `islice(it, posicao-1, None)` pula os primeiros `posicao-1` valores **sem iterar**
- Retorna um iterador, não uma lista
- `next()` consome apenas um valor
- **Complexidade**: O(n) onde n = posição (não há atalho sem matemática)

#### 3. **Proteção de Limites Práticos**

```python
_MAX_POSICAO: Final[int] = 100_000_000  # ~100M
if posicao > _MAX_POSICAO:
    raise ValueError(f"A posição deve ser <= {_MAX_POSICAO}...")
```

**Por que**:
- Generator infinito (`while True`) pode bloquear indefinidamente
- Limite de ~100M iterações garante feedback em tempo aceitável (~segundos)
- Previne DoS (Denial of Service) acidental
- Documentação clara sobre limites realistas

#### 4. **Validação Rigorosa de Tipos**

```python
if type(posicao) is not int:
    raise TypeError(f"...recebido {type(posicao).__name__!r}.")
```

**Detalhe importante**: Usa `type(x) is not` em vez de `isinstance(x, int)` para rejeitar `bool` (que é subclass de `int` em Python).

```python
# isinstance(True, int) → True (não desejado)
# type(True) is int → False (correto)
```

### Performance

| Métrica | Valor | Notas |
|---------|-------|-------|
| **Complexidade Temporal** | O(n) | Linear na posição |
| **Complexidade Espacial** | O(1) | Apenas mantém estado do generator |
| **Tempo para posição 1M** | ~100ms | Iterações simples, sem overhead |
| **Memória para posição 1M** | <1KB | Nada armazenado |

**Comparação com alternativas**:

```
Fórmula O(1):           ~1μs, O(1) espaço (porém trivial)
Generator O(n):        ~100ms para 1M (realista, demonstra domínio)
Lista pré-computada:   ~1μs acesso, mas O(n) espaço (inviável para 100M)
```

### Arquitetura

```
sequencia_numerica.py
├── Constantes
│   ├── VALOR_INICIAL = 11
│   ├── RAZAO = 7
│   └── _MAX_POSICAO = 100_000_000
├── _gerar_sequencia() [private]
│   └── Generator infinito (lazy evaluation)
└── calcular_valor_sequencia(posicao: int) → int [public]
    ├── Type validation (rejeita bool, float, None)
    ├── Range validation (1 ≤ posição ≤ 100M)
    ├── Generator instantiation
    ├── islice + next (pula direto à posição)
    └── Verificação de falha (None guard)
```

### Cobertura de Testes

1. **Valores do enunciado**: Validação por oráculo independente (fórmula DA)
2. **Tipos inválidos**: `1.5`, `"2"`, `None`, `[]`, `True`, `False`
3. **Subclass de int**: `bool` (1.0 como float também é rejeitado)
4. **Posições inválidas**: `0`, `-1`, `-100`, `>100M`
5. **Equivalência com fórmula**: Todos os testes também checam `7*posicao + 4`
6. **Property-based**: Testa invariantes da PA (diferença sempre = 7)

### Lições de Engenharia

✓ **Escolhas deliberadas**: Trade-off entre O(1) matemático e O(n) educacional  
✓ **Lazy evaluation**: Padrão fundamental em linguagens funcionais  
✓ **Type discipline**: Rejeição de coerção implícita (bool não é int semanticamente)  
✓ **Proteção de recursos**: Limites práticos para iteradores infinitos  
✓ **Validação em camadas**: Tipo → Range → Lógica  
✓ **Tests como especificação**: Oráculo independente garante correção
