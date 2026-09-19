# Aprender é minimizar

Aprendizado de máquina supervisionado cabe numa frase: escolha
uma família de funções, escolha uma *perda*, desça a perda
mexendo nos parâmetros.

A família é a arquitetura (linear, MLP, Transformer). A
perda é o juiz. O juiz mais comum para classificação e
para modelos de linguagem é a entropia cruzada.

## A reta que tenta

Queremos prever *y* a partir de *x* com *ŷ = w x + b*.
Três pontos: (1, 2), (2, 4), (3, 5). A perda quadrática
média:

    L = média de (ŷ - y) ao quadrado

Se *w = 1, b = 0*, as previsões são 1, 2, 3. Os erros são
-1, -2, -2. *L = (1+4+4)/3 ≈ 3*. Ruim.

O *gradiente* diz para que lado *L* cresce. Andamos para
o lado oposto, com um passo *η* (taxa de aprendizado):

    w ← w - η * dL/dw
    b ← b - η * dL/db

Isto é *descida de gradiente*. Com *mini-batches*, é
SGD. Com momentos e escalas por parâmetro, é Adam — o
otimizador que você vai ver em quase todo treino moderno.

Não decore a fórmula do Adam no primeiro dia. Decore a
ideia: o passo não é o mesmo para todo peso, e o passado
do gradiente importa.

## Overfitting é memorizar a prova

Se Areia tem parâmetros demais e dados de menos, *L* no
treino cai e *L* no teste sobe. O modelo decorou. Regularizar
(peso L2, *dropout*, mais dado, parar cedo) é impedir a
decoreba.

Num modelo de linguagem, overfitting no pré-treino às vezes
é *o objetivo*: caber a internet. O perigo muda de lugar.
Vira *memorizar um número de cartão*. Vira *recitar um
artigo sob copyright*. Avaliação e filtro de dado viram
parte do ofício, não um apêndice ético.

## Generalização

O que queremos não é *L* baixo no conjunto que já vimos.
É comportamento útil no que não vimos. Papers de *scaling
laws* (Kaplan e colegas; Hoffmann e colegas, o chamado
Chinchilla) tentam prever como perda de teste cai quando
se aumenta parâmetros, dados e computação. A lição de
engenheiro: há um orçamento ótimo. Modelo grande demais
com dado de menos desperdiça GPU.

## O loop que você vai escrever cem vezes

    for batch in dados:
        pred = modelo(batch.x)
        perda = criterio(pred, batch.y)
        perda.backward()
        otimizador.step()
        otimizador.zero_grad()

Quatro linhas. A carreira está no que *não* cabe aí: o
dado está limpo? O *batch* cabe na memória? O gradiente
estourou (*NaN*)? O eval do dia piorou?

## Caderno

Implemente a reta à mão, sem biblioteca, para os três
pontos. Dez passos de gradiente bastam para *L* cair.
Anote *w* e *b* no fim. Se não cair, o sinal do passo
está invertido — o bug mais didático da área.
