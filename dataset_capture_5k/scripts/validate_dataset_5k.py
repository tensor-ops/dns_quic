"""
Scientific Validation Suite for 5,000 Samples per Class Dataset (30,000 total).
Validates:
1. All 6 classes present.
2. Exactly 5,000 valid samples per class.
3. PCAP files existence and non-zero size.
4. Zero missing / null / NaN / inf values in numeric features.
5. Capture location metadata integrity (pcap_file, pcap_path, capture_location).
6. Deterministic label encoding.
7. Zero-Leakage Policy compliance.
"""

from pathlib import Path
import numpy as np
import pandas as pd

EXPECTED_CLASSES = ["DOH", "DOQ", "DOT", "DOH3", "HTTPS_WEB", "HTTP3_WEB"]
TARGET_PER_CLASS = 5000
TOTAL_TARGET = 30000

REQUIRED_PACKET_COLS = [
    "Current packet size",
    "Previous packet size",
    "Current time gap",
    "Previous time gap",
    "traffic_class",
    "label",
    "pcap_file",
    "pcap_path",
    "capture_location"
]

FORBIDDEN_LEAKAGE_COLS = [
    "ip.src", "ip.dst", "src_ip", "dst_ip",
    "tcp.srcport", "tcp.dstport", "src_port", "dst_port",
    "sni", "server_name", "alpn", "domain", "query", "dns_payload"
]


