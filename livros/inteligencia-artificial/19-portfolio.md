# O que construir para ser contratável

Nenhum repositório garante a OpenAI. Os que chegam
perto mostram as quatro coisas do capítulo 1, em
público, com cicatrizes.

## Três artefatos que pesam

**1. Um treino que você explica.** Um Transformer
mínimo em Python, dataset próprio (mesmo pequeno),
curva de perda, um bug que você documentou. Não
um notebook copiado. Um *relatório*.

**2. Um eval harness.** Dez tarefas do seu domínio,
execução reproduzível, comparação entre dois
modelos, um parágrafo sobre o que a métrica *não*
vê.

**3. Um sistema.** Servir o modelo com *streaming*,
corte de contexto por token, log de custo, uma
ferramenta validada. CPU serve. A clareza não.

Se puder, um quarto: um kernel ou um *profile*
que mudou um número (tokens/s, memória). Isto
conversa com as vagas de inferência.

## O que não colocar no portfólio

- Uma sopa de *wrappers* de API sem critério.
- Fine-tune de um modelo aberto sem eval.
- "Agente autônomo" que só funciona na demo.
- Trabalho que você não consegue defender em
  uma hora no quadro.

## Como falar numa entrevista

Conte um incidente. O que você mediu. O que
chutou errado. O que mudou no sistema depois.
Laboratórios contratam o hábito, não o stack
da semana.

## Caderno

Abra um repositório vazio. Commita o Areia 0.1
do capítulo 5 com um README de vinte linhas:
como rodar, o que a perda fez, o que falta.
Este é o primeiro tijolo. O livro inteiro é
o projeto de completar os outros.
