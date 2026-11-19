# Multi-Vantage Point & Multi-ISP Encrypted DNS / QUIC Datasets

**Location:** `/Users/paru/paru/projects/RM/PROJECT_DATASET`  
**Generated:** 2026-11-19 20:30 IST  
**Traffic Classes (6):** `DOH`, `DOQ`, `DOH3`, `QUIC`, `HTTPS_WEB`, `HTTP3_WEB` (DOT protocol completely removed)

---

## 1. Directory Structure

This folder contains the complete multi-vantage point hierarchy partitioned across locations (**Prayagraj**, **Tumsar**, **Mirzapur**) and service providers (**Airtel AS45609**, **Jio AS55836**).

| Dataset Name | File Path | Records | Vantage Point & Network |
|---|---|---|---|
| **PRAYAGRAJ AIRTEL COMBINED** | `PRAYAGRAJ_AIRTEL_COMBINED.csv` | 30,000 | Prayagraj, UP · Airtel AS45609 (5,000 / class balanced) |
| **PRAYAGRAJ JIO COMBINED** | `PRAYAGRAJ_JIO_COMBINED.csv` | 26,000 | Prayagraj, UP · Reliance Jio AS55836 |
| **TUMSAR AIRTEL COMBINED** | `TUMSAR_AIRTEL_COMBINED.csv` | 8,399 | Tumsar, Maharashtra · Airtel / Docker Lab |
| **MIRZAPUR JIO COMBINED** | `MIRZAPUR_JIO_COMBINED.csv` | 6,000 | Mirzapur, UP · Reliance Jio AS55836 (1,000 / class) |
| **JIO COMBINED** | `JIO_COMBINED.csv` | 32,000 | All Jio vantage points (Prayagraj Jio + Mirzapur Jio) |
| **AIRTEL COMBINED** | `AIRTEL_COMBINED.csv` | 38,399 | All Airtel vantage points (Prayagraj Airtel + Tumsar Airtel) |
| **FULL COMBINED** | `FULL_COMBINED.csv` | **70,399** | Complete 4-vantage point unified dataset |

*(Each dataset is provided in the standard 5-column format, with a companion `*_WITH_METADATA.csv` that includes `city`, `isp`, `vantage_point`, `state`, and `label`).*

---

## 2. Per-Class Sample Distribution

| Traffic Class | Prayagraj Airtel | Prayagraj Jio | Tumsar Airtel | Mirzapur Jio | Jio Combined | Airtel Combined | Full Combined |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **DOH** | 5,000 | 4,000 | 1,986 | 1,000 | 5,000 | 6,986 | **11,986** |
| **DOQ** | 5,000 | 2,000 | 460 | 1,000 | 3,000 | 5,460 | **8,460** |
| **DOH3** | 5,000 | 2,000 | 452 | 1,000 | 3,000 | 5,452 | **8,452** |
| **QUIC** | 5,000 | 4,000 | 1,501 | 1,000 | 5,000 | 6,501 | **11,501** |
| **HTTPS_WEB** | 5,000 | 8,000 | 2,000 | 1,000 | 9,000 | 7,000 | **16,000** |
| **HTTP3_WEB** | 5,000 | 6,000 | 2,000 | 1,000 | 7,000 | 7,000 | **14,000** |
| **TOTAL** | **30,000** | **26,000** | **8,399** | **6,000** | **32,000** | **38,399** | **70,399** |

---

## 3. Schema Reference

### 5-Core Feature Columns (Plug-and-play with uploaded CSVs):
1. `Current packet size` (int): Byte size of the observed packet.
2. `Previous packet size` (int): Byte size of the immediately preceding packet in flow.
3. `Current time gap` (float): Inter-arrival delta $t_i - t_{i-1}$ in seconds.
4. `Previous time gap` (float): Inter-arrival delta $t_{i-1} - t_{i-2}$ in seconds.
5. `traffic_class` (str): Protocol label (`DOH`, `DOQ`, `DOH3`, `QUIC`, `HTTPS_WEB`, `HTTP3_WEB`).

### Metadata Columns (in `*_WITH_METADATA.csv`):
6. `label` (int): Standard numeric class index (0: DOH, 1: DOQ, 2: DOH3, 3: QUIC, 4: HTTPS_WEB, 5: HTTP3_WEB).
7. `city` (str): Capture municipality (`Prayagraj`, `Tumsar`, `Mirzapur`).
8. `isp` (str): Service provider (`Airtel`, `Jio`).
9. `vantage_point` (str): Unique monitoring tap identifier.
10. `state` (str): State/province (`Uttar Pradesh`, `Maharashtra`).

> **Zero-Leakage Guarantee:** No IP addresses, port numbers, SNI, ALPN strings, or payload content are present in the feature columns.
