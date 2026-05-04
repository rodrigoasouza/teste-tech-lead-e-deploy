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
