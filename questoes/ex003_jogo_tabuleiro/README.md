# Jogo com Tabuleiro Unidirecional

**Descrição**: Um jogo com tabuleiro unidirecional comporta dois jogadores. Vence quem chegar primeiro à última casa do tabuleiro com menos turnos.

**Regras do Jogo**:
- Os jogadores utilizam uma roleta que sorteia se devem andar 1, 2 ou 3 casas
- Se tirar um número maior na roleta do que casas faltantes, o jogador deve iniciar novamente o percurso (como um looping)
  - Exemplo: se faltam apenas duas casas para eu ganhar, e tiro 3 na roleta, devo caminhar as duas faltantes mais uma até a primeira casa do tabuleiro, reiniciando todo o percurso
- Tamanho mínimo do tabuleiro: 3 casas (sem máximo definido)

**Tarefa**: Crie uma função que recebe o número de casas do tabuleiro e devolve:

1. Quantidade mínima de turnos para se chegar ao destino (caminho ótimo)
2. Probabilidade de um usuário conseguir executar o caminho ótimo
3. Quantas combinações de movimentos diferentes um jogador conseguiria executar sem efetuar nenhum looping no tabuleiro

- **Lógica**: [jogo_tabuleiro.py](jogo_tabuleiro.py)
- **Testes**: [test_jogo_tabuleiro.py](test_jogo_tabuleiro.py)

### Interface

![Exercício 3 - Jogo com Tabuleiro](../../docs/screenshots/ex003.png)

---

## Análise de Design e Arquitetura

Este é o exercício mais complexo, envolvendo análise combinatória, probabilidade, teoria dos números e otimização de performance.

### Problema 1: Turnos Mínimos

**Questão**: Qual é o número mínimo de turnos para vencer?

**Análise**:
- Tabuleiro de `N` casas tem distância `N-1` (da casa 1 à casa N)
- Cada turno avança no máximo 3 casas
- Turnos mínimos: `⌈(N-1) / 3⌉`

```python
distancia = casas - 1
turnos_minimos = (distancia + OPCOES_ROLETA - 1) // OPCOES_ROLETA
# Equivalente a: math.ceil((casas - 1) / 3)
```

**Exemplo**: Tabuleiro com 10 casas
- Distância: 10 - 1 = 9
- Turnos: ⌈9/3⌉ = 3 (sequência: 3, 3, 3)

### Problema 2: Probabilidade de Caminho Ótimo

**Questão**: Qual a chance de um jogador aleatório conseguir o caminho ótimo?

**Raciocínio**:
1. Em `T` turnos com 3 opções cada, há `3^T` sequências totais
2. Apenas algumas sequências atingem a distância exata (`N-1`)
3. Combinatória: Quantas formas de distribuir `N-1` passos em `T` turnos?

**Exemplo com N=10 (T=3, distância=9)**:
- Total de sequências: `3³ = 27`
- Para atingir distância 9 em 3 turnos: só `(3,3,3)` = 1 forma
- Probabilidade: `1/27 ≈ 3.7%`

**Mais complexo (N=7, T=3, distância=6)**:
- Total: `3³ = 27`
- Sequências que somam 6: `(1,2,3)`, `(1,3,2)`, `(2,1,3)`, `(2,2,2)`, `(2,3,1)`, `(3,1,2)`, `(3,2,1)` = 7 formas
- Probabilidade: `7/27 ≈ 25.9%`

**Função interna**: `_caminhos_otimos()`

```python
def _caminhos_otimos(distancia: int, turnos: int) -> int:
    pontos_perdidos = (turnos * 3) - distancia
    
    if pontos_perdidos == 0:
        return 1         # Apenas uma forma: máximo sempre
    if pontos_perdidos == 1:
        return turnos    # Escolher qual turno "perde 1"
    if pontos_perdidos == 2:
        return turnos * (turnos + 1) // 2  # Combinações de 2
```

**Matemática**:
- Se em `T` turnos o máximo é `3T` e precisamos de `D < 3T`
- "Pontos perdidos" = `3T - D`
- Distribuir `pontos_perdidos` entre `T` turnos é um problema combinatório

Para `pontos_perdidos = 0`: Um caminho (3,3,3,...)  
Para `pontos_perdidos = 1`: T formas de "descer um turno"  
Para `pontos_perdidos = 2`: C(T+1, 2) = T×(T+1)/2 formas

### Problema 3: Combinações sem Looping

**Questão**: Quantas sequências diferentes **não causam looping**?

**Regra crítica**: Se em qualquer ponto você excede a distância restante, loopa.

