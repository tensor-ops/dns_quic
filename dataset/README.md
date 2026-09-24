# Encrypted DNS Traffic Fingerprinting — Dataset

This directory contains the dataset pipeline for the research project:

> **Can Modern Encrypted DNS Hide Among Encrypted Web Traffic?**

The objective is to construct a reproducible traffic dataset to determine whether **DoH, DoH/3, and DoQ traffic can be distinguished from ordinary encrypted Web traffic using only encrypted-traffic metadata**.

---

## 1. Traffic Classes

| Class ID | Label | Protocol |
|---:|---|---|
| 0 | `HTTPS_WEB` | HTTPS over TCP/TLS |
| 1 | `HTTP3_WEB` | HTTP/3 over QUIC |
| 2 | `DOH` | DNS over HTTPS |
| 3 | `DOH3` | DNS over HTTPS/3 |
| 4 | `DOQ` | DNS over QUIC |

The primary research question is:

> **Can encrypted DNS traffic be identified from observable traffic metadata even when payload and application content are encrypted?**

---

## 2. Dataset Pipeline

```text
Raw PCAP Files
      |
      v
Packet Extraction
      |
      v
Flow Reconstruction
      |
      v
Packet-Level Dataset
      |
      v
Feature Extraction
      |
      +----------------------+
      |                      |
      v                      v
Full Feature Dataset   Fingerprint Dataset
      |                      |
      +----------+-----------+
                 |
                 v
          Machine Learning
```

---

## 3. Directory Structure

```text
dataset/
|
├── README.md
|
├── raw/
│   ├── HTTPS_WEB/
│   ├── HTTP3_WEB/
│   ├── DOH/
│   ├── DOH3/
│   └── DOQ/
|
├── packets/
│   └── packets.parquet
|
├── flows/
│   └── flows.parquet
|
├── features/
│   ├── full_features.csv
│   ├── fingerprint_features.csv
│   └── early_packets.csv
|
├── metadata/
│   ├── experiments.csv
│   ├── captures.csv
│   └── networks.csv
|
└── splits/
    ├── train.csv
    ├── validation.csv
    └── test.csv
```

---

## 4. Raw PCAP Dataset

The `raw/` directory contains the original packet captures.

```text
raw/
├── HTTPS_WEB/
├── HTTP3_WEB/
├── DOH/
├── DOH3/
└── DOQ/
```

Each traffic class should contain multiple independent captures.

Example:

```text
raw/
└── DOQ/
    ├── capture_0001.pcapng
    ├── capture_0002.pcapng
    ├── capture_0003.pcapng
    └── ...
```

Raw PCAP files are the **source of truth** and should never be overwritten during preprocessing.

---

## 5. Capture Naming Convention

Recommended format:

```text
<CAPTURE_CLASS>_<NETWORK>_<REPETITION>.pcapng
```

Examples:

```text
DOH_WIFI_001.pcapng
DOH_WIFI_002.pcapng
DOQ_WIFI_001.pcapng
HTTP3_WEB_WIFI_001.pcapng
HTTPS_WEB_WIFI_001.pcapng
```

If multiple devices or networks are used:

```text
DOH_WIFI_DEV01_001.pcapng
DOH_WIFI_DEV02_001.pcapng
DOQ_MOBILE_DEV01_001.pcapng
```

---

## 6. Packet-Level Dataset

File:

```text
packets/packets.parquet
```

Each row represents one packet.

### Recommended Schema

| Column | Type | Description |
|---|---|---|
| `flow_id` | string | Parent flow identifier |
| `packet_index` | integer | Packet order within flow |
| `timestamp` | float | Relative timestamp |
| `direction` | categorical | `F` or `B` |
| `packet_size` | integer | Total packet length |
| `payload_size` | integer | Encrypted payload length |
| `iat` | float | Inter-arrival time |
| `transport_protocol` | categorical | TCP/QUIC |
| `tcp_flags` | string | TCP flags when available |
| `quic_packet_type` | string | QUIC packet type when observable |

### Timestamp Rule

Use relative timestamps:

```text
relative_time = packet_timestamp - first_packet_timestamp
```

Example:

```text
0.000000
0.001234
0.003821
0.011241
```

Do not use absolute capture timestamps as ML features.

---

## 7. Flow-Level Dataset

File:

```text
flows/flows.parquet
```

Each row represents one bidirectional flow.

### Recommended Schema

