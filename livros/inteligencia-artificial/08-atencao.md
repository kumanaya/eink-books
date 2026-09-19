# Atenção

Atenção é uma busca. Dado o que estou tentando escrever
agora (*query*), quais pedaços do passado (*keys*)
importam, e o que eles carregam (*values*)?

A fórmula de Vaswani e colegas (2017), *scaled
dot-product attention*:

    Attention(Q, K, V) = softmax(Q K^T / sqrt(d_k)) V

*Q*, *K*, *V* são matrizes. Cada linha é um token.
*Q K^T* é uma grade de produtos internos: token *i*
contra token *j*. Dividimos por *sqrt(d_k)* para o
softmax não saturar. O resultado pondera as linhas de
*V*.

Lido em voz alta: "pareça com quem importa, e traga o
que essa gente carrega."

<eink-image id="atencao" alt="Diagrama de atenção: query olha keys e mistura values">
Technical woodcut diagram, no letters, no numbers. Three vertical
stacks of small rectangles on the left labeled only by position:
one stack slightly highlighted as a query, a row of stacks as keys,
a row of stacks as values. Arrows of different thickness from the
query to each key, then flowing into a single mixed stack on the
right. High contrast black ink on cream paper, O'Reilly engraving
style, portrait, no captions.
</eink-image>

## Exemplo mínimo, com números

Três tokens. *d_k = 2*. Uma query, três keys, três values.

    q  = (1.0, 0.0)
    k1 = (1.0, 0.0)    v1 = (10, 0)
    k2 = (0.0, 1.0)    v2 = (0, 10)
    k3 = (0.2, 0.1)    v3 = (3, 3)

Produtos: 1.00, 0.00, 0.20. Divida por *sqrt(2) ≈ 1.41*:
0.71, 0.00, 0.14. Softmax ≈ 0.58, 0.29, 0.13. (Os
números redondos mentem um pouco; o 0.29 não é exato.
Faça com uma calculadora. O ponto permanece.)

A saída é 0.58*v1 + 0.29*v2 + 0.13*v3: um vetor puxado
para *v1*, com um cheiro de *v2*. O token atual "olhou"
para o parecido e ainda assim misturou o resto. Atenção
não é um ponteiro único. É uma média. Médias mentem
quando você precisa de um fato preciso — daí alucinação,
daí a vontade de *ferramentas* e *RAG*.

## Máscara causal

Num GPT, o token 5 não pode ver o 6: estamos *gerando*
o futuro. A matriz de scores ganha *-infinito* acima da
diagonal, e o softmax zera essas casas. Isto é *causal
mask*. Esquecer a máscara no treino é o jeito mais
elegante de fazer o modelo colar a resposta.

## Várias cabeças

Uma cabeça de atenção é uma opinião sobre "o que importa".
Oito cabeças são oito opiniões em paralelo, depois
concatenadas e projetadas. O paper original usa *h = 8*,
*d_model = 512*, *d_k = 64*. O custo total se parece com
o de uma cabeça gorda. A ganho é especialização: uma
cabeça caça sintaxe, outra caça um nome três parágrafos
acima — às vezes. Nem sempre as cabeças são interpretáveis.
Ainda assim, *multi-head* é o padrão.

## Complexidade

Para sequência de comprimento *n*, atenção clássica é
*O(n²)* em tempo e memória. Por isso contexto de 128 mil
tokens dói. A engenharia moderna é uma guerra contra este
quadrado: *FlashAttention* (Dao e colegas) reduz memória
sem mudar a matemática; variantes de janela, de
*state-space*, de latência linear tentam pagar menos.
Um engenheiro de inferência que não sabe que o KV cache
cresce com *n * camadas * dimensões* não vai achar o
*OOM*.

## Caderno

Implemente o exemplo 3x2 em Python, com *numpy*. Imprima
a matriz de pesos do softmax. Mude *q* para *(0, 1)* e
veja o peso migrar para *k2*. Este é o melhor diagrama
que existe: um print.