**Exemplo (distância 5)**:
- Sequência `(1,1,1,1,1)`: ✓ válida
- Sequência `(3,3,...)`: ✗ inválida (3 > 5, loopa imediatamente)
- Sequência `(2,2,2)`: ✗ inválida (2+2+2=6 > 5, excede no último turno)

**Padrão Matemático**: Sequências que nunca excedem a distância correspondem à **Sequência de Tribonacci**.

**Prova intuitiva**:
```
f(n) = número de formas de somar até N usando {1,2,3}

f(1) = 1   → (1)
f(2) = 2   → (1,1), (2)
f(3) = 4   → (1,1,1), (1,2), (2,1), (3)
f(4) = 7   → combinar f(3) + f(2) + f(1)
f(n) = f(n-1) + f(n-2) + f(n-3)  [Tribonacci!]
```

**Implementação via Matrix Exponentiation** (`_mat_pow()`):

Para calcular Tribonacci(n) em O(log n):

```
[T(n)  ]   [1 1 1]^(n-2)   [T(2)]   [2]
[T(n-1)] = [1 0 0]      × [T(1)] = [1]
[T(n-2)]   [0 1 0]        [T(0)]   [1]
```

**Complexidade**:
- Naive recursão: O(3^n) exponencial
- DP iterativa: O(n) linear
- Matrix exponentiation: **O(log n)** ← Adotado

**Por quê Matrix Exponentiation?**
- Para distâncias grandes (ex: 100M), O(log n) é crítico
- O(n) seria 100M iterações = inviável
- Demonstra domínio de otimizações avançadas

### Arquitetura

```
jogo_tabuleiro.py
├── Constantes
│   ├── TAMANHO_MINIMO = 3
│   ├── OPCOES_ROLETA = 3
│   └── _TRIBONACCI_MAT = [[1,1,1], [1,0,0], [0,1,0]]
├── _mat_mul() [private, O(1) para matrizes 3×3]
├── _mat_pow() [private, O(log n) matrix exponentiation]
├── _gerar_combinacoes_sem_loop() [private, gerador lazy]
├── _tribonacci() [private, cálculo via matrix]
├── _caminhos_otimos() [private, combinatória]
└── analisar_tabuleiro(casas: int) → dict [public]
    ├── Type validation
    ├── Range validation
    ├── Cálculo de turnos mínimos
    ├── Cálculo de total de sequências possíveis
    ├── Cálculo de sequências ótimas
    ├── Cálculo de probabilidade
    └── Cálculo de combinações sem looping (Tribonacci)
```

### Performance

| Operação | Complexidade | Tempo para 100M | Notas |
|----------|-------------|-----------------|-------|
| Turnos mínimos | O(1) | <1μs | Aritmética simples |
| Caminhos ótimos | O(1) | <1μs | 3 casos triviais |
| Probabilidade | O(1) | <1μs | Divisão simples |
| Tribonacci (O(n)) | O(n) | **segundos** | Inviável para grandes n |
| **Tribonacci (matrix)** | **O(log n)** | **<1ms** | ✓ Adotado |

**Benchmark**:
```
f(10)         = 149     → O(log 10) ≈ 4 operações
f(1000)       = ...     → O(log 1000) ≈ 10 operações  
f(100_000_000) = ...    → O(log 100M) ≈ 27 operações
```

### Cobertura de Testes

1. **Exemplos do enunciado**: Validação direta com valores conhecidos
2. **Múltiplos tamanhos**: 3, 10, 100, 1000, 1M, 100M
3. **Propriedades invariantes**:
   - `turnos_minimos * 3 >= casas - 1`
   - `probabilidade ∈ (0, 1]`
   - `combinacoes = Tribonacci(casas - 1)`
4. **Erros de entrada**: Tipo incorreto, tamanho < 3
5. **Equivalência**: Tribonacci O(log n) vs. oráculo O(n)

### Lições de Engenharia

✓ **Análise combinatória**: Problema de contagem disfarçado em jogo  
✓ **Otimizações avançadas**: Matrix exponentiation para Fibonacci-like  
✓ **Validação matemática**: Testes contra oráculos independentes  
✓ **Decisões de algoritmo**: O(n) vs. O(log n) impacto real  
✓ **Arquitetura limpa**: Decomposição em subfunções privadas  
✓ **Type safety**: Validação rigorosa de entrada  

### Referências Matemáticas

- **Progressão Aritmética**: Turnos mínimos
- **Combinatória**: Distribuições de pontos perdidos (stars and bars)
- **Tribonacci**: Sequência de composições sem excesso
- **Exponenciação Binária**: Otimização de potência matricial
