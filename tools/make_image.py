#!/usr/bin/env python3
"""Draw a classic newspaper front page for Friday 20 November 2026.

Everything on the poster is drawn in code with PIL; no network access,
no downloaded images or fonts. Output is deterministic: the same input
always produces the same bytes.
"""

import hashlib
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

W, H = 1024, 1024
PAPER = (247, 242, 231)      # aged newsprint
INK = (18, 18, 18)           # near-black ink
RED = (139, 26, 26)          # deep headline red, used sparingly
GREY = (90, 86, 78)          # secondary ink
GREEN = (31, 94, 52)         # market-up green
RULE = (60, 58, 52)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_width):
    """Greedy word wrap; returns a list of lines that fit max_width."""
    lines, line = [], ""
    for word in text.split():
        trial = (line + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_width:
            line = trial
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def draw_lines(draw, lines, fnt, x, y, fill, leading, align="left", width=None):
    """Draw wrapped lines; returns the y just below the last line."""
    for line in lines:
        if align == "center":
            lx = x + (width - draw.textlength(line, font=fnt)) / 2
        else:
            lx = x
        draw.text((lx, y), line, font=fnt, fill=fill)
        y += leading
    return y


def rule(draw, x0, y, x1, width=1, fill=RULE):
    draw.line([(x0, y), (x1, y)], fill=fill, width=width)


def draw_skyline(draw, x, y, w, h):
    """Stylised night skyline with missile streaks (Kyiv story art)."""
    # dusk sky block
    draw.rectangle([x, y, x + w, y + h], fill=(38, 40, 52))
    # stars
    for sx, sy in [(0.12, 0.18), (0.30, 0.10), (0.52, 0.22), (0.68, 0.08),
                   (0.85, 0.16), (0.44, 0.06), (0.94, 0.30), (0.22, 0.32)]:
        draw.ellipse([x + w * sx - 1, y + h * sy - 1,
                      x + w * sx + 1, y + h * sy + 1], fill=PAPER)
    # buildings, back row lighter, front row darker
    back = [(0.00, 0.55), (0.14, 0.42), (0.28, 0.60), (0.42, 0.38),
            (0.56, 0.52), (0.70, 0.44), (0.84, 0.58)]
    for bx, bh in back:
        draw.rectangle([x + w * bx, y + h * bh, x + w * bx + w * 0.13,
                        y + h], fill=(74, 76, 92))
    front = [(0.06, 0.72), (0.24, 0.62), (0.40, 0.78), (0.58, 0.66),
             (0.76, 0.74), (0.90, 0.64)]
    for bx, bh in front:
        draw.rectangle([x + w * bx, y + h * bh, x + w * bx + w * 0.11,
                        y + h], fill=(16, 16, 22))
    # lit windows
    for wx, wy in [(0.10, 0.78), (0.27, 0.68), (0.44, 0.84), (0.61, 0.72),
                   (0.80, 0.80), (0.93, 0.70), (0.33, 0.86), (0.67, 0.88)]:
        draw.rectangle([x + w * wx, y + h * wy, x + w * wx + 4,
                        y + h * wy + 5], fill=(232, 196, 110))
    # missile streaks
    for sx0, sy0, sx1, sy1 in [(0.18, 0.05, 0.34, 0.34),
                               (0.55, 0.02, 0.68, 0.26),
                               (0.82, 0.10, 0.92, 0.30)]:
        draw.line([(x + w * sx0, y + h * sy0), (x + w * sx1, y + h * sy1)],
                  fill=(232, 196, 110), width=2)
        draw.ellipse([x + w * sx1 - 3, y + h * sy1 - 3,
                      x + w * sx1 + 3, y + h * sy1 + 3],
                     fill=(240, 120, 60))
    draw.rectangle([x, y, x + w, y + h], outline=INK, width=1)


def draw_bars(draw, x, y, w, h):
    """Mini market chart: Anthropic +17%, S&P 500 -2%, Nikkei -4.8%."""
    draw.rectangle([x, y, x + w, y + h], outline=INK, width=1)
    base = y + h * 0.45
    draw.line([(x + 8, base), (x + w - 8, base)], fill=INK, width=1)
    data = [("ANTHROPIC", "+17%", 17.0, GREEN),
            ("S&P 500", "-2%", -2.0, RED),
            ("NIKKEI", "-4.8%", -4.8, RED)]
    slot = w / 3
    for i, (label, pct, value, colour) in enumerate(data):
        cx = x + slot * i + slot / 2
        bar_w = 34
        top = base - (value / 17.0) * (h * 0.32)
        if value >= 0:
            draw.rectangle([cx - bar_w / 2, top, cx + bar_w / 2, base],
                           fill=colour)
            pf = font(SANS_BOLD, 14)
            tw = draw.textlength(pct, font=pf)
            draw.text((cx - tw / 2, top + (base - top) / 2 - 8),
                      pct, font=pf, fill=PAPER)
        else:
            draw.rectangle([cx - bar_w / 2, base, cx + bar_w / 2, top],
                           fill=colour)
            pf = font(SANS_BOLD, 14)
            tw = draw.textlength(pct, font=pf)
            draw.text((cx - tw / 2, top + 5), pct, font=pf, fill=colour)
        lf = font(SANS, 12)
        tw = draw.textlength(label, font=lf)
        draw.text((cx - tw / 2, y + h - 18), label, font=lf, fill=INK)


def draw_numbers_box(draw, x, y, w):
    """'The day in numbers' box: figures already in the stories."""
    rows = [("+17%", "Anthropic's first-day gain"),
            ("8", "killed in the Kyiv strikes"),
            ("4.8%", "Nikkei's fall on the day")]
    tf = font(SANS_BOLD, 13)
    vf = font(SERIF_BOLD, 16)
    lf = font(SERIF, 15)
    box_h = 30 + len(rows) * 24 + 10
    draw.rectangle([x, y, x + w, y + box_h], outline=INK, width=1)
    d_title = "THE DAY IN NUMBERS"
    draw.text((x + 10, y + 8), d_title, font=tf, fill=RED)
    ry = y + 32
    for value, label in rows:
        draw.text((x + 10, ry), value, font=vf, fill=INK)
        draw.text((x + 72, ry + 1), label, font=lf, fill=INK)
        ry += 24
    return y + box_h


def story(draw, x, y, w, kicker, headline, body, hsize=25):
    """One column story: kicker, headline, body. Returns y below it."""
    kf = font(SANS_BOLD, 13)
    draw.text((x, y), kicker, font=kf, fill=RED)
    y += 22
    hf = font(SERIF_BOLD, hsize)
    lines = wrap(draw, headline, hf, w)
    y = draw_lines(draw, lines, hf, x, y, INK, hsize + 6)
    y += 6
    bf = font(SERIF, 15)
    lines = wrap(draw, body, bf, w)
    y = draw_lines(draw, lines, bf, x, y, INK, 20)
    return y


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    mx = 40                      # side margin
    cw = 298                     # column width
    col_x = [mx, mx + cw + 24, mx + 2 * (cw + 24)]

    # ---- masthead ----
    rule(d, mx, 26, W - mx, 2)
    rule(d, mx, 32, W - mx, 1)
    mf = font(SERIF_BOLD, 76)
    title = "THE WORLD HERALD"
    tw = d.textlength(title, font=mf)
    d.text(((W - tw) / 2, 44), title, font=mf, fill=INK)
    df = font(SANS, 16)
    left = "EST. 1912  ·  VOL. CXII  ·  No. 324"
    right = "FRIDAY EDITION"
    d.text((mx, 136), left, font=df, fill=GREY)
    tw = d.textlength(right, font=df)
    d.text((W - mx - tw, 136), right, font=df, fill=GREY)
    date = "Friday, 20 November 2026"
    df2 = font(SERIF_BOLD, 19)
    tw = d.textlength(date, font=df2)
    d.text(((W - tw) / 2, 133), date, font=df2, fill=INK)
    rule(d, mx, 162, W - mx, 4)
    rule(d, mx, 170, W - mx, 1)

    # ---- lead story ----
    kf = font(SANS_BOLD, 19)
    kicker = "S H E N Z H E N   S U M M I T"
    tw = d.textlength(kicker, font=kf)
    d.text(((W - tw) / 2, 188), kicker, font=kf, fill=RED)
    hf = font(SERIF_BOLD, 54)
    head = "TRUMP, XI AND PUTIN HOLD FIRST THREE-WAY SUMMIT"
    lines = wrap(d, head, hf, W - 2 * mx)
    y = draw_lines(d, lines, hf, mx, 220, INK, 62, align="center",
                   width=W - 2 * mx)
    deck = ("Leaders sign a joint peace declaration and pledge further "
            "talks to reduce nuclear risks.")
    df3 = font(SERIF, 23)
    lines = wrap(d, deck, df3, W - 2 * mx - 60)
    y = draw_lines(d, lines, df3, mx + 30, y + 8, INK, 30,
                   align="center", width=W - 2 * mx - 60)
    rule(d, mx, y + 12, W - mx, 2)
    rule(d, mx, y + 17, W - mx, 1)

    top = y + 30

    # ---- column rules ----
    for gx in (mx + cw + 12, mx + 2 * cw + 36):
        d.line([(gx, top), (gx, 968)], fill=RULE, width=1)

    # ---- column 1: ICJ, then Senate ----
    y1 = story(d, col_x[0], top, cw, "THE HAGUE",
               "WORLD COURT RULES MYANMAR COMMITTED GENOCIDE",
               "The International Court of Justice finds Myanmar "
               "committed genocide against the Rohingya — the first "
               "such ruling against a state.")
    rule(d, col_x[0], y1 + 12, col_x[0] + cw, 1)
    y1 = story(d, col_x[0], y1 + 26, cw, "WASHINGTON",
               "SENATE PASSES ENERGY AND DATA-CENTRE BILL",
               "A bipartisan bill to speed up energy projects clears "
               "the U.S. Senate, aiming to power the data-centre boom.")

    # ---- column 2: Kyiv attack + skyline art ----
    y2 = story(d, col_x[1], top, cw, "KYIV",
               "KYIV HIT HOURS AFTER PEACE DECLARATION",
               "Russia launches a major overnight missile and drone "
               "attack on Kyiv; eight killed and power facilities hit.")
    draw_skyline(d, col_x[1], y2 + 16, cw, 150)
    cf = font(SANS, 12)
    cap = "KYIV UNDER FIRE OVERNIGHT"
    tw = d.textlength(cap, font=cf)
    d.text((col_x[1] + (cw - tw) / 2, y2 + 172), cap, font=cf, fill=GREY)
    draw_numbers_box(d, col_x[1], y2 + 196, cw)

    # ---- column 3: Anthropic + chart, then Riyadh ----
    y3 = story(d, col_x[2], top, cw, "WALL STREET",
               "ANTHROPIC SOARS ON RECORD NASDAQ DEBUT",
               "Shares close near $97, 17% above the $83 offer price, "
               "even as AI stocks sell off; the S&P 500 falls about "
               "2% and the Nikkei 4.8%.")
    draw_bars(d, col_x[2], y3 + 10, cw, 110)
    y3b = y3 + 10 + 110 + 12
    rule(d, col_x[2], y3b - 4, col_x[2] + cw, 1)
    y3 = story(d, col_x[2], y3b + 8, cw, "RIYADH",
               "HOUTHI MISSILE DAMAGES RIYADH'S TALLEST TOWER",
               "A missile damages the Saudi PIF tower, the tallest in "
               "Riyadh, in the capital's financial district.")

    # ---- footer ----
    rule(d, mx, 978, W - mx, 2)
    ff = font(SANS, 13)
    foot = "THE WORLD HERALD  ·  FRIDAY, 20 NOVEMBER 2026  ·  SIX STORIES THAT SHAPED THE DAY"
    tw = d.textlength(foot, font=ff)
    d.text(((W - tw) / 2, 990), foot, font=ff, fill=GREY)

    out = os.path.join(ROOT, "entry.png")
    img.save(out, "PNG")
    data = open(out, "rb").read()
    print("entry.png: %d bytes  sha256=%s" %
          (len(data), hashlib.sha256(data).hexdigest()))


if __name__ == "__main__":
    main()
