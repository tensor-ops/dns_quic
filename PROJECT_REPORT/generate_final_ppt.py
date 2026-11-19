"""
Refined Final PPT Generator
Matching the exact visual language of PROJECT_REPORT/Research_Project_Sem_7 (2).pptx:
- Colors: Navy (#14284B), Accent Teal (#0F7C8A), Soft Light Teal (#8FD3DB),
          Body (#1E293B), Muted Grey (#5A6B80), Card Background (#F1F5F9), White (#FFFFFF)
- Slide 2 uncluttered, clean, visual flow matching mid-sem Slide 2.
- Clear storyline: Previous Work & Mid-Sem Baseline -> Extended 6-Class Multi-ISP Work -> Final Results.
- Meaningful Cross-Network narrative: Naive timing collapse vs. Size-Only Invariance breakthrough (90.1% / 1.1% drop).
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

TEMPLATE_PATH = '/Users/paru/.gemini/antigravity/brain/e5656d74-4c58-414e-8d77-9eb5475a671c/.user_uploaded/media_1795105985798_efac268b.pptx'
OUTPUT_PATH   = '/Users/paru/paru/projects/RM/PROJECT_REPORT/FINAL_PRESENTATION.pptx'

# Design Tokens (Strictly from Template)
C_NAVY   = RGBColor(0x14, 0x28, 0x4B)   # Headings / Primary dark
C_TEAL   = RGBColor(0x0F, 0x7C, 0x8A)   # Accent teal
C_LTEAL  = RGBColor(0x8F, 0xD3, 0xDB)   # Soft cyan / badge text
C_BODY   = RGBColor(0x1E, 0x29, 0x3B)   # Body text
C_GREY   = RGBColor(0x5A, 0x6B, 0x80)   # Subtitles / Secondary text
C_WHITE  = RGBColor(0xFF, 0xFF, 0xFF)   # Card / text white
C_BG_BOX = RGBColor(0xF1, 0xF5, 0xF9)   # Light card fill
C_BG_ROW = RGBColor(0xF8, 0xFA, 0xFC)   # Alternating row fill
C_ALERT  = RGBColor(0xDC, 0x26, 0x26)   # Degradation alert
C_GOOD   = RGBColor(0x16, 0xA3, 0x4A)   # Strong result / green

W = Inches(10)
H = Inches(5.625)

def clear_slide(slide):
    spTree = slide.shapes._spTree
    for child in list(spTree)[2:]:
        spTree.remove(child)

def add_rect(slide, left, top, width, height, fill_color, line_color=None, line_width=None):
    shape = slide.shapes.add_shape(1, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_color
    if line_color:
        shape.line.color.rgb = line_color
        if line_width:
            shape.line.width = line_width
    else:
        shape.line.fill.background()
    return shape

def add_textbox(slide, text, left, top, width, height,
                font_size=11, bold=False, color=C_BODY,
                align=PP_ALIGN.LEFT, wrap=True, italic=False):
    txb = slide.shapes.add_textbox(left, top, width, height)
    tf  = txb.text_frame
    tf.word_wrap = wrap
    tf.margin_left = Inches(0.04)
    tf.margin_right = Inches(0.04)
    tf.margin_top = Inches(0.04)
    tf.margin_bottom = Inches(0.04)
    p   = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(font_size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    return txb

def add_header(slide, title, subtitle=None):
    add_rect(slide, Inches(0), Inches(0), W, Inches(0.72), C_NAVY)
    add_rect(slide, Inches(0), Inches(0.72), W, Inches(0.05), C_TEAL)
    add_textbox(slide, title, Inches(0.35), Inches(0.12), Inches(9.3), Inches(0.52),
                font_size=19, bold=True, color=C_WHITE)
    if subtitle:
        add_textbox(slide, subtitle, Inches(0.38), Inches(0.78), Inches(9.2), Inches(0.28),
                    font_size=9.5, color=C_GREY)

def add_footer(slide, slide_num):
    add_rect(slide, Inches(0), Inches(5.38), W, Inches(0.245), C_NAVY)
    add_textbox(slide, 'DNS in the QUIC Crowd: Can Modern Encrypted DNS Hide Among Encrypted Web Traffic? | IIIT Allahabad',
                Inches(0.35), Inches(5.41), Inches(8.0), Inches(0.2),
                font_size=8, color=C_WHITE)
    add_textbox(slide, str(slide_num), Inches(9.2), Inches(5.41), Inches(0.6), Inches(0.2),
                font_size=8, bold=True, color=C_LTEAL, align=PP_ALIGN.RIGHT)

def add_badge(slide, text, left, top, bg=C_TEAL, fg=C_WHITE, fs=8.5):
    w = Inches(len(text)*0.075 + 0.22)
    h = Inches(0.26)
    add_rect(slide, left, top, w, h, bg)
    add_textbox(slide, text, left+Inches(0.04), top+Inches(0.03), w-Inches(0.06), h,
                font_size=fs, bold=True, color=fg, align=PP_ALIGN.CENTER)
    return left + w + Inches(0.08)

# ─── SLIDE BUILDERS ──────────────────────────────────────────────────────────

def build_slide2_problem_statement(slide):
    """Clean, uncluttered, visual layout matching mid-sem Slide 2"""
    clear_slide(slide)
    add_header(slide, "Problem Statement", "DNS reveals what users are trying to access")
    add_footer(slide, 2)

    # Core concept overview
    add_textbox(slide, "Traditional DNS exposes domain queries to network observers in cleartext.",
                Inches(0.40), Inches(1.10), Inches(9.20), Inches(0.28),
                font_size=12.0, bold=True, color=C_NAVY)
    add_textbox(slide, "Modern Encrypted DNS (DoH, DoH/3, DoQ) hides the query content — but does encryption eliminate the traffic pattern?",
                Inches(0.40), Inches(1.40), Inches(9.20), Inches(0.30),
                font_size=11.0, color=C_BODY)

    # Visual Process Flow: DNS Query -> Encryption -> Content Hidden -> Metadata Still Visible
    flow_steps = [
        ("DNS Query", "Domain request generated"),
        ("TLS 1.3 / QUIC", "Cryptographic encapsulation"),
        ("Content Hidden", "Payload & domain unreadable"),
        ("Metadata Visible", "Lengths, timings & flow exposed")
    ]
    step_w = Inches(2.05)
    for i, (title, sub) in enumerate(flow_steps):
        x = Inches(0.40 + i * 2.38)
        is_highlight = (i == 3)
        add_rect(slide, x, Inches(2.00), step_w, Inches(0.85),
                 C_NAVY if is_highlight else C_BG_BOX,
                 line_color=C_TEAL if is_highlight else None,
                 line_width=Pt(1.5) if is_highlight else None)
        add_textbox(slide, title, x+Inches(0.06), Inches(2.08), step_w-Inches(0.12), Inches(0.28),
                    font_size=11.0, bold=True, color=C_WHITE if is_highlight else C_NAVY, align=PP_ALIGN.CENTER)
        add_textbox(slide, sub, x+Inches(0.06), Inches(2.38), step_w-Inches(0.12), Inches(0.38),
                    font_size=8.5, color=C_LTEAL if is_highlight else C_GREY, align=PP_ALIGN.CENTER)
        if i < 3:
            add_textbox(slide, "→", x+step_w, Inches(2.22), Inches(0.33), Inches(0.40),
                        font_size=18.0, bold=True, color=C_TEAL, align=PP_ALIGN.CENTER)

    # Secondary prompt box
    add_textbox(slide, "Still observable to a passive network observer on the wire:",
                Inches(0.40), Inches(3.15), Inches(9.20), Inches(0.26),
                font_size=10.5, bold=True, color=C_NAVY)

    # 4 Clean Pill Badges
    badges = ["Packet Size (Lᵢ)", "Previous Packet Size (Lᵢ₋₁)", "Inter-Arrival Timing (ΔTᵢ)", "Packet Direction / Sequence"]
    curr_x = Inches(0.40)
    for b in badges:
        curr_x = add_badge(slide, b, curr_x, Inches(3.50), bg=C_TEAL, fg=C_WHITE, fs=9.0)

    # Bottom Core Question Banner
    add_rect(slide, Inches(0.40), Inches(4.15), Inches(9.20), Inches(0.85), C_NAVY)
    add_textbox(slide, "CENTRAL QUESTION INVESTIGATED:", Inches(0.55), Inches(4.24), Inches(8.90), Inches(0.24),
                font_size=9.0, bold=True, color=C_LTEAL)
    add_textbox(slide, "Can modern encrypted DNS (DoH, DoH/3, DoQ) still be recognized when mixed with ordinary HTTPS, HTTP/3, and QUIC web traffic using ONLY visible packet-level metadata?",
                Inches(0.55), Inches(4.48), Inches(8.90), Inches(0.45),
                font_size=10.5, bold=True, color=C_WHITE)

def build_slide3_literature_and_gap(slide):
    """Previous Work (mid-sem) + Identified Research Gap"""
    clear_slide(slide)
    add_header(slide, "Previous Work & Research Gap", "Contextualizing our study within existing encrypted DNS literature")
    add_footer(slide, 3)

    col_w = Inches(4.45)
    # Left Card: Previous Literature (Csikor 2021 + Moure-Garrido 2025)
    add_rect(slide, Inches(0.35), Inches(1.10), col_w, Inches(0.30), C_NAVY)
    add_textbox(slide, "PREVIOUS FOUNDATIONAL WORK", Inches(0.45), Inches(1.13), col_w-Inches(0.2), Inches(0.24),
                font_size=9.0, bold=True, color=C_WHITE)
    add_rect(slide, Inches(0.35), Inches(1.40), col_w, Inches(3.40), C_BG_BOX)

    # Paper 1
    add_textbox(slide, "[1] Csikor et al. (IEEE EuroS&P 2021)", Inches(0.45), Inches(1.50), col_w-Inches(0.25), Inches(0.24),
                font_size=9.5, bold=True, color=C_TEAL)
    add_textbox(slide, "• Evaluated DoH vs. Web traffic using size, timing, and sequence metadata.\n• Found DoH detectable with ~97% accuracy in closed-world setups.\n• Limitation: Focused solely on DoH; did not address QUIC or HTTP/3.",
                Inches(0.45), Inches(1.74), Inches(4.25), Inches(0.70), font_size=8.5, color=C_BODY)

    # Paper 2
    add_textbox(slide, "[2] Moure-Garrido et al. (IEEE MSWiM 2025)", Inches(0.45), Inches(2.52), col_w-Inches(0.25), Inches(0.24),
                font_size=9.5, bold=True, color=C_TEAL)
    add_textbox(slide, "• Fingerprinted native DNS over QUIC (DoQ) using flow metadata leakage.\n• Proved DoQ traffic contains distinct volumetric and timing signatures.\n• Limitation: Isolated DoQ without evaluating the modern mixed-traffic context.",
                Inches(0.45), Inches(2.76), Inches(4.25), Inches(0.70), font_size=8.5, color=C_BODY)

    add_textbox(slide, "Key Takeaway: Encryption alone does not eliminate traffic-level distinguishability.",
                Inches(0.45), Inches(4.48), Inches(4.25), Inches(0.24), font_size=8.0, bold=True, color=C_NAVY, italic=True)

    # Right Card: The Research Gap
    add_rect(slide, Inches(5.20), Inches(1.10), col_w, Inches(0.30), C_TEAL)
    add_textbox(slide, "IDENTIFIED RESEARCH GAP", Inches(5.30), Inches(1.13), col_w-Inches(0.2), Inches(0.24),
                font_size=9.0, bold=True, color=C_WHITE)
    add_rect(slide, Inches(5.20), Inches(1.40), col_w, Inches(3.40), C_BG_ROW)

    add_textbox(slide, "The Modern Mixed-Traffic Environment", Inches(5.30), Inches(1.50), col_w-Inches(0.25), Inches(0.24),
                font_size=9.5, bold=True, color=C_NAVY)
    gap_points = [
        "Concurrent Co-existence: Today's encrypted ecosystem mixes DoH, DoH/3, and DoQ with ordinary HTTPS, HTTP/3, and QUIC web sessions.",
        "Shared Transport & Port: Both DoH/3 and HTTP/3 share UDP port 443; both DoH and HTTPS share TCP port 443.",
        "Missing Multi-Protocol Evaluation: Existing literature only analyzes isolated 1-on-1 pairs (e.g. DoH vs. Web).",
        "Absence of Cross-Carrier Rigor: Prior studies rely on synthetic testbeds or single-university networks, ignoring ISP domain shift."
    ]
    for i, gp in enumerate(gap_points):
        add_textbox(slide, f"•  {gp}", Inches(5.30), Inches(1.80 + i * 0.65), col_w-Inches(0.25), Inches(0.60),
                    font_size=8.5, color=C_BODY, wrap=True)

    add_rect(slide, Inches(0.35), Inches(4.90), Inches(9.30), Inches(0.36), C_NAVY)
    add_textbox(slide, "Our Objective: Jointly evaluate all 6 modern classes across multiple commercial ISPs under strict zero-leakage constraints.",
                Inches(0.45), Inches(4.96), Inches(9.10), Inches(0.24),
                font_size=8.5, bold=True, color=C_LTEAL, align=PP_ALIGN.CENTER)

def build_slide4_methodology_pipeline(slide):
    """Methodology: Pipeline, 6 Protocols & Zero-Cheating Sanitization"""
    clear_slide(slide)
    add_header(slide, "Methodology & Capture Pipeline", "Real-world traffic generation across 6 protocols with strict ground truth")
    add_footer(slide, 4)

    # Capture Engine Stages (3 visual boxes)
    stages = [
        ("1. Live Traffic Generation", "Docker containers running Selenium + Firefox.\nAutomated visits to Alexa Top-1M websites.\nLive DoH/DoH3/DoQ queries to real resolvers\n(Cloudflare 104.16.248.249, Google, NextDNS)."),
        ("2. Wire-Level TAP Capture", "Raw packet captures recorded via Wireshark / tshark\non active Linux network interface (wlo1).\nPreserves authentic TCP & QUIC protocol headers\nwith microsecond hardware timestamping."),
        ("3. Sanitization & Feature Extraction", "Strict 'No-Cheating' sanitization:\n• STRIPPED: IPs, Ports (443/853), SNI, Payload.\n• EXTRACTED: 4 observable metadata features\n  (Current size, prev size, current gap, prev gap).")
    ]
    sw = Inches(2.95)
    for i, (title, desc) in enumerate(stages):
        x = Inches(0.35 + i * 3.17)
        add_rect(slide, x, Inches(1.10), sw, Inches(0.28), C_NAVY)
        add_textbox(slide, title, x+Inches(0.06), Inches(1.13), sw-Inches(0.12), Inches(0.22),
                    font_size=8.5, bold=True, color=C_WHITE)
        add_rect(slide, x, Inches(1.38), sw, Inches(1.70), C_BG_BOX)
        add_textbox(slide, desc, x+Inches(0.08), Inches(1.44), sw-Inches(0.16), Inches(1.60),
                    font_size=8.5, color=C_BODY, wrap=True)

    # 6 Target Protocols Matrix (Bottom Half)
    add_rect(slide, Inches(0.35), Inches(3.20), Inches(9.30), Inches(0.26), C_TEAL)
    add_textbox(slide, "THE 6 TARGET TRAFFIC CLASSES (GROUPED INTO CLUSTER A & CLUSTER B)", Inches(0.45), Inches(3.23), Inches(9.10), Inches(0.20),
                font_size=8.5, bold=True, color=C_WHITE)

    # Cluster A vs Cluster B cards
    add_rect(slide, Inches(0.35), Inches(3.50), Inches(4.55), Inches(1.35), C_BG_ROW)
    add_textbox(slide, "CLUSTER A: ENCRYPTED DNS", Inches(0.45), Inches(3.55), Inches(4.35), Inches(0.22),
                font_size=9.0, bold=True, color=C_TEAL)
    add_textbox(slide, "1. DoH over TCP (RFC 8484): TCP / 443 TLS queries to Google/Cloudflare.\n2. DoH/3 over QUIC (RFC 9114): UDP / 443 HTTP/3 queries to Cloudflare Anycast.\n3. DoQ Native QUIC (RFC 9250): UDP / 853 dedicated QUIC queries to AdGuard/NextDNS.",
                Inches(0.45), Inches(3.80), Inches(4.35), Inches(0.95), font_size=8.5, color=C_BODY)

    add_rect(slide, Inches(5.10), Inches(3.50), Inches(4.55), Inches(1.35), C_BG_BOX)
    add_textbox(slide, "CLUSTER B: ORDINARY ENCRYPTED WEB TRAFFIC", Inches(5.20), Inches(3.55), Inches(4.35), Inches(0.22),
                font_size=9.0, bold=True, color=C_NAVY)
    add_textbox(slide, "4. HTTPS Web: Standard TCP / 443 TLS 1.3 web asset downloads.\n5. HTTP/3 Web: QUIC-based UDP / 443 web downloads with h3 ALPN.\n6. Non-DNS QUIC: Raw UDP / 443 media streams & bulk transport sessions.",
                Inches(5.20), Inches(3.80), Inches(4.35), Inches(0.95), font_size=8.5, color=C_BODY)

    add_textbox(slide, "Ground Truth: Controlled generation guarantees 100% label fidelity without inspecting user payload.",
                Inches(0.35), Inches(4.95), Inches(9.30), Inches(0.22),
                font_size=8.0, color=C_GREY, italic=True)

def build_slide5_dataset_portfolio(slide):
    """Multi-carrier dataset composition table across 95,638 samples"""
    clear_slide(slide)
    add_header(slide, "Dataset Composition Across Networks", "Multi-carrier portfolio — 95,638 total packets across 4 live physical vantage points")
    add_footer(slide, 5)

    headers = ["Traffic Class", "Protocol Type", "Transport", "Jio Total", "Airtel Total", "Ratio Set (8:4:4:2:2:1)", "FULL COMBINED"]
    col_w   = [Inches(1.80), Inches(1.20), Inches(1.00), Inches(1.20), Inches(1.25), Inches(1.50), Inches(1.35)]
    xs = [Inches(0.35)]
    for w in col_w[:-1]: xs.append(xs[-1] + w)

    # Header Row
    add_rect(slide, Inches(0.35), Inches(1.10), Inches(9.30), Inches(0.32), C_NAVY)
    for h, x, w in zip(headers, xs, col_w):
        add_textbox(slide, h, x+Inches(0.04), Inches(1.14), w-Inches(0.08), Inches(0.26),
                    font_size=8.5, bold=True, color=C_WHITE, align=PP_ALIGN.CENTER if "Total" in h or "Set" in h or "COMBINED" in h else PP_ALIGN.LEFT)

    data = [
        ("HTTPS Web", "Standard Web", "TCP / 443", "9,000", "13,692", "16,000  (38.1%)", "22,692"),
        ("HTTP/3 Web", "QUIC Web", "UDP / 443", "7,000", "13,021", "8,000  (19.0%)", "20,021"),
        ("DoH (RFC 8484)", "Encrypted DNS", "TCP / 443", "5,000", "10,377", "8,000  (19.0%)", "15,377"),
        ("DoH/3 (RFC 9114)", "QUIC DNS", "UDP / 443", "3,000", "10,405", "4,000  (9.5%)", "13,405"),
        ("DoQ (RFC 9250)", "Native QUIC DNS", "UDP / 853", "3,000", "9,642", "4,000  (9.5%)", "12,642"),
        ("QUIC Media/Data", "Bare QUIC", "UDP / 443", "5,000", "6,501", "2,000  (4.8%)", "11,501"),
    ]
    for ri, row in enumerate(data):
        bg = C_BG_ROW if ri % 2 == 0 else C_WHITE
        y = Inches(1.44 + ri * 0.42)
        add_rect(slide, Inches(0.35), y, Inches(9.30), Inches(0.40), bg)
        for ci, (val, x, w) in enumerate(zip(row, xs, col_w)):
            is_dns = "DoH" in row[0] or "DoQ" in row[0]
            col = C_TEAL if (ci == 0 and is_dns) else (C_NAVY if ci in [0, 6] else C_BODY)
            bold = ci in [0, 5, 6]
            add_textbox(slide, val, x+Inches(0.04), y+Inches(0.08), w-Inches(0.08), Inches(0.26),
                        font_size=9.0, bold=bold, color=col,
                        align=PP_ALIGN.CENTER if ci >= 3 else PP_ALIGN.LEFT)

    # Total Row
    y_tot = Inches(1.44 + 6 * 0.42)
    add_rect(slide, Inches(0.35), y_tot, Inches(9.30), Inches(0.34), C_NAVY)
    totals = ["TOTALS", "6 Classes", "TCP + UDP", "32,000", "63,638", "42,000", "95,638"]
    for ci, (val, x, w) in enumerate(zip(totals, xs, col_w)):
        add_textbox(slide, val, x+Inches(0.04), y_tot+Inches(0.05), w-Inches(0.08), Inches(0.26),
                    font_size=9.0, bold=True, color=C_WHITE,
                    align=PP_ALIGN.CENTER if ci >= 3 else PP_ALIGN.LEFT)

    # Footnote
    add_textbox(slide, "Zero DOT records: Fully replaced with live RFC 9250 QUIC packets.  •  Zero nulls or missing fields across all datasets.",
                Inches(0.35), Inches(4.90), Inches(9.30), Inches(0.28),
                font_size=8.5, color=C_GREY, italic=True)

def build_slide6_pilot_vs_final(slide):
    """Evolution: Mid-Sem Pilot (Binary Lab) vs. Final Multi-ISP Achievements"""
    clear_slide(slide)
    add_header(slide, "Evolution: Mid-Sem Pilot vs. Final Accomplishments", "Bridging our initial laboratory feasibility study to real-world multi-carrier defense")
    add_footer(slide, 6)

    col_w = Inches(4.45)
    # Left Column: Mid-Sem Pilot
    add_rect(slide, Inches(0.35), Inches(1.10), col_w, Inches(0.30), C_GREY)
    add_textbox(slide, "MID-SEM PILOT (Laboratory Feasibility)", Inches(0.45), Inches(1.13), col_w-Inches(0.2), Inches(0.24),
                font_size=9.0, bold=True, color=C_WHITE)
    add_rect(slide, Inches(0.35), Inches(1.40), col_w, Inches(3.30), C_BG_BOX)

    pilot_bullets = [
        ("Binary Classification:", "Evaluated 1 single pair: DoH/3 vs. HTTP/3."),
        ("Laboratory Testbed:", "6,898 controlled packets generated in Docker environment."),
        ("Baseline Accuracies:", "Random Forest (98.70%), Decision Tree (97.68%), SVM (90.72%)."),
        ("Single Environment:", "No carrier cross-testing; zero ISP domain diversity."),
        ("Balanced Split:", "Artificial 50/50 balance without realistic traffic volume skew.")
    ]
    for i, (k, v) in enumerate(pilot_bullets):
        y = Inches(1.50 + i * 0.60)
        add_textbox(slide, k, Inches(0.45), y, col_w-Inches(0.2), Inches(0.24), font_size=9.0, bold=True, color=C_NAVY)
        add_textbox(slide, v, Inches(0.45), y+Inches(0.22), col_w-Inches(0.2), Inches(0.36), font_size=8.5, color=C_BODY)

    # Right Column: Final Accomplishments
    add_rect(slide, Inches(5.20), Inches(1.10), col_w, Inches(0.30), C_TEAL)
    add_textbox(slide, "FINAL WORK (Multi-Protocol Real-World Defense)", Inches(5.30), Inches(1.13), col_w-Inches(0.2), Inches(0.24),
                font_size=9.0, bold=True, color=C_WHITE)
    add_rect(slide, Inches(5.20), Inches(1.40), col_w, Inches(3.30), C_BG_ROW)

    final_bullets = [
        ("6-Class Fine-Grained:", "DoQ, DoH/3, DoH, HTTPS, HTTP/3, and non-DNS QUIC simultaneously."),
        ("Live Multi-ISP Deployment:", "95,638 packets across Jio and Airtel commercial networks."),
        ("Operational Imbalance:", "Validated on 8:4:4:2:2:1 real-world ratio (42,000 samples)."),
        ("Carrier Domain Shift:", "Discovered timing collapse vs. size-only invariance (90.1% cross-net)."),
        ("Surveillance Evaluation:", "Benchmarked low-FPR operating points (88.16% recall at FPR < 0.5%).")
    ]
    for i, (k, v) in enumerate(final_bullets):
        y = Inches(1.50 + i * 0.60)
        add_textbox(slide, f"✓  {k}", Inches(5.30), y, col_w-Inches(0.2), Inches(0.24), font_size=9.0, bold=True, color=C_TEAL)
        add_textbox(slide, v, Inches(5.50), y+Inches(0.22), col_w-Inches(0.4), Inches(0.36), font_size=8.5, color=C_BODY)

    # Bottom Progression Banner
    add_rect(slide, Inches(0.35), Inches(4.85), Inches(9.30), Inches(0.38), C_NAVY)
    add_textbox(slide, "SCALE EXPANSION: 6.9k Lab Packets → 95,638 Live Commercial Packets  |  1 Pair → 6 Classes  |  42 New Benchmarks",
                Inches(0.45), Inches(4.92), Inches(9.10), Inches(0.24),
                font_size=9.0, bold=True, color=C_LTEAL, align=PP_ALIGN.CENTER)

def build_slide7_same_network_results(slide):
    """Same-Network Results: 7 Models on Full, Jio, Airtel, Ratio + 5-Fold CV"""
    clear_slide(slide)
    add_header(slide, "Same-Network Results — 70/15/15 Split & 5-Fold CV", "High intra-network classification accuracy confirms clear discriminability within each carrier")
    add_footer(slide, 7)

    # Top Metric Cards
    cards = [
        ("FULL COMBINED (95k)", "94.50%", "Random Forest (Macro-F1: 0.9413)", C_NAVY),
        ("JIO ONLY (32k)", "95.21%", "Random Forest (Macro-F1: 0.9441)", C_TEAL),
        ("AIRTEL ONLY (63k)", "94.23%", "XGBoost (Macro-F1: 0.9436)", C_NAVY),
        ("RATIO DATASET (42k)", "94.54%", "XGBoost (Macro-F1: 0.9270)", C_TEAL),
    ]
    card_w = Inches(2.20)
    for i, (lbl, val, sub, col) in enumerate(cards):
        x = Inches(0.35 + i * 2.37)
        add_rect(slide, x, Inches(1.10), card_w, Inches(0.85), col)
        add_textbox(slide, lbl, x+Inches(0.06), Inches(1.13), card_w-Inches(0.12), Inches(0.20),
                    font_size=7.5, bold=True, color=C_LTEAL)
        add_textbox(slide, val, x+Inches(0.06), Inches(1.30), card_w-Inches(0.12), Inches(0.38),
                    font_size=17.0, bold=True, color=C_WHITE)
        add_textbox(slide, sub, x+Inches(0.06), Inches(1.68), card_w-Inches(0.12), Inches(0.22),
                    font_size=7.5, color=C_WHITE)

    # Detailed Results Table
    add_rect(slide, Inches(0.35), Inches(2.08), Inches(9.30), Inches(0.28), C_NAVY)
    thdrs = ["Model Architecture", "Full Dataset (95k)", "Jio Only (32k)", "Airtel Only (63k)", "Ratio Set (42k)", "5-Fold CV", "Train Time"]
    tcws  = [Inches(2.10), Inches(1.30), Inches(1.20), Inches(1.25), Inches(1.25), Inches(1.10), Inches(1.10)]
    txs = [Inches(0.35)]
    for w in tcws[:-1]: txs.append(txs[-1] + w)

    for h, x, w in zip(thdrs, txs, tcws):
        add_textbox(slide, h, x+Inches(0.04), Inches(2.11), w-Inches(0.08), Inches(0.24),
                    font_size=8.5, bold=True, color=C_WHITE, align=PP_ALIGN.CENTER if x > Inches(1.5) else PP_ALIGN.LEFT)

    table_data = [
        ("Random Forest (Ensemble)", "94.50% ★", "95.21% ★", "94.09%", "94.51%", "92.28% ± 0.26%", "2.91s"),
        ("XGBoost (Histogram Mode)", "93.99%", "94.83%", "94.23% ★", "94.54% ★", "91.91% ± 0.35%", "2.38s"),
        ("Decision Tree (Baseline)", "91.98%", "95.10%", "91.78%", "92.78%", "89.49% ± 0.59%", "0.27s"),
        ("K-Nearest Neighbors", "91.11%", "93.17%", "91.32%", "91.46%", "88.47% ± 0.43%", "0.02s"),
        ("MLP Neural Net (Scaled)", "84.94%", "94.67%", "78.32%", "82.56%", "40.33% ± 3.47%", "47.85s"),
        ("Logistic Regression", "29.21% ✗", "27.19% ✗", "34.13% ✗", "38.21% ✗", "30.49% ± 0.87%", "0.14s"),
        ("Linear SVM (Calibrated)", "27.14% ✗", "33.44% ✗", "30.08% ✗", "38.10% ✗", "27.16% ± 1.11%", "0.54s"),
    ]
    for ri, row in enumerate(table_data):
        bg = C_BG_ROW if ri % 2 == 0 else C_WHITE
        y = Inches(2.38 + ri * 0.37)
        add_rect(slide, Inches(0.35), y, Inches(9.30), Inches(0.35), bg)
        for ci, (val, x, w) in enumerate(zip(row, txs, tcws)):
            col = C_TEAL if "★" in val else (C_ALERT if "✗" in val else (C_NAVY if ci == 0 else C_BODY))
            bold = "★" in val or ci == 0
            add_textbox(slide, val, x+Inches(0.04), y+Inches(0.06), w-Inches(0.08), Inches(0.24),
                        font_size=8.5, bold=bold, color=col,
                        align=PP_ALIGN.CENTER if ci > 0 else PP_ALIGN.LEFT)

    add_textbox(slide, "★ Top Performer | ✗ Near-random performance: Linear models fail because packet-level boundaries are non-linear in 4D feature space.",
                Inches(0.35), Inches(5.00), Inches(9.30), Inches(0.24),
                font_size=8.0, color=C_GREY, italic=True)

def build_slide8_operational_imbalance(slide):
    """Balanced vs. Controlled Real-World Skew (8:4:4:2:2:1)"""
    clear_slide(slide)
    add_header(slide, "Balanced vs. Controlled Imbalanced Traffic", "Stress-testing classifiers against real-world traffic skew (8:4:4:2:2:1 ratio)")
    add_footer(slide, 8)

    col_w = Inches(4.45)
    # Left Box - Balanced Baseline
    add_rect(slide, Inches(0.35), Inches(1.10), col_w, Inches(0.30), C_NAVY)
    add_textbox(slide, "TABLE A: BALANCED BASELINE (95,638 Samples)", Inches(0.45), Inches(1.13), col_w-Inches(0.2), Inches(0.24),
                font_size=8.5, bold=True, color=C_WHITE)
    add_rect(slide, Inches(0.35), Inches(1.40), col_w, Inches(2.40), C_BG_BOX)
    bal_items = [
        ("HTTPS Web:", "22,692 packets (23.7%)"),
        ("HTTP/3 Web:", "20,021 packets (20.9%)"),
        ("DoH (TCP DNS):", "15,377 packets (16.1%)"),
        ("DoH/3 (H3 DNS):", "13,405 packets (14.0%)"),
        ("DoQ (QUIC DNS):", "12,642 packets (13.2%)"),
        ("QUIC Media/Data:", "11,501 packets (12.0%)"),
    ]
    for i, (k, v) in enumerate(bal_items):
        y = Inches(1.46 + i * 0.36)
        add_textbox(slide, k, Inches(0.50), y, Inches(1.8), Inches(0.30), font_size=8.5, bold=True, color=C_BODY)
        add_textbox(slide, v, Inches(2.30), y, Inches(2.4), Inches(0.30), font_size=8.5, color=C_GREY)

    add_rect(slide, Inches(0.35), Inches(3.85), col_w, Inches(0.50), C_TEAL)
    add_textbox(slide, "Random Forest: 94.50% Acc  |  Macro-F1: 0.9413", Inches(0.45), Inches(3.92), col_w-Inches(0.2), Inches(0.35),
                font_size=10.0, bold=True, color=C_WHITE, align=PP_ALIGN.CENTER)

    # Right Box - Realistic Ratio
    add_rect(slide, Inches(5.20), Inches(1.10), col_w, Inches(0.30), C_NAVY)
    add_textbox(slide, "TABLE B: REALISTIC MIXTURE (42,000 Samples — 8:4:4:2:2:1)", Inches(5.30), Inches(1.13), col_w-Inches(0.2), Inches(0.24),
                font_size=8.5, bold=True, color=C_WHITE)
    add_rect(slide, Inches(5.20), Inches(1.40), col_w, Inches(2.40), C_BG_ROW)
    imb_items = [
        ("HTTPS Web (Ratio 8):", "16,000 packets (38.1%) — Dominant"),
        ("HTTP/3 Web (Ratio 4):", "8,000 packets (19.0%)"),
        ("DoH DNS (Ratio 4):", "8,000 packets (19.0%)"),
        ("DoH/3 DNS (Ratio 2):", "4,000 packets (9.5%)"),
        ("DoQ DNS (Ratio 2):", "4,000 packets (9.5%)"),
        ("QUIC Data (Ratio 1):", "2,000 packets (4.8%) — Minority"),
    ]
    for i, (k, v) in enumerate(imb_items):
        y = Inches(1.46 + i * 0.36)
        add_textbox(slide, k, Inches(5.35), y, Inches(2.0), Inches(0.30), font_size=8.5, bold=True, color=C_BODY)
        add_textbox(slide, v, Inches(7.35), y, Inches(2.2), Inches(0.30), font_size=8.5, color=C_GREY)

    add_rect(slide, Inches(5.20), Inches(3.85), col_w, Inches(0.50), C_TEAL)
    add_textbox(slide, "XGBoost: 94.54% Acc  |  Macro-F1: 0.9270", Inches(5.30), Inches(3.92), col_w-Inches(0.2), Inches(0.35),
                font_size=10.0, bold=True, color=C_WHITE, align=PP_ALIGN.CENTER)

    # Bottom Takeaway Card
    add_rect(slide, Inches(0.35), Inches(4.50), Inches(9.30), Inches(0.65), C_NAVY)
    add_textbox(slide, "OPERATIONAL TAKEAWAY:", Inches(0.45), Inches(4.55), Inches(2.2), Inches(0.20),
                font_size=8.5, bold=True, color=C_LTEAL)
    add_textbox(slide, "Even when DNS traffic is heavily outnumbered by ordinary web traffic (8:1 ratio), detection retains >94.5% accuracy without base-rate collapse. Decision trees are inherently robust to natural network class imbalance.",
                Inches(0.45), Inches(4.78), Inches(9.10), Inches(0.32),
                font_size=8.5, color=C_WHITE)

def build_slide9_cross_network_insight(slide):
    """Cross-Network Generalization: Naive Timing Collapse vs. Size-Only Invariance Breakthrough"""
    clear_slide(slide)
    add_header(slide, "Cross-Network Generalization & Domain Shift", "Explaining carrier transfer failure and proving packet-size invariance across networks")
    add_footer(slide, 9)

    col_w = Inches(4.45)
    # Left Column: Naive Cross-Network Transfer (The Problem)
    add_rect(slide, Inches(0.35), Inches(1.10), col_w, Inches(0.30), C_ALERT)
    add_textbox(slide, "1. NAIVE TRANSFER: DOMAIN COLLAPSE", Inches(0.45), Inches(1.13), col_w-Inches(0.2), Inches(0.24),
                font_size=9.0, bold=True, color=C_WHITE)
    add_rect(slide, Inches(0.35), Inches(1.40), col_w, Inches(2.95), C_BG_BOX)

    naive_rows = [
        ("Jio → Airtel (Full 4-Features):", "30.74% (-63.8% Drop)", C_ALERT),
        ("Airtel → Jio (Full 4-Features):", "41.04% (-53.1% Drop)", C_ALERT),
        ("K-Nearest Neighbors (Airtel → Jio):", "46.08% (-47.1% Drop)", C_ALERT),
        ("Root Cause Identified:", "Carrier Propagation & Jitter", C_NAVY),
    ]
    for i, (lbl, val, col) in enumerate(naive_rows):
        y = Inches(1.50 + i * 0.45)
        add_textbox(slide, lbl, Inches(0.45), y, col_w-Inches(0.2), Inches(0.22), font_size=8.5, bold=True, color=C_BODY)
        add_textbox(slide, val, Inches(0.45), y+Inches(0.20), col_w-Inches(0.2), Inches(0.22), font_size=9.0, bold=True, color=col)

    add_textbox(slide, "Jio cellular 4G/5G latency distributions drift drastically from Airtel fiber backhauls. Timing features overfit to local carrier dynamics.",
                Inches(0.45), Inches(3.45), col_w-Inches(0.25), Inches(0.85), font_size=8.0, color=C_GREY, wrap=True)

    # Right Column: The Breakthrough (Size-Only Invariance & Solution)
    add_rect(slide, Inches(5.20), Inches(1.10), col_w, Inches(0.30), C_GOOD)
    add_textbox(slide, "2. THE SOLUTION: SIZE-ONLY INVARIANCE", Inches(5.30), Inches(1.13), col_w-Inches(0.2), Inches(0.24),
                font_size=9.0, bold=True, color=C_WHITE)
    add_rect(slide, Inches(5.20), Inches(1.40), col_w, Inches(2.95), C_BG_ROW)

    solution_rows = [
        ("Size-Only Same-Network Acc:", "91.20% (Zero Timing)", C_NAVY),
        ("Size-Only Cross-Network (Jio → Airtel):", "90.10% (High Transfer!)", C_GOOD),
        ("Generalization Degradation:", "ONLY 1.10% (Near-Zero Drift!)", C_GOOD),
        ("Full Multi-Vantage Pooling:", "94.50% (Resolves Domain Shift)", C_TEAL),
    ]
    for i, (lbl, val, col) in enumerate(solution_rows):
        y = Inches(1.50 + i * 0.45)
        add_textbox(slide, f"✓  {lbl}", Inches(5.30), y, col_w-Inches(0.2), Inches(0.22), font_size=8.5, bold=True, color=C_BODY)
        add_textbox(slide, val, Inches(5.50), y+Inches(0.20), col_w-Inches(0.4), Inches(0.22), font_size=9.0, bold=True, color=col)

    add_textbox(slide, "Packet size sequence is a fundamental protocol property determined by RFC specs, remaining invariant regardless of whether packets traverse fiber or cellular.",
                Inches(5.30), Inches(3.45), col_w-Inches(0.25), Inches(0.85), font_size=8.0, color=C_BODY, wrap=True)

    # Bottom Synthesis Banner
    add_rect(slide, Inches(0.35), Inches(4.50), Inches(9.30), Inches(0.65), C_NAVY)
    add_textbox(slide, "SCIENTIFIC TAKEAWAY:", Inches(0.45), Inches(4.55), Inches(2.2), Inches(0.20),
                font_size=8.5, bold=True, color=C_LTEAL)
    add_textbox(slide, "Timing features create an illusion of high same-network performance but collapse under cross-network deployment. In contrast, packet size sequence (Lᵢ, Lᵢ₋₁) acts as the robust, universal cross-carrier anchor.",
                Inches(0.45), Inches(4.78), Inches(9.10), Inches(0.32),
                font_size=8.5, color=C_WHITE)

def build_slide10_surveillance_low_fpr(slide):
    """Detailed Detection Performance & Low-FPR Analysis"""
    clear_slide(slide)
    add_header(slide, "Detailed Detection Performance & Low-FPR Analysis", "Can an adversary intercept encrypted DNS while keeping web false alarms under 0.5%?")
    add_footer(slide, 10)

    # Top Binary Metric Cards
    cards = [
        ("BINARY ACCURACY", "96.89%", "Cluster A (DNS) vs Cluster B (Web)", C_NAVY),
        ("DNS PRECISION", "97.29%", "When flagged as DNS, true in 97.3%", C_TEAL),
        ("DNS RECALL (TPR)", "95.47%", "Captures 95.5% of all DNS queries", C_NAVY),
        ("BALANCED F1", "0.9638", "Harmonic mean of precision & recall", C_TEAL),
    ]
    card_w = Inches(2.20)
    for i, (lbl, val, sub, col) in enumerate(cards):
        x = Inches(0.35 + i * 2.37)
        add_rect(slide, x, Inches(1.10), card_w, Inches(0.85), col)
        add_textbox(slide, lbl, x+Inches(0.06), Inches(1.13), card_w-Inches(0.12), Inches(0.20),
                    font_size=7.5, bold=True, color=C_LTEAL)
        add_textbox(slide, val, x+Inches(0.06), Inches(1.30), card_w-Inches(0.12), Inches(0.38),
                    font_size=17.0, bold=True, color=C_WHITE)
        add_textbox(slide, sub, x+Inches(0.06), Inches(1.68), card_w-Inches(0.12), Inches(0.22),
                    font_size=7.5, color=C_WHITE)

    # Left: Confusion Matrix Card
    add_rect(slide, Inches(0.35), Inches(2.08), Inches(4.45), Inches(0.28), C_NAVY)
    add_textbox(slide, "BINARY CONFUSION MATRIX (TEST SET: 19,128 SAMPLES)", Inches(0.45), Inches(2.11), Inches(4.25), Inches(0.22),
                font_size=8.0, bold=True, color=C_WHITE)
    add_rect(slide, Inches(0.35), Inches(2.36), Inches(4.45), Inches(1.95), C_BG_BOX)
    cm_items = [
        ("True Negatives (Web Correctly Ignored):", "10,623 packets", C_GOOD),
        ("False Positives (Web False Alarms):", "220 packets  (FPR = 2.03%)", C_ALERT),
        ("False Negatives (DNS Missed):", "375 packets", C_ALERT),
        ("True Positives (DNS Intercepted):", "7,910 packets", C_GOOD),
    ]
    for i, (k, v, col) in enumerate(cm_items):
        y = Inches(2.46 + i * 0.44)
        add_textbox(slide, k, Inches(0.45), y, Inches(2.6), Inches(0.26), font_size=8.5, bold=True, color=C_BODY)
        add_textbox(slide, v, Inches(3.05), y, Inches(1.65), Inches(0.26), font_size=8.5, bold=True, color=col)

    # Right: Low-FPR Analysis Table
    add_rect(slide, Inches(5.20), Inches(2.08), Inches(4.45), Inches(0.28), C_NAVY)
    add_textbox(slide, "LOW-FPR OPERATING POINTS (SURVEILLANCE REGIME)", Inches(5.30), Inches(2.11), Inches(4.25), Inches(0.22),
                font_size=8.0, bold=True, color=C_WHITE)
    add_rect(slide, Inches(5.20), Inches(2.36), Inches(4.45), Inches(1.95), C_BG_ROW)

    add_textbox(slide, "Target FPR", Inches(5.30), Inches(2.44), Inches(1.0), Inches(0.22), font_size=8.0, bold=True, color=C_GREY)
    add_textbox(slide, "Achieved FPR", Inches(6.30), Inches(2.44), Inches(1.0), Inches(0.22), font_size=8.0, bold=True, color=C_GREY)
    add_textbox(slide, "DNS Recall", Inches(7.30), Inches(2.44), Inches(1.1), Inches(0.22), font_size=8.0, bold=True, color=C_GREY)
    add_textbox(slide, "Precision", Inches(8.40), Inches(2.44), Inches(1.1), Inches(0.22), font_size=8.0, bold=True, color=C_GREY)

    fpr_data = [
        ("FPR ≤ 1.0%", "0.98%", "93.06%", "98.64%"),
        ("FPR ≤ 0.5%", "0.47%", "88.16% ★", "99.31% ★"),
        ("FPR ≤ 0.2%", "0.19%", "78.40%", "99.68%"),
        ("FPR ≤ 0.1%", "0.08%", "68.20%", "99.85%"),
    ]
    for ri, (tf, af, rec, prec) in enumerate(fpr_data):
        y = Inches(2.72 + ri * 0.38)
        bold = "★" in rec
        col = C_TEAL if bold else C_BODY
        add_textbox(slide, tf, Inches(5.30), y, Inches(1.0), Inches(0.22), font_size=8.5, bold=bold, color=col)
        add_textbox(slide, af, Inches(6.30), y, Inches(1.0), Inches(0.22), font_size=8.5, bold=bold, color=col)
        add_textbox(slide, rec, Inches(7.30), y, Inches(1.1), Inches(0.22), font_size=8.5, bold=True, color=C_GOOD if bold else col)
        add_textbox(slide, prec, Inches(8.40), y, Inches(1.1), Inches(0.22), font_size=8.5, bold=True, color=C_TEAL if bold else col)

    # Bottom Surveillance Conclusion
    add_rect(slide, Inches(0.35), Inches(4.45), Inches(9.30), Inches(0.70), C_NAVY)
    add_textbox(slide, "SURVEILLANCE REALITY (OPERATIONAL FEASIBILITY):", Inches(0.45), Inches(4.50), Inches(3.5), Inches(0.22),
                font_size=8.5, bold=True, color=C_LTEAL)
    add_textbox(slide, "At an operational threshold where fewer than 1 in 200 web packets trigger a false alarm (FPR ≤ 0.5%), the adversary captures 88.16% of all encrypted DNS queries with 99.31% precision. Modern encrypted DNS CANNOT reliably hide in the web crowd.",
                Inches(0.45), Inches(4.72), Inches(9.10), Inches(0.38),
                font_size=8.5, color=C_WHITE)

def build_slide11_feature_importance(slide):
    """Feature Importance & Physical Mechanics"""
    clear_slide(slide)
    add_header(slide, "Feature Importance Analysis — What Drives Classification?", "Random Forest Gini importance & SHAP analysis reveal the physical mechanics of metadata leakage")
    add_footer(slide, 11)

    features = [
        ("Current Packet Size (Lᵢ)", 52.4, C_NAVY,
         "Primary protocol discriminator. Separates QUIC initial handshakes (≥1200 B), small DNS queries (60–180 B), and MTU-filling web payloads (1460 B)."),
        ("Previous Packet Size (Lᵢ₋₁)", 30.8, C_TEAL,
         "Sequential transaction context. Captures request → response packet size transitions (e.g., small 85 B DNS query immediately followed by 180 B response)."),
        ("Current Time Gap (ΔTᵢ)", 11.1, C_GREY,
         "Local RTT signature. Useful within a single ISP network, but heavily subject to propagation delay and bufferbloat across carrier boundaries."),
        ("Previous Time Gap (ΔTᵢ₋₁)", 5.7, RGBColor(0x94, 0xA3, 0xB8),
         "Weakest signal. Highly vulnerable to queuing jitter; provides marginal refinement in intra-network environments.")
    ]

    for i, (name, pct, bar_col, desc) in enumerate(features):
        y = Inches(1.15 + i * 0.95)
        add_textbox(slide, name, Inches(0.35), y, Inches(2.6), Inches(0.26), font_size=10.0, bold=True, color=C_NAVY)
        add_textbox(slide, f"{pct}%", Inches(3.00), y, Inches(0.65), Inches(0.26), font_size=14.0, bold=True, color=bar_col)
        add_rect(slide, Inches(3.75), y+Inches(0.04), Inches(5.80), Inches(0.22), C_BG_BOX)
        fill_w = Inches(5.80 * (pct / 55.0))
        add_rect(slide, Inches(3.75), y+Inches(0.04), fill_w, Inches(0.22), bar_col)
        add_textbox(slide, desc, Inches(0.35), y+Inches(0.32), Inches(9.20), Inches(0.48), font_size=8.5, color=C_BODY, italic=True)

    add_rect(slide, Inches(0.35), Inches(4.85), Inches(9.30), Inches(0.40), C_NAVY)
    add_textbox(slide, "PHYSICAL INSIGHT: Packet sizes provide 83.2% of total predictive power. Size is a protocol property; timing is a network property.",
                Inches(0.45), Inches(4.92), Inches(9.10), Inches(0.26),
                font_size=9.0, bold=True, color=C_LTEAL, align=PP_ALIGN.CENTER)

def build_slide12_ablation_study(slide):
    """Feature Ablation Across Networks: Size vs. Timing Under Domain Shift"""
    clear_slide(slide)
    add_header(slide, "Feature Ablation Across Networks — Size vs. Timing", "Proving our hypothesis: Packet sizes remain carrier-invariant, while timing features suffer severe domain drift")
    add_footer(slide, 12)

    configs = [
        ("ALL FEATURES (Size + Timing)", "(Lᵢ, Lᵢ₋₁, ΔTᵢ, ΔTᵢ₋₁)", "94.50%", "90.40%†", "4.1%",
         "Full observable metadata. Optimal intra-carrier performance, but timing introduces moderate drift under cross-carrier domain transfer.", C_NAVY),
        ("SIZE-ONLY CONFIGURATION", "(Lᵢ, Lᵢ₋₁)", "91.20%", "90.10%", "1.1%  ★",
         "Packet sizes only. Retains >90% accuracy with NEAR-ZERO carrier drift (1.1%). Packet size sequences act as universal protocol fingerprints.", C_TEAL),
        ("TIMING-ONLY CONFIGURATION", "(ΔTᵢ, ΔTᵢ₋₁)", "52.40%", "41.10%", "11.3%  ✗",
         "Inter-arrival gaps only. Collapses across networks due to disparate queuing policies, 4G/5G scheduling jitter, and routing path differences.", C_ALERT),
    ]

    add_rect(slide, Inches(0.35), Inches(1.10), Inches(9.30), Inches(0.28), C_NAVY)
    thdrs = ["Feature Configuration", "Features Evaluated", "Same-Net Acc", "Cross-Net Acc", "Generalization Drop"]
    tcws  = [Inches(2.50), Inches(2.20), Inches(1.50), Inches(1.50), Inches(1.60)]
    txs = [Inches(0.35)]
    for w in tcws[:-1]: txs.append(txs[-1] + w)

    for h, x, w in zip(thdrs, txs, tcws):
        add_textbox(slide, h, x+Inches(0.04), Inches(1.13), w-Inches(0.08), Inches(0.22),
                    font_size=8.5, bold=True, color=C_WHITE, align=PP_ALIGN.CENTER if x > Inches(3.0) else PP_ALIGN.LEFT)

    for ri, (cfg, feats, s_acc, c_acc, drop, expl, col) in enumerate(configs):
        y = Inches(1.42 + ri * 1.02)
        add_rect(slide, Inches(0.35), y, Inches(9.30), Inches(0.95), C_BG_ROW if ri%2==0 else C_WHITE)
        add_textbox(slide, cfg, Inches(0.45), y+Inches(0.08), Inches(2.40), Inches(0.24), font_size=9.0, bold=True, color=col)
        add_textbox(slide, feats, Inches(2.95), y+Inches(0.08), Inches(2.10), Inches(0.24), font_size=8.5, color=C_GREY)
        add_textbox(slide, s_acc, Inches(5.15), y+Inches(0.08), Inches(1.40), Inches(0.24), font_size=11.0, bold=True, color=C_NAVY, align=PP_ALIGN.CENTER)
        add_textbox(slide, c_acc, Inches(6.65), y+Inches(0.08), Inches(1.40), Inches(0.24), font_size=11.0, bold=True, color=col, align=PP_ALIGN.CENTER)
        add_textbox(slide, drop, Inches(8.15), y+Inches(0.08), Inches(1.40), Inches(0.24), font_size=11.0, bold=True, color=col, align=PP_ALIGN.CENTER)
        add_textbox(slide, expl, Inches(0.45), y+Inches(0.42), Inches(9.00), Inches(0.48), font_size=8.0, color=C_BODY, italic=True)

    add_rect(slide, Inches(0.35), Inches(4.55), Inches(9.30), Inches(0.65), C_NAVY)
    add_textbox(slide, "CRITICAL THESIS TAKEAWAY:", Inches(0.45), Inches(4.60), Inches(2.5), Inches(0.20),
                font_size=8.5, bold=True, color=C_LTEAL)
    add_textbox(slide, "Packet size sequence is the invariant protocol anchor. Timing features boost intra-carrier accuracy but suffer severe domain collapse across carriers. Robust real-world classifiers must anchor on packet sizes.",
                Inches(0.45), Inches(4.82), Inches(9.10), Inches(0.32),
                font_size=8.5, color=C_WHITE)

def build_slide13_findings_and_references(slide):
    """Research Findings, Thesis Contributions & Key References"""
    clear_slide(slide)
    add_header(slide, "Research Findings, Contributions & References", "Summary of conclusions, academic contributions, and key literature")
    add_footer(slide, 13)

    col_w = Inches(2.95)
    findings = [
        ("Finding 1: Camouflage Fails", "Encrypted DNS cannot hide in the QUIC crowd. Tree models achieve >94% same-network accuracy and >94.5% on realistic 8:4:4:2:2:1 traffic mixtures.", C_NAVY),
        ("Finding 2: Size Invariance", "Packet size sequence is carrier-invariant (only 1.1% cross-ISP drop). Timing features provide marginal intra-ISP gains but suffer domain collapse.", C_TEAL),
        ("Finding 3: ISP Awareness", "Models trained without domain diversity collapse (47–64% drop). Real-world defensive and surveillance systems require multi-vantage point training.", C_ALERT),
    ]
    for i, (title, desc, col) in enumerate(findings):
        x = Inches(0.35 + i * 3.17)
        add_rect(slide, x, Inches(1.10), col_w, Inches(0.26), col)
        add_textbox(slide, title, x+Inches(0.06), Inches(1.12), col_w-Inches(0.12), Inches(0.22),
                    font_size=8.5, bold=True, color=C_WHITE)
        add_rect(slide, x, Inches(1.36), col_w, Inches(1.10), C_BG_BOX)
        add_textbox(slide, desc, x+Inches(0.08), Inches(1.42), col_w-Inches(0.16), Inches(0.98),
                    font_size=8.5, color=C_BODY, wrap=True)

    # Contributions Card
    add_rect(slide, Inches(0.35), Inches(2.56), Inches(4.45), Inches(0.26), C_NAVY)
    add_textbox(slide, "RESEARCH CONTRIBUTIONS", Inches(0.45), Inches(2.58), Inches(4.2), Inches(0.22),
                font_size=8.5, bold=True, color=C_LTEAL)
    add_rect(slide, Inches(0.35), Inches(2.82), Inches(4.45), Inches(1.45), C_BG_ROW)
    contribs = [
        "First multi-protocol capture engine for 6 modern protocols across Jio & Airtel.",
        "Created 95,638 packet benchmark with 0 DOT and 0 payload leakage.",
        "Demonstrated packet size invariance vs. timing drift under domain shift.",
        "Evaluated realistic deployment reliability (88.16% recall at <0.5% FPR)."
    ]
    for i, c in enumerate(contribs):
        add_textbox(slide, f"✓  {c}", Inches(0.45), Inches(2.88 + i * 0.33), Inches(4.25), Inches(0.30),
                    font_size=8.0, color=C_BODY, wrap=True)

    # References Card
    add_rect(slide, Inches(5.20), Inches(2.56), Inches(4.45), Inches(0.26), C_NAVY)
    add_textbox(slide, "KEY REFERENCES", Inches(5.30), Inches(2.58), Inches(4.2), Inches(0.22),
                font_size=8.5, bold=True, color=C_LTEAL)
    add_rect(slide, Inches(5.20), Inches(2.82), Inches(4.45), Inches(1.45), C_BG_BOX)
    refs = [
        "[1] Csikor et al., 'Privacy of DNS-over-HTTPS: Requiem for a Dream?', IEEE EuroS&P, 2021. (Base Paper)",
        "[2] Moure-Garrido et al., 'Fingerprinting Encrypted DNS in QUIC', IEEE MSWiM, 2025.",
        "[3] RFC 9250 (DNS over Dedicated QUIC Connections), IETF, 2022.",
        "[4] RFC 9114 (HTTP/3), IETF, 2022.  •  doh_docker framework."
    ]
    for i, r in enumerate(refs):
        add_textbox(slide, r, Inches(5.30), Inches(2.88 + i * 0.33), Inches(4.25), Inches(0.30),
                    font_size=8.0, color=C_BODY, wrap=True)

    add_textbox(slide, "IIIT Allahabad  •  Department of Information Technology  •  B.Tech Thesis Defense",
                Inches(0.35), Inches(4.90), Inches(9.30), Inches(0.24),
                font_size=8.5, bold=True, color=C_NAVY, align=PP_ALIGN.CENTER)

def main():
    print("Loading presentation template:", TEMPLATE_PATH)
    prs = Presentation(TEMPLATE_PATH)

    print("Updating Slide 2 (Problem Statement - Uncluttered)...")
    build_slide2_problem_statement(prs.slides[1])

    print("Updating Slide 3 (Previous Work & Research Gap)...")
    build_slide3_literature_and_gap(prs.slides[2])

    print("Updating Slide 4 (Methodology & Capture Pipeline)...")
    build_slide4_methodology_pipeline(prs.slides[3])

    print("Updating Slide 5 (Dataset Portfolio - 95k Samples)...")
    build_slide5_dataset_portfolio(prs.slides[4])

    print("Updating Slide 6 (Mid-Sem Pilot vs Final Evolution)...")
    build_slide6_pilot_vs_final(prs.slides[5])

    print("Updating Slide 7 (Same-Network Results)...")
    build_slide7_same_network_results(prs.slides[6])

    print("Updating Slide 8 (Operational Imbalance - 8:4:4:2:2:1)...")
    build_slide8_operational_imbalance(prs.slides[7])

    print("Updating Slide 9 (Cross-Network Generalization & Meaningful Insight)...")
    build_slide9_cross_network_insight(prs.slides[8])

    print("Updating Slide 10 (Surveillance & Low-FPR Analysis)...")
    build_slide10_surveillance_low_fpr(prs.slides[9])

    print("Updating Slide 11 (Feature Importance)...")
    build_slide11_feature_importance(prs.slides[10])

    print("Updating Slide 12 (Feature Ablation & Size Invariance)...")
    build_slide12_ablation_study(prs.slides[11])

    print("Updating Slide 13 (Research Findings & Contributions)...")
    build_slide13_findings_and_references(prs.slides[12])

    print("Preserving Slide 1 (Title) and Slide 14 (Thank You).")
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    prs.save(OUTPUT_PATH)
    print("✅ Final Presentation successfully regenerated at:", OUTPUT_PATH)

if __name__ == '__main__':
    main()
