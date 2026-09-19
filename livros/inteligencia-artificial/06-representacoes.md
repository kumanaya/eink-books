# Representações

O truque de ouro da área: não classifique o mundo cru.
Empurre o mundo para um espaço onde a geometria *já*
ajuda.

Uma palavra vira um vetor de 256 ou 4096 dimensões. Palavras
usadas em contextos parecidos ficam perto — a observação
de Harris, a prática de Mikolov (*word2vec*), o cotidiano
de qualquer *embedding* moderno.

## Analogia que quase é verdade

Nos embeddings clássicos, *rei - homem + mulher* caía
perto de *rainha*. A conta é bonita e frágil. Serve para
ensinar: direções no espaço podem carregar atributos. Não
serve como prova de que o modelo "entende gênero".

## Embeddings contextuais

*Word2vec* dá um vetor por palavra. *ELMo*, *BERT* e os
Transformers dão um vetor *por ocorrência*. "Banco" em
"banco de praça" e "banco central" não são o mesmo ponto.
O contexto move o vetor. Isto é o que a atenção faz de
manhã à noite.

## Exemplo: três frases, um espaço mentiroso

    A. "O relógio caiu na areia."
    B. "A ampulheta sumiu na praia."
    C. "O servidor caiu na nuvem."

Um embedding decente aproxima A e B. C usa "caiu" e mora
longe. Se o seu recuperador de documentos junta A e C,
o espaço está medindo palavra, não sentido. Aí você troca
o modelo de embedding, não o *cosine threshold* pela
milésima vez.

## Tokens especiais e o começo da engenharia

Modelos de encoder (BERT) usam *[CLS]* como âncora da
frase. Modelos autorregressivos (GPT) não precisam: o
estado no último token *é* o resumo até ali. Projetar
uma API de embeddings — o que devolver, de qual camada,
se normalizar — é decisão de engenharia. Devolver a média
de todos os tokens às vezes ganha de devolver o último.
Meça.

## O espaço como produto

Uma loja de busca, um *RAG*, um classificador de
intenção: todos são "texto entra, vetor sai, vizinho
decide". O modelo de linguagem grande é outra espécie —
gera. Mas por baixo, gera *a partir* de representações.
Quem não respeita o espaço trata o LLM como oráculo e
paga em alucinação.

## Caderno

Pegue cinco frases suas, duas delas parafrases. Se tiver
acesso a um modelo de embedding (mesmo pequeno, local),
calcule cossenos. Se não tiver, escreva à mão quais pares
*deveriam* ser próximos e por quê. Este hábito — prever
a geometria antes de medir — é o que separa quem tunica
de quem investiga.
