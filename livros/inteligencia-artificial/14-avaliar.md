# Avaliar: o que não se mede vira fé

Um modelo novo que "parece melhor" no chat do time é o
modo mais caro de se enganar. *Eval* é um contrato:
entrada, saída esperada ou juiz, número, fatia do
mundo que aquele número representa.

## Tipos

- **Exato.** O código compilou. A conta deu 42. A
  tradução bate o BLEU de 2014 (e BLEU mente; ainda
  assim é exato).
- **Juiz.** Um humano ou um modelo compara. Barato,
  enviesado. Documente o juiz como documenta o dado.
- **Produto.** Tempo de sessão, retrabalho, tickets.
  O único que paga salário. Chega tarde.

## O eval que o modelo decora

Se o conjunto é público e velho, o pré-treino já o
viu. A nota sobe e o usuário não sente. *Contamination*
é o fantasma. Técnicas: conjuntos privados, renovação,
tarefas geradas depois do corte do treino.

## Exemplo: um eval de três linhas que vale

Tarefa: extrair o valor e a moeda de uma frase.

    "O relógio custou 40 reais." → 40, BRL
    "It was $12.50." → 12.50, USD
    "grátis" → null, null

Métrica: acerto exato dos dois campos. Sem juiz. Sem
poesia. Se Areia começa a escrever "quarenta" por
extenso, o eval quebra — e deve quebrar. Aí você
decide se o produto aceita normalização.

## Ablation

Tire uma peça. Meça. Se a nota não muda, a peça era
teatro. Laboratórios sérios publicam *ablação* porque
é a única defesa contra arquitetura-fashion.

## Caderno

Escreva dez casos do seu domínio, com a resposta
canônica. Rode o modelo que você usa hoje. Anote os
erros sem carinho. Este arquivo é o começo de um
*eval harness*. Sem ele, você não é engenheiro de
modelo. É um usuário com conta cara.
