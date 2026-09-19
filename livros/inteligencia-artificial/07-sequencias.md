# Sequências e o problema da memória

Texto é uma fila. A palavra 12 depende das 11 anteriores,
às vezes da primeira. Durante anos a fila foi processada
por *RNNs*: um estado *h* que se atualiza a cada passo.

    h_t = tanh(W_h h_{t-1} + W_x x_t + b)

Simples. Frágil. O gradiente, ao voltar 80 passos, some
ou explode. *LSTM* e *GRU* inventam portas para o estado
decidir o que lembrar. Funcionam. Treinam devagar: o passo
*t* espera o *t-1*. A GPU, que adora matrizes gordas em
paralelo, fica entediada.

## Convoluções em texto

Redes convolucionais leem janelas. Paralelas, rápidas,
cegas ao longo alcance a menos que a pilha seja funda.
Úteis em classificação. Insuficientes para traduzir uma
frase cujo verbo está a quarenta tokens de distância.

## A crise que o Transformer resolve

Queremos:

- olhar para qualquer par de posições com custo
  previsível;
- treinar muitos tokens ao mesmo tempo;
- não depender de um estado que esquece.

A atenção (próximo capítulo) calcula, para cada posição,
uma média ponderada de *todas* as outras. Custo: quadrático
no comprimento. Ganho: paralelismo no treino e memória
explícita, não escondida num vetor *h*.

## Posição

Sem informação de ordem, "cão morde homem" e "homem morde
cão" são o mesmo saco de palavras. RNNs ganham ordem de
graça, porque processam no tempo. Transformers precisam
que a ordem seja *injetada*: senoides do paper de 2017,
ou *RoPE* (Su e colegas), hoje o padrão em muitos
modelos abertos — uma rotação do vetor que depende da
posição.

Areia, quando virar Transformer, vai receber não só o
token, mas *onde* ele está. Esquecer isto é o bug que
faz o modelo tratar um livro como uma sopa.

## Caderno

Escreva uma RNN de um único neurônio que lê a sequência
1, 0, 1 e começa com *h = 0*. Use *tanh* e pesos 0.5.
Anote *h* a cada passo. Depois imagine 512 passos. Sinta
por que "lembrar o primeiro 1" é um pedido cruel a este
mecanismo.
