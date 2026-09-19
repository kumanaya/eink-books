---
name: write-kindle-book
description: >-
  Authors a complete Kindle-quality book in Markdown for eink-books:
  store-style metadata, front matter, chapters, <eink-image> prompts,
  cover, and back matter. Use when writing, outlining, or revising a
  book, conto, or manuscript destined for KOReader or a jailbroken
  Kindle library.
---

# Write a Kindle-quality book

Output is a `.md` (or a folder of chapter files) that `eink-books build`
turns into an EPUB and/or an FBInk scriptlet. Aim for the same *parts*
a title on the Kindle Store has — not DRM or an ASIN.

For the converter itself, see [eink-books](../eink-books/SKILL.md).

## Manuscript file

One file, or a folder of `*.md` sorted by name. First file owns book
metadata. `#` headings are chapters (one XHTML file each).

```yaml
---
title: O Relogio de Areia          # required for a store-like listing
subtitle: Um conto                 # optional; goes into the EPUB title
author: Daniel Kumanaya            # contributor; use a real byline
language: pt                       # BCP 47: pt, pt-BR, en
identifier: urn:uuid:…             # ISBN if you have one, else UUID
cover: cover.jpg                   # 600×800 JPEG, high contrast
publisher: E-INK HACK
date: 2026-09-19                   # publication date (YYYY-MM-DD)
rights: All rights reserved.
description: >                     # jacket blurb, 150–4000 characters
  One or two paragraphs. No spoilers in the first sentence.
  Say who the book is for and what it feels like.
subjects:                          # BISAC-ish, 1–3
  - Fiction
  - Short stories
  - Magical realism
---
```

Optional extras you may add later in frontmatter if the parser grows:
`series`, `series_index`, `translator`. Until then, put series in the
subtitle (`Book Two of X`) or the blurb.

## Store-like parts (in order)

Write these as chapters or as H1s in the single file:

1. **Cover** — not in the `.md`. Generate with `eink-books cover-puter`
   (or `cover`). Portrait, readable at 600×800 grayscale. No tiny type.
2. **Title page** (optional H1 `Pagina de rosto`) — title, subtitle,
   author, publisher, year. Keep it short.
3. **Copyright** (optional H1 `Direitos autorais`) — rights line, year,
   “All rights reserved”, any edition note. No fake ISBN.
4. **Dedication** (optional)
5. **Body chapters** — every H1 is a chapter the TOC will list
6. **About the author** (optional last H1)

Do not fake a Kindle Store ASIN, price, or “Look Inside” chrome.

## Prose

- One idea per paragraph. Kindle panels are small.
- `**bold**` and `*italic*` survive both EPUB and FBInk (`**` / `*`).
- No tables, no nested HTML, no JavaScript (KOReader will not run it).
- Horizontal rules become a thin line. Prefer a new H1.
- Portuguese: write without relying on the bundled bitmap font; the
  reader ships Liberation Serif / Caecilia for accents.

## Illustrations

Any excerpt that should become a picture uses a tag. The tag body *is*
the image prompt. It is replaced at build time.

```markdown
<eink-image id="praia" alt="Clara encontra o relogio">
A girl kneeling on an empty beach at low tide, a glass hourglass half
buried in wet sand. Literary charcoal drawing, high contrast, no text.
</eink-image>
```

Rules for the prompt:

- Describe a **full page**, not a spot icon
- High contrast, limited palette, grayscale-safe
- **No lettering** (models misspell titles)
- Include `id` so rebuilds keep the same filename
- `alt` is the accessible caption (EPUB) — write it in the book language
- One illustration per scene beat, not every paragraph

Self-closing form: `<eink-image prompt="..." id="x" alt="..." />`

The scriptlet shows the book cover as page 1, then text, and each
generated image as its own full-screen page. The EPUB embeds the cover
as `cover.xhtml` plus `<figure class="illustration">` in the chapter,
in the spirit of the [IDPF EPUB3 samples](https://github.com/IDPF/epub3-samples).

## Cover copy

Jacket description (frontmatter `description`):

- First sentence: character + situation
- Second: the tension
- Tone, not plot dump
- Language matches `language:`

Cover image prompt (for `cover-puter`): scene, not a photo of a Kindle.
The CLI already adds an e-ink / no-watermark suffix and draws title +
author on a band.

## Build checklist

- [ ] Frontmatter complete (title, author, language, identifier, cover, description)
- [ ] Cover JPEG exists and is referenced
- [ ] Every H1 is a real chapter title
- [ ] Every `<eink-image>` has `id`, `alt`, and a lettering-free prompt
- [ ] `eink-books build livro.md --target both --out out/`
- [ ] Open the EPUB in KOReader or an EPUB unzip; confirm `cover.xhtml`, `nav`, `chap_*.xhtml`
- [ ] Scriptlet `pages/0001.page` starts with `@image:cover.jpg` when a cover exists

## Example

See `eink-books/examples/hello-book.md`.
