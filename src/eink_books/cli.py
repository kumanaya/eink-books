from __future__ import annotations

import argparse
import sys
from pathlib import Path

from eink_books import __version__
from eink_books.build import build
from eink_books.cover import (
    choose_aspect_ratio,
    choose_quality,
    cover_prompt,
    find_model,
    generate_cover_bytes,
    list_image_models,
    pick_cheapest_model,
    prompt_from_source,
    resolve_api_key,
    save_cover,
    write_frontmatter_cover,
)
from eink_books.puter_cover import (
    DEFAULT_MODEL as PUTER_DEFAULT_MODEL,
    generate_puter_cover_bytes,
    list_puter_models,
    resolve_puter_token,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="eink-books",
        description="Turn Markdown into a KOReader EPUB or a Kindle scriptlet book.",
    )
    parser.add_argument("--version", action="version", version=f"eink-books {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    build_cmd = sub.add_parser("build", help="compile a markdown source into book artifacts")
    build_cmd.add_argument("source", help="a .md file or a folder of chapter files")
    build_cmd.add_argument(
        "--target",
        choices=("koreader", "scriptlet", "both"),
        default="both",
        help="koreader writes an EPUB (+ launcher); scriptlet writes an FBInk reader",
    )
    build_cmd.add_argument("--out", default="out", help="output directory (default: out)")
    build_cmd.add_argument("--device", default="kt4", help="pagination profile (default: kt4)")
    build_cmd.add_argument("--width", type=int, help="override profile width in pixels")
    build_cmd.add_argument("--height", type=int, help="override profile height in pixels")
    build_cmd.add_argument("--font-size", type=float, default=14.0, help="body size in points")
    build_cmd.add_argument("--font", help="TTF used to paginate and shipped with the reader")
    build_cmd.add_argument(
        "--launcher",
        action="store_true",
        help="also write a second library scriptlet that opens the EPUB in KOReader",
    )
    build_cmd.add_argument(
        "--no-launcher",
        action="store_true",
        help="do not write the KOReader launcher (default when --target both)",
    )
    build_cmd.add_argument(
        "--no-images",
        action="store_true",
        help="do not call Puter for missing <eink-image> tags (use cached files only)",
    )

    cover_cmd = sub.add_parser(
        "cover",
        help="generate a book cover via the OpenRouter Image API",
    )
    cover_cmd.add_argument(
        "source",
        nargs="?",
        help="a .md file or folder; used for title/author unless you pass --title",
    )
    cover_cmd.add_argument("--title", help="cover title (overrides the markdown frontmatter)")
    cover_cmd.add_argument("--author", help="cover author")
    cover_cmd.add_argument("--prompt", default="", help="extra instructions appended to the cover prompt")
    cover_cmd.add_argument(
        "--model",
        help="OpenRouter image model slug (default: cheapest model with a live Image API endpoint)",
    )
    cover_cmd.add_argument("--aspect-ratio", default="3:4", help="requested ratio; falls back if unsupported")
    cover_cmd.add_argument("--quality", help="auto/low/medium/high when the model supports it")
    cover_cmd.add_argument("--out", help="output image path (default: <source-dir>/cover.jpg)")
    cover_cmd.add_argument("--api-key", help="OpenRouter key; otherwise OPENROUTER_API_KEY")
    cover_cmd.add_argument(
        "--write-frontmatter",
        action="store_true",
        help="set cover: on the source markdown file",
    )
    cover_cmd.add_argument("--no-overlay", action="store_true", help="do not draw title/author on the image")
    cover_cmd.add_argument("--list-models", action="store_true", help="list image models and estimated cost, then exit")
    cover_cmd.add_argument(
        "--dry-run",
        action="store_true",
        help="print model, estimate and prompt; do not call the Image API",
    )

    puter_cmd = sub.add_parser(
        "cover-puter",
        help="generate a book cover via Puter's free User-Pays image API",
    )
    puter_cmd.add_argument(
        "source",
        nargs="?",
        help="a .md file or folder; used for title/author unless you pass --title",
    )
    puter_cmd.add_argument("--title", help="cover title (overrides the markdown frontmatter)")
    puter_cmd.add_argument("--author", help="cover author")
    puter_cmd.add_argument("--prompt", default="", help="extra instructions appended to the cover prompt")
    puter_cmd.add_argument(
        "--model",
        default=PUTER_DEFAULT_MODEL,
        help=f"Puter image model slug (default: {PUTER_DEFAULT_MODEL})",
    )
    puter_cmd.add_argument("--aspect-ratio", default="3:4", help="requested ratio (default: 3:4)")
    puter_cmd.add_argument("--quality", help="low/medium/high when the model supports it")
    puter_cmd.add_argument("--out", help="output image path (default: <source-dir>/cover.jpg)")
    puter_cmd.add_argument(
        "--token",
        help="Puter auth token; otherwise PUTER_AUTH_TOKEN (https://puter.com/dashboard)",
    )
    puter_cmd.add_argument(
        "--write-frontmatter",
        action="store_true",
        help="set cover: on the source markdown file",
    )
    puter_cmd.add_argument("--no-overlay", action="store_true", help="do not draw title/author on the image")
    puter_cmd.add_argument(
        "--list-models",
        action="store_true",
        help="list Puter image models (live list if a token is set, else the published catalog)",
    )
    puter_cmd.add_argument(
        "--test-mode",
        action="store_true",
        help="ask Puter for a sample image without spending account credits",
    )
    puter_cmd.add_argument(
        "--dry-run",
        action="store_true",
        help="print model and prompt; do not call Puter",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.command == "build":
        try:
            artifacts = build(
                source=Path(args.source),
                out_dir=Path(args.out),
                target=args.target,
                device=args.device,
                width=args.width,
                height=args.height,
                font_size=args.font_size,
                font=args.font,
                launcher=True if args.launcher else False if args.no_launcher else None,
                generate_images=not args.no_images,
            )
        except (FileNotFoundError, ValueError, RuntimeError) as exc:
            print(f"eink-books: {exc}", file=sys.stderr)
            return 1
        print(f"built {args.target} -> {args.out}")
        for key, path in artifacts.items():
            print(f"  {key}: {path}")
        return 0
    if args.command == "cover":
        return _cover_command(args)
    if args.command == "cover-puter":
        return _cover_puter_command(args)
    return 2


def _cover_meta(args: argparse.Namespace) -> tuple[str, str, str, Path | None]:
    title = args.title
    author = args.author or "Unknown"
    language = "en"
    source = Path(args.source) if args.source else None
    if source is not None:
        src_title, src_author, language, _built = prompt_from_source(source, args.prompt)
        title = title or src_title
        if not args.author:
            author = src_author
    if not title:
        raise ValueError("pass a markdown source or --title")
    return title, author, language, source


def _cover_dest(args: argparse.Namespace, source: Path | None) -> Path:
    if args.out:
        return Path(args.out)
    if source and source.is_file():
        return source.resolve().parent / "cover.jpg"
    if source and source.is_dir():
        return source / "cover.jpg"
    return Path("cover.jpg")


def _cover_command(args: argparse.Namespace) -> int:
    try:
        if args.list_models:
            models = list_image_models()
            print(f"{'model':48} {'est.usd':>8}  endpoints  ratios")
            for model in models:
                estimate = (
                    f"{model.estimate_usd:.4f}" if model.estimate_usd is not None else "?"
                )
                ratios = ",".join(model.aspect_ratios[:6]) or "-"
                mark = "yes" if model.has_endpoint else "no"
                print(f"{model.id:48} {estimate:>8}  {mark:9}  {ratios}")
            print(f"{len(models)} models with a live Image API endpoint")
            return 0

        title, author, language, source = _cover_meta(args)
        prompt = cover_prompt(title, author, args.prompt, language)
        picked = find_model(args.model) if args.model else pick_cheapest_model()
        if args.model and not picked.has_endpoint:
            print(
                f"eink-books: {picked.id} is in the catalog but has no Image API endpoint",
                file=sys.stderr,
            )

        aspect = choose_aspect_ratio(picked, args.aspect_ratio)
        quality = choose_quality(picked, args.quality)
        dest = _cover_dest(args, source)

        print(f"model:         {picked.id}")
        if picked.estimate_usd is not None:
            print(f"est. cost:     ${picked.estimate_usd:.4f}  ({picked.pricing_note})")
        else:
            print(f"est. cost:     unknown  ({picked.pricing_note})")
        print(f"aspect_ratio:  {aspect}")
        print(f"quality:       {quality or '-'}")
        print(f"out:           {dest}")
        print(f"prompt:        {prompt}")
        if args.dry_run:
            print("dry-run: no request sent")
            return 0

        api_key = resolve_api_key(args.api_key)
        raw, media, usage = generate_cover_bytes(
            model=picked.id,
            prompt=prompt,
            api_key=api_key,
            aspect_ratio=aspect,
            quality=quality,
        )
        save_cover(raw, dest, title=title, author=author, overlay=not args.no_overlay)
        if args.write_frontmatter:
            if source is None or not source.is_file():
                raise ValueError("--write-frontmatter needs a markdown file")
            write_frontmatter_cover(source, dest)
        cost = usage.get("cost")
        print(f"saved:         {dest}  ({media})")
        if cost is not None:
            print(f"billed:        ${cost}")
        return 0
    except (FileNotFoundError, ValueError, RuntimeError) as exc:
        print(f"eink-books: {exc}", file=sys.stderr)
        return 1


def _cover_puter_command(args: argparse.Namespace) -> int:
    try:
        if args.list_models:
            token = (args.token or "").strip() or None
            if token is None:
                try:
                    token = resolve_puter_token(None)
                except ValueError:
                    token = None
            models = list_puter_models(token)
            print(f"{'model':48}  provider")
            for model in models:
                print(f"{model.id:48}  {model.provider or '-'}")
            print(f"{len(models)} Puter image models")
            return 0

        title, author, language, source = _cover_meta(args)
        prompt = cover_prompt(title, author, args.prompt, language)
        dest = _cover_dest(args, source)

        print(f"provider:      puter")
        print(f"model:         {args.model}")
        print(f"aspect_ratio:  {args.aspect_ratio}")
        print(f"quality:       {args.quality or '-'}")
        print(f"test_mode:     {args.test_mode}")
        print(f"cost:          User-Pays (Puter account credits; developer pays $0)")
        print(f"out:           {dest}")
        print(f"prompt:        {prompt}")
        if args.dry_run:
            print("dry-run: no request sent")
            return 0

        token = resolve_puter_token(args.token)
        raw, media = generate_puter_cover_bytes(
            prompt=prompt,
            token=token,
            model=args.model,
            aspect_ratio=args.aspect_ratio,
            quality=args.quality,
            test_mode=args.test_mode,
        )
        save_cover(raw, dest, title=title, author=author, overlay=not args.no_overlay)
        if args.write_frontmatter:
            if source is None or not source.is_file():
                raise ValueError("--write-frontmatter needs a markdown file")
            write_frontmatter_cover(source, dest)
        print(f"saved:         {dest}  ({media})")
        return 0
    except (FileNotFoundError, ValueError, RuntimeError) as exc:
        print(f"eink-books: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
