# Multi-Vantage Point Capture Provenance Report

This repository contains network traffic captured from two distinct geographical and network vantage points in India:
1. **Vantage Point 1 (Current 30,000-Sample Capture)**: Prayagraj, Uttar Pradesh
2. **Vantage Point 2 (Historical September 2026 Captures)**: Tumsar, Maharashtra

---

## 1. Vantage Point 1: Prayagraj, Uttar Pradesh (Current 30k Dataset)

- **Location**: Prayagraj (Allahabad), Eastern Uttar Pradesh, India (`UTC+05:30`)
- **Network Interface**: `en0` (`172.17.246.115` on subnet `172.17.246.0/24`)
- **Carrier / ISP**: Bharti Airtel Ltd. (`AS45609`) via Gateway `223.189.244.49`
- **Classes Captured**: All 6 canonical classes (`DOH`, `DOQ`, `DOT`, `DOH3`, `HTTPS_WEB`, `HTTP3_WEB`)
- **Dataset Scale**: Exactly 5,000 samples per class = 30,000 total packet vectors
- **Raw PCAP Traces (684 files)**:
  - `RM/dataset_capture_5k/captures/DOH/` (16 PCAPs)
  - `RM/dataset_capture_5k/captures/DOQ/` (20 PCAPs)
  - `RM/dataset_capture_5k/captures/DOT/` (184 PCAPs)
  - `RM/dataset_capture_5k/captures/DOH3/` (19 PCAPs)
  - `RM/dataset_capture_5k/captures/HTTPS_WEB/` (184 PCAPs)
  - `RM/dataset_capture_5k/captures/HTTP3_WEB/` (261 PCAPs)
- **Processed Datasets**:
  - `RM/dataset_capture_5k/processed/dataset_packet_level_30k.csv` (30,000 packet vectors)
  - `RM/dataset_capture_5k/processed/dataset_flow_level.csv` (461 bidirectional flows)
  - `RM/dataset_capture_5k/processed/master_final_dataset_30k.csv` (Ready for ML training)

---

## 2. Vantage Point 2: Tumsar, Maharashtra (Historical Captures)

These are the previous real-world captures collected in late September 2026:

- **Location**: Tumsar, Bhandara District, Maharashtra, India
- **Capture Pipeline**: Firefox automation with Geckodriver and Docker container network tap (`eth0` on Docker bridge `172.17.0.2`)
- **Target Protocols**: DoH, DoQ, DoH/3, HTTPS Web, HTTP/3 Web
- **Raw PCAP Traces (Over 2.5 GB of PCAP files)**:
  - `RM/Docker_dataset/doh_docker/host_pcaps/capture-5-801-1000.pcap` (**1.36 GB**)
  - `RM/Docker_dataset/doh_docker/host_pcaps/capture-6-1001-1200` (**193 MB**)
  - `RM/Docker_dataset/doh_docker/host_pcaps/pcap/pcap/capture-5-801-1000` (**976 MB**)
- **Batch TShark CSVs**:
  - `RM/Docker_dataset/doh_docker/host_pcaps/csvfile-1-1-200.csv` (**17.1 MB**)
  - `RM/Docker_dataset/doh_docker/host_pcaps/csvfile-3-401-600.csv` (**24.3 MB**)
  - `RM/Docker_dataset/doh_docker/full_features_dataset.csv` (**36.4 MB**)
- **Processed Master Datasets**:
  - `RM/Docker_dataset/doh_docker/master_dataset.csv` (3,392 samples)
  - `RM/notebooks/final_multiprotocol_dataset.csv` (4,346 samples)
  - `RM/Docker_dataset/doh_docker/master_final_dataset.csv` (6,898 combined packet samples across 289 flows)
  - `RM/notebooks/master_final_dataset.csv` (Synchronized master copy)

---

## 3. Cross-Vantage Point Research Value

Having captures from both **Tumsar, Maharashtra** and **Prayagraj, Uttar Pradesh** enables **cross-network and cross-regional invariance evaluation**:
- Models trained on Prayagraj traffic can be tested against Tumsar traffic (and vice-versa) to scientifically prove that the observable feature representations generalize across different geographical regions, access networks, and routing latencies.
