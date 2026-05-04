# Atividade Técnica - Entrevista para Líder Técnico

## Sobre esta Atividade

Este documento apresenta uma série de desafios de programação propostos pela e-DEPLOY como parte de um processo de avaliação técnica. Os problemas cobrem diferentes áreas: manipulação de strings, análise de sequências numéricas, probabilidade e lógica de jogos, além de cálculos de benefícios trabalhistas.

### Interface Principal

![Dashboard Principal](docs/screenshots/main.png)

---

## Questões Propostas

1. **[Exercício 01: Validação de String](questoes/ex001_validacao_string/README.md)**
2. **[Exercício 02: Sequência Numérica](questoes/ex002_sequencia_numerica/README.md)**
3. **[Exercício 03: Jogo com Tabuleiro Unidirecional](questoes/ex003_jogo_tabuleiro/README.md)**
4. **[Exercício 04: Cálculo de Benefícios Trabalhistas](questoes/ex004_calculo_beneficios/README.md)**

---

## Contexto

Esta atividade foi realizada como parte do processo de entrevista técnica para a posição de **Líder Técnico (Tech Lead)** na empresa **e-DEPLOY**.

### Objetivo da Avaliação

O objetivo desta atividade é avaliar as competências técnicas do candidato em:

- Resolução de problemas algorítmicos complexos
- Manipulação de dados e estruturas de dados
- Cálculos matemáticos e análise probabilística
- Implementação de lógica de negócio
- Pensamento crítico e capacidade de arquitetura de soluções
- Clareza na comunicação técnica

---

## Como Rodar a Aplicação

Este projeto utiliza **NiceGUI** para fornecer uma interface moderna e interativa.

### 1. Instalação das Dependências

Certifique-se de ter o Python 3.10 ou superior instalado. No diretório raiz, execute:

```bash
pip install .
```

### 2. Executando o Dashboard

Você pode iniciar a aplicação de duas formas:

#### A. Via Script (Mais fácil)
Se você instalou o projeto via `pip install .`, basta digitar:
```bash
tech-lead
```

#### B. Via Python diretamente
```bash
python app.py
```

### 3. Notas sobre o Ambiente

- **Windows (Nativo)**: A aplicação abrirá em uma janela própria (Modo Nativo).
- **WSL (Linux)**: A aplicação detectará o ambiente e rodará em **Modo Navegador**. Basta acessar `http://localhost:8080` no seu navegador do Windows.

---

## Como Rodar os Testes

Para validar a lógica de todos os exercícios:

```bash
# Instala as dependências de desenvolvimento
pip install -e ".[dev]"

# Roda todos os testes
python -m pytest
```

---

## Esteira de Integração Contínua

O projeto implementa uma **esteira CI/CD robusta** via GitHub Actions que valida a qualidade e integridade do código em 4 domínios complementares:

### Componentes da Esteira

1. **Qualidade e Estilo de Código** ([Ruff](https://docs.astral.sh/ruff/))
   - Linting e formatação automática
   - Garante consistência de estilo em toda a base de código

2. **Segurança** (pip-audit + Bandit)
   - Auditoria de vulnerabilidades em dependências
   - Análise de riscos de segurança no código Python

3. **Análise Estática de Tipos** (MyPy)
   - Verificação de type hints
   - Garante arquitetura e contratos de tipos

4. **Validação Funcional** (Pytest + Playwright)
   - Testes unitários com cobertura de código
   - Testes de UI automatizados end-to-end

### Fluxo de Execução

A esteira é disparada automaticamente em:
- **Push** para a branch `main`
- **Pull Requests** contra a branch `main`
- **Acionamento manual** via `workflow_dispatch`

Os jobs executam em **paralelo otimizado**: lint e type-check são independentes, enquanto os testes aguardam a conclusão dos passos anteriores. Isso garante feedback rápido sem comprometer a qualidade.