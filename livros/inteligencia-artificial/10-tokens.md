# Tokenização: o texto vira inteiros

O modelo não lê letras. Lê IDs. *Tokenizar* é o contrato
entre o mundo e a matriz de embeddings.

O método dominante é *BPE* (byte-pair encoding) e seus
primos (*WordPiece*, *Unigram*). Começa-se por unidades
mínimas (bytes, no caso de um BPE de bytes) e vai-se
fundindo os pares mais frequentes. "areia" pode ser um
token só. "ampulheta" pode ser *ampu* + *lheta*. Um
número de cartão pode virar um token por dígito — ou
não, e aí o modelo erra conta.

## Por que português dói mais

Inglês tem mais massa nos corpora. Palavras comuns viram
um token. Em português, acentos e morfologia partem o
que deveria ser inteiro. "é" e "e" não são o mesmo ID.
Um modelo sub-treinado em pt-BR gasta contexto demais
para dizer pouco. Isto é dado, não destino: um tokenizer
treinado no seu domínio muda o teto do modelo.

## Exemplo

Frase: "O relógio caiu."

Um tokenizer imaginário devolve:

    [bos, o, Ġrel, ógio, Ġcaiu, ., eos]

O *Ġ* marca espaço. Contar tokens *não* é contar
palavras. Cobrar API por token e planejar contexto por
palavra é o erro de orçamento mais comum.

## Bugs clássicos

- Comparar dois modelos com tokenizers diferentes e
  declarar um "mais inteligente".
- Truncar no meio de um token e achar que o modelo
  "viu" a palavra.
- Treinar com um tokenizer e inferir com outro. Os
  embeddings não combinam. O resultado é lixo confiante.

## Caderno

Pegue um tokenizer real (*tiktoken* da OpenAI, ou o de
um modelo aberto) e tokenize seu nome completo, um CPF
falso e um verso de poema. Conte IDs. Anote o que
surpreendeu. Este é o primeiro perfil de um engenheiro
de LLM: obsessão por *quantos tokens isto custa*.
