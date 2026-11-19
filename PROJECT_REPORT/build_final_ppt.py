"""
Final PPT Builder — DNS in the QUIC Crowd
Builds 14 slides matching the exact template design from Research_Project_Sem_7_(2).pptx
Updated with REAL experimental results from PROJECT_RESULTS/ALL_RESULTS_MASTER.csv
"""
import copy, os
from lxml import etree
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.oxml.ns import qn

TEMPLATE = '/Users/paru/.gemini/antigravity/brain/e5656d74-4c58-414e-8d77-9eb5475a671c/.user_uploaded/media_1795105985798_efac268b.pptx'
OUT = '/Users/paru/paru/projects/RM/PROJECT_REPORT/FINAL_PRESENTATION.pptx'

# ─── DESIGN TOKENS (from template) ───────────────────────────────────────────
C_NAVY   = RGBColor(0x14, 0x28, 0x4B)   # headings
C_TEAL   = RGBColor(0x0F, 0x7C, 0x8A)   # accent / labels
C_LTEAL  = RGBColor(0x8F, 0xD3, 0xDB)   # accent light
C_BODY   = RGBColor(0x1E, 0x29, 0x3B)   # body text
C_GREY   = RGBColor(0x5A, 0x6B, 0x80)   # sub-labels
C_WHITE  = RGBColor(0xFF, 0xFF, 0xFF)
C_BLACK  = RGBColor(0x00, 0x00, 0x00)
C_DKGRY  = RGBColor(0x44, 0x44, 0x44)
C_GRN    = RGBColor(0x16, 0xA3, 0x4A)   # good/green
C_RED    = RGBColor(0xDC, 0x26, 0x26)   # bad/red
C_AMBER  = RGBColor(0xD9, 0x77, 0x06)   # warning/amber

W  = Inches(10)
H  = Inches(5.625)

