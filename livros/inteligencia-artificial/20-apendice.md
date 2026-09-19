# Apêndice: mapa, papers, glossário

## Ordem de leitura dos papers

Não leia por prestígio. Leia por dependência.

1. *Attention Is All You Need* (Vaswani et al., 2017).
   A peça.
2. *The Illustrated Transformer* (Alammar) e *The
   Annotated Transformer* (Harvard NLP). A mesma
   peça, com as mãos no código.
3. *Language Models are Few-Shot Learners* (Brown
   et al., 2020). Escala e o choque do few-shot.
4. *Scaling Laws for Neural Language Models* (Kaplan
   et al., 2020) e *Chinchilla* (Hoffmann et al.,
   2022). Orçamento.
5. *Training language models to follow instructions
   with human feedback* (Ouyang et al., 2022).
   O pipeline de preferência.
6. *FlashAttention* (Dao et al.). Quando a matemática
   encontra a hierarquia de memória.
7. Um paper recente do laboratório que você mira —
   não para decorar, para ver o *eval* da semana.

## Glossário curto

- **Logit.** Número cru antes do softmax.
- **Token.** Inteiro do vocabulário; não é palavra.
- **Embedding.** Vetor de um token ou de um texto.
- **Atenção.** Média ponderada de values, pesos via
  queries e keys.
- **KV cache.** Keys e values guardados na inferência.
- **SFT.** Fine-tune supervisionado em demonstrações.
- **RM.** Modelo de recompensa, prediz preferência.
- **PPO / DPO.** Jeitos de otimizar contra preferência.
- **Eval.** Contrato de medida, não um feeling.
- **Prefill / decode.** Ler o prompt / emitir token.

## Exercício final

Construa Areia 1.0:

- tokenizer BPE minúsculo (200 merges) num texto
  seu em pt-BR;
- um decoder de 2 camadas, *d = 64*, 4 cabeças;
- perda de próximo token;
- um eval de 20 continuações que *você* julga;
- um relatório de duas páginas: o que aprendeu, o
  que o eval revelou, o que faria com 100 vezes
  mais dado.

Quando isto existir, você não será engenheiro da
OpenAI. Será alguém que o ofício reconhece. O resto
é tempo, cluster e o hábito do capítulo 18.

## Sobre o autor

Daniel Kumanaya escreve ferramentas e livros para
o Kindle no workshop E-INK HACK. Este volume é o
caderno que ele gostaria de ter ganhado antes de
tratar modelo como oráculo.

## Colofão

Composto em Markdown, paginado para um painel
600 por 800. Capa gravada à maneira das guias de
animal. Um único diagrama de atenção. O relógio
de areia, desta vez, mede o próximo token.
