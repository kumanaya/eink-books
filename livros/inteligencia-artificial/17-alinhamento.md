# Segurança e alinhamento

Alinhar, na prática, é estreitar o que o modelo *pode*
fazer ao que o produto *deve* fazer. Recusar o pedido
perigoso. Não inventar um medicamento. Não bajular o
usuário até o delírio. Não vazar o dado de treino.

Isto não é um capítulo moral opcional. Times de
*safety* e *policy* em laboratórios fronteira são
engenharia: classificadores, recusas, red-team,
avaliações adversariais, taxas de *jailbreak*.

## Três camadas

1. **Dado.** Não treinar no que você não quer
   reproduzir.
2. **Pós-treino.** Preferência e recusa entram no
   gradiente (capítulo 12).
3. **Sistema.** Filtros na porta, na saída, no
   ferramenta. O modelo é um componente. O produto é
   o envelope.

Quem confia só na camada 2 descobre um prompt novo
numa sexta à noite.

## Red team

Contrate alguém cuja meta é fazer o modelo falhar.
Documente os ataques que funcionaram. Transforme-os
em eval. Sem isto, "está seguro" é marketing.

## Spec e honestidade

Uma tendência recente é *spec*: escrever o
comportamento desejado como documento, e treinar /
avaliar contra o documento. Outra é ensinar o modelo
a dizer incerteza em vez de preencher o vazio. As
duas são engenharia de objetivo. Nenhuma substitui
o juiz humano nos casos que importam.

## Caderno

Liste cinco pedidos que o *seu* assistente deve
recusar, e cinco que deve aceitar mesmo parecendo
sensíveis (um jornalista investigando, um médico
falando de dose *com* contexto profissional). A
fronteira é o produto. Se você não consegue
escrevê-la, o modelo vai improvisá-la.
