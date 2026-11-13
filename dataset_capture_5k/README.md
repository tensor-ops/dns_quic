# Real-World Encrypted DNS Traffic Dataset (5,000 Samples Per Class = 30,000 Total)

A comprehensive real-world dataset of network traffic captured from genuine public encrypted DNS and Web endpoints across 6 classes:
1. `DOH`: DNS-over-HTTPS (RFC 8484) on TCP 443
2. `DOQ`: DNS-over-QUIC (RFC 9250) on UDP 853
3. `DOT`: DNS-over-TLS (RFC 7858) on TCP 853
4. `DOH3`: DNS-over-HTTP/3 (RFC 9114) on UDP 443
5. `HTTPS_WEB`: Encrypted Web browsing via TLS 1.3 / HTTP/2 on TCP 443
6. `HTTP3_WEB`: Modern Web browsing via HTTP/3 over QUIC on UDP 443

---

## 🏛️ Directory Structure

```text
dataset_capture_5k/
├── config/
│   └── capture_config.yaml
├── scripts/
│   ├── common.py
│   ├── capture_dot.py
│   ├── capture_doh.py
│   ├── capture_doq.py
│   ├── capture_doh3.py
│   ├── capture_https_web.py
│   ├── capture_http3_web.py
│   ├── extract_features.py
│   ├── generate_dataset_5k.py
│   └── validate_dataset_5k.py
├── captures/
│   ├── DOH/
│   ├── DOQ/
│   ├── DOT/
│   ├── DOH3/
│   ├── HTTPS_WEB/
│   └── HTTP3_WEB/
├── processed/
│   ├── dataset_packet_level_30k.csv      # Exactly 30,000 packet vectors
│   ├── dataset_flow_level.csv            # Reconstructed flows
│   └── master_final_dataset_30k.csv      # Multiclass dataset for RM ML models
├── reports/
│   ├── capture_summary.csv
│   ├── validation_report.txt
│   └── capture_locations.md
└── README.md
```

---

## 🚀 Execution Commands

```bash
cd /Users/paru/paru/projects/RM/dataset_capture_5k

# Run full capture and feature generation (5k per class)
python3 scripts/generate_dataset_5k.py --samples 5000

# Re-extract features with capture location metadata
python3 scripts/extract_features.py

# Re-run scientific validation
python3 scripts/validate_dataset_5k.py
```

