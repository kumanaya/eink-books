#!/bin/sh
# Copy eink-books output onto a mounted Kindle.
#
#   sh tools/deploy.sh /mnt/kindle
#   sh tools/deploy.sh /mnt/kindle out
#
# The mount point is the Kindle root (the folder that contains documents/).

set -eu

if [ "${1:-}" = "" ]; then
    echo "usage: sh tools/deploy.sh <kindle-mount> [out-dir]" >&2
    exit 1
fi

MOUNT=$1
OUT=${2:-out}
DOCS="$MOUNT/documents"
APPS="$MOUNT/extensions/eink-books"

if [ ! -d "$DOCS" ]; then
    echo "eink-books: $DOCS is not a directory (is the Kindle mounted?)" >&2
    exit 1
fi

if [ ! -d "$OUT" ]; then
    echo "eink-books: output directory not found: $OUT" >&2
    exit 1
fi

copied=0

for f in "$OUT"/*.epub "$OUT"/*.sh; do
    [ -e "$f" ] || continue
    cp -f "$f" "$DOCS/"
    echo "copied $(basename "$f")"
    copied=$((copied + 1))
done

mkdir -p "$APPS"
for d in "$OUT"/*/; do
    [ -d "$d" ] || continue
    [ -d "${d}pages" ] || [ -f "${d}font.ttf" ] || [ -f "${d}cover.jpg" ] || continue
    name=$(basename "$d")
    # Old deploys put pages under documents/, and the Kindle indexed
    # 0001.txt as library books. Remove that copy if it is still there.
    rm -rf "$DOCS/$name" "$DOCS/$name.sdr"
    rm -rf "$APPS/$name"
    cp -R "$d" "$APPS/$name"
    echo "copied $name/ -> extensions/eink-books/"
    copied=$((copied + 1))
done

if [ "$copied" -eq 0 ]; then
    echo "eink-books: nothing to copy in $OUT" >&2
    exit 1
fi

echo "done. eject the Kindle; the scriptlets show up in the library."
