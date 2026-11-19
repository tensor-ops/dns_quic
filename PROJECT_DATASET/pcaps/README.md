# PCAP Traces for Encrypted DNS & QUIC Protocols

**Directory:** `/Users/paru/paru/projects/RM/PROJECT_DATASET/pcaps`  
**Generated:** 2026-11-19 20:38 IST  
**Total PCAP Files:** 913  
**Target Classes (6):** `DOH`, `DOQ`, `DOH3`, `QUIC`, `HTTPS_WEB`, `HTTP3_WEB` (No DOT)

---

## Directory Organization

```
pcaps/
├── PRAYAGRAJ_AIRTEL/     (709 PCAPs)
│   ├── DOH/              (16 PCAPs)
│   ├── DOQ/              (20 PCAPs)
│   ├── DOH3/             (19 PCAPs)
│   ├── QUIC/             (209 PCAPs)
│   ├── HTTPS_WEB/        (184 PCAPs)
│   └── HTTP3_WEB/        (261 PCAPs)
│
├── PRAYAGRAJ_JIO/        (104 PCAPs)
│   ├── DOH/              (16 PCAPs)
│   ├── DOQ/              (8 PCAPs)
│   ├── DOH3/             (8 PCAPs)
│   ├── QUIC/             (16 PCAPs)
│   ├── HTTPS_WEB/        (32 PCAPs)
│   └── HTTP3_WEB/        (24 PCAPs)
│
├── TUMSAR_AIRTEL/        (76 PCAPs)
│   ├── DOH/              (8 PCAPs)
│   ├── DOQ/              (2 PCAPs)
│   ├── DOH3/             (2 PCAPs)
│   ├── QUIC/             (48 PCAPs)
│   ├── HTTPS_WEB/        (8 PCAPs)
│   └── HTTP3_WEB/        (8 PCAPs)
│
└── MIRZAPUR_JIO/         (24 PCAPs)
    ├── DOH/              (4 PCAPs)
    ├── DOQ/              (4 PCAPs)
    ├── DOH3/             (4 PCAPs)
    ├── QUIC/             (4 PCAPs)
    ├── HTTPS_WEB/        (4 PCAPs)
    └── HTTP3_WEB/        (4 PCAPs)
```

## Protocol Specifications

| Class | Transport Layer | Default Port | ALPN / Protocol |
|---|---|---|---|
| `DOH` | TCP | 443 | `h2` / RFC 8484 DNS over HTTPS |
| `DOQ` | UDP (QUIC) | 853 | `doq` / RFC 9250 DNS over QUIC |
| `DOH3` | UDP (QUIC) | 443 | `h3` / RFC 9114 DNS over HTTP/3 |
| `QUIC` | UDP (QUIC) | 443 | `hq-interop` / RFC 9000 QUIC Transport |
| `HTTPS_WEB` | TCP | 443 | TLS 1.3 / HTTP/2 Web |
| `HTTP3_WEB` | UDP (QUIC) | 443 | `h3` Web |
