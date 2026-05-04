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
