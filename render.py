#!/usr/bin/env python3
"""Render the front page for Thursday 26 November 2026.

Draws a newspaper front page with Pillow: masthead, one lead story with
a drawn illustration, six news panels, a ticker of further items and a
sources footer. All text is baked into the script; the output is a
deterministic 1024x1024 PNG.
"""

import sys
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (250, 246, 236)
INK = (24, 24, 24)
NAVY = (15, 36, 64)
GOLD = (212, 175, 88)
RED = (178, 34, 34)
GREY = (96, 96, 96)
LINE = (180, 172, 158)

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap returning a list of lines that fit max_w."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_para(draw, x, y, text, fnt, max_w, leading, color=INK, max_lines=None):
    lines = wrap(draw, text, fnt, max_w)
    if max_lines is not None:
        lines = lines[:max_lines]
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=color)
        y += leading
    return y


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- Masthead: 0-122 -------------------------------------------------
    d.rectangle([0, 0, W, 116], fill=NAVY)
    title_f = font(SERIF_B, 62)
    title = "THE WORLD IN ONE PAGE"
    tw = d.textlength(title, font=title_f)
    d.text(((W - tw) / 2, 12), title, font=title_f, fill=(255, 255, 255))
    date_f = font(SANS_B, 24)
    date = "THURSDAY  26  NOVEMBER  2026"
    dw = d.textlength(date, font=date_f)
    d.text(((W - dw) / 2, 78), date, font=date_f, fill=GOLD)
    d.rectangle([0, 116, W, 122], fill=RED)

    # ---- Lead story: 130-420 ---------------------------------------------
    lead_top = 130
    lx, lw = 36, 552
    kick_f = font(SANS_B, 19)
    d.text((lx, lead_top), "WAR  ·  UKRAINE", font=kick_f, fill=RED)
    head_f = font(SERIF_B, 46)
    y = draw_para(d, lx, lead_top + 30,
                  "Russia's own count puts Ukraine war dead near 500,000",
                  head_f, lw, 54, max_lines=3)
    deck_f = font(SANS, 20)
    draw_para(d, lx, y + 8,
              "Moscow's own tally, reported on Thursday, counts almost half a "
              "million of its people lost in the war.",
              deck_f, lw, 27, max_lines=3)

    # Lead illustration: a quiet field of memorial crosses at dusk.
    ix, iy, iw, ih = 612, 130, 376, 256
    for i in range(ih):
        t = i / ih
        r = int(38 + (120 - 38) * t)
        g = int(48 + (70 - 48) * t)
        b = int(70 + (96 - 70) * t)
        d.line([(ix, iy + i), (ix + iw, iy + i)], fill=(r, g, b))
    d.ellipse([ix + 288, iy + 26, ix + 336, iy + 74], fill=(226, 190, 110))
    d.rectangle([ix, iy + 196, ix + iw, iy + ih], fill=(28, 34, 46))
    for row, (cy, s, col) in enumerate([(iy + 206, 26, (210, 208, 198)),
                                        (iy + 228, 18, (180, 178, 168)),
                                        (iy + 246, 12, (150, 148, 138))]):
        n = 9 - row * 2
        step = iw / n
        for k in range(n):
            cx = ix + step * k + step / 2
            d.rectangle([cx - 1.5, cy - s, cx + 1.5, cy], fill=col)
            d.rectangle([cx - s * 0.35, cy - s * 0.72, cx + s * 0.35, cy - s * 0.52],
                        fill=col)
    d.rectangle([ix, iy + ih, ix + iw, iy + ih + 34], fill=(20, 20, 20))
    cap_f = font(SANS_B, 14)
    d.text((ix + 10, iy + ih + 9), "A WAR IN ITS FOURTH YEAR", font=cap_f,
           fill=(255, 255, 255))

    # ---- Panels: six stories, 2 cols x 3 rows, 432-864 -------------------
    panels = [
        ("MARKETS  ·  SEOUL",
         "Bank of Korea lifts rate to 3.25%",
         "South Korea's central bank raised its benchmark rate a quarter "
         "point, citing an AI-led export boom."),
        ("SPACE  ·  BEIJING",
         "Pakistan's first astronaut heads for China's station",
         "Muhammad Zeeshan Ali is set to become the first foreign astronaut "
         "aboard China's Tiangong station."),
        ("ECONOMY  ·  DHAKA",
         "Bangladesh lifts garment pay by 36%",
         "Dhaka raised the minimum wage for entry-level garment workers by "
         "more than a third."),
        ("DIPLOMACY  ·  PYONGYANG",
         "North Korea expels Swiss diplomat",
         "Pyongyang ordered Switzerland to close its newly opened office in "
         "a row over sanctions."),
        ("CRIME  ·  COLOMBIA",
         "Police free 20 supermarket hostages",
         "Colombian police stormed a supermarket and freed 20 people held "
         "hostage for 17 hours."),
        ("SCIENCE  ·  SPACE",
         "Hera shows crater of asteroid-defence test",
         "Europe's Hera spacecraft revealed close-ups of the crater left by "
         "the asteroid-defence test."),
    ]
    px0, py0 = 36, 432
    pw, ph = 470, 136
    gx, gy = 16, 12
    pk_f = font(SANS_B, 15)
    ph_f = font(SERIF_B, 23)
    pb_f = font(SANS, 15)
    for i, (kick, head, body) in enumerate(panels):
        col, row = i % 2, i // 2
        x = px0 + col * (pw + gx)
        y0 = py0 + row * (ph + gy)
        d.rectangle([x, y0, x + pw, y0 + ph], outline=LINE, width=1)
        d.rectangle([x, y0, x + 5, y0 + ph], fill=RED)
        d.text((x + 16, y0 + 8), kick, font=pk_f, fill=RED)
        y = draw_para(d, x + 16, y0 + 28, head, ph_f, pw - 32, 27, max_lines=2)
        draw_para(d, x + 16, y + 4, body, pb_f, pw - 32, 19, max_lines=2)

    # ---- Ticker: ALSO TODAY, 874-974 --------------------------------------
    ty0 = 874
    d.rectangle([0, ty0, W, 974], fill=NAVY)
    tick_f = font(SANS_B, 18)
    d.text((36, ty0 + 8), "ALSO TODAY", font=tick_f, fill=GOLD)
    d.line([(36, ty0 + 34), (988, ty0 + 34)], fill=(90, 110, 140), width=1)
    left_items = [
        "US markets shut for Thanksgiving",
        "India marks Constitution Day; Rs 15,000-crore Nepal aid",
        "Ghana unveils new Heritage Series banknotes",
    ]
    right_items = [
        "Kenya discharges last Ebola patient; DRC toll tops 5,300",
        "IPL 2027 auction draws 1,220 players",
        "Gukesh faces Sindarov in the World Chess Championship",
    ]
    tf = font(SANS, 15)
    for col, items in enumerate((left_items, right_items)):
        x = 52 if col == 0 else 528
        y = ty0 + 42
        for item in items:
            d.text((x, y), "\u2022", font=tf, fill=GOLD)
            draw_para(d, x + 16, y, item, tf, 440, 19,
                      color=(235, 235, 235), max_lines=1)
            y += 19

    # ---- Footer: 980-1020 -------------------------------------------------
    ff = font(SANS, 14)
    foot = "Sources: Reuters  ·  BBC  ·  AP  ·  AFP  ·  EUR Radio  ·  C54 News"
    fw = d.textlength(foot, font=ff)
    d.text(((W - fw) / 2, 982), foot, font=ff, fill=GREY)
    foot2 = "All events of Thursday 26 November 2026"
    fw2 = d.textlength(foot2, font=ff)
    d.text(((W - fw2) / 2, 1002), foot2, font=ff, fill=GREY)

    out = sys.argv[1] if len(sys.argv) > 1 else "entry.png"
    img.save(out, "PNG", optimize=True)
    print("wrote", out, img.size)


if __name__ == "__main__":
    main()
