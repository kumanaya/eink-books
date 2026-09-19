# Inferência: o modelo no relógio de parede

Treino é um job. Inferência é um produto. A cada token
gerado, o decoder precisa das *keys* e *values* do
passado. Recalcular tudo a cada passo é desperdício.
Guarda-se um *KV cache*. A memória cresce com
*batch * camadas * cabeças * comprimento * dimensão*.

Estourar memória no token 8 mil não é mistério. É
aritmética que ninguém fez.

## Latência versus vazão

- **TTFT** (*time to first token*): o usuário espera o
  começo. Prefill: atenção sobre o prompt inteiro.
- **TPOT** (*time per output token*): cada token
  seguinte. Decode: uma linha nova, cache velho.

Otimizar um sem medir o outro é como acelerar o carro
e esquecer o semáforo. Vagas de *research inference* na
OpenAI falam exatamente disto: batching, scheduling,
kernels, o caminho do request até o stream.

## Amostragem de novo, agora como produto

*seed* fixo não torna a API determinística se o backend
é especulativo ou se há empates. *logprobs* ajudam a
debugar, não a provar verdade. *max_tokens* é um
corta-luz, não um plano. Quem implementa um agente sem
orçamento de tokens descobre a fatura no cartão.

## Paralelismo na hora de servir

Um modelo que não cabe numa GPU parte-se: *tensor
parallel* (fatias de matriz), *pipeline* (fatias de
camada). Comunicação é o preço. Inferência *multi-GPU*
é um runtime, não um flag. Engines como vLLM e SGLang
existem porque *paged attention* e *continuous batching*
são engenharia, não paper de domingo.

## Exemplo de conta

Prompt de 2 mil tokens, resposta de 200, modelo com
cache de 2 KB por token por camada, 32 camadas. Cache
só da resposta + prompt: 2200 * 32 * 2 KB ≈ 140 MB
por request. Cem requests concorrentes: 14 GB só de
KV, sem pesos. Agora você entende o "contexto de 128k"
como decisão de dinheiro.

## Caderno

Perfile um generate local (mesmo num CPU, modelo
minúsculo). Anote tempo até o primeiro token e tempo
médio dos seguintes. Mude o tamanho do prompt. O
prefill deve doer mais. Se não doer, o framework está
escondendo o trabalho — ainda assim o trabalho existe.
