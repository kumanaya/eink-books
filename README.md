<p align="center">
  <img src="docs/banner.jpg" alt="E-INK BOOKS — Markdown in. A book out." width="720" />
</p>

<h1 align="center">E-INK BOOKS</h1>

<p align="center">
  <strong>Markdown in. A book out.</strong><br />
  An EPUB for KOReader, or a scriptlet that is the book.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Kindle-e--ink-111111?style=flat-square" alt="Kindle" />
  <img src="https://img.shields.io/badge/KOReader-EPUB-6b6b6b?style=flat-square" alt="KOReader" />
  <img src="https://img.shields.io/badge/scriptlet-FBInk-6b6b6b?style=flat-square" alt="scriptlet" />
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square" alt="MIT" />
</p>

<p align="center">
  <a href="#on-your-desk">On your desk</a>
  ·
  <a href="#on-the-kindle">On the Kindle</a>
  ·
  <a href="#why-epub-not-raw-markdown">Why EPUB</a>
  ·
  <a href="#license">License</a>
</p>

A house project of **E-INK HACK**. The converter runs on your desk. The Kindle
only receives the artifacts.

```
eink-books build livro.md --target koreader
eink-books build livro.md --target scriptlet
eink-books build livro.md --target both
eink-books build ./capitulos/ --target both --out out/
```

| Target | What you get | What opens it |
|---|---|---|
| `koreader` | `out/<slug>.epub` and a launcher scriptlet | KOReader, from the Kindle library |
| `both` | EPUB + the FBInk reader. No second library icon unless you pass `--launcher` | the scriptlet, or KOReader's file browser |
| `scriptlet` | `out/<slug>.sh` plus `out/<slug>/pages/` and a TTF | the scriptlet itself, via FBInk |

