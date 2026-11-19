"""
Master Dataset Generation Orchestrator (5,000 Samples per Class = 30,000 Total).
Coordinates:
1. Automated packet capture for 6 classes into captures/<CLASS>/
2. Observable feature extraction into processed/dataset_packet_level_30k.csv
3. Capture location metadata tracking (pcap_file, pcap_path, capture_location)
4. Comprehensive 8-point scientific validation
"""

import argparse
import sys
import time
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
BASE_DIR = SCRIPT_DIR.parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from capture_quic import run_quic_capture
from capture_doh import run_doh_capture
from capture_doq import run_doq_capture
from capture_doh3 import run_doh3_capture
from capture_https_web import run_https_web_capture
from capture_http3_web import run_http3_web_capture
from extract_features import extract_features_from_captures
from validate_dataset_5k import validate_capture_dataset_5k


def run_pipeline_5k(samples_per_class: int = 5000, base_dir: Path = BASE_DIR):
    captures_dir = base_dir / "captures"
    processed_dir = base_dir / "processed"
    reports_dir = base_dir / "reports"

    print("================================================================================")
    print("      RM ENCRYPTED DNS RESEARCH: 30,000-SAMPLE PACKET CAPTURE PIPELINE")
    print(f"      Target: 6 Classes × {samples_per_class:,} Samples = {6*samples_per_class:,} Total Samples")
    print("================================================================================")

    # 1. Packet Captures
    print("\n[PHASE 1/3] Generating Legitimate Network Traffic & Capturing Real PCAPs...")

    # Class 1: QUIC
    print("\n>>> Capturing Class 1: QUIC (RFC 9000 QUIC Transport, UDP 443/853)")
    run_quic_capture(target_samples=samples_per_class, output_dir=str(captures_dir / "QUIC"))

    # Class 2: DOH
    print("\n>>> Capturing Class 2: DOH (DNS-over-HTTPS, TCP 443)")
    run_doh_capture(target_samples=samples_per_class, output_dir=str(captures_dir / "DOH"))

    # Class 3: DOQ
    print("\n>>> Capturing Class 3: DOQ (DNS-over-QUIC, UDP 853)")
    run_doq_capture(target_samples=samples_per_class, output_dir=str(captures_dir / "DOQ"))

    # Class 4: DOH3
    print("\n>>> Capturing Class 4: DOH3 (DNS-over-HTTP/3, UDP 443)")
    run_doh3_capture(target_samples=samples_per_class, output_dir=str(captures_dir / "DOH3"))

    # Class 5: HTTPS_WEB
    print("\n>>> Capturing Class 5: HTTPS_WEB (Ordinary HTTPS Web, TCP 443)")
    run_https_web_capture(target_samples=samples_per_class, output_dir=str(captures_dir / "HTTPS_WEB"))

    # Class 6: HTTP3_WEB
    print("\n>>> Capturing Class 6: HTTP3_WEB (Modern HTTP/3 Web over QUIC, UDP 443)")
    run_http3_web_capture(target_samples=samples_per_class, output_dir=str(captures_dir / "HTTP3_WEB"))

    # 2. Feature Extraction with Capture Locations
    print("\n[PHASE 2/3] Extracting Features & Capture Locations from PCAP Traces...")
    extract_features_from_captures(
        base_capture_dir=str(captures_dir),
        output_packet_csv=str(processed_dir / "dataset_packet_level_30k.csv"),
        output_flow_csv=str(processed_dir / "dataset_flow_level.csv"),
        samples_per_class=samples_per_class,
    )

    # 3. Scientific Validation
    print("\n[PHASE 3/3] Executing Dataset Quality & Scientific Validation...")
    success = validate_capture_dataset_5k(
        packet_csv_path=str(processed_dir / "dataset_packet_level_30k.csv"),
        captures_dir=str(captures_dir),
        output_report=str(reports_dir / "validation_report.txt"),
        output_summary_csv=str(reports_dir / "capture_summary.csv"),
    )

    print("\n================================================================================")
    if success:
        print("      30,000-SAMPLE PIPELINE EXECUTION COMPLETED SUCCESSFULLY!")
    else:
        print("      PIPELINE EXECUTION COMPLETED WITH VALIDATION WARNINGS.")
    print("================================================================================")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="5k Per Class Encrypted DNS Capture Pipeline")
    parser.add_argument("--samples", "-s", type=int, default=5000, help="Target samples per class (default: 5000)")
    args = parser.parse_args()

    run_pipeline_5k(samples_per_class=args.samples)