```text
flow_id
capture_id
traffic_class
transport_protocol
start_time
end_time
duration
packet_count
forward_packet_count
backward_packet_count
total_bytes
forward_bytes
backward_bytes
```

The `flow_id` must uniquely connect packet-level and flow-level records.

---

## 8. Direction Definition

Traffic direction is represented as:

```text
F = client -> server
B = server -> client
```

Example:

```text
packet_index    direction
0               F
1               B
2               B
3               F
4               F
```

Source and destination IP addresses should not be used as ML features.

---

## 9. Full Feature Dataset

File:

```text
features/full_features.csv
```

This dataset contains the complete set of extracted traffic statistics.

### Flow Statistics

```text
duration
packet_count
forward_packet_count
backward_packet_count
total_bytes
forward_bytes
backward_bytes
```

### Packet-Size Statistics

```text
mean_packet_size
median_packet_size
std_packet_size
min_packet_size
max_packet_size
p25_packet_size
p75_packet_size
p90_packet_size
p95_packet_size
p99_packet_size
```

### Timing Statistics

```text
mean_iat
median_iat
std_iat
min_iat
max_iat
p25_iat
p75_iat
p90_iat
p95_iat
p99_iat
```

### Rate Features

```text
packet_rate
byte_rate
```

### Directionality

```text
packet_direction_ratio
byte_direction_ratio
```

### Burst Statistics

```text
burst_count
forward_burst_count
backward_burst_count
mean_burst_packets
max_burst_packets
mean_burst_bytes
max_burst_bytes
```

### Activity

```text
active_time
idle_time
```

---

## 10. Fingerprint Dataset

File:

```text
features/fingerprint_features.csv
```

This is the **primary dataset for machine learning**.

The classifier should learn traffic behavior rather than traffic identity.

### Allowed Features

```text
packet sizes
packet counts
byte counts
timing
inter-arrival times
flow duration
directionality
burst statistics
activity statistics
```

### Forbidden Features

```text
source_ip
destination_ip
source_port
destination_port
domain
dns_query
url
sni
http_host
payload
resolver_identity
mac_address
capture_id
device_id
network_id
```

---

## 11. Early-Traffic Datasets

To determine how early encrypted DNS can be identified, a single consolidated dataset is generated:

```text
features/early_packets.csv
```

This file contains features calculated across early observation windows (5, 10, 20, and 30 packets per flow), identified by the `packet_window` column.

The experiment compares:

```text
5 packets
10 packets
20 packets
30 packets
Full flow
```

This answers:

> **How many packets are required before encrypted DNS becomes identifiable?**

---

## 12. Metadata

The `metadata/` directory contains information required for reproducibility.

### `experiments.csv`

```text
experiment_id
capture_id
traffic_class
protocol_family
network_type
device_id
scenario_id
repetition_id
capture_date
```

### `captures.csv`

```text
capture_id
traffic_class
capture_file
network_type
scenario_id
repetition_id
duration
packet_count
```

### `networks.csv`

```text
network_id
network_type
environment
bandwidth
latency
packet_loss
```

Metadata is for experiment tracking and should not automatically be used as ML features.

---

## 13. Labels

Every flow must have exactly one target label:

```text
HTTPS_WEB
HTTP3_WEB
DOH
DOH3
DOQ
```

Recommended numerical encoding:

```text
0 -> HTTPS_WEB
1 -> HTTP3_WEB
2 -> DOH
3 -> DOH3
4 -> DOQ
```

Keep the textual label in analysis datasets even when numerical labels are used during training.

---

## 14. Data Leakage Rules

Avoid features that allow the model to identify the application through trivial identifiers.

### Never use as ML features

```text
IP addresses
ports
DNS names
domain names
URLs
SNI
HTTP Host
MAC addresses
resolver IP
capture ID
device ID
network ID
file name
```

For example, allowing:

```text
destination_port = 853
```

could let a classifier learn:

```text
port 853 -> DNS
```

instead of learning an encrypted traffic fingerprint.

---

## 15. Train / Validation / Test Split

Do **not** randomly split packets from the same capture into different datasets.

Use a **capture-level split**:

```text
Capture-level split
        |
        +-- Training captures
        |
        +-- Validation captures
        |
        +-- Testing captures
```

Recommended initial split:

```text
70% -> Training
15% -> Validation
15% -> Testing
```

The split should be performed using `capture_id`.

All packets and flows originating from one capture must remain in the same split.

---

## 16. Cross-Network Evaluation

If multiple networks are available, perform an additional generalization experiment.

Example:

