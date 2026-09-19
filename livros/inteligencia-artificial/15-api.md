# A API não é mágica

A OpenAI, e qualquer laboratório com produto, expõe um
contrato HTTP: você manda mensagens, ferramentas, um
identificador de modelo; recebe tokens de volta, às
vezes em stream. Os nomes mudam (*Chat Completions*,
*Responses*). A física não.

## Mensagens são estado

    system: regras do ofício
    user: o pedido
    assistant: o que o modelo já disse
    tool: o que o mundo devolveu

O modelo *não lembra* da sessão anterior a menos que
você reenvie o estado, ou que o produto tenha memória
à parte. "O ChatGPT lembra de mim" é um sistema em
volta, não um milagre do decoder.

## Ferramentas

Você descreve uma função (*nome, JSON schema*). O
modelo pode pedir a chamada. Você executa. Devolve o
resultado. O modelo continua. Isto é um agente mínimo.
O risco é óbvio: o modelo inventa argumentos. Valide
como validaria input de um estranho — porque é o que
é.

## Exemplo honesto

    messages = [
      {"role": "system", "content": "Responda em pt-BR. Se não souber, diga."},
      {"role": "user", "content": "Qual o KV cache de um token neste livro?"},
    ]

Um modelo sem o livro alucina um número. A resposta
correta de engenheiro é: "não está no contexto; calcule
como no capítulo 13 ou recuse." O *system* que pede
humildade ajuda. Não garante. Por isso eval.

## O que um engenheiro da porta para dentro vê

Rate limit, fila, *batching* de requests alheios no
mesmo batch, *speculative decoding*, um fallback de
modelo. O seu *timeout* de 30 segundos pode ser o
prefill de outra pessoa. Logs de *request id* valem
ouro. Tratar a API como função pura é o primeiro
passo; o segundo é tratar como sistema distribuído.

## Caderno

Implemente um cliente que: (1) corta o histórico nos
últimos *N* tokens, não *N* mensagens; (2) registra
prompt tokens e completion tokens; (3) falha se a
ferramenta devolver JSON inválido. Sem a parte (1),
você estoura contexto. Sem a (2), não tem custo. Sem
a (3), tem incidente.
