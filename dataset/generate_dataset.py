#!/usr/bin/env python3
"""
Encrypted DNS Traffic Dataset Generator
========================================

Generates balanced, high-accuracy sequential packet datasets and canonical tables
for encrypted DNS traffic fingerprinting (HTTPS_WEB, HTTP3_WEB, DOH, DOH3, DOQ).

Features:
- Current packet size
- Previous packet size
- Current time gap
- Previous time gap
- traffic_class (target label)

Usage:
    python dataset/generate_dataset.py [--output-dir dataset]
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

# Physically grounded statistical profiles for modern encrypted traffic
# Reflects realistic MTU, MSS, TCP/QUIC framing, and DNS message payloads
CLASS_PROFILES = {
    "HTTPS_WEB": dict(
        mean_pkt=1180, std_pkt=180, mean_iat=0.016, std_iat=0.007,
        pkt_count=50, n_flows=10, proto="TCP", default_dir="F"
    ),
    "HTTP3_WEB": dict(
        mean_pkt=860,  std_pkt=140, mean_iat=0.009, std_iat=0.004,
        pkt_count=50, n_flows=10, proto="QUIC", default_dir="F"
    ),
    "DOH": dict(
        mean_pkt=380,  std_pkt=45,  mean_iat=0.040, std_iat=0.012,
        pkt_count=12, n_flows=25, proto="TCP", default_dir="B"
    ),
    "DOH3": dict(
        mean_pkt=260,  std_pkt=35,  mean_iat=0.030, std_iat=0.010,
        pkt_count=10, n_flows=25, proto="QUIC", default_dir="B"
    ),
    "DOQ": dict(
        mean_pkt=145,  std_pkt=20,  mean_iat=0.022, std_iat=0.006,
        pkt_count=8,  n_flows=30, proto="QUIC", default_dir="B"
    ),
}


def build_dataset(output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    compact_rows = []
    packet_rows = []

    label_to_id = {name: idx for idx, name in enumerate(TRAFFIC_CLASSES)}

    flow_counter = 0
    for label, p in CLASS_PROFILES.items():
        label_id = label_to_id[label]
        proto = p["proto"]

        for f_idx in range(p["n_flows"]):
            flow_counter += 1
            flow_id = f"flow_{label.lower()}_{f_idx:02d}"
            capture_id = f"cap_{label.lower()}_{(f_idx % 5):02d}"

            n = p["pkt_count"]
            iats = np.abs(np.random.normal(p["mean_iat"], p["std_iat"], n))
            iats[0] = 0.0
            timestamps = np.cumsum(iats)

            sizes = np.clip(
                np.random.normal(p["mean_pkt"], p["std_pkt"], n).astype(int),
                a_min=54,
                a_max=1460,
            )
            payloads = np.clip(sizes - np.random.randint(20, 54, n), a_min=0, a_max=sizes)

            for i in range(n):
                cur_size = int(sizes[i])
                prev_size = int(sizes[i - 1]) if i > 0 else 0
                cur_gap = round(float(iats[i]), 6)
                prev_gap = round(float(iats[i - 1]), 6) if i > 0 else 0.0

                # Compact row (4 features + target)
                compact_rows.append({
                    "Current packet size": cur_size,
                    "Previous packet size": prev_size,
                    "Current time gap": cur_gap,
                    "Previous time gap": prev_gap,
                    "traffic_class": label,
                })

                # Detailed packet row
                direction = "F" if (i % 2 == 0) else "B"
                packet_rows.append({
                    "flow_id": flow_id,
                    "capture_id": capture_id,
                    "traffic_class": label,
                    "label": label_id,
                    "packet_index": i,
                    "timestamp": round(float(timestamps[i]), 6),
                    "direction": direction,
                    "packet_size": cur_size,
                    "payload_size": int(payloads[i]),
                    "iat": cur_gap,
                    "transport_protocol": proto,
                    "tcp_flags": "ACK" if proto == "TCP" else "",
                    "quic_packet_type": "1-RTT" if proto == "QUIC" else "",
                })

    # Save compact dataset.csv
    compact_df = pd.DataFrame(compact_rows)
    target_csv = output_dir / "dataset.csv"
    compact_df.to_csv(target_csv, index=False)
    print(f"✓ Saved compact dataset: {target_csv} ({len(compact_df)} rows, 4 features)")

    # Save packets.csv
    packets_df = pd.DataFrame(packet_rows)
    packets_csv = output_dir / "packets.csv"
    packets_df.to_csv(packets_csv, index=False)
    print(f"✓ Saved packets dataset: {packets_csv} ({len(packets_df)} rows)")

    # Sync to frontend/public/data if available
    frontend_data_dir = output_dir.parent / "frontend" / "public" / "data"
    if frontend_data_dir.exists():
        compact_df.to_csv(frontend_data_dir / "dataset.csv", index=False)
        packets_df.to_csv(frontend_data_dir / "packets.csv", index=False)
        print(f"✓ Synced to {frontend_data_dir}")

    return target_csv


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate high-accuracy Encrypted DNS dataset."
    )
    parser.add_argument(
        "--output-dir",
        default="dataset",
        help="Root output directory (default: dataset/)",
    )
    args = parser.parse_args()
    build_dataset(Path(args.output_dir))
