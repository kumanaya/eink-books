---
name: eink-books
description: >-
  Explains and operates the eink-books project: Markdown to KOReader EPUB
  or Kindle FBInk scriptlet, covers, <eink-image> tags, deploy paths, and
  jailbreak constraints. Use when building, debugging, or extending
  eink-books, generating covers, writing scriptlets, or deploying a book
  to a Kindle.
---

# eink-books

House project of E-INK HACK. The converter runs on the desk. The Kindle
only receives artifacts.

## When to use

Working in `eink-books/`, changing `src/eink_books/`, running `eink-books`
CLI, writing `examples/*.md`, or copying output onto a mounted Kindle.

Also read [write-kindle-book](../write-kindle-book/SKILL.md) when the task
is authoring the manuscript itself.

## Pipeline

```
.md (+ YAML frontmatter)
  → parse.load_book
      expand <eink-image> → images/eink-*.jpg (Puter, cached)
      split on ATX H1
      HTML (figures) + FBInk paragraphs
  → target koreader: EPUB3-ish (cover.xhtml, nav, chapters, book CSS)
  → target scriptlet: <slug>.sh + extensions/eink-books/<slug>/{pages,images,cover.jpg,font.ttf}
  → tools/deploy.sh copies .sh/.epub to documents/, internals to extensions/
```

Do not put `pages/`, `.txt`, or images under `documents/`. The stock
library indexes them as extra books.

## CLI

```sh
cd eink-books
. .venv/bin/activate          # system Python may be externally managed
eink-books build livro.md --target both --out out/
eink-books build livro.md --no-images          # reuse cached illustrations
eink-books cover-puter livro.md --write-frontmatter
eink-books cover livro.md                      # OpenRouter, paid
```

Secrets live in `eink-books/.env` (gitignored): `PUTER_AUTH_TOKEN`,
optionally `OPENROUTER_API_KEY`. `load_project_env()` reads it.

`--target both` writes one library icon (the FBInk reader). `--launcher`
adds a second icon that opens the EPUB in KOReader `--asap`.

## Image tags

```markdown
<eink-image id="praia" alt="Clara na areia">
A girl kneeling on an empty beach, glass hourglass half buried.
High contrast, no lettering.
</eink-image>
```

Self-closing: `<eink-image prompt="..." id="x" />`.

Build replaces the tag with `![alt](images/eink-<id>.jpg)`. EPUB wraps
standalone images in `<figure class="illustration">`. The scriptlet
turns each image into its own `@image:` page; `fbink -g` draws it.
Page 1 is `cover.jpg` when frontmatter has `cover:`.

## Scriptlet rules

Same as the rest of the workshop. `dev-tools/check.sh` enforces them:

- LF, no BOM, `#!/bin/sh`
- `# Name:` / `# Author:` in the first ten lines
- `# DontUseFBInk` — automatic pipe is append-only
- Write only under `/mnt/us`

Reader stays alive, redraws, uses Caecilia then bundled Liberation Serif.

## Devices

Default `--device kt4` is 600×800. Profiles: `kt4`, `pw1`, `pw3`, `pw5`.

## Tests

```sh
python -m unittest discover -s tests -v
```

No Kindle required. Do not call live image APIs from tests: use
`generate_images=False` and fixture JPEGs.

## Do not

- Jailbreak from this repo (see kindlemodding.org)
- Deploy page files into `documents/`
- Duplicate the book via both reader + launcher unless asked
- Commit `.env`
