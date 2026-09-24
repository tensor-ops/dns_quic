#!/usr/bin/env python3
"""
Encrypted DNS Traffic Dataset Generator (Compact 4-Feature Mode)
================================================================

Generates a single compact CSV containing only the 4 sequential packet features:
- Current packet size
- Previous packet size
- Current time gap
- Previous time gap
- traffic_class (target label)

Traffic Classes:
    - HTTPS_WEB   (HTTPS over TCP/TLS)
    - HTTP3_WEB   (HTTP/3 over QUIC)
    - DOH         (DNS over HTTPS)
    - DOH3        (DNS over HTTPS/3)
    - DOQ         (DNS over QUIC)

Usage:
    python generate_dataset.py [--output-dir dataset]
"""

import argparse
import random
from pathlib import Path

import numpy as np
import pandas as pd

RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)
random.seed(RANDOM_SEED)

TRAFFIC_CLASSES = [
    "HTTPS_WEB",
    "HTTP3_WEB",
    "DOH",
    "DOH3",
    "DOQ",
]

CLASS_PROFILES = {
    "HTTPS_WEB": dict(mean_pkt=900, std_pkt=350, mean_iat=0.020, std_iat=0.015, pkt_count=120),
    "HTTP3_WEB": dict(mean_pkt=850, std_pkt=300, mean_iat=0.018, std_iat=0.012, pkt_count=110),
    "DOH":       dict(mean_pkt=220, std_pkt=80,  mean_iat=0.035, std_iat=0.020, pkt_count=8),
    "DOH3":      dict(mean_pkt=210, std_pkt=70,  mean_iat=0.032, std_iat=0.018, pkt_count=7),
    "DOQ":       dict(mean_pkt=195, std_pkt=65,  mean_iat=0.028, std_iat=0.015, pkt_count=6),
}


def generate_flow_packets(label: str, profile: dict) -> list:
    """Generate per-packet sequential records for a flow."""
    n = profile["pkt_count"]
    iats = np.abs(np.random.normal(profile["mean_iat"], profile["std_iat"], n))
    iats[0] = 0.0

    sizes = np.clip(
        np.random.normal(profile["mean_pkt"], profile["std_pkt"], n).astype(int),
        a_min=54,
        a_max=1460,
    )

    rows = []
    for i in range(n):
        cur_size = int(sizes[i])
        prev_size = int(sizes[i - 1]) if i > 0 else 0
        cur_gap = round(float(iats[i]), 6)
        prev_gap = round(float(iats[i - 1]), 6) if i > 0 else 0.0

        rows.append({
            "Current packet size": cur_size,
            "Previous packet size": prev_size,
            "Current time gap": cur_gap,
            "Previous time gap": prev_gap,
            "traffic_class": label,
        })
    return rows


def build_dataset(output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    all_rows = []

    for label in TRAFFIC_CLASSES:
        profile = CLASS_PROFILES[label]
        rows = generate_flow_packets(label, profile)
        all_rows.extend(rows)

    df = pd.DataFrame(all_rows)
    target_csv = output_dir / "dataset.csv"
    df.to_csv(target_csv, index=False)
    print(f"✓ Saved compact dataset: {target_csv} ({len(df)} rows, {len(df.columns)} columns)")
    print(f"  Features: {[c for c in df.columns if c != 'traffic_class']}")
    print(f"  Target: traffic_class ({df['traffic_class'].nunique()} classes)")
    return target_csv


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate compact 4-feature Encrypted DNS dataset."
    )
    parser.add_argument(
        "--output-dir",
        default="dataset",
        help="Root output directory (default: dataset/)",
    )
    args = parser.parse_args()
    build_dataset(Path(args.output_dir))
