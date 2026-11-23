#!/usr/bin/env python3
"""
Sum up 23 November 2026's world news in one image.

Pure Python standard library only. No network, no external files,
no external imaging libraries, fonts, or images. Text is rendered with an
embedded 5x7 bitmap font written for this entry, and the PNG is
encoded by hand with zlib/struct.

Deterministic: the same input always produces byte-identical output.
No time, no randomness, no environment data is baked into the image.

Output: writes entry.png into the directory named by the
MAKEFUN_OUTPUT_DIR environment variable (default "out" for local
testing; the sandbox sets it to /output).
"""

import os
import struct
import zlib

WIDTH = 1024
HEIGHT = 1024

# ---------------------------------------------------------------- font
# 5x7 bitmap font. Each glyph is 7 rows of 5 pixels, "#" = on.
# Lowercase letters are real lowercase forms, not just small caps.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "a": ("00000", "00000", "01110", "00001", "01111", "10001", "01111"),
    "b": ("10000", "10000", "10110", "11001", "10001", "10001", "11110"),
    "c": ("00000", "00000", "01110", "10001", "10000", "10001", "01110"),
    "d": ("00001", "00001", "01101", "10011", "10001", "10001", "01111"),
    "e": ("00000", "00000", "01110", "10001", "11111", "10000", "01110"),
    "f": ("00110", "01001", "01000", "11110", "01000", "01000", "01000"),
    "g": ("00000", "01111", "10001", "10001", "01111", "00001", "01110"),
    "h": ("10000", "10000", "10110", "11001", "10001", "10001", "10001"),
    "i": ("00100", "00000", "01100", "00100", "00100", "00100", "01110"),
    "j": ("00010", "00000", "00110", "00010", "00010", "10010", "01100"),
    "k": ("10000", "10000", "10010", "10100", "11000", "10100", "10010"),
    "l": ("01100", "00100", "00100", "00100", "00100", "00100", "01110"),
    "m": ("00000", "00000", "11010", "10101", "10101", "10101", "10101"),
    "n": ("00000", "00000", "10110", "11001", "10001", "10001", "10001"),
    "o": ("00000", "00000", "01110", "10001", "10001", "10001", "01110"),
    "p": ("00000", "00000", "10110", "11001", "10001", "11110", "10000"),
    "q": ("00000", "00000", "01101", "10011", "10001", "01111", "00001"),
    "r": ("00000", "00000", "10110", "11001", "10000", "10000", "10000"),
    "s": ("00000", "00000", "01111", "10000", "01110", "00001", "11110"),
    "t": ("01000", "01000", "11100", "01000", "01000", "01010", "00100"),
    "u": ("00000", "00000", "10001", "10001", "10001", "10011", "01101"),
    "v": ("00000", "00000", "10001", "10001", "10001", "01010", "00100"),
    "w": ("00000", "00000", "10001", "10101", "10101", "10101", "01010"),
    "x": ("00000", "00000", "10001", "01010", "00100", "01010", "10001"),
    "y": ("00000", "00000", "10001", "10001", "01111", "00001", "01110"),
    "z": ("00000", "00000", "11111", "00010", "00100", "01000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "00000", "01100", "01100", "00100", "01000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "-": ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "*": ("00000", "10101", "01110", "10101", "00000", "00000", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "|": ("00100", "00100", "00100", "00100", "00100", "00100", "00100"),
    "<": ("00010", "00100", "01000", "10000", "01000", "00100", "00010"),
    ">": ("01000", "00100", "00010", "00001", "00010", "00100", "01000"),
}

# Characters not in the font fall back to this.
FALLBACK = ("01110", "10001", "00001", "00110", "00100", "00000", "00100")

# ---------------------------------------------------------------- canvas
WHITE = (255, 255, 255)
INK = (17, 24, 39)
NAVY = (15, 42, 68)
NAVY_LIGHT = (27, 63, 96)
RED = (192, 57, 43)
GREY = (107, 114, 128)
LIGHT_GREY = (229, 231, 235)
PALE = (243, 244, 246)


class Canvas:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.pixels = bytearray(b"\xff" * (width * height * 3))

    def _idx(self, x, y):
        return (y * self.width + x) * 3

    def set_pixel(self, x, y, color):
        if 0 <= x < self.width and 0 <= y < self.height:
            i = self._idx(x, y)
            self.pixels[i] = color[0]
            self.pixels[i + 1] = color[1]
            self.pixels[i + 2] = color[2]

    def fill_rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.width, x + w)
        y1 = min(self.height, y + h)
        for yy in range(y0, y1):
            base = (yy * self.width + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.pixels[i] = color[0]
                self.pixels[i + 1] = color[1]
                self.pixels[i + 2] = color[2]

    def hline(self, x, y, w, color, thickness=1):
        self.fill_rect(x, y, w, thickness, color)

    def text_width(self, text, scale):
        # 5 px glyph + 1 px gap, per character.
        return len(text) * 6 * scale - scale if text else 0

    def draw_text(self, x, y, text, scale, color):
        cx = x
        for ch in text:
            glyph = FONT.get(ch, FALLBACK)
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits[col] == "1":
                        self.fill_rect(
                            cx + col * scale, y + row * scale,
                            scale, scale, color,
                        )
            cx += 6 * scale
        return cx

    def draw_text_centered(self, x, y, width, text, scale, color):
        w = self.text_width(text, scale)
        return self.draw_text(x + (width - w) // 2, y, text, scale, color)


def wrap_text(canvas, text, scale, max_width):
    """Greedy word wrap. Returns a list of lines that fit max_width."""
    words = text.split(" ")
    lines = []
    current = ""
    for word in words:
        trial = word if not current else current + " " + word
        if canvas.text_width(trial, scale) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            # A single word too long: split it by characters.
            while canvas.text_width(word, scale) > max_width:
                cut = max_width // (6 * scale)
                lines.append(word[:cut])
                word = word[cut:]
            current = word
    if current:
        lines.append(current)
    return lines


# ---------------------------------------------------------------- PNG
def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def encode_png(canvas):
    ihdr = struct.pack(">IIBBBBB", canvas.width, canvas.height, 8, 2, 0, 0, 0)
    raw = bytearray()
    stride = canvas.width * 3
    for y in range(canvas.height):
        raw.append(0)  # filter: none
        start = y * stride
        raw += canvas.pixels[start:start + stride]
    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", ihdr)
    png += _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += _chunk(b"IEND", b"")
    return png


# ---------------------------------------------------------------- content
# Seven stories, all reported on Monday 23 November 2026. Headlines are
# short enough for one line at scale 3; summaries are one or two lines
# at scale 2. Wording is kept factual: no speculation, no invented
# quotes, no casualty or share figures beyond what was reported.
STORIES = [
    {
        "tag": "CLIMATE  |  TURKEY",
        "headline": "COP31 ends with no climate deal",
        "summary": (
            "The UN summit in Antalya closed after a record two days of "
            "overtime, with no new pact on fossil fuels or finance."
        ),
    },
    {
        "tag": "UKRAINE  |  EUROPE",
        "headline": "Russian strike on Dymer kills 11",
        "summary": (
            "Kyiv region declared 23 November a day of mourning after the "
            "attack on a five-storey block; rescuers pulled a child out alive."
        ),
    },
    {
        "tag": "MIDDLE EAST  |  IRAN",
        "headline": "Iran war: Trump says deal not yet acceptable",
        "summary": (
            "The US president said Iran wants a deal to end hostilities, "
            "but not one acceptable to him, as Bahrain reported an Iranian "
            "attack on Saturday."
        ),
    },
    {
        "tag": "BUSINESS  |  TECH",
        "headline": "Nvidia brings back Jensen Huang as CEO",
        "summary": (
            "Nvidia said on Monday it was reinstating Huang with immediate "
            "effect; shares surged more than 31% in premarket trading."
        ),
    },
    {
        "tag": "USA  |  POLITICS",
        "headline": "Democrats clinch 258-seat House majority",
        "summary": (
            "A North Carolina recount confirmed Chuck Hubbard's win, giving "
            "Democrats their largest House majority since 1992."
        ),
    },
    {
        "tag": "ASIA  |  INDONESIA",
        "headline": "Three dead, 36 missing in factory fire",
        "summary": (
            "A fire at a candy factory in Serang, Banten, killed three "
            "workers; rescuers were still searching for 36 people."
        ),
    },
    {
        "tag": "ASIA  |  SOUTH KOREA",
        "headline": "South Korea minister quits over AI cheating row",
        "summary": (
            "The education minister resigned days before the Suneung college "
            "entrance exam after AI-cheating rules caused an uproar."
        ),
    },
]


def render():
    c = Canvas(WIDTH, HEIGHT)
    margin = 36
    content_w = WIDTH - 2 * margin

    # --- masthead ------------------------------------------------------
    c.fill_rect(0, 0, WIDTH, 128, NAVY)
    c.fill_rect(0, 128, WIDTH, 6, RED)
    c.draw_text(margin, 18, "THE WORLD IN ONE PAGE", 2, (255, 255, 255))
    c.draw_text(margin, 48, "23 NOVEMBER 2026", 6, (255, 255, 255))
    # Right-hand masthead block: day + story count.
    rx = WIDTH - margin - 150
    c.fill_rect(rx - 18, 20, 2, 88, (255, 255, 255))
    c.draw_text(rx, 24, "MONDAY", 3, (255, 255, 255))
    c.draw_text(rx, 58, "7 STORIES", 3, (255, 255, 255))
    c.draw_text(rx, 88, "ONE PAGE", 2, (200, 210, 220))

    # --- standfirst ----------------------------------------------------
    y = 152
    sub = "Seven stories that shaped the day, from Antalya to Jakarta."
    c.draw_text(margin, y, sub, 2, GREY)
    y += 30
    c.hline(margin, y, content_w, INK, 2)
    y += 14

    # --- stories -------------------------------------------------------
    for i, story in enumerate(STORIES, start=1):
        top = y
        # Number badge.
        c.fill_rect(margin, top, 38, 38, NAVY)
        num = str(i)
        c.draw_text_centered(margin, top + 8, 38, num, 3, (255, 255, 255))
        text_x = margin + 54
        text_w = WIDTH - margin - text_x
        # Tag line.
        c.draw_text(text_x, top + 2, story["tag"], 2, RED)
        # Headline (one line by construction; wrap defensively).
        head_lines = wrap_text(c, story["headline"], 3, text_w)
        hy = top + 22
        for line in head_lines:
            c.draw_text(text_x, hy, line, 3, INK)
            hy += 24
        # Summary.
        sum_lines = wrap_text(c, story["summary"], 2, text_w)
        sy = hy + 2
        for line in sum_lines:
            c.draw_text(text_x, sy, line, 2, (55, 65, 81))
            sy += 17
        # Advance: bottom of summary + gap, then a divider.
        y = sy + 12
        if i < len(STORIES):
            c.hline(margin, y, content_w, LIGHT_GREY, 1)
            y += 13

    # --- footer --------------------------------------------------------
    # Keep the footer clear of the last story block.
    footer_y = HEIGHT - 30
    c.hline(margin, footer_y - 12, content_w, INK, 2)
    c.draw_text(
        margin, footer_y,
        "Sources: Reuters, Just Security, Dawn - 23 Nov 2026",
        2, GREY,
    )
    return c


def main():
    # Only this one output-directory variable is read. No other
    # environment data is read, printed, or embedded in the image.
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    os.makedirs(out_dir, exist_ok=True)
    canvas = render()
    data = encode_png(canvas)
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(data)
    print("wrote %s (%d bytes, %dx%d)" % (path, len(data), WIDTH, HEIGHT))


if __name__ == "__main__":
    main()