```text
Training:
    WiFi Network A

Testing:
    WiFi Network B
```

or:

```text
Training:
    WiFi

Testing:
    Mobile Network
```

This evaluates whether the traffic fingerprint generalizes across network environments.

---

## 17. Class Balance

Try to maintain approximately balanced classes.

Example target:

```text
HTTPS_WEB     1000 flows
HTTP3_WEB     1000 flows
DOH           1000 flows
DOH3          1000 flows
DOQ           1000 flows
```

Perfect balance is not mandatory, but severe class imbalance should be avoided.

If imbalance exists, report:

```text
accuracy
precision
recall
F1-score
macro-F1
confusion matrix
```

Do not rely only on accuracy.

---

## 18. Recommended Data Formats

### Raw Traffic

```text
.pcap
.pcapng
```

### Packet and Flow Data

```text
.parquet
```

### Feature Tables

```text
.csv
```

Parquet is preferred for large packet and flow datasets because it is efficient for analytical workloads.

---

## 19. Data Validation

Before ML training, run the following checks:

```text
[ ] No missing flow IDs
[ ] No duplicate flow IDs
[ ] Every flow has exactly one label
[ ] Every packet belongs to a flow
[ ] Packet indices are valid
[ ] Timestamps are non-negative
[ ] Packet sizes are valid
[ ] No NaN/Inf values in ML features
[ ] No forbidden identity features
[ ] All five classes are represented
[ ] Train/test captures do not overlap
[ ] Dataset passes validation
```

---

## 20. Processing Pipeline

The implementation should follow:

```text
1. Collect PCAP
        |
2. Store original PCAP
        |
3. Identify traffic class
        |
4. Extract packets
        |
5. Reconstruct flows
        |
6. Normalize timestamps
        |
7. Calculate packet features
        |
8. Calculate flow features
        |
9. Calculate burst features
        |
10. Generate fingerprint features
        |
11. Generate early-traffic features
        |
12. Validate dataset
        |
13. Split by capture
        |
14. Export ML datasets
```

---

## 21. Recommended Implementation Modules

A clean implementation can use:

```text
src/
|
├── capture/
│   └── capture_manager.py
|
├── preprocessing/
│   ├── packet_extractor.py
│   ├── flow_builder.py
│   └── timestamp_normalizer.py
|
├── features/
│   ├── packet_features.py
│   ├── timing_features.py
│   ├── size_features.py
│   ├── direction_features.py
│   └── burst_features.py
|
├── dataset/
│   ├── builder.py
│   ├── validator.py
│   └── splitter.py
|
└── config/
    └── dataset_config.yaml
```

---

## 22. Final Dataset Deliverables

The dataset-generation phase should produce:

```text
[✓] Raw PCAP dataset
[✓] Packet-level dataset
[✓] Flow-level dataset
[✓] Full feature dataset
[✓] Privacy-preserving fingerprint dataset
[✓] 5-packet dataset
[✓] 10-packet dataset
[✓] 20-packet dataset
[✓] 30-packet dataset
[✓] Training dataset
[✓] Validation dataset
[✓] Testing dataset
[✓] Dataset metadata
[✓] Dataset validation report
```

---

## 23. Definition of Done

The dataset phase is complete when:

```text
[ ] All 5 traffic classes are captured
[ ] Multiple independent captures exist per class
[ ] Packet-level data is extracted
[ ] Bidirectional flows are reconstructed
[ ] Flow-level features are generated
[ ] Timing features are generated
[ ] Packet-size features are generated
[ ] Directional features are generated
[ ] Burst features are generated
[ ] Early-traffic datasets are generated
[ ] Identifying features are removed from the main ML dataset
[ ] Dataset leakage checks pass
[ ] Classes are sufficiently balanced
[ ] Train/validation/test are capture-disjoint
[ ] Dataset validation passes
[ ] All generated data can be traced back to PCAPs
```

---

## 24. Core Research Principle

The central principle of this dataset is:

> **The classifier should learn how encrypted traffic behaves, not who generated it, where it came from, or what the encrypted application is called.**

Therefore, the main research dataset should rely primarily on:

```text
Packet Size
     +
Timing
     +
Direction
     +
Burst Behavior
     +
Flow Statistics
     =
Encrypted Traffic Fingerprint
```

The ultimate goal is not simply to obtain high classification accuracy. The dataset should allow us to investigate whether **DoH, DoH/3, and DoQ retain observable traffic-level fingerprints despite encryption**, and how robust those fingerprints are across networks and observation windows.
