# O ofício, não o milagre

Inteligência artificial, neste livro, não é um aplicativo que
responde. É um sistema que *ajusta números* até uma medida de
erro cair — e depois serve esses números milhões de vezes por
segundo, sem mentir sobre o que sabe.

Um engenheiro de um laboratório como a OpenAI não é só
"alguém que usa GPT". As vagas públicas da empresa pedem, em
combinações diferentes, quatro músculos:

1. **Modelo.** Por que a atenção escala com o quadrado do
   contexto. O que um *KV cache* guarda. Onde o softmax
   satura.
2. **Sistema.** GPUs, comunicação entre chips, *batching*,
   falha de um nó no meio de um treino de semanas.
3. **Avaliação.** Um número que prediz o produto. Um *eval*
   que não se deixa enganar por um modelo bajulador.
4. **Julgamento.** Qual experimento vale o cluster. Qual
   atalho corrompe o dado. Quando parar.

Você não precisa ter os quatro no primeiro mês. Precisa saber
que o emprego é a interseção deles. Pesquisador puro sem
sistema não escala. Sistemista sem modelo otimiza o kernel
errado. Produto sem eval envia regressão para a produção.

## O que um modelo faz, em uma frase

Recebe um vetor. Devolve outro. No meio, multiplica matrizes
e aplica funções não-lineares. O "conhecimento" está nos
pesos — milhões ou bilhões de números. O treino é a busca
desses números. A inferência é usá-los.

Areia, no capítulo 5, terá seis pesos. Um GPT moderno tem
ordens de grandeza a mais. A *forma* é a mesma. Quem
entende Areia lê um paper de 2017 sem pânico.

## Três mentiras úteis, e quando largá-las

**"É só estatística."** Útil no começo: um classificador de
spam *é* estatística. Largue quando o objeto for um modelo
autorregressivo de 100 bilhões de parâmetros com pós-treino
por preferência humana. A estatística continua lá. O sistema
ao redor é o emprego.

**"É só um autocomplete."** Útil para matar o misticismo.
Um modelo de linguagem de fato prediz o próximo token. Largue
quando precisar explicar ferramentas, memória, ou um agente
que chama código. O autocomplete é o motor. O carro é outra
peça.

**"A API é o produto."** Útil para enviar o primeiro *hello
world*. Largue quando a latência do oitavo token, o custo
por milhão e a taxa de alucinação forem o seu KPI. A API é
a porta. O engenheiro mora atrás dela.

## Como este livro se parece com o trabalho

No laboratório, um ciclo típico é:

1. Uma hipótese ("se mascararmos a atenção de outra forma,
   o contexto longo barateia").
2. Um *eval* pequeno que falharia se a hipótese fosse falsa.
3. Um treino ou um *ablation* que cabe no orçamento.
4. Um post-mortem: o que o gráfico mentiu.

Os capítulos 4 e 18 ensinam esse ciclo em miniatura. Os
capítulos 14 e 17 ensinam a não se apaixonar pelo próprio
gráfico.

## Caderno

Escreva, sem consultar nada, a diferença entre *treino* e
*inferência* em duas frases. Depois escreva um exemplo em
que inferência é mais cara que treino (há vários; um deles
é servir um modelo enorme para milhões de usuários). Se a
segunda parte travar, você ainda está no modo usuário. Siga
em frente: o livro existe para essa travada.