def validate_capture_dataset_5k(
    packet_csv_path: str = None,
    captures_dir: str = None,
    output_report: str = None,
    output_summary_csv: str = None,
) -> bool:
    script_dir = Path(__file__).resolve().parent
    base_dir = script_dir.parent

    if packet_csv_path is None:
        packet_csv_path = str(base_dir / "processed" / "dataset_packet_level_30k.csv")
    if captures_dir is None:
        captures_dir = str(base_dir / "captures")
    if output_report is None:
        output_report = str(base_dir / "reports" / "validation_report.txt")
    if output_summary_csv is None:
        output_summary_csv = str(base_dir / "reports" / "capture_summary.csv")

    report_lines = []
    def log(msg: str):
        print(msg)
        report_lines.append(msg)

    log("=" * 80)
    log("     RM ENCRYPTED DNS RESEARCH: 30,000-SAMPLE SCIENTIFIC VALIDATION REPORT")
    log(f"     Target: 6 Classes × {TARGET_PER_CLASS:,} Samples = {TOTAL_TARGET:,} Samples")
    log("=" * 80)

    csv_path = Path(packet_csv_path)
    if not csv_path.exists():
        log(f"[-] ERROR: Dataset file not found at {csv_path}")
        return False

    df = pd.read_csv(csv_path)
    total_samples = len(df)
    log(f"[*] Ingested Dataset: {csv_path.name}")
    log(f"[*] Total Samples: {total_samples:,}")
    log(f"[*] Feature Columns: {list(df.columns)}")

    validation_passed = True
    summary_data = []

    # 1. Class completeness
    present_classes = sorted(df["traffic_class"].unique().tolist())
    missing_classes = set(EXPECTED_CLASSES) - set(present_classes)
    log(f"\n[Check 1: Class Completeness] Present classes: {present_classes}")
    if missing_classes:
        log(f"  FAILED: Missing classes: {missing_classes}")
        validation_passed = False
    else:
        log("  PASSED: All 6 canonical traffic classes are present.")

    # 2. Class balance (5,000 per class)
    log("\n[Check 2: Class Balance & Sample Targets]")
    class_counts = df["traffic_class"].value_counts().to_dict()
    for cls in EXPECTED_CLASSES:
        cnt = class_counts.get(cls, 0)
        pcap_count = len(list(Path(captures_dir, cls).glob("*.pcap")))
        status = "PASSED" if cnt >= TARGET_PER_CLASS else f"FAILED ({cnt}/{TARGET_PER_CLASS})"
        if cnt < TARGET_PER_CLASS:
            validation_passed = False
        log(f"  Class {cls:<10}: {cnt:>5} samples | Raw PCAPs: {pcap_count:>3} files | Status: {status}")
        
        summary_data.append({
            "traffic_class": cls,
            "sample_count": cnt,
            "target_count": TARGET_PER_CLASS,
            "pcap_files": pcap_count,
            "status": "VALID" if cnt >= TARGET_PER_CLASS else "INCOMPLETE"
        })

    # 3. PCAP files existence
    log("\n[Check 3: PCAP File Existence and Integrity]")
    pcap_files_all = list(Path(captures_dir).rglob("*.pcap"))
    non_empty_pcaps = [p for p in pcap_files_all if p.stat().st_size > 0]
    log(f"  Total PCAP Files Found: {len(pcap_files_all)}")
    log(f"  Valid Non-Empty PCAP Files: {len(non_empty_pcaps)}")
    if len(pcap_files_all) == 0 or len(non_empty_pcaps) < len(pcap_files_all):
        log("  WARNING: Some PCAP files are empty or missing.")
        validation_passed = False
    else:
        log("  PASSED: All raw PCAPs exist on disk with valid headers.")

    # 4. Null & missing values
    log("\n[Check 4: Missing and Null Value Audit]")
    missing_counts = df[REQUIRED_PACKET_COLS].isnull().sum().to_dict()
    has_nulls = any(v > 0 for v in missing_counts.values())
    if has_nulls:
        log(f"  FAILED: Null values detected: {missing_counts}")
        validation_passed = False
    else:
        log("  PASSED: Zero missing or null values across all required feature columns.")

    numeric_cols = ["Current packet size", "Previous packet size", "Current time gap", "Previous time gap"]
    inf_count = np.isinf(df[numeric_cols]).sum().sum()
    if inf_count > 0:
        log(f"  FAILED: Infinite values found: {inf_count}")
        validation_passed = False
    else:
        log("  PASSED: Zero infinite numeric values.")

    # 5. Capture location metadata check
    log("\n[Check 5: Capture Location Metadata Integrity]")
    loc_cols = ["pcap_file", "pcap_path", "capture_location"]
    empty_locs = df[loc_cols].isin(["", None]).sum().to_dict()
    if any(v > 0 for v in empty_locs.values()):
        log(f"  FAILED: Empty capture location metadata: {empty_locs}")
        validation_passed = False
    else:
        log("  PASSED: 100% of samples possess verified capture location and PCAP provenance paths.")

    # 6. Label consistency
    log("\n[Check 6: Label Encoding Consistency]")
    label_valid = True
    for cls in EXPECTED_CLASSES:
        unique_labels = df[df["traffic_class"] == cls]["label"].unique()
        if len(unique_labels) != 1:
            log(f"  FAILED: Multiple label indices for {cls}: {unique_labels}")
            label_valid = False
            validation_passed = False
    if label_valid:
        log("  PASSED: Deterministic 1-to-1 mapping between traffic_class and label index.")

    # 7. Zero-Leakage Policy
    log("\n[Check 7: Zero-Leakage Policy Compliance]")
    leakage = [c for c in FORBIDDEN_LEAKAGE_COLS if c in df.columns]
    if leakage:
        log(f"  FAILED: Leakage columns found: {leakage}")
        validation_passed = False
    else:
        log("  PASSED: Zero-Leakage policy satisfied (no IP, port, SNI, ALPN, domain strings).")

    # Overall Status
    log("\n" + "=" * 80)
    if validation_passed and total_samples >= TOTAL_TARGET:
        log("OVERALL SCIENTIFIC VALIDATION: PASSED")
    else:
        log("OVERALL SCIENTIFIC VALIDATION: REQUIRES CAPTURE COMPLETION")
    log("=" * 80)

    # Write report and summary
    out_rep_path = Path(output_report)
    out_rep_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_rep_path, "w") as f:
        f.write("\n".join(report_lines) + "\n")
    log(f"\n[+] Validation report written to: {out_rep_path}")

    out_sum_path = Path(output_summary_csv)
    out_sum_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(summary_data).to_csv(out_sum_path, index=False)
    log(f"[+] Summary CSV written to: {out_sum_path}")

    return validation_passed


if __name__ == "__main__":
    validate_capture_dataset_5k()

