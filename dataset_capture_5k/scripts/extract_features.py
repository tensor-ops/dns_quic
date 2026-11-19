"""
Feature Extraction Pipeline for Real-World Encrypted DNS & Web Captures.
Extracts 5,000 samples per class (30,000 total packet samples) along with:
- Exact PCAP file location on disk (pcap_file, pcap_path)
- Capture vantage point and network location (capture_location, vantage_point)
- Csikor et al. / RM kinematic features (pkt_len, prev_pkt_len, time_lag, prev_time_lag)
- Canonical bidirectional flow statistical features.
"""

import os
import sys
from pathlib import Path
from typing import Dict, List
import pandas as pd

# Path configurations
SCRIPT_DIR = Path(__file__).resolve().parent
BASE_DIR = SCRIPT_DIR.parent
LAB_ROOT = Path("/Users/paru/paru/projects/encrypted-dns-lab")

if str(LAB_ROOT) not in sys.path:
    sys.path.insert(0, str(LAB_ROOT))
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from ml.data.pcap_extractor import PcapFeatureExtractor
from common import CAPTURE_LOCATION_INFO

CLASSES = ["DOH", "DOQ", "DOH3", "QUIC", "HTTPS_WEB", "HTTP3_WEB"]

CLASS_MAP = {
    "DOH": 0,
    "DOQ": 1,
    "DOH3": 2,
    "QUIC": 3,
    "HTTPS_WEB": 4,
    "HTTP3_WEB": 5,
}

CLASS_PROTOCOL = {
    "DOH": "TCP",
    "DOQ": "QUIC",
    "DOH3": "QUIC",
    "QUIC": "QUIC",
    "HTTPS_WEB": "TCP",
    "HTTP3_WEB": "QUIC",
}


def extract_features_from_captures(
    base_capture_dir: str = None,
    output_packet_csv: str = None,
    output_flow_csv: str = None,
    samples_per_class: int = 5000,
):
    if base_capture_dir is None:
        base_capture_dir = str(BASE_DIR / "captures")
    if output_packet_csv is None:
        output_packet_csv = str(BASE_DIR / "processed" / "dataset_packet_level_30k.csv")
    if output_flow_csv is None:
        output_flow_csv = str(BASE_DIR / "processed" / "dataset_flow_level.csv")

    extractor = PcapFeatureExtractor(min_packets_per_flow=2)
    capture_path = Path(base_capture_dir)

    all_packet_rows: List[Dict] = []
    all_flow_rows: List[Dict] = []

    print("=" * 80)
    print(f"[*] Starting Feature Extraction: Target {samples_per_class:,} Samples per Class")
    print(f"[*] Network Capture Location: {CAPTURE_LOCATION_INFO['vantage_point']} ({CAPTURE_LOCATION_INFO['interface_ip']})")
    print("=" * 80)

    for cls in CLASSES:
        cls_dir = capture_path / cls
        pcap_files = sorted(cls_dir.glob("*.pcap"))
        print(f"\n--- Processing Class: {cls} ({len(pcap_files)} PCAP files found) ---")
        
        cls_packet_rows = []
        cls_flow_rows = []

        for pcap_file in pcap_files:
            rel_pcap = str(pcap_file.relative_to(BASE_DIR))
            abs_pcap = str(pcap_file.resolve())

            try:
                # 1. Extract packet-level vectors
                df_csikor = extractor.pcap_to_csikor_dataframe(
                    str(pcap_file),
                    label=cls,
                    request_only=False
                )
                if not df_csikor.empty:
                    for _, r in df_csikor.iterrows():
                        row_dict = {
                            "Current packet size": int(r["pkt_len"]),
                            "Previous packet size": int(r["prev_pkt_len"]),
                            "Current time gap": float(r["time_lag"]),
                            "Previous time gap": float(r["prev_time_lag"]),
                            "traffic_class": cls,
                            "label": float(CLASS_MAP[cls]),
                            "protocol": CLASS_PROTOCOL[cls],
                            "flow_id": str(r["flow_id"]),
                            "direction": str(r["direction"]),
                            "pcap_file": rel_pcap,
                            "pcap_path": abs_pcap,
                            "capture_location": f"{CAPTURE_LOCATION_INFO['network_id']} ({CAPTURE_LOCATION_INFO['interface_ip']})",
                            "vantage_point": CAPTURE_LOCATION_INFO["vantage_point"]
                        }
                        cls_packet_rows.append(row_dict)

                # 2. Extract canonical flow-level features
                df_flows = extractor.pcap_to_canonical_dataframe(
                    str(pcap_file),
                    default_class=cls,
                    network_id=CAPTURE_LOCATION_INFO["network_id"]
                )
                if not df_flows.empty:
                    for flow_dict in df_flows.to_dict("records"):
                        flow_dict["pcap_file"] = rel_pcap
                        flow_dict["pcap_path"] = abs_pcap
                        flow_dict["capture_location"] = f"{CAPTURE_LOCATION_INFO['network_id']} ({CAPTURE_LOCATION_INFO['interface_ip']})"
                        flow_dict["vantage_point"] = CAPTURE_LOCATION_INFO["vantage_point"]
                        cls_flow_rows.append(flow_dict)

            except Exception as e:
                print(f"  [Warning] Failed to parse {pcap_file.name}: {e}")

        print(f"  -> Extracted {len(cls_packet_rows):,} raw packet vectors, {len(cls_flow_rows):,} flows for {cls}")

        selected_packets = cls_packet_rows[:samples_per_class]
        all_packet_rows.extend(selected_packets)
        all_flow_rows.extend(cls_flow_rows)

    # Save packet-level CSV
    df_packets = pd.DataFrame(all_packet_rows)
    out_pkt_path = Path(output_packet_csv)
    out_pkt_path.parent.mkdir(parents=True, exist_ok=True)
    df_packets.to_csv(out_pkt_path, index=False)
    print(f"\n[+] Saved Packet-Level Dataset: {out_pkt_path} ({len(df_packets):,} rows, {df_packets.shape[1]} columns)")

    # Save flow-level CSV
    df_flows = pd.DataFrame(all_flow_rows)
    out_flow_path = Path(output_flow_csv)
    out_flow_path.parent.mkdir(parents=True, exist_ok=True)
    df_flows.to_csv(out_flow_path, index=False)
    print(f"[+] Saved Flow-Level Dataset: {out_flow_path} ({len(df_flows):,} rows, {df_flows.shape[1]} columns)")

    # Also save master_final_dataset_30k.csv for direct compatibility with RM notebooks
    master_path = out_pkt_path.parent / "master_final_dataset_30k.csv"
    df_packets.to_csv(master_path, index=False)
    print(f"[+] Saved Master Final Dataset: {master_path}")

    return df_packets, df_flows


if __name__ == "__main__":
    extract_features_from_captures()

