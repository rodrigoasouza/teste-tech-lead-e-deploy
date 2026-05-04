# Cálculo de Benefícios Trabalhistas

**Descrição**: Escreva uma função que calcula o quanto um funcionário tem a receber de dois benefícios: Férias e Décimo Terceiro Salário ao pedir demissão.

Simplificando o cenário, as férias zeram a cada aniversário de emprego (ou seja, ele sempre tirou as férias corretamente) e o décimo terceiro zera a cada virada de ano (não fica nenhum valor residual de um ano para outro).

- **Lógica**: [calculo_beneficios.py](calculo_beneficios.py)
- **Testes**: [test_calculo_beneficios.py](test_calculo_beneficios.py)

### Interface

![Exercício 4 - Cálculo de Benefícios Trabalhistas](../../docs/screenshots/ex004.png)

---

## Análise de Design e Arquitetura

Este é o exercício mais desafiador em termos de **lógica de negócio**, **manipulação de datas** e **precisão monetária**. Envolve conceitos trabalhistas brasileiros com múltiplos edge cases.

### Conceitos Fundamentais

#### 1. **Décimo Terceiro Salário (13º)**

**Regra**: Direito proporcional ao tempo trabalhado no **ano civil** (jan-dez).

- Zera a cada 1º de janeiro
- Mínimo de 15 dias no mês para contar como mês cheio
- Cálculo: `(salário × meses_completos_no_ano) / 12`

**Exemplo**:
```
Admissão: 15/03/2023
Demissão: 30/11/2024

Ano 2023: Trabalhou março→dezembro = 10 meses (desde 15/03)
Ano 2024: Trabalhou jan→novembro = 11 meses completos

Total direito 2024: (11 meses × salário) / 12
```

#### 2. **Férias Proporcionais**

**Regra**: Direito proporcional em **ciclos de 12 meses** a partir do aniversário de admissão.

- Ciclo recomeça a cada aniversário (mesma data/mês)
- Mínimo de 15 dias no mês para contar
- Máximo de 12/12 avos (não acumula além de um ciclo)
- Cálculo: `(salário × meses_completos_no_ciclo) / 12`

**Diferença do 13º**: Não é por ano civil, mas por ciclo de 12 meses individual.

**Exemplo**:
```
Admissão: 15/03/2023
Demissão: 30/11/2024

Ciclos:
- 15/03/2023 → 14/03/2024: ciclo 1 completo (12 meses)
- 15/03/2024 → 30/11/2024: 8 meses e 16 dias (conta como 9 meses)

Total: 12 + 9 = 21 meses → 21/12 = 1.75 meses de férias
```

### Decisões de Design

#### 1. **Tipo Monetário: `Decimal` vs. `float`**

```python
salario: Decimal  # NÃO float
```

**Por quê?**
- `float` tem erros de arredondamento em ponto flutuante
- `0.1 + 0.2 != 0.3` em binário (erro clássico)
- Cálculos monetários exigem precisão exata

```python
# Problema com float:
0.1 + 0.2  # 0.30000000000000004 ❌

# Com Decimal:
Decimal("0.1") + Decimal("0.2")  # Decimal("0.3") ✓
```

#### 2. **Arredondamento: `ROUND_HALF_UP`**

```python
valor.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
```

**Por quê?**
- Brasil usa arredondamento "para cima em caso de empate" (ROUND_HALF_UP)
- `0.015` vira `0.02` (não `0.01`)
- Padrão legal em cálculos trabalhistas

#### 3. **Estrutura de Dados: `BeneficiosRescisao` (Dataclass)**

```python
@dataclass
class BeneficiosRescisao:
    decimo_terceiro: Decimal
    ferias_proporcionais: Decimal
    
    @property
    def total(self) -> Decimal:
        return self.decimo_terceiro + self.ferias_proporcionais
```

**Vantagens**:
- Type-safe: tipos explícitos
- Imutável: sem mutação acidental
- Property `total`: cálculo sob demanda
- Testável: comparação automática de instâncias

### Algoritmo: Décimo Terceiro

**Desafio**: Contar meses completos no ano da demissão de forma robusta.

**Abordagem: Interseção de Períodos**

```python
for mes in range(1, 13):
    # Janela calendário do mês
    inicio_mes = date(ano_demissao, mes, 1)
    fim_mes = date(ano_demissao, mes, ultimo_dia_mes)
    
    # Interseção entre contrato e o mês
    inicio_real = max(data_admissao, inicio_mes)
    fim_real = min(data_demissao, fim_mes)
    
    # Se houve sobreposição válida
    if inicio_real <= fim_real:
        dias_no_mes = (fim_real - inicio_real).days + 1
        if dias_no_mes >= 15:
            meses_direito += 1
```

**Exemplo prático** (ano 2024):
```
Admissão: 15/03/2023
Demissão: 30/11/2024

Mês 1 (jan): 01/01 ~ 31/01 ∩ 15/03/2023 ~ 30/11/2024 = 01/01 ~ 31/01 (31 dias) ✓
Mês 2 (fev): 01/02 ~ 29/02 ∩ ...                        = 01/02 ~ 29/02 (29 dias) ✓
...
Mês 11 (nov): 01/11 ~ 30/11 ∩ ...                       = 01/11 ~ 30/11 (30 dias) ✓
Mês 12 (dez): 01/12 ~ 31/12 ∩ ...                       = ∅ (fim do contrato 30/11) ✗

Total 2024: 11 meses → (11 × salário) / 12
```

