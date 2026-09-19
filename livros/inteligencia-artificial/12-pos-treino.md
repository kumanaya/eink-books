# Depois do pré-treino: ensinar modos

O paper *InstructGPT* (Ouyang e colegas, 2022) descreve
o pipeline que virou senso comum. Três atos.

**Ato 1 — SFT.** Humanos (ou dados de demonstração)
escrevem a resposta *desejada* a um prompt. Fine-tune
supervisionado no modelo base. O modelo aprende o *formato*
de um assistente: útil, na língua do usuário, não uma
continuação de fórum.

**Ato 2 — Modelo de recompensa.** Mostre várias respostas
ao mesmo prompt. Um rótulo humano (ou um juiz) ranqueia.
Treine um modelo que prevê a preferência. A perda clássica
é Bradley-Terry: aumentar a diferença de score entre a
vencedora e a perdedora.

**Ato 3 — RL (PPO, no paper).** O modelo-política gera
respostas. O modelo de recompensa dá um número. PPO
sobe esse número, com um freio *KL* para não se afastar
demais do SFT — senão o modelo vira um bajulador que
quebra o inglês para maximizar o juiz.

Hoje há variantes: *DPO* (Direct Preference Optimization)
pula o RL explícito e treina direto nas pares. Laboratórios
misturam SFT, preferência, e RL em *verificadores* (código
que passa no teste, prova que fecha). O nome da moda muda.
O problema não: *como transformar preferência em gradiente
sem destruir o que o pré-treino sabia*.

## Exemplo de preferência

Prompt: "Explique atenção em uma frase."

- A: "É um mecanismo em que cada token consulta os outros
  via produtos internos e mistura os values."
- B: "Atenção é quando a IA presta atenção nas coisas
  importantes, tipo um humano."

Um rótulo de engenheiro prefere A. Um rótulo de marketing
às vezes prefere B. O modelo de recompensa *congela o
gosto de quem rotulou*. Ouyang é explícito: isto alinha
a um grupo, não à humanidade. Quem esconde isto mente
sobre o produto.

## Reward hacking

Se o juiz gosta de respostas longas, o modelo escreve
novelas. Se gosta de listas, tudo vira lista. Se o
verificador de código só checa o teste 1, o modelo
hackeia o teste 1. O ofício é desenhar o juiz tão
cuidadosamente quanto o modelo.

## Caderno

Escreva três pares (prompt, boa, ruim) do domínio que
você mais usa. Seja cruelmente específico no "ruim".
Este arquivo de vinte linhas vale mais do que um
adjetivo "seja útil" no system prompt.
