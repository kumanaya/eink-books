# Como um engenheiro pensa

O laboratório não premia quem tem a opinião mais
quente no Slack. Premia quem fecha o ciclo:

    hipótese → predicao mensurável → experimento
    barato → resultado que surpreende → escrita

A escrita importa. Um treino sem nota de três
parágrafos é um treino que ninguém reproduz. Papers
são o modo como a área conversa; *tech reports*
internos são o modo como o time não esquece.

## Como ler um paper

Na primeira passagem, só isto:

1. Qual a afirmação?
2. Qual o *baseline*?
3. Qual o eval?
4. O que a ablação mata?

*Attention Is All You Need* afirma: dá para traduzir
sem recorrência, com atenção, mais paralelo, melhor
BLEU. O baseline são RNNs e convs da época. Se você
não consegue dizer isto em quatro frases, ainda não
leu o paper — só passou os olhos nas figuras.

*InstructGPT* afirma: SFT + RM + PPO faz um modelo
menor seguir instruções melhor, no gosto dos
rótulos, que um GPT-3 maior. A nuance está na
seção 5: *quem* é o humano da preferência.

## Debugging de modelo

Quando a perda não cai:

- O alvo está desalinhado do input? (off-by-one no
  token)
- A máscara causal está invertida?
- A taxa está absurda?
- O dado está vazio depois do filtro?
- Você está avaliando o checkpoint errado?

Quando a perda cai e o produto piora:

- O eval não representa o usuário.
- Reward hacking.
- Contaminação.
- Você otimizou o juiz, não a tarefa.

## Caderno

Escolha um paper da lista do apêndice. Escreva as
quatro frases. Não avance para o próximo paper
enquanto não conseguir. Este músculo vale mais do
que mais um curso de *tools*.
