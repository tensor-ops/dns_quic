# Final Combined Encrypted-DNS & QUIC Dataset

**Updated:** 2026-11-19 · Research Project: Encrypted DNS Traffic Intelligence

---

## Overview

`final_combined_dataset.csv` merges **all real packet captures** from both
physical vantage points into a single, deduplicated, ML-ready CSV file.

In accordance with protocol requirements, **DOT (DNS-over-TLS) has been completely removed**,
and replaced by **QUIC (RFC 9000 QUIC Transport Protocol)** across both Prayagraj and Tumsar vantage points.

| Metric | Value |
|---|---|
| Total samples | **36,928** |
| Traffic classes | **6** (`DOH`, `DOQ`, `DOH3`, `QUIC`, `HTTPS_WEB`, `HTTP3_WEB`) |
| Vantage points | **2** (`Prayagraj_Airtel_Tap`, `Tumsar_Docker_Tap`) |
| Missing values | 0 |
| Exact duplicates | 0 (deduplicated across all features) |

---

## Vantage Points

| Vantage Point | Location | Network | Interface IP | Samples |
|---|---|---|---|---|
| `Prayagraj_Airtel_Tap` | Prayagraj, Uttar Pradesh, India | Airtel AS45609 | 172.17.246.115 | 30,000 captured → **29,398 after dedup** |
| `Tumsar_Docker_Tap` | Tumsar, Bhandara District, Maharashtra, India | Docker Bridge eth0 | 172.17.0.2 | 8,399 captured → **7,530 after dedup** |

---

## Class Distribution

| Label | Class | Prayagraj | Tumsar | Total |
|---|---|---|---|---|
| 0 | DOH | 4,984 | 1,185 | **6,169** |
| 1 | DOQ | 4,987 | 440 | **5,427** |
| 2 | DOH3 | 4,983 | 443 | **5,426** |
| 3 | QUIC | 4,803 | 1,464 | **6,267** |
| 4 | HTTPS_WEB | 4,819 | 1,998 | **6,817** |
| 5 | HTTP3_WEB | 4,822 | 2,000 | **6,822** |
| — | **TOTAL** | **29,398** | **7,530** | **36,928** |

---

## Column Schema

| Column | Type | Description |
|---|---|---|
| `Current packet size` | int | Size of the current packet in bytes |
| `Previous packet size` | int | Size of the immediately preceding packet in the flow |
| `Current time gap` | float | Inter-arrival time from previous → current packet (seconds) |
| `Previous time gap` | float | Inter-arrival time two packets back (seconds) |
| `traffic_class` | str | Protocol class label (DOH / DOQ / DOH3 / QUIC / HTTPS_WEB / HTTP3_WEB) |
| `label` | int | Numeric label (0–5), consistent across both vantage points |
| `capture_location` | str | Lab identifier + interface IP |
| `vantage_point` | str | Short vantage-point key |
| `city` | str | Physical city of capture (Prayagraj / Tumsar) |
| `state` | str | State/province of capture (Uttar Pradesh / Maharashtra) |
| `geolocation` | str | Full location string with timezone |
| `network_id` | str | Network/ISP identifier |
| `interface_ip` | str | Interface IP at time of capture |

> **Zero-leakage policy:** No IP addresses, ports, SNI, ALPN, DNS query content,
> or payload data are included in ML feature vectors. Only observable packet-timing and size metadata.
