# O Transformer, peça por peça

O paper de 2017 descreve um encoder-decoder para tradução.
Os GPTs jogam o encoder fora e empilham blocos decoders
causais. BERT empilha encoders bidirecionais. A peça é a
mesma. A máscara muda.

Um *bloco* decoder moderno, em prosa:

1. Norma (às vezes antes, *pre-norm*).
2. Autoatenção causal, com *Q, K, V* projetados do mesmo
   *x*. Residual: *x = x + attn*.
3. Norma.
4. MLP (duas matrizes, uma não-linearidade no meio, às
   vezes *SwiGLU*). Residual: *x = x + mlp*.

Empilhe 12, 32, 96 blocos. No começo, um *embedding* de
token mais posição. No fim, uma matriz que devolve logits
do tamanho do vocabulário. Isto é Areia 1.0. Isto é, em
forma, um GPT.

## O MLP não é figurante

A atenção mistura informação *entre* tokens. O MLP, aplicado
na mesma posição, *pensa* naquela mistura. Boa parte dos
parâmetros de um LLM mora no MLP. Quando alguém diz
"comprimimos o modelo", muitas vezes está matando dimensões
daí.

## Residuais e o caminho do gradiente

Cada bloco é *x + f(x)*. O gradiente de *x* tem uma
estrada que não passa por *f*. Sem isso, 96 camadas não
treinam. Se o seu treino raso funciona e o fundo não,
desconfie da norma e do residual antes da poesia da
arquitetura.

## Encoder versus decoder

- **Encoder (BERT):** cada token vê todos. Bom para
  classificar, recuperar, preencher lacuna.
- **Decoder (GPT):** cada token vê só o passado. Bom para
  gerar.
- **Encoder-decoder (T5, o Transformer original):** um
  lê, o outro escreve olhando o que foi lido.

Escolher a família é escolha de produto. Um classificador
de ticket não precisa gerar. Um assistente precisa.

## Exemplo: um passo de geração

Vocabulário minúsculo: *o, relógio, caiu, .* . Areia já
viu "o relógio". Os logits do próximo token favorecem
"caiu". Amostramos. Agora o contexto é "o relógio caiu".
De novo. O ponto ganha. Paramos.

Nada no bloco "sabe" que a frase acabou além do que os
pesos aprenderam sobre pontos. *EOS* é um token como
outro. O engenheiro que não trata *stop* como parte do
modelo passa a vida cortando texto no cliente.

## Caderno

Desenhe um bloco com duas setas residuais. Escreva, ao
lado, as dimensões se *n = 8* tokens e *d = 16*: *Q* é
8x16 (depois projetado para *d_k*). Este desenho vale
mais que um vídeo de uma hora se você o fizer sem copiar.
