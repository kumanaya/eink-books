# A linguagem da incerteza

Um modelo não "sabe". Ele *distribui*. A frase mais honesta
da área é: "dado o que vi, estas saídas são mais críveis
que aquelas."

Probabilidade aqui não é cassino. É a gramática com que
medimos surpresa.

## Dois axiomas que bastam

Um evento *A* tem probabilidade entre 0 e 1. Eventos
impossíveis de coincidir somam. O resto — Bayes, esperança,
entropia — cresce daí.

A regra de Bayes, sem teatro:

    P(hipótese | dado) é proporcional a
    P(dado | hipótese) vezes P(hipótese)

Em português: depois de ver o dado, reescreva a crença
antiga pela *verossimilhança* (quanto aquele dado seria
esperado se a hipótese fosse verdadeira).

## Exemplo: o dado que mente

Areia tenta adivinhar se um e-mail é spam. Antes de abrir
a caixa, 3 em 100 são spam: *prior* 0.03. A palavra
"grátis" aparece em 80% dos spams e em 5% dos e-mails
limpos.

Chega um e-mail com "grátis". Bayes:

    P(spam | grátis) =
      (0.80 * 0.03) / (0.80 * 0.03 + 0.05 * 0.97)
      ≈ 0.33

Um terço. Não é certeza. Um filtro ingênuo que dispara em
"grátis" erra dois terços das vezes neste mundo. O engenheiro
que só olha a verossimilhança (0.80) e ignora o prior
constrói um produto histérico.

Troque "spam" por "o próximo token é *areia*". O modelo faz
a mesma conta, com milhões de hipóteses (o vocabulário) e
uma verossimilhança aprendida, não tabelada.

## Variável aleatória, esperança, perda

Uma *variável aleatória* é um número que o mundo ainda não
fixou. A *esperança* é a média ponderada pelas
probabilidades.

A *entropia* de uma distribuição é a surpresa média. Uma
moeda honesta tem entropia 1 bit. Uma moeda viciada tem
menos: o mundo é mais previsível.

A *entropia cruzada* entre a distribuição verdadeira *p* e
a do modelo *q* é a surpresa média de quem usa *q* no
mundo de *p*. Treinar um classificador com *softmax* e
*cross-entropy* é isto: punir *q* por estar surpreso
quando *p* não está.

## Amostragem não é argmax

Na inferência, o modelo devolve um vetor de *logits*.
Softmax vira distribuição. Há pelo menos três jeitos de
escolher o token:

- **Ganancioso:** pega o máximo. Texto seco, às vezes
  repetitivo.
- **Temperatura:** divide os logits por *T*. T alta
  achata; T baixa aguça.
- **Núcleo (top-p):** corta a cauda até acumular
  probabilidade *p*, depois amostra.

Um engenheiro de produto que só conhece temperatura vai
passar uma semana caçando "criatividade" no lugar errado.
Às vezes o bug é o *top-p*. Às vezes é o prompt. Às vezes
é o modelo sem pós-treino.

## Caderno

Calcule P(spam | grátis) de novo com prior 0.30. O número
muda muito. Escreva uma frase sobre por que *dataset
desbalanceado* e *prior* são o mesmo problema com roupa
diferente.
