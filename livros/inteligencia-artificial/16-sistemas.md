# Sistemas: onde o emprego mora

Leia uma vaga de *GPT Infrastructure* ou *RL Training
Infra* na OpenAI. Os substantivos são: kernel, runtime,
orquestração, GPU, rede, *checkpoint*, verificador,
latência. O adjetivo é *generalista que debuga fundo*.

Você não vira isto num capítulo. Vira isto quando um
treino de 14 horas morre no minuto 13:51 e você ainda
quer saber *qual* NCCL travou.

## A GPU em uma analogia

A GPU é uma fábrica de matrizes. A memória é o estoque.
Se o estoque não alimenta a fábrica, os operários
esperam: *memory bound*. Atenção em decode, com batch
pequeno, muitas vezes é isto. Se a fábrica não dá
conta das contas: *compute bound*. Prefill gordo pode
ser isto. Perfilar é perguntar qual dos dois está
mentindo no gráfico.

*CUDA* e *Triton* são as linguagens com que se escreve
o operário. Você pode viver anos em PyTorch sem
escrever um kernel. No time que serve o modelo, não.

## Paralelismo, os três eixos

- **Dados.** Cada GPU vê um pedaço do batch. Simples.
  Exige sincronizar gradientes.
- **Tensor.** Cada GPU vê um pedaço da matriz. Mais
  comunicação por camada.
- **Pipeline.** Cada GPU vê um pedaço da profundidade.
  *Bubbles* se o *microbatch* estiver mal feito.

*ZeRO* / FSDP espalha estados do otimizador para o
modelo caber. O preço é comunicação. Não há almoço.

## Observabilidade

Um job sem métrica de *tokens/s*, norma de gradiente,
perda por fatia de dado e temperatura dos chips é um
voo por instrumentos quebrados. O engenheiro de
laboratório ama gráfico. O bom ama o gráfico *antes*
do incidente.

## Caderno

Se tiver uma GPU, rode um matmul *N x N* crescendo *N*
até a memória reclamar. Anote o tempo. Se não tiver,
escreva por que *batch size* 1 na inferência de um
modelo gordo desperdiça silício — e por que o produto
às vezes exige mesmo assim (privacidade, latência do
único usuário).