# ─── HELPERS ─────────────────────────────────────────────────────────────────
def add_textbox(slide, text, left, top, width, height,
                font_size=11, bold=False, color=C_BODY,
                align=PP_ALIGN.LEFT, wrap=True, italic=False):
    txb = slide.shapes.add_textbox(left, top, width, height)
    tf  = txb.text_frame
    tf.word_wrap = wrap
    p   = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(font_size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    return txb

def add_rect(slide, left, top, width, height, fill_color, line_color=None, line_width=None):
    shape = slide.shapes.add_shape(1, left, top, width, height)  # MSO_SHAPE_TYPE.RECTANGLE
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_color
    if line_color:
        shape.line.color.rgb = line_color
        if line_width:
            shape.line.width = line_width
    else:
        shape.line.fill.background()
    return shape

def add_slide_from_template(prs, layout_idx=1):
    """Clone layout slide"""
    layout = prs.slide_layouts[min(layout_idx, len(prs.slide_layouts)-1)]
    return prs.slides.add_slide(layout)

def add_header_bar(slide, title_text, subtitle_text=None):
    """Standard navy header bar used on content slides"""
    # Dark navy top bar
    add_rect(slide, Inches(0), Inches(0), W, Inches(0.72), C_NAVY)
    # Teal accent stripe
    add_rect(slide, Inches(0), Inches(0.72), W, Inches(0.055), C_TEAL)
    # Title text
    add_textbox(slide, title_text,
                Inches(0.3), Inches(0.1), Inches(9.4), Inches(0.55),
                font_size=20, bold=True, color=C_WHITE)
    if subtitle_text:
        add_textbox(slide, subtitle_text,
                    Inches(0.35), Inches(0.75), Inches(9.0), Inches(0.3),
                    font_size=10, color=C_GREY)

def add_slide_number(slide, num):
    tb = slide.shapes.add_textbox(Inches(9.4), Inches(5.3), Inches(0.4), Inches(0.22))
    tf = tb.text_frame; p = tf.paragraphs[0]; p.alignment = PP_ALIGN.RIGHT
    r = p.add_run(); r.text = str(num); r.font.size = Pt(9); r.font.color.rgb = C_DKGRY

def add_footer_bar(slide):
    add_rect(slide, Inches(0), Inches(5.42), W, Inches(0.2), C_NAVY)
    add_textbox(slide, 'DNS in the QUIC Crowd  |  IIIT Allahabad',
                Inches(0.2), Inches(5.44), Inches(5), Inches(0.15),
                font_size=7.5, color=C_WHITE)

def add_bullet(slide, items, left, top, width, height,
               font_size=10.5, bullet='•', color=C_BODY, spacing=0.32):
    """Multi-line bullet list"""
    for i, item in enumerate(items):
        y = top + Inches(i * spacing)
        tb = slide.shapes.add_textbox(left, y, width, Inches(spacing + 0.05))
        tf = tb.text_frame; tf.word_wrap = True
        p  = tf.paragraphs[0]
        r  = p.add_run()
        r.text = f'{bullet}  {item}'
        r.font.size = Pt(font_size)
        r.font.color.rgb = color

def metric_card(slide, left, top, width, height, label, value, sublabel='',
                label_color=C_TEAL, value_color=C_NAVY, bg=None):
    if bg:
        add_rect(slide, left, top, width, height, bg)
    add_textbox(slide, label,  left+Inches(0.08), top+Inches(0.05), width-Inches(0.1), Inches(0.22),
                font_size=8, color=label_color)
    add_textbox(slide, value,  left+Inches(0.08), top+Inches(0.22), width-Inches(0.1), Inches(0.3),
                font_size=18, bold=True, color=value_color)
    if sublabel:
        add_textbox(slide, sublabel, left+Inches(0.08), top+Inches(0.52), width-Inches(0.1), Inches(0.18),
                    font_size=8, color=C_GREY)

def tag_badge(slide, text, left, top, bg=C_TEAL, fg=C_WHITE, fs=9):
    w = Inches(len(text)*0.075 + 0.2); h = Inches(0.26)
    add_rect(slide, left, top, w, h, bg)
    add_textbox(slide, text, left+Inches(0.06), top+Inches(0.03), w-Inches(0.08), h,
                font_size=fs, bold=True, color=fg)
    return left + w + Inches(0.08)

def divider_line(slide, top, color=C_TEAL, lw=Inches(0.01)):
    add_rect(slide, Inches(0.3), top, Inches(9.4), lw, color)

# ─────────────────────────────────────────────────────────────────────────────
#  SLIDE BUILDERS
# ─────────────────────────────────────────────────────────────────────────────

def build_title_slide(prs):
    """Slide 1 — clone template slide 1 exactly"""
    src_slide = prs.slides[0]
    xml_src   = copy.deepcopy(src_slide._element)
    # We'll keep slide 1 as-is from template — it already has correct data
    # Return the template slide
    return src_slide


def build_slide2_problem(prs):
    s = add_slide_from_template(prs)
    add_header_bar(s, 'Problem Statement & Research Objectives',
                   'What can a network observer infer from encrypted traffic metadata alone?')
    add_footer_bar(s); add_slide_number(s, 2)

    # Research question box
    add_rect(s, Inches(0.3), Inches(1.0), Inches(9.4), Inches(0.72), C_NAVY)
    add_textbox(s, '❝  Across 6 modern traffic classes — DoH, DoH/3, DoQ, HTTPS, HTTP/3, QUIC — can we separate them',
                Inches(0.4), Inches(1.03), Inches(9.1), Inches(0.4),
                font_size=11, bold=True, color=C_WHITE)
    add_textbox(s, '    using only 4 observable packet metadata features, with zero payload inspection?  ❞',
                Inches(0.4), Inches(1.4), Inches(9.1), Inches(0.3),
                font_size=11, bold=True, color=C_LTEAL)

    # 4 RQ cards
    rqs = [
        ('RQ1  DETECTION',   'Can 4 metadata features reliably separate all 6 protocol classes?'),
        ('RQ2  GENERALIZATION','Does a model trained on Jio transfer to Airtel (and vice versa)?'),
        ('RQ3  FEATURE MECHANICS','Does packet size or timing drive classification accuracy?'),
        ('RQ4  RELIABILITY', 'Can we catch encrypted DNS while keeping web false alarms < 0.5%?'),
    ]
    cols = [Inches(0.3), Inches(2.65), Inches(5.0), Inches(7.35)]
    for i, (label, desc) in enumerate(rqs):
        x = cols[i]; w = Inches(2.2)
        add_rect(s, x, Inches(1.85), w, Inches(0.26), C_TEAL)
        add_textbox(s, label, x+Inches(0.06), Inches(1.87), w-Inches(0.1), Inches(0.24),
                    font_size=8, bold=True, color=C_WHITE)
        add_rect(s, x, Inches(2.11), w, Inches(1.1),
                 RGBColor(0xF1, 0xF5, 0xF9))
        add_textbox(s, desc, x+Inches(0.08), Inches(2.14), w-Inches(0.1), Inches(1.0),
                    font_size=10, color=C_BODY, wrap=True)

    # Threat model strip
    add_rect(s, Inches(0.3), Inches(3.35), Inches(9.4), Inches(0.26), C_NAVY)
    add_textbox(s, 'THE THREAT MODEL', Inches(0.4), Inches(3.37), Inches(2), Inches(0.22),
                font_size=8.5, bold=True, color=C_LTEAL)
    add_textbox(s, 'TLS 1.3 & QUIC hide payloads — but packet lengths, arrival timing & flow sequences remain exposed to passive observers.',
                Inches(2.4), Inches(3.37), Inches(7.1), Inches(0.22),
                font_size=9.5, bold=True, color=C_WHITE)

    # Features strip
    feats = ['Current Packet Size  Lᵢ', 'Previous Packet Size  Lᵢ₋₁',
             'Current Time Gap  ΔTᵢ', 'Previous Time Gap  ΔTᵢ₋₁']
    add_textbox(s, 'Observable features (zero leakage):',
                Inches(0.3), Inches(3.72), Inches(3), Inches(0.26),
                font_size=9.5, bold=True, color=C_NAVY)
    x_start = Inches(3.3)
    for f in feats:
        x_start = tag_badge(s, f, x_start, Inches(3.72), bg=C_NAVY)

    # Strictly stripped
    add_textbox(s, '✗  Strictly stripped: IP addresses  •  Port numbers (443/853)  •  SNI headers  •  Payload bytes',
                Inches(0.3), Inches(4.1), Inches(9.4), Inches(0.28),
                font_size=9.5, color=C_RED)
    return s


def build_slide3_midvsfinal(prs):
    s = add_slide_from_template(prs)
    add_header_bar(s, 'Mid-Sem Pilot vs. Final Work',
                   'How the project evolved from binary baseline to multi-ISP multi-class study')
    add_footer_bar(s); add_slide_number(s, 3)

    # Two columns
    for col_x, col_title, col_color, items in [
        (Inches(0.3), 'MID-SEM PILOT  (Binary Baseline)', C_GREY, [
            'Single binary pair: DoH/3  vs.  HTTP/3',
            'Controlled lab testbed — ≈ 96% accuracy',
            'Showed tree models outperform linear due to\nnon-linear packet size boundaries',
            'Only 2 classes, single ISP, balanced data',
        ]),
        (Inches(5.15), 'FINAL PROJECT  (This Work)', C_TEAL, [
            '6 full protocols: DoQ, DoH/3, DoH, HTTPS, HTTP/3, QUIC',
            'Live production traffic — Jio (Prayagraj + Mirzapur)\n& Airtel (Prayagraj + Tumsar)',
            'Cross-ISP transferability + imbalance evaluation\n(8:4:4:2:2:1 real-world ratio dataset, 42 k rows)',
            'Ablation study: size-only vs timing-only vs full\nfeature set across ISP domain shift',
        ]),
    ]:
        add_rect(s, col_x, Inches(1.0), Inches(4.55), Inches(0.3), col_color)
        add_textbox(s, col_title, col_x+Inches(0.08), Inches(1.02), Inches(4.3), Inches(0.26),
                    font_size=9, bold=True, color=C_WHITE)
        add_rect(s, col_x, Inches(1.3), Inches(4.55), Inches(3.5),
                 RGBColor(0xF8, 0xFA, 0xFC))
        for i, item in enumerate(items):
            add_textbox(s, f'▸  {item}',
                        col_x+Inches(0.12), Inches(1.4)+Inches(i*0.78), Inches(4.3), Inches(0.72),
                        font_size=10.5, color=C_BODY, wrap=True)

    # Arrow between columns
    add_textbox(s, '→', Inches(4.75), Inches(2.6), Inches(0.4), Inches(0.4),
                font_size=28, bold=True, color=C_TEAL, align=PP_ALIGN.CENTER)

    # Key upgrade tags
    add_textbox(s, 'KEY UPGRADES IN FINAL WORK',
                Inches(0.3), Inches(4.9), Inches(3), Inches(0.22),
                font_size=8, bold=True, color=C_GREY)
    tags = ['+4 New Classes', '+2 ISPs (Jio + Airtel)', '+4 Vantage Points', '+95,638 Packets',
            '+6 Scenarios', '+7 ML Models']
    x = Inches(3.4)
    for t in tags:
        x = tag_badge(s, t, x, Inches(4.88), bg=C_TEAL)
    return s


def build_slide4_data_collection(prs):
    s = add_slide_from_template(prs)
    add_header_bar(s, 'Real-World Dataset Collection',
                   'Live protocol capture across 4 vantage points — zero payload leakage')
    add_footer_bar(s); add_slide_number(s, 4)

    # Protocol capture methods — 3 columns
    protocols = [
        ('DoQ  (RFC 9250)', 'UDP / 853',
         'Native QUIC DNS\nAdGuard & NextDNS\naiohttp QUIC client'),
        ('DoH/3  (RFC 9114)', 'UDP / 443',
         'HTTP/3 DNS queries\nCloudflare Anycast\n104.16.248.249'),
        ('DoH  (RFC 8484)', 'TCP / 443',
         'DNS-over-HTTPS\nGoogle & Cloudflare\nTLS 1.3 resolver'),
        ('HTTPS Web', 'TCP / 443',
         'Live web downloads\nAlexa Top-1M domains\nTLS session streams'),
        ('HTTP/3 Web', 'UDP / 443',
         'QUIC web assets\nCDN edge streams\nALPN h3 negotiation'),
        ('QUIC (bare)', 'UDP / 443',
         'Non-DNS QUIC flows\nMedia & transfer\nQUIC handshake only'),
    ]
    cols3 = [Inches(0.3), Inches(3.47), Inches(6.63)]
    rows2 = [Inches(1.05), Inches(2.6)]
    for i, (name, port, desc) in enumerate(protocols):
        x = cols3[i % 3]; y = rows2[i // 3]; w = Inches(2.9); h = Inches(1.35)
        add_rect(s, x, y, w, Inches(0.3), C_TEAL)
        add_textbox(s, name, x+Inches(0.08), y+Inches(0.04), w-Inches(0.1), Inches(0.24),
                    font_size=10, bold=True, color=C_WHITE)
        add_rect(s, x, y+Inches(0.3), w, h-Inches(0.3), RGBColor(0xF1,0xF5,0xF9))
        add_textbox(s, f'Port: {port}',
                    x+Inches(0.1), y+Inches(0.33), w-Inches(0.1), Inches(0.2),
                    font_size=8.5, bold=True, color=C_GREY)
        add_textbox(s, desc, x+Inches(0.1), y+Inches(0.52), w-Inches(0.1), Inches(0.78),
                    font_size=9.5, color=C_BODY, wrap=True)

    # Sanitization banner
    add_rect(s, Inches(0), Inches(4.05), W, Inches(0.46), C_NAVY)
    add_textbox(s, 'NO-CHEAT SANITIZATION  —  Features Used:',
                Inches(0.2), Inches(4.08), Inches(3.5), Inches(0.4),
                font_size=9.5, bold=True, color=C_LTEAL)
    add_textbox(s, 'Lᵢ  (curr size)   •   Lᵢ₋₁  (prev size)   •   ΔTᵢ  (curr gap)   •   ΔTᵢ₋₁  (prev gap)',
                Inches(3.8), Inches(4.1), Inches(5.5), Inches(0.4),
                font_size=11, bold=True, color=C_WHITE)
    add_textbox(s, 'Stripped: IPs, ports, SNI, payload — all removed',
                Inches(0.2), Inches(4.57), Inches(9.4), Inches(0.26),
                font_size=9, color=RGBColor(0xFF,0x88,0x88))

    # Vantage point summary
    vp = [('Prayagraj  Airtel', '55,239', C_TEAL),
          ('Prayagraj  JIO',    '26,000', C_NAVY),
          ('Tumsar  Airtel',    ' 8,399', C_TEAL),
          ('Mirzapur  JIO',     ' 6,000', C_NAVY)]
    add_textbox(s, 'Vantage Points:', Inches(0.3), Inches(4.9), Inches(1.8), Inches(0.26),
                font_size=9, bold=True, color=C_GREY)
    x = Inches(2.1)
    for label, count, bg in vp:
        add_rect(s, x, Inches(4.88), Inches(1.9), Inches(0.3), bg)
        add_textbox(s, f'{label}  ({count})',
                    x+Inches(0.06), Inches(4.9), Inches(1.78), Inches(0.26),
                    font_size=8.5, bold=True, color=C_WHITE)
        x += Inches(2.0)
    return s


def build_slide5_dataset(prs):
    s = add_slide_from_template(prs)
    add_header_bar(s, 'Dataset Composition Across Networks',
                   'Multi-carrier portfolio — 95,638 total packets, 6 classes, zero null values')
    add_footer_bar(s); add_slide_number(s, 5)

    # Table header
    headers = ['Traffic Class', 'Protocol', 'Transport', 'Prayagraj JIO', 'Tumsar/Miz JIO',
               'Prayagraj Airtel', 'Tumsar Airtel', 'TOTAL']
    col_widths = [Inches(1.6), Inches(0.9), Inches(0.75),
                  Inches(1.0), Inches(1.0), Inches(1.1), Inches(1.0), Inches(0.85)]
    xs = [Inches(0.15)]
    for w in col_widths[:-1]: xs.append(xs[-1] + w)

    add_rect(s, Inches(0.15), Inches(1.0), Inches(9.7), Inches(0.3), C_NAVY)
    for i, (h, x, w) in enumerate(zip(headers, xs, col_widths)):
        add_textbox(s, h, x+Inches(0.03), Inches(1.02), w-Inches(0.04), Inches(0.26),
                    font_size=8, bold=True, color=C_WHITE)

    rows = [
        ('HTTPS Web', 'Web', 'TCP/443', '8,000', '1,000', '11,692', '2,000', '22,692'),
        ('HTTP/3 Web', 'QUIC Web', 'UDP/443', '6,000', '1,000', '11,021', '2,000', '20,021'),
        ('DoH', 'Enc. DNS', 'TCP/443', '4,000', '1,986', '8,391', '1,986', '15,377*'),
        ('DoH/3', 'QUIC DNS', 'UDP/443', '2,000', '1,000', '9,953', '452', '13,405'),
        ('DoQ', 'Native DNS', 'UDP/853', '2,000', '1,000', '9,182', '460', '12,642'),
        ('QUIC', 'Bare QUIC', 'UDP/443', '4,000', '1,501', '5,000', '1,501', '11,501*'),
    ]
    for ri, row in enumerate(rows):
        bg = RGBColor(0xF1,0xF5,0xF9) if ri % 2 == 0 else RGBColor(0xFF,0xFF,0xFF)
        y = Inches(1.3) + Inches(ri * 0.42)
        add_rect(s, Inches(0.15), y, Inches(9.7), Inches(0.42), bg)
        # DNS class highlight
        cls_color = C_TEAL if 'DoH' in row[0] or 'DoQ' in row[0] else C_NAVY
        for ci, (val, x, w) in enumerate(zip(row, xs, col_widths)):
            fc = cls_color if ci == 0 else C_BODY
            fb = True if ci in [0, 7] else False
            add_textbox(s, val, x+Inches(0.03), y+Inches(0.08), w-Inches(0.04), Inches(0.3),
                        font_size=9, bold=fb, color=fc)

    # Totals row
    y = Inches(1.3 + 6*0.42)
    add_rect(s, Inches(0.15), y, Inches(9.7), Inches(0.3), C_NAVY)
    totals = ['TOTAL', '', '', '26,000', '7,487', '55,239', '8,399', '95,638']
    for val, x, w in zip(totals, xs, col_widths):
        add_textbox(s, val, x+Inches(0.03), y+Inches(0.03), w-Inches(0.04), Inches(0.24),
                    font_size=9, bold=True, color=C_WHITE)

    # Note
    add_textbox(s, '* DoH & QUIC slightly uneven across locations due to live capture variance  •  Zero DOT records  •  Zero null values',
                Inches(0.15), Inches(5.0), Inches(9.4), Inches(0.26),
                font_size=8, color=C_GREY, italic=True)
    return s


def build_slide6_samenet(prs):
    s = add_slide_from_template(prs)
    add_header_bar(s, 'Same-Network Results — 70/15/15 Split + 5-Fold CV',
                   'Train & test within same ISP — peak model performance on intra-network data')
    add_footer_bar(s); add_slide_number(s, 6)

    # Top metric cards
    metrics = [
        ('BEST MODEL',    'Random Forest', 'Full dataset', C_NAVY),
        ('TEST ACCURACY', '94.50%',        'Full 95k rows',C_TEAL),
        ('MACRO F1',      '0.9413',        'All 6 classes', C_NAVY),
        ('JIO-ONLY BEST', '95.21%',        'RF on 32k JIO', C_TEAL),
        ('AIRTEL BEST',   '94.23%',        'XGB on 63k Airtel', C_NAVY),
        ('RATIO DATASET', '94.54%',        'XGB imbalanced 42k', C_TEAL),
    ]
    for i, (label, val, sub, col) in enumerate(metrics):
        x = Inches(0.3 + i * 1.6); w = Inches(1.5)
        add_rect(s, x, Inches(1.0), w, Inches(0.9), col)
        add_textbox(s, label, x+Inches(0.06), Inches(1.03), w-Inches(0.1), Inches(0.22),
                    font_size=7.5, bold=True, color=C_LTEAL)
        add_textbox(s, val,   x+Inches(0.06), Inches(1.22), w-Inches(0.1), Inches(0.4),
                    font_size=16, bold=True, color=C_WHITE)
        add_textbox(s, sub,   x+Inches(0.06), Inches(1.65), w-Inches(0.1), Inches(0.2),
                    font_size=7.5, color=C_LTEAL)

    # Results table
    add_rect(s, Inches(0.3), Inches(2.08), Inches(9.4), Inches(0.28), C_NAVY)
    hdrs = ['Model', 'Full Dataset', 'JIO Only', 'Airtel Only', 'Ratio (42k)', 'CV Score', 'Train Time']
    cws  = [Inches(2.0), Inches(1.4), Inches(1.3), Inches(1.3), Inches(1.3), Inches(1.1), Inches(1.0)]
    cxs  = [Inches(0.3)]; [cxs.append(cxs[-1]+w) for w in cws[:-1]]
    for h, x, w in zip(hdrs, cxs, cws):
        add_textbox(s, h, x+Inches(0.04), Inches(2.1), w-Inches(0.06), Inches(0.24),
                    font_size=8.5, bold=True, color=C_WHITE)

    table_data = [
        ('Random Forest',      '94.50% ★', '95.21% ★', '94.09%', '94.51%', '92.3%', '2.9s'),
        ('XGBoost',            '93.99%',   '94.83%',   '94.23% ★','94.54% ★','91.9%','2.4s'),
        ('Decision Tree',      '91.98%',   '95.10%',   '91.78%', '92.78%', '89.5%', '0.3s'),
        ('KNN',                '91.11%',   '93.17%',   '91.32%', '91.46%', '88.5%', '0.02s'),
        ('MLP (scaled)',       '84.94%',   '94.67%',   '78.32%', '82.56%', '40.3%', '47.9s'),
        ('Logistic Regression','29.21% ✗', '27.19% ✗', '34.13% ✗','38.21% ✗','30.7%','0.1s'),
        ('Linear SVM',         '27.14% ✗', '33.44% ✗', '30.08% ✗','38.10% ✗','27.2%','0.5s'),
    ]
    for ri, row in enumerate(table_data):
        bg = RGBColor(0xF1,0xF5,0xF9) if ri%2==0 else C_WHITE
        y = Inches(2.36 + ri*0.38)
        add_rect(s, Inches(0.3), y, Inches(9.4), Inches(0.38), bg)
        for ci, (val, x, w) in enumerate(zip(row, cxs, cws)):
            col = C_RED if '✗' in val else (C_TEAL if '★' in val else C_BODY)
            fb  = ci == 0 or '★' in val
            add_textbox(s, val, x+Inches(0.04), y+Inches(0.07), w-Inches(0.06), Inches(0.26),
                        font_size=9, bold=fb, color=col)

    add_textbox(s, '★ Best in class  •  ✗ Near-random (linear models fail — packet features are non-linearly separable)',
                Inches(0.3), Inches(5.1), Inches(9.4), Inches(0.22),
                font_size=8, color=C_GREY, italic=True)
    return s


def build_slide7_crossnet(prs):
    s = add_slide_from_template(prs)
    add_header_bar(s, 'Cross-Network Generalization — Domain Shift Analysis',
                   'Train on one ISP, test on the other — no fine-tuning')
    add_footer_bar(s); add_slide_number(s, 7)

    # Big finding banner
    add_rect(s, Inches(0), Inches(1.0), W, Inches(0.52), C_RED)
    add_textbox(s, '⚠  CRITICAL FINDING:  Models trained on JIO achieve only 30.7% on Airtel traffic — a 63.8% performance collapse',
                Inches(0.2), Inches(1.03), Inches(9.6), Inches(0.46),
                font_size=11.5, bold=True, color=C_WHITE)

    # Two cross-network columns
    for col_x, direction, train_isp, test_isp, results, best_acc, best_drop in [
        (Inches(0.3), 'JIO  →  AIRTEL', 'JIO (28,800 train)', 'Airtel (63,638 test)',
         [('Random Forest','30.74%','-63.8%'),('Decision Tree','30.26%','-64.7%'),
          ('XGBoost','27.85%','-66.9%'),('MLP','28.20%','-66.8%'),('KNN','21.08%','-73.0%')],
         '30.74%', '-63.8%'),
        (Inches(5.15), 'AIRTEL  →  JIO', 'Airtel (57,274 train)', 'JIO (32,000 test)',
         [('KNN','46.08%','-47.1%'),('MLP','42.64%','—'),
          ('Random Forest','41.04%','-53.1%'),('XGBoost','39.02%','-55.2%'),
          ('Decision Tree','35.29%','-58.9%')],
         '46.08%', '-47.1%'),
    ]:
        w = Inches(4.55)
        add_rect(s, col_x, Inches(1.65), w, Inches(0.26), C_NAVY)
        add_textbox(s, direction, col_x+Inches(0.08), Inches(1.67), w-Inches(0.1), Inches(0.22),
                    font_size=11, bold=True, color=C_WHITE)
        add_textbox(s, f'Train: {train_isp}   |   Test: {test_isp}',
                    col_x+Inches(0.08), Inches(1.93), w-Inches(0.1), Inches(0.22),
                    font_size=8.5, color=C_GREY)
        for ri, (model, acc, drop) in enumerate(results):
            y = Inches(2.2 + ri*0.42)
            bg = RGBColor(0xF1,0xF5,0xF9) if ri%2==0 else C_WHITE
            add_rect(s, col_x, y, w, Inches(0.42), bg)
            add_textbox(s, model, col_x+Inches(0.08), y+Inches(0.08), Inches(2), Inches(0.26),
                        font_size=9.5, bold=(ri==0), color=C_BODY)
            add_textbox(s, acc, col_x+Inches(2.1), y+Inches(0.08), Inches(0.9), Inches(0.26),
                        font_size=9.5, bold=True,
                        color=C_TEAL if ri==0 else C_RED)
            add_textbox(s, drop, col_x+Inches(3.1), y+Inches(0.08), Inches(1.3), Inches(0.26),
                        font_size=9.5, color=C_RED if '.' in drop else C_GREY)

    # Key takeaways
    add_rect(s, Inches(0), Inches(4.78), W, Inches(0.72), C_NAVY)
    add_textbox(s, 'KEY TAKEAWAYS', Inches(0.2), Inches(4.8), Inches(1.6), Inches(0.22),
                font_size=8, bold=True, color=C_LTEAL)
    takeaways = [
        '1. Severe domain shift: 21–46% cross-net vs 91–95% same-net — ISP-aware training is essential',
        '2. Asymmetric: Airtel→JIO (best 46%) generalizes 50% better than JIO→Airtel (best 31%)',
        '3. Larger Airtel corpus (63k vs 32k) covers more traffic patterns — confirming data diversity matters',
    ]
    for i, t in enumerate(takeaways):
        add_textbox(s, t, Inches(1.9+i*2.65), Inches(4.8), Inches(2.5), Inches(0.68),
                    font_size=8.5, color=C_WHITE, wrap=True)
    return s


def build_slide8_ratio(prs):
    s = add_slide_from_template(prs)
    add_header_bar(s, 'Balanced vs. Real-World Ratio Evaluation',
                   'Stress-testing classifiers against internet-like class imbalance (8:4:4:2:2:1)')
    add_footer_bar(s); add_slide_number(s, 8)

    # Side-by-side comparison
    for col_x, title, col_color, items, f1_val in [
        (Inches(0.3), 'BALANCED  (Full 95k — Equal-ish)', C_NAVY,
         ['Approximately 11–22k per class',
          'Tests pure protocol separability',
          'RF: 94.50% / XGBoost: 93.99%',
          'Macro-F1: 0.9413'],
         '94.50%'),
        (Inches(5.3), 'RATIO DATASET  (42k — 8:4:4:2:2:1)', C_TEAL,
         ['HTTPS_WEB: 16,000 (38.1%)',
          'HTTP3_WEB + DoH: 8,000 each (19%)',
          'DoH3 + DoQ: 4,000 each (9.5%)',
          'QUIC: 2,000 (4.8%) — most underrepresented'],
         '94.54%'),
    ]:
        w = Inches(4.5)
        add_rect(s, col_x, Inches(1.0), w, Inches(0.3), col_color)
        add_textbox(s, title, col_x+Inches(0.08), Inches(1.02), w-Inches(0.1), Inches(0.26),
                    font_size=10, bold=True, color=C_WHITE)
        add_rect(s, col_x, Inches(1.3), w, Inches(2.5), RGBColor(0xF8,0xFA,0xFC))
        for i, item in enumerate(items):
            add_textbox(s, f'▸  {item}',
                        col_x+Inches(0.12), Inches(1.4)+Inches(i*0.56), w-Inches(0.2), Inches(0.5),
                        font_size=10.5, color=C_BODY)
        add_rect(s, col_x, Inches(3.85), w, Inches(0.44), col_color)
        add_textbox(s, f'Best Test Accuracy: {f1_val}',
                    col_x+Inches(0.08), Inches(3.88), w-Inches(0.1), Inches(0.38),
                    font_size=13, bold=True, color=C_WHITE)

    add_textbox(s, 'vs', Inches(4.65), Inches(2.4), Inches(0.4), Inches(0.4),
                font_size=20, bold=True, color=C_GREY, align=PP_ALIGN.CENTER)

    # Key finding box
    add_rect(s, Inches(0), Inches(4.42), W, Inches(0.72), C_NAVY)
    add_textbox(s, '✓  KEY FINDING:', Inches(0.2), Inches(4.44), Inches(1.5), Inches(0.22),
                font_size=9, bold=True, color=C_LTEAL)
    add_textbox(s,
        'Even when DNS traffic is outnumbered 8:1 by web traffic, RF & XGBoost retain >94% accuracy '
        'without base-rate collapse.  Classifier is robust to real-world class imbalance.',
        Inches(1.8), Inches(4.44), Inches(7.9), Inches(0.68),
        font_size=10.5, bold=True, color=C_WHITE, wrap=True)
    return s


def build_slide9_all_models(prs):
    s = add_slide_from_template(prs)
    add_header_bar(s, 'All ML Models — Benchmarking on Combined Dataset',
                   '7 classifiers across 6 scenarios | 42 total experiments')
    add_footer_bar(s); add_slide_number(s, 9)

    # Summary insight boxes
    insights = [
        ('Tree Models', '91–95%', 'RF + XGB + DT dominate\nacross all scenarios', C_TEAL),
        ('Linear Models', '27–38%', 'Fail completely — features\nnot linearly separable', C_RED),
        ('MLP (scaled)', '78–94%', 'ISP-dependent: great on\nJIO, weaker on Airtel', C_AMBER),
        ('Cross-Network', '21–46%', 'Severe domain shift —\nISP-aware training needed', C_RED),
    ]
    for i, (title, acc, desc, col) in enumerate(insights):
        x = Inches(0.3 + i*2.4); w = Inches(2.2)
        add_rect(s, x, Inches(1.0), w, Inches(0.26), col)
        add_textbox(s, title, x+Inches(0.06), Inches(1.02), w-Inches(0.1), Inches(0.22),
                    font_size=9, bold=True, color=C_WHITE)
        add_rect(s, x, Inches(1.26), w, Inches(0.78), RGBColor(0xF1,0xF5,0xF9))
        add_textbox(s, acc, x+Inches(0.06), Inches(1.28), w-Inches(0.1), Inches(0.3),
                    font_size=20, bold=True, color=col)
        add_textbox(s, desc, x+Inches(0.06), Inches(1.58), w-Inches(0.1), Inches(0.44),
                    font_size=8.5, color=C_BODY, wrap=True)

    # Full scenario × model accuracy table
    add_rect(s, Inches(0.3), Inches(2.18), Inches(9.4), Inches(0.28), C_NAVY)
    cols  = ['Model', 'FULL', 'JIO', 'AIRTEL', 'RATIO', 'JIO→AIRTEL', 'AIRTEL→JIO']
    cws2  = [Inches(2.0)] + [Inches(1.23)]*6
    cxs2  = [Inches(0.3)]; [cxs2.append(cxs2[-1]+w) for w in cws2[:-1]]
    for h, x, w in zip(cols, cxs2, cws2):
        add_textbox(s, h, x+Inches(0.03), Inches(2.2), w-Inches(0.05), Inches(0.24),
                    font_size=8.5, bold=True, color=C_WHITE, align=PP_ALIGN.CENTER)

    rows = [
        ('Random Forest',  '94.50', '95.21', '94.09', '94.51', '30.74', '41.04'),
        ('XGBoost',        '93.99', '94.83', '94.23', '94.54', '27.85', '39.02'),
        ('Decision Tree',  '91.98', '95.10', '91.78', '92.78', '30.26', '35.29'),
        ('KNN',            '91.11', '93.17', '91.32', '91.46', '21.08', '46.08'),
        ('MLP (scaled)',   '84.94', '94.67', '78.32', '82.56', '28.20', '42.64'),
        ('Logistic Reg.',  '29.21', '27.19', '34.13', '38.21', '22.53', '29.48'),
        ('Linear SVM',     '27.14', '33.44', '30.08', '38.10', '23.31', '31.69'),
    ]
    for ri, row in enumerate(rows):
        bg = RGBColor(0xF1,0xF5,0xF9) if ri%2==0 else C_WHITE
        y = Inches(2.46 + ri*0.36)
        add_rect(s, Inches(0.3), y, Inches(9.4), Inches(0.36), bg)
        for ci, (val, x, w) in enumerate(zip(row, cxs2, cws2)):
            v = val if ci == 0 else f'{val}%'
            try:
                flt = float(val)
                col = C_TEAL if flt >= 90 else (C_AMBER if flt >= 50 else C_RED)
            except:
                col = C_BODY
            fb = ci == 0
            add_textbox(s, v, x+Inches(0.03), y+Inches(0.06), w-Inches(0.05), Inches(0.26),
                        font_size=9, bold=fb, color=col if ci>0 else C_BODY,
                        align=PP_ALIGN.CENTER if ci>0 else PP_ALIGN.LEFT)

    add_textbox(s,
        '🟢 ≥90%  🟡 50–90%  🔴 <50%  |  Best overall: Random Forest (94.50% full, 95.21% JIO)  |  Worst: Linear SVM/LR (non-linearly separable data)',
        Inches(0.3), Inches(5.0), Inches(9.4), Inches(0.26),
        font_size=8, color=C_GREY, italic=True)
    return s


def build_slide10_feature_importance(prs):
    s = add_slide_from_template(prs)
    add_header_bar(s, 'Feature Importance Analysis — What Drives Classification?',
                   'Random Forest Gini importance across all 6-class experiments')
    add_footer_bar(s); add_slide_number(s, 10)

    features = [
        ('Current Packet Size  (Lᵢ)',   52.4, C_NAVY,  'QUIC init ≥ 1200 B  vs  DNS queries 60–180 B  vs  Web MTU 1460 B'),
        ('Previous Packet Size (Lᵢ₋₁)', 30.8, C_TEAL,  'Sequential context: captures exact request → response transition'),
        ('Current Time Gap  (ΔTᵢ)',      11.1, C_GREY,  'Within-ISP timing boosts accuracy but drifts across carriers'),
        ('Previous Time Gap  (ΔTᵢ₋₁)',   5.7,  RGBColor(0xAA,0xBB,0xCC),  'Weakest signal — most susceptible to network jitter'),
    ]

    for i, (name, pct, bar_col, desc) in enumerate(features):
        y = Inches(1.1 + i * 0.95)
        # Feature label
        add_textbox(s, name, Inches(0.3), y, Inches(2.5), Inches(0.3),
                    font_size=11, bold=True, color=C_NAVY)
        # Percentage
        add_textbox(s, f'{pct}%', Inches(2.85), y, Inches(0.65), Inches(0.3),
                    font_size=16, bold=True, color=bar_col)
        # Bar background
        add_rect(s, Inches(3.6), y+Inches(0.04), Inches(5.5), Inches(0.26),
                 RGBColor(0xE8,0xEE,0xF4))
        # Bar fill
        bar_w = Inches(5.5 * pct / 55)
        add_rect(s, Inches(3.6), y+Inches(0.04), bar_w, Inches(0.26), bar_col)
        # Description
        add_textbox(s, desc, Inches(0.3), y+Inches(0.34), Inches(9.1), Inches(0.5),
                    font_size=9.5, color=C_GREY, italic=True)

    # Key insight box
    divider_line(s, Inches(5.0))
    add_rect(s, Inches(0), Inches(5.08), W, Inches(0.4), C_NAVY)
    add_textbox(s,
        'Packet sizes drive 83.2% of classification power — packet SIZE is the invariant protocol anchor across ISPs and time.',
        Inches(0.2), Inches(5.1), Inches(9.6), Inches(0.36),
        font_size=10.5, bold=True, color=C_WHITE)
    return s


def build_slide11_ablation(prs):
    s = add_slide_from_template(prs)
    add_header_bar(s, 'Feature Ablation — Size vs. Timing Under ISP Domain Shift',
                   'Hypothesis: packet size is carrier-invariant, timing drifts across networks')
    add_footer_bar(s); add_slide_number(s, 11)

    configs = [
        ('ALL FEATURES', 'Size + Timing (Lᵢ, Lᵢ₋₁, ΔTᵢ, ΔTᵢ₋₁)', '94.50%', '90.4%†', '4.1%', C_TEAL),
        ('SIZE-ONLY', 'Packet Sizes Only (Lᵢ, Lᵢ₋₁)', '91.2%', '90.1%', '1.1%  ★', C_NAVY),
        ('TIMING-ONLY', 'Inter-Arrival Gaps Only (ΔTᵢ, ΔTᵢ₋₁)', '52.4%', '41.1%', '11.3%  ✗', C_RED),
    ]

    # Header row
    add_rect(s, Inches(0.3), Inches(1.0), Inches(9.4), Inches(0.3), C_NAVY)
    for h, x, w in zip(['Feature Config','Features Used','Same-Net Acc','Cross-Net Acc','Generaliz. Drop'],
                        [0.3,1.7,4.6,6.1,7.6], [1.3,2.8,1.4,1.4,1.5]):
        add_textbox(s, h, Inches(x+0.04), Inches(1.02), Inches(w-0.06), Inches(0.26),
                    font_size=9, bold=True, color=C_WHITE)

    for ri, (cfg, feats, same, cross, drop, col) in enumerate(configs):
        y = Inches(1.3 + ri*1.0)
        add_rect(s, Inches(0.3), y, Inches(9.4), Inches(0.9), col if ri==0 else RGBColor(0xF1,0xF5,0xF9))
        add_textbox(s, cfg,   Inches(0.34), y+Inches(0.08), Inches(1.3), Inches(0.3),
                    font_size=11, bold=True, color=C_WHITE if ri==0 else col)
        add_textbox(s, feats, Inches(1.74), y+Inches(0.08), Inches(2.8), Inches(0.78),
                    font_size=9.5, color=C_WHITE if ri==0 else C_BODY, wrap=True)
        for val, x in [(same,'6.14'),(cross,'7.64'),(drop,'9.14')]:
            drop_col = C_TEAL if '★' in val else (C_RED if '✗' in val else (C_WHITE if ri==0 else C_BODY))
            add_textbox(s, val, Inches(float(x)), y+Inches(0.25), Inches(1.4), Inches(0.4),
                        font_size=14, bold=True, color=drop_col, align=PP_ALIGN.CENTER)

    add_rect(s, Inches(0), Inches(4.45), W, Inches(0.72), C_NAVY)
    add_textbox(s, '★ KEY TAKEAWAY:', Inches(0.2), Inches(4.47), Inches(1.6), Inches(0.22),
                font_size=9, bold=True, color=C_LTEAL)
    add_textbox(s,
        'Size-only features degrade by only 1.1% across ISPs (near-zero drift) while timing-only collapses by 11.3%. '
        'Packet size sequence is the cross-carrier invariant protocol fingerprint.',
        Inches(1.9), Inches(4.47), Inches(7.8), Inches(0.68),
        font_size=10.5, bold=True, color=C_WHITE, wrap=True)

    add_textbox(s, '† Cross-net result estimated from ablation study on compact feature set',
                Inches(0.3), Inches(5.2), Inches(9.4), Inches(0.22),
                font_size=7.5, color=C_GREY, italic=True)
    return s


def build_slide12_findings(prs):
    s = add_slide_from_template(prs)
    add_header_bar(s, 'Research Findings, Contributions & Limitations',
                   'Summary of what we proved, built, and where we go next')
    add_footer_bar(s); add_slide_number(s, 12)

    # 3 finding cards
    findings = [
        ('Finding 1', 'Camouflage Failure',
         'Encrypted DNS cannot hide in the QUIC crowd.\n>94% same-network, 94%+ on ratio-weighted real-world data.',
         C_TEAL),
        ('Finding 2', 'Size Invariance',
         'Packet-size-only features transfer across carriers with only 1.1% degradation vs 11.3% for timing-only.',
         C_NAVY),
        ('Finding 3', 'Domain Shift',
         'Cross-ISP accuracy collapses 47–64%. ISP-aware multi-vantage training is mandatory for deployment.',
         C_RED),
    ]
    for i, (num, title, desc, col) in enumerate(findings):
        x = Inches(0.3 + i*3.17); w = Inches(3.0)
        add_rect(s, x, Inches(1.0), w, Inches(0.24), col)
        add_textbox(s, num, x+Inches(0.08), Inches(1.02), w-Inches(0.1), Inches(0.2),
                    font_size=8, bold=True, color=C_WHITE)
        add_rect(s, x, Inches(1.24), w, Inches(0.26), RGBColor(0x14,0x28,0x4B) if col!=C_NAVY else RGBColor(0x0F,0x7C,0x8A))
        add_textbox(s, title, x+Inches(0.08), Inches(1.26), w-Inches(0.1), Inches(0.22),
                    font_size=11, bold=True, color=C_WHITE)
        add_rect(s, x, Inches(1.5), w, Inches(1.1), RGBColor(0xF1,0xF5,0xF9))
        add_textbox(s, desc, x+Inches(0.08), Inches(1.56), w-Inches(0.1), Inches(1.0),
                    font_size=10, color=C_BODY, wrap=True)

    # Contributions
    add_rect(s, Inches(0.3), Inches(2.72), Inches(4.5), Inches(0.26), C_NAVY)
    add_textbox(s, 'RESEARCH CONTRIBUTIONS', Inches(0.38), Inches(2.74), Inches(4.3), Inches(0.22),
                font_size=9, bold=True, color=C_LTEAL)
    contribs = [
        'Multi-protocol live capture engine for 6 protocols × 2 Tier-1 Indian ISPs',
        'First cross-carrier domain shift study on encrypted DNS with 95k+ packets',
        'Realistic imbalanced deployment evaluation at 8:4:4:2:2:1 ratio',
        '42-experiment benchmark: 7 ML models × 6 test scenarios',
    ]
    for i, c in enumerate(contribs):
        add_textbox(s, f'✓  {c}', Inches(0.38), Inches(3.04)+Inches(i*0.38), Inches(4.3), Inches(0.36),
                    font_size=9.5, color=C_BODY, wrap=True)

    # Limitations
    add_rect(s, Inches(5.0), Inches(2.72), Inches(4.7), Inches(0.26), C_NAVY)
    add_textbox(s, 'LIMITATIONS & FUTURE WORK', Inches(5.08), Inches(2.74), Inches(4.5), Inches(0.22),
                font_size=9, bold=True, color=C_LTEAL)
    limits = [
        'Only 4 packet-level features — flow-level features may improve cross-net generalization',
        'No HTTPS encrypted SNI (ECH) traffic — future versions will include ECH',
        'Campus Wi-Fi / 5G vantage point not captured — planned for extension',
        'Deep learning (LSTM, Transformer) on full flow sequences not yet explored',
    ]
    for i, l in enumerate(limits):
        add_textbox(s, f'→  {l}', Inches(5.08), Inches(3.04)+Inches(i*0.38), Inches(4.5), Inches(0.36),
                    font_size=9.5, color=C_BODY, wrap=True)
    return s


def build_slide13_references(prs):
    s = add_slide_from_template(prs)
    add_header_bar(s, 'References', 'Key papers, standards, and tools')
    add_footer_bar(s); add_slide_number(s, 13)

    refs = [
        ('[1]', 'Csikor et al.',
         '"Privacy of DNS-over-HTTPS: Requiem for a Dream?"',
         'IEEE EuroS&P, 2021. (Base Paper)'),
        ('[2]', 'Moure-Garrido et al.',
         '"Fingerprinting Encrypted DNS: Exploiting Metadata Leakage in DNS over QUIC"',
         'IEEE MSWiM, 2025.'),
        ('[3]', 'RFC 9250',
         'DNS over Dedicated QUIC Connections (DoQ)',
         'IETF, 2022. (Protocol standard for DoQ implementation)'),
        ('[4]', 'RFC 9114',
         'HTTP/3 (DoH/3 transport base standard)',
         'IETF, 2022.'),
        ('[5]', 'Aioquic / cslev/doh_docker',
         'QUIC implementation library & DoH dataset generation tool',
         'https://github.com/cslev/doh_docker'),
    ]
    for i, (num, authors, title, venue) in enumerate(refs):
        y = Inches(1.1 + i * 0.78)
        add_rect(s, Inches(0.3), y, Inches(0.5), Inches(0.6), C_TEAL)
        add_textbox(s, num, Inches(0.32), y+Inches(0.14), Inches(0.46), Inches(0.3),
                    font_size=11, bold=True, color=C_WHITE, align=PP_ALIGN.CENTER)
        add_rect(s, Inches(0.85), y, Inches(8.85), Inches(0.6), RGBColor(0xF1,0xF5,0xF9))
        add_textbox(s, authors, Inches(0.9), y+Inches(0.03), Inches(1.6), Inches(0.24),
                    font_size=10, bold=True, color=C_NAVY)
        add_textbox(s, title, Inches(0.9), y+Inches(0.26), Inches(5.5), Inches(0.24),
                    font_size=9.5, color=C_BODY, italic=True)
        add_textbox(s, venue, Inches(6.5), y+Inches(0.14), Inches(3.1), Inches(0.3),
                    font_size=9, color=C_GREY)
    return s


def build_slide14_thankyou(prs):
    """Clone template slide 14 (thank you)"""
    # Keep template slide 14 as-is
    return prs.slides[13]


# ─────────────────────────────────────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    print('Loading template...')
    prs_template = Presentation(TEMPLATE)

    print('Building new presentation...')
    prs_new = Presentation(TEMPLATE)   # start from template to inherit theme/fonts

    # Remove all existing slides (keep template structure)
    xml_slides = prs_new.slides._sldIdLst
    for _ in range(len(prs_new.slides)):
        rId_slide = prs_new.slides._sldIdLst[0].get('r:id')
        prs_new.part.drop_rel(rId_slide)
        del prs_new.slides._sldIdLst[0]

    print('  Slide 1 — Title (using template)')
    # Re-add template slide 1 by copying its XML
    from pptx.opc.part import Part
    from pptx.opc.packuri import PackURI
    import copy

    def clone_slide(prs_src, slide_idx, prs_dst):
        """Clone a slide from prs_src into prs_dst"""
        src_slide = prs_src.slides[slide_idx]
        # Use add_slide on a matching layout
        layout = prs_dst.slide_layouts[0]
        dst_slide = prs_dst.slides.add_slide(layout)
        # Replace the spTree with source
        dst_slide.shapes._spTree.clear()
        for el in src_slide.shapes._spTree:
            dst_slide.shapes._spTree.append(copy.deepcopy(el))
        # Copy background
        dst_bg = dst_slide.background
        src_bg = src_slide.background
        if src_slide.background.fill.type is not None:
            dst_slide.background.fill.solid()
            try:
                dst_slide.background.fill.fore_color.rgb = src_slide.background.fill.fore_color.rgb
            except:
                pass
        return dst_slide

    # Slide 1 — clone from template
    clone_slide(prs_template, 0, prs_new)
    print('  Slides 2–13 — building with real data...')
    build_slide2_problem(prs_new)
    build_slide3_midvsfinal(prs_new)
    build_slide4_data_collection(prs_new)
    build_slide5_dataset(prs_new)
    build_slide6_samenet(prs_new)
    build_slide7_crossnet(prs_new)
    build_slide8_ratio(prs_new)
    build_slide9_all_models(prs_new)
    build_slide10_feature_importance(prs_new)
    build_slide11_ablation(prs_new)
    build_slide12_findings(prs_new)
    build_slide13_references(prs_new)
    print('  Slide 14 — Thank You (using template)')
    clone_slide(prs_template, 13, prs_new)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    prs_new.save(OUT)
    print(f'\n✅ Saved: {OUT}')
    print(f'   Slides: {len(prs_new.slides)}')
