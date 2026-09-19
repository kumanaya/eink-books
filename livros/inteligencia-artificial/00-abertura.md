---
title: Inteligência Artificial
subtitle: Do primeiro gradiente ao laboratório
author: Daniel Kumanaya
language: pt-BR
identifier: urn:uuid:a1e0b00c-0a11-4e11-9e11-einkbooks0ai01
cover: cover.jpg
publisher: E-INK HACK
date: 2026-09-19
rights: Todos os direitos reservados.
description: >
  Você não precisa de um laboratório em São Francisco para começar a
  pensar como quem constrói modelos. Este livro parte da pergunta
  "o que é aprender?" e chega a Transformers, RLHF, inferência e
  sistemas — o ofício de um engenheiro de IA, em português, com
  exemplos que cabem num caderno.
subjects:
  - Computers
  - Artificial intelligence
  - Software engineering
---

# Página de rosto

**Inteligência Artificial**

Do primeiro gradiente ao laboratório

Daniel Kumanaya

E-INK HACK
2026

Um livro no espírito das guias de bancada: animal na capa, exemplo
no meio da página, e nenhuma frase que finja que o assunto é simples
quando não é.

# Direitos autorais

Copyright 2026 Daniel Kumanaya / E-INK HACK.

Todos os direitos reservados. Nenhuma parte desta edição finge ser
um ISBN da O'Reilly Media. O formato — progressão, exemplos, tom de
bancada — é uma homenagem. O conteúdo é nosso.

Este livro não é afiliado à OpenAI. Nenhuma editora, nenhum
laboratório e nenhum processo seletivo garante emprego. O que ele
oferece é o mapa do ofício: matemática que você usa, código que você
debuga, papers que você lê de verdade.

# Dedicatória

Para quem já perguntou a um modelo "como você funciona?" e não
aceitou "é mágica" como resposta.

# Como ler este livro

Este não é um livro de prompts. Também não é um livro de provas. É
o caminho que um engenheiro percorre quando decide *construir*
inteligência artificial em vez de só chamá-la por uma API.

A progressão é a de uma guia O'Reilly clássica. Os primeiros
capítulos cabem num fim de semana com papel e lápis. Os do meio
exigem que você escreva um loop de treino e sinta o gradiente
na ponta dos dedos. Os últimos falam a língua de quem lê
*Attention Is All You Need*, *InstructGPT* e vagas de
infraestrutura da OpenAI no mesmo dia.

Cada capítulo técnico tem três camadas:

1. A ideia em uma frase, sem jargão.
2. Um exemplo que você consegue calcular ou digitar.
3. O detalhe que um laboratório não perdoa: a escala, o bug,
   o paper.

Quando o texto diz **Caderno**, pare e faça. Não é decoração.
Engenheiro de modelo que só lê vira comentarista.

Há um personagem que volta: o modelo **Areia**. Ele começa
como dois pesos e uma função de perda. No fim do livro, Areia
é um Transformer minúsculo, com tokens, atenção e um critério
de avaliação. Você não vai treinar um GPT. Vai entender o
esqueleto de um.

Imagens neste volume são raras de propósito. A capa é um
gravado, à maneira das guias de animal. Há um único diagrama
de página inteira, no capítulo da atenção — o mecanismo que
quase ninguém internaliza só com fórmula. O resto é texto,
porque texto é o meio em que os modelos também aprendem.

Convenções:

- `código` em bloco é Python 3, o mais próximo possível do
  que você rodaria. Não precisa de GPU até o capítulo de
  sistemas.
- *Itálico* marca um termo na primeira aparência.
- **Negrito** marca o conceito que o capítulo quer que você
  leve embora.

Se você só tem o Kindle e este arquivo, está bem. O laboratório
cabe na cabeça primeiro. O cluster vem depois.
