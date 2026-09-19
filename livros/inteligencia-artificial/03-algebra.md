# O espaço onde os modelos moram

Redes neurais não pensam em palavras. Pensam em listas de
números. Uma palavra, uma imagem, um estado interno: tudo
vira um *vetor*. Operar o modelo é multiplicar esses
vetores por *matrizes*.

Se isto parecer abstrato, pense em uma planilha. Uma linha
é um vetor. Uma grade de números é uma matriz. Multiplicar
é "cada linha da esquerda conversa com cada coluna da
direita e vira um número".

## Vetor

*v = (2, -1, 3)* mora em três dimensões. O *módulo* é o
comprimento. O *produto interno* *u · v* mede quanto os
dois apontam para o mesmo lado: positivo, alinhados;
negativo, opostos; zero, de lado.

O produto interno é a operação mais importante deste livro.
Atenção, no capítulo 8, é um produto interno entre uma
*query* e várias *keys*, depois uma média ponderada dos
*values*.

## Exemplo numérico

    q = (1, 0)
    k1 = (1, 0)    # igual a q
    k2 = (0, 1)    # de lado
    k3 = (-1, 0)   # oposto

    q·k1 = 1
    q·k2 = 0
    q·k3 = -1

Depois de um softmax (capítulo 8), k1 leva quase toda a
atenção. O modelo "olhou" para o token parecido. Não há
mágica: há geometria.

## Matriz

Uma matriz *W* de 3 por 2 transforma um vetor de 2 números
num vetor de 3. Cada camada densa de uma rede é uma dessas
transformações, mais um viés, mais uma não-linearidade.

    h = relu(W x + b)

*relu(z)* é *max(0, z)*. Sem ela, empilhar camadas é
inútil: o produto de matrizes continua uma única matriz.
A não-linearidade é o que deixa a rede *curvar* o espaço.

## Norma, estabilidade, o número que explode

A *norma L2* de um vetor é a raiz da soma dos quadrados.
Se os produtos internos crescem com a dimensão — e crescem,
como Vaswani e colegas notaram em 2017 — o softmax vai
para um canto e o gradiente some. Por isso a atenção
*escala* o produto por *1 / sqrt(d)*. Não é estética. É
sobrevivência do gradiente.

*LayerNorm* (ou *RMSNorm*, nas variantes modernas) puxa
cada vetor de volta para uma escala previsível. Sem isso,
redes profundas viram foguetes.

## Autovalor, por alto

Uma matriz pode esticar o espaço mais numa direção que em
outra. Essas direções são *autovetores*. Você não precisa
diagonalizar nada à mão neste livro. Precisa da intuição:
treinar é achar uma transformação que separe o que importa.
Às vezes a direção que importa é "este token é um verbo".
Às vezes é "este parágrafo contradiz o anterior".

## Caderno

Escreva *W* 2x2 e *x = (1, 1)*. Calcule *W x*. Troque um
sinal em *W* e calcule de novo. Sinta que *aprender* será,
mais tarde, mexer nesses sinais com um objetivo — não com
inspiração.