> [!NOTE]
> The Kindle must already be running a jailbreak that provides scriptlets
> (`sh_integration`) and, for the EPUB path, KOReader. This project does not
> jailbreak a device. See [kindlemodding.org](https://kindlemodding.org/).

---

## On your desk

Python 3.11+ (use a venv if the system Python is marked externally managed):

```sh
python -m venv .venv
. .venv/bin/activate
python -m pip install -e .
eink-books build examples/hello-book.md --target both --out out/
```

YAML frontmatter on the first file:

```yaml
---
title: O Relogio de Areia
subtitle: Um conto
author: Daniel Kumanaya
language: pt
cover: cover.jpg
identifier: urn:uuid:…
publisher: E-INK HACK
date: 2026-09-19
rights: All rights reserved.
description: >
  Numa praia que so existe quando a mare baixa, Clara encontra um
  relogio de areia. Cada grao mede atencao, nao horas.
subjects:
  - Fiction
  - Short stories
---
```

`#` headings become chapters (one XHTML file each, so KOReader can render
partially). A folder of `.md` files is concatenated in name order; a file
without an `#` heading gets one from its `title` or from the filename.

Inline illustrations are `<eink-image>` tags. The body is the prompt.
On build, Puter generates `images/eink-<id>.jpg` (cached) and the tag
becomes a figure in the EPUB and a full-screen page in the scriptlet.
The book cover is page 1 of the reader and `cover.xhtml` in the EPUB
spine, following the [IDPF EPUB3 samples](https://github.com/IDPF/epub3-samples)
pattern (cover document, nav, then chapters).

```markdown
<eink-image id="praia" alt="Clara encontra o relogio">
A girl kneeling on an empty beach at low tide, a glass hourglass
half buried in wet sand. High contrast, no lettering.
</eink-image>
```

`--no-images` skips the API and uses files already in `images/`.

`--device kt4` paginates for a 600×800 panel. Override with `--width` /
`--height` / `--font-size`. Known profiles: `kt4`, `pw1`, `pw3`, `pw5`.

### Covers (OpenRouter)

`eink-books cover` calls OpenRouter's Image API (`POST /api/v1/images`).
Set `OPENROUTER_API_KEY`. `eink-books cover --list-models` asks the
OpenRouter Image API which slugs have a live endpoint. Models that appear
in the catalog with zero endpoints (today: `meta/muse-image`) are skipped.
The default is the cheapest remaining portrait model — currently
`openai/gpt-image-1-mini` at about $0.006 with `quality=low`. The CLI
resizes the result to 600×800 and draws the title so the Kindle library
icon stays readable.

```sh
eink-books cover examples/hello-book.md --dry-run
eink-books cover examples/hello-book.md --write-frontmatter
eink-books cover examples/hello-book.md --model black-forest-labs/flux.2-klein-4b
eink-books cover --list-models
```

`--dry-run` prints the model, the estimate and the prompt, and does not
spend credit.

### Covers (Puter, no image-API key)

`eink-books cover-puter` is the same pipeline through Puter's
User-Pays image API — the call behind
[`puter.ai.txt2img()`](https://developer.puter.com/tutorials/free-unlimited-image-generation-api/).
You do not pay OpenRouter or OpenAI. Create a free token at
[puter.com/dashboard](https://puter.com/dashboard) and put
`PUTER_AUTH_TOKEN` in `.env` (gitignored) or in the environment.
Generation spends the Puter account's own credits.

Default model: `openai/gpt-image-1-mini` (Puter's `txt2img` default).
`--list-models` prints the published catalog, or the live driver list
when a token is set.

```sh
eink-books cover-puter examples/hello-book.md --dry-run
eink-books cover-puter examples/hello-book.md --write-frontmatter
eink-books cover-puter examples/hello-book.md --model black-forest-labs/flux-schnell
eink-books cover-puter --list-models
eink-books cover-puter examples/hello-book.md --test-mode
```

`--test-mode` asks Puter for a sample image and does not spend credits.
`--dry-run` prints the prompt and does not call the API.

Tests, with no Kindle around:

```sh
python -m unittest discover -s tests -v
sh ../dev-tools/check.sh tools/deploy.sh
```

The second command is the same checker the rest of the workshop uses: LF, no
BOM, a real shebang, `# Name:` at the top of generated scriptlets.

## On the Kindle

```sh
sh tools/deploy.sh /path/to/kindle-mount out
```

That copies the EPUB and the `.sh` files into `documents/`, and the
pages/font/cover into `extensions/eink-books/` — never into `documents/`,
or the stock library indexes `0001.txt` as extra books. Eject. The
scriptlets show up in the library.

**KOReader.** `--target both` writes the EPUB into `documents/` but does not
add a second library icon. Open the EPUB from KOReader's file browser. Pass
`--launcher` only if you want a second home-screen book that runs
`koreader.sh --asap`.

**FBInk reader.** Tap the `<slug>.sh` book. Pages were already cut on the desk.
A tap on the right (or any tap, if coordinates cannot be read) goes forward; the
left third goes back; the top-left corner, or a tap on the last page, returns
to the library. Physical page keys on a Kindle 4 do the same. The process stays
alive and redraws so the screensaver does not eat the page.

The reader looks for Caecilia on the device, then for the Liberation Serif TTF
shipped next to the pages. The bundled bitmap font is not enough for Portuguese.

## Why EPUB, not raw Markdown

KOReader can open `.md`, but a leading `---` / a horizontal rule can confuse
CREngine. EPUB with one XHTML file per chapter is the format the engine is
good at. No JavaScript: KOReader will never run it.

Publisher CSS (`eink.css`) is written for CREngine: justified body,
first-line indent, and no raw newlines inside `<p>` (manuscript wraps
become spaces). KOReader can still override it.

## Details that break scriptlets

Same traps as the rest of the workshop:

- Line endings must be LF.
- No UTF-8 BOM.
- `# Name:` / `# Author:` in the first ten lines.
- `# DontUseFBInk` — the automatic pipe is append-only, so a book could not
  turn the page.
- `/mnt/us` is the only safe place to write.

`dev-tools/check.sh` catches the first four before they reach the device.

## License

MIT. See [LICENSE](LICENSE). Liberation Serif (the bundled TTF) is SIL OFL;
see [src/eink_books/data/FONT-LICENSE.txt](src/eink_books/data/FONT-LICENSE.txt).
