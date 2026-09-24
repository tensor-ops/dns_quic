# Encrypted DNS Traffic Fingerprinting Dataset (Compact)

## Overview
This compact dataset contains sequential packet-level features designed for machine learning classification of encrypted network traffic.

All extraneous multi-folder datasets, raw PCAPs, and aggregates have been condensed into a single `.csv` file: [`dataset.csv`](./dataset.csv).

## Features Schema
| Feature Name | Type | Description |
|---|---|---|
| `Current packet size` | Integer | Wire size of the current packet in bytes |
| `Previous packet size` | Integer | Wire size of the previous packet in the same flow (0 if first packet) |
| `Current time gap` | Float | Inter-arrival time (in seconds) between previous and current packet |
| `Previous time gap` | Float | Inter-arrival time (in seconds) for the previous packet (0.0 if first or second packet) |
| `traffic_class` | String | Target label (`HTTPS_WEB`, `HTTP3_WEB`, `DOH`, `DOH3`, `DOQ`) |

## File Location
- Dataset file: `dataset/dataset.csv`
- Generator script: `dataset/generate_dataset.py`
