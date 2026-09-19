# A rede que aprende

Um neurônio é uma frase: soma ponderada, depois um corte.

    z = w1*x1 + w2*x2 + b
    a = relu(z)

*a* é a ativação. Empilhe neurônios lado a lado: uma
*camada*. Empilhe camadas: um *MLP* (perceptron de múltiplas
camadas). Isto, com entropia cruzada, já classifica dígitos.

## Areia, versão 0.1

Areia recebe dois números *(x1, x2)* — digamos, "tamanho
do e-mail" e "quantidade da palavra grátis" — e devolve
um *logit* de spam.

    z = 0.4*x1 + 1.2*x2 - 0.5
    p = 1 / (1 + exp(-z))     # sigmoide

Se *x = (2, 3)*, *z = 0.4*2 + 1.2*3 - 0.5 = 3.9*,
*p ≈ 0.98*. Areia está quase certa. A perda, se o rótulo
é 1 (spam):

    L = -log(p) ≈ 0.02

Se o rótulo é 0:

    L = -log(1-p) ≈ 3.9

O modelo pagou caro por ter certeza do lado errado. Isto
é o que a entropia cruzada faz de melhor: punir arrogância.

## Backpropagation sem mistério

O gradiente de *L* em relação a cada peso flui *de trás
para frente*. Cada operação local sabe sua derivada. A
regra da cadeia costura. Bibliotecas (PyTorch, JAX)
constroem um grafo e fazem a conta. O engenheiro que nunca
fez uma à mão não sabe quando o grafo está errado.

Derivada da sigmoide: *p * (1-p)*. Derivada de *z* em
relação a *w1*: *x1*. Logo *dL/dw1* no caso rótulo 1 é
*(p-1) * x1*. Números, não poesia.

## Profundidade

Duas camadas escondidas com ReLU já aproximam funções que
uma reta não alcança. O teorema de aproximação universal
diz que uma camada escondida larga o bastante aproxima
quase qualquer função contínua. Na prática, *profundidade*
generaliza melhor e treina melhor em visão e linguagem —
até o ponto em que o sinal some. Aí entram residual
connections (He e colegas, ResNet, 2015): somar a entrada
da camada à saída, para o gradiente ter uma estrada reta.

O Transformer, mais tarde, é residual até a raiz. Cada
bloco é *x + f(x)*.

## Inicialização e o NaN

Se os pesos começam grandes, as ativações explodem. Se
começam minúsculos, o sinal some. Inicializações modernas
(*He*, *Xavier*) acertam a variância. Se o seu treino
vira *NaN* no passo 3, olhe taxa de aprendizado, norma
dos logits e *mixed precision* antes de culpar o dataset.

## Caderno

Escreva Areia 0.1 em Python puro. Um passo de gradiente
no exemplo *(2, 3)* com rótulo 0. Confira que *p* cai.
Se *p* subir, você somou o gradiente em vez de subtrair.
