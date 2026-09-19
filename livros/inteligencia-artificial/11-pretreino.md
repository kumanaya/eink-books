# Pré-treino: caber o mundo numa perda

O objetivo clássico de um GPT: dado o passado, maximize
a probabilidade do próximo token. A perda é entropia
cruzada média sobre bilhões de tokens.

Isto não ensina "a verdade". Ensena a *distribuição do
texto que viu*. Se o texto mente, o modelo mente com
estilo. Se o texto é código, o modelo completa código.
Se o texto é um fórum raivoso, o modelo sabe ser raivoso.

## O dado é o destino

Um laboratório sério trata *dataset* como produto:
filtro de qualidade, deduplicação, licença, PII, mistura
de idiomas, mistura de código. Papers de *data mixture*
mostram que a receita da sopa muda o modelo mais do que
mais um bilhão de parâmetros às cegas.

Areia, se treinada só em receitas de bolo, será uma
péssima engenheira e uma boa confeiteira. Escala não
lava dado podre. Só espalha.

## Scaling

Kaplan e colegas (2020) mediram: perda cai como lei de
potência quando se aumenta modelo, dado e compute. Hoffmann
e colegas (Chinchilla, 2022) argumentaram que muitos
modelos grandes estavam *sub-treinados*: faltava token
por parâmetro. A lição prática muda a cada ano, mas o
hábito permanece: desenhe o orçamento *antes* do treino,
não depois do susto na fatura.

## Estabilidade de um job longo

Treinar semanas em milhares de GPUs é um problema de
sistema. *Checkpoint*. *Gradient clipping*. Precisão
mista. Uma GPU que falha não pode matar o mês. *ZeRO*
e paralelismo (de dado, de tensor, de pipeline) partem
o modelo e o batch pelo cluster. Você não precisa
implementar FSDP no capítulo 11. Precisa saber por que
ele existe: o modelo não cabe num chip.

## O que o pré-treino não faz

Não alinha. Não segue instrução com educação. Não se
recusa a dar uma receita de bomba com a nuance que o
produto quer. Isto é o capítulo 12. Quem vende um
modelo *base* como assistente está vendendo um papagaio
muito lido.

## Caderno

Escreva a perda de um único passo: contexto "o relógio",
alvo "caiu", probabilidade do modelo 0.2. *L = -log(0.2)
≈ 1.61 nats*. Se a probabilidade fosse 0.8, *L ≈ 0.22*.
Sinta o preço de não ter certeza. Depois imagine a média
disso em 2 trilhões de tokens.