### Algoritmo: Férias Proporcionais

**Desafio**: Determinar qual ciclo de aniversário aplica.

**Abordagem: Ciclos de 12 Meses + Fração**

```python
# Encontra o aniversário mais recente antes/em da demissão
if aniversario_ano_demissao > data_demissao:
    ultimo_aniversario = aniversario_ano_anterior
else:
    ultimo_aniversario = aniversario_ano_demissao

# Conta meses completos desde último aniversário
meses = (data_demissao.year - ultimo_aniversario.year) * 12 + \
        (data_demissao.month - ultimo_aniversario.month)

# Ajuste se não completou o mês
if data_demissao.day < ultimo_aniversario.day:
    meses -= 1

# Verifica fração do mês incompleto
dias_fracao = (data_demissao - data_inicio_mes).days + 1
if dias_fracao >= 15:
    meses += 1
```

**Exemplo complexo** (ciclo de aniversário):
```
Admissão: 15/03/2023
Demissão: 30/11/2024

Aniversário em 2024: 15/03/2024 (não ultrapassado, pois demissão é 30/11)
Último aniversário: 15/03/2024

De 15/03/2024 a 30/11/2024:
- Meses completos: 8 (março→outubro)
- Mês incompleto (nov): 01/11 a 30/11 (30 dias ≥ 15) → conta +1

Total: 9 meses → (9 × salário) / 12
```

**Edge Case Crítico: Ajuste para Dia do Mês**

```python
_, ultimo_dia = calendar.monthrange(ano, mes)
return date(ano, mes, min(data_admissao.day, ultimo_dia))
```

Problema: Admissão em 31/01, aniversário em fevereiro (mês com 28/29 dias).

```
Solução: Aniversário = 28/02 (ou 29/02 em bissextos)
```

### Validações de Entrada

```python
if not isinstance(salario, Decimal):
    raise TypeError("O salário deve ser do tipo Decimal.")

if salario < Decimal("1.0"):
    raise ValueError("O salário deve ser superior a R$ 1,00.")

if salario > Decimal("1000000.00"):
    raise ValueError("Salário acima do limite permitido (R$ 1.000.000,00).")

if data_demissao < data_admissao:
    raise ValueError("A data de demissão não pode ser anterior à data de admissão.")
```

**Por quê tão rigoroso?**
- Evita problemas legais em cálculos reais
- Limites realistas para salários em BR
- Protege contra entrada acidental inválida

### Arquitetura

```
calculo_beneficios.py
├── Constantes
│   ├── MESES_ANO = 12
│   ├── DIAS_MINIMOS_MES = 15
│   └── PRECISAO_MONETARIA = Decimal("0.01")
├── BeneficiosRescisao [dataclass]
│   ├── decimo_terceiro: Decimal
│   ├── ferias_proporcionais: Decimal
│   └── @property total() → Decimal
├── calcular_decimo_terceiro() [private]
│   ├── Iteração por 12 meses
│   ├── Interseção de períodos
│   └── Cálculo proporcional
├── calcular_ferias_proporcionais() [private]
│   ├── Determinação do ciclo (aniversário)
│   ├── Contagem de meses + fração
│   └── Limite de 12/12 avos
└── calcular_beneficios_rescisao() [public]
    ├── Validações (tipo, range, datas)
    ├── Chamada às duas subfunções
    └── Retorno estruturado + arredondamento
```

### Performance

| Operação | Complexidade | Tempo |
|----------|-------------|-------|
| Décimo terceiro | O(12) = **O(1)** | <1μs |
| Férias proporcionais | O(1) | <1μs |
| Arredondamento Decimal | O(1) | <1μs |
| **Total** | **O(1)** | **<5μs** |

(Ambos são O(1) pois iteração é sobre 12 meses fixos)

### Cobertura de Testes

1. **Casos ideais**: Demissão clara, sem sobreposição complexa
2. **Aniversários**: Admissão em 29/02 (bissexto) afetando cálculos
3. **Meses com dias variáveis**: Fevereiro, abril, junho, etc.
4. **Múltiplos ciclos**: Demissão após vários aniversários
5. **Frações de mês**: Demissão no meio do mês
6. **Edge cases**:
   - Demissão no mesmo dia da admissão
   - Demissão 1 dia antes de aniversário
   - Admissão em 31/01, demissão em 01/03 (fevereiro não tem 31 dias)
7. **Precisão monetária**: Valores com centavos, arredondamento HALF_UP
8. **Limites de entrada**: Salários extremos, datas fora de range

### Lições de Engenharia

✓ **Precisão financeira**: Decimal, arredondamento explícito, tipos seguros  
✓ **Manipulação de datas**: Operações de período, intersecção, ciclos  
✓ **Lógica de negócio complexa**: Múltiplas regras interagindo  
✓ **Validação rigorosa**: Proteção contra dados ruins  
✓ **Estruturas de dados**: Dataclass para retorno tipo-seguro  
✓ **Documentação executável**: Testes como especificação de regras  
✓ **Acessibilidade**: Properties para cálculos derivados  

### Referências Legais

- Consolidação das Leis do Trabalho (CLT) - Artigos sobre férias e 13º
- Normas de arredondamento monetário brasileiro
- Regras de prova de dias trabalhados (mínimo 15 dias/mês)
