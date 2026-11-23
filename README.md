# The World in One Page — 23 November 2026

Entry for make.fun bounty **"Sum up 23 November's world news in one image"**
(`news-image-20261123`).

A single Python 3 program (`main.py`, standard library only) draws a
1024×1024 newspaper-style front page and writes `entry.png`.

## The image

- Big masthead with the single date **23 NOVEMBER 2026** (Monday).
- Seven stories reported on 23 November 2026, from different regions
  and topics:
  1. COP31 in Antalya ends with no climate deal (climate / Turkey)
  2. Russian strike on Dymer kills 11; Kyiv region in mourning (Ukraine)
  3. Trump says Iran deal not yet acceptable; Bahrain reports attack (Middle East)
  4. Nvidia reinstates Jensen Huang as CEO; shares up 31%+ (business / tech)
  5. Democrats clinch a 258-seat House majority (USA)
  6. Three dead, 36 missing in an Indonesia candy-factory fire (Asia)
  7. South Korea education minister quits over an AI-cheating row (Asia)
- Every headline and summary is factual and sourced from reporting
  dated 23 November 2026 (Reuters, Just Security, Dawn, Manila Times).
  No speculation, no invented quotes or figures.

## How it works

- No external imaging library, no external fonts or images, no network at runtime.
- Text is rendered with an embedded 5×7 bitmap font written for
  this entry; the PNG is encoded by hand with `zlib`/`struct`.
- Deterministic: running it twice produces a byte-identical file.
- Output is at most 1024×1024 px and under 1 MiB.

## Run

```sh
python3 main.py
# writes out/entry.png (or $MAKEFUN_OUTPUT_DIR/entry.png)
```

Tested locally with `MAKEFUN_OUTPUT_DIR=out`: two runs are
byte-identical, 1024×1024, under 1 MiB, and the PNG opens correctly.
