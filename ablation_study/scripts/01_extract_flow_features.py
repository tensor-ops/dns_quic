#!/usr/bin/env python3
"""
01_extract_flow_features.py
────────────────────────────
Builds the combined flow-level feature CSV used by all downstream scripts.

Sources:
  • Prayagraj:  dataset_capture_5k/processed/dataset_flow_level.csv   (461 flows, 59 cols)
  • Tumsar:     Docker_dataset/doh_docker/master_final_dataset.csv     (packet-level only)
                → aggregate packet-level records into flow-level stats

Output:
  ablation_study/data/flow_features_combined.csv
"""

import os, sys, warnings
import pandas as pd
import numpy as np
import yaml

warnings.filterwarnings("ignore")

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT    = os.path.join(ROOT, "ablation_study", "data", "flow_features_combined.csv")

# ── Load feature group definitions ──────────────────────────────────────────
with open(os.path.join(ROOT, "ablation_study", "data", "feature_groups.yaml")) as f:
    cfg = yaml.safe_load(f)

ALL_FEAT_COLS = []
for grp in cfg["feature_groups"].values():
    ALL_FEAT_COLS.extend(grp["columns"])

CLASS_LABEL_MAP = cfg["classes"]   # DOH→0, DOT→1, ...

# ═══════════════════════════════════════════════════════════════════════════
# A) Prayagraj — flow-level CSV already exists
# ═══════════════════════════════════════════════════════════════════════════
pry_path = os.path.join(ROOT, "dataset_capture_5k", "processed", "dataset_flow_level.csv")
pry = pd.read_csv(pry_path)
pry = pry[pry["traffic_class"] != "DOT"]

# Standardise column names (some cols use underscores, check alignment)
pry.rename(columns={"packet_count": "packet_count"}, inplace=True)   # already correct

pry["vantage_point"]   = "Prayagraj_Airtel_Tap"
pry["city"]            = "Prayagraj"
pry["state"]           = "Uttar Pradesh"
pry["label"]           = pry["traffic_class"].map(CLASS_LABEL_MAP)

present_pry = [c for c in ALL_FEAT_COLS if c in pry.columns]
missing_pry = [c for c in ALL_FEAT_COLS if c not in pry.columns]
print(f"[Prayagraj] {len(pry)} flows — found {len(present_pry)}/{len(ALL_FEAT_COLS)} feature cols")
if missing_pry:
    print(f"  Missing: {missing_pry}")

# ═══════════════════════════════════════════════════════════════════════════
# B) Tumsar — aggregate packet-level records into flow-level statistics
#    We use master_final_dataset.csv (has flow_id column)
# ═══════════════════════════════════════════════════════════════════════════
tum_path = os.path.join(ROOT, "Docker_dataset", "doh_docker", "master_final_dataset.csv")
tum_pkt  = pd.read_csv(tum_path)
tum_pkt  = tum_pkt[tum_pkt["traffic_class"] != "DOT"]

# If no flow_id exists, create one from sequential runs within traffic_class
if "flow_id" not in tum_pkt.columns:
    # Assign synthetic flow_id: group consecutive rows of the same class
    tum_pkt["flow_id"] = (tum_pkt["traffic_class"] != tum_pkt["traffic_class"].shift()).cumsum()
    tum_pkt["flow_id"] = tum_pkt["traffic_class"].str[:4] + "_T_" + tum_pkt["flow_id"].astype(str).str.zfill(5)

def agg_flow(grp):
    sizes = grp["Current packet size"].values
    iats  = grp["Current time gap"].values * 1000   # → ms

    n = len(sizes)
    tot_bytes = sizes.sum()
    duration  = iats.sum()

    # Rough direction heuristic: larger packets assumed downstream (server responses)
    median_sz = np.median(sizes)
    up_mask   = sizes <= median_sz
    dn_mask   = ~up_mask
    up_pkts   = up_mask.sum()
    dn_pkts   = dn_mask.sum()
    up_bytes  = sizes[up_mask].sum()
    dn_bytes  = sizes[dn_mask].sum()

    # Burst: consecutive packets with IAT < 10 ms
    burst_starts = np.where((iats > 10) | (np.arange(n) == 0))[0]
    burst_sizes  = np.diff(np.append(burst_starts, n))
    n_bursts     = len(burst_starts)
    burst_durations = []
    for i, bs in enumerate(burst_starts):
        end = burst_starts[i+1] if i+1 < len(burst_starts) else n
        burst_durations.append(iats[bs:end].sum())

    # Temporal accumulation
    cum_pkt   = np.arange(1, n+1)
    cum_bytes = np.cumsum(sizes)
    timestamps = np.cumsum(iats)

    def at_t(t_ms):
        idx = np.searchsorted(timestamps, t_ms)
        if idx == 0: return 0, 0
        return int(cum_pkt[min(idx-1,n-1)]), float(cum_bytes[min(idx-1,n-1)])

    t100p,  t100b  = at_t(100)
    t250p,  t250b  = at_t(250)
    t500p,  t500b  = at_t(500)
    t1sp,   t1sb   = at_t(1000)
    t2sp,   t2sb   = at_t(2000)
    t3sp,   t3sb   = at_t(3000)
    t5sp,   t5sb   = at_t(5000)
    t10sp,  t10sb  = at_t(10000)

    return pd.Series({
        "packet_count":          n,
        "byte_count":            tot_bytes,
        "duration_ms":           duration,
        "packets_per_sec":       n / (duration/1000) if duration > 0 else 0,
        "bytes_per_sec":         tot_bytes / (duration/1000) if duration > 0 else 0,
        "packet_size_mean":      float(np.mean(sizes)),
        "packet_size_std":       float(np.std(sizes)),
        "packet_size_min":       float(np.min(sizes)),
        "packet_size_max":       float(np.max(sizes)),
        "packet_size_median":    float(np.median(sizes)),
        "packet_size_p25":       float(np.percentile(sizes, 25)),
        "packet_size_p75":       float(np.percentile(sizes, 75)),
        "packet_size_p90":       float(np.percentile(sizes, 90)),
        "packet_size_p95":       float(np.percentile(sizes, 95)),
        "packet_size_p99":       float(np.percentile(sizes, 99)),
        "iat_mean_ms":           float(np.mean(iats)),
        "iat_std_ms":            float(np.std(iats)),
        "iat_min_ms":            float(np.min(iats)),
        "iat_max_ms":            float(np.max(iats)),
        "iat_median_ms":         float(np.median(iats)),
        "iat_p25_ms":            float(np.percentile(iats, 25)),
        "iat_p75_ms":            float(np.percentile(iats, 75)),
        "iat_p90_ms":            float(np.percentile(iats, 90)),
        "iat_p95_ms":            float(np.percentile(iats, 95)),
        "iat_p99_ms":            float(np.percentile(iats, 99)),
        "upstream_packets":      int(up_pkts),
        "downstream_packets":    int(dn_pkts),
        "packet_direction_ratio":float(up_pkts/n) if n > 0 else 0.5,
        "upstream_bytes":        float(up_bytes),
        "downstream_bytes":      float(dn_bytes),
        "byte_direction_ratio":  float(up_bytes/tot_bytes) if tot_bytes > 0 else 0.5,
        "upstream_burst_count":  int(n_bursts // 2 + n_bursts % 2),
        "downstream_burst_count":int(n_bursts // 2),
        "burst_count":           int(n_bursts),
        "mean_burst_size":       float(np.mean(burst_sizes)) if n_bursts else 0,
        "maximum_burst_size":    float(np.max(burst_sizes))  if n_bursts else 0,
        "minimum_burst_size":    float(np.min(burst_sizes))  if n_bursts else 0,
        "mean_burst_duration_ms":float(np.mean(burst_durations)) if burst_durations else 0,
        "maximum_burst_duration_ms": float(np.max(burst_durations)) if burst_durations else 0,
        "first_100ms_packets":   t100p,  "first_100ms_bytes":   t100b,
        "first_250ms_packets":   t250p,  "first_250ms_bytes":   t250b,
        "first_500ms_packets":   t500p,  "first_500ms_bytes":   t500b,
        "first_1s_packets":      t1sp,   "first_1s_bytes":      t1sb,
        "first_2s_packets":      t2sp,   "first_2s_bytes":      t2sb,
        "first_3s_packets":      t3sp,   "first_3s_bytes":      t3sb,
        "first_5s_packets":      t5sp,   "first_5s_bytes":      t5sb,
        "first_10s_packets":     t10sp,  "first_10s_bytes":     t10sb,
    })

print("[Tumsar] Aggregating packet records into flows …")
tum_flow = tum_pkt.groupby(["flow_id", "traffic_class"]).apply(agg_flow).reset_index()
tum_flow["vantage_point"] = "Tumsar_Docker_Tap"
tum_flow["city"]          = "Tumsar"
tum_flow["state"]         = "Maharashtra"
tum_flow["label"]         = tum_flow["traffic_class"].map(CLASS_LABEL_MAP)

print(f"[Tumsar]  {len(tum_flow)} flows — classes: {tum_flow['traffic_class'].value_counts().to_dict()}")

# ═══════════════════════════════════════════════════════════════════════════
# C) Merge
# ═══════════════════════════════════════════════════════════════════════════
KEEP = ALL_FEAT_COLS + ["traffic_class", "label", "vantage_point", "city", "state"]

# Prayagraj: pick only columns that exist
pry_sub = pry[[c for c in KEEP if c in pry.columns]].copy()
# Fill any missing cols with NaN
for c in KEEP:
    if c not in pry_sub.columns:
        pry_sub[c] = np.nan

tum_sub = tum_flow[[c for c in KEEP if c in tum_flow.columns]].copy()
for c in KEEP:
    if c not in tum_sub.columns:
        tum_sub[c] = np.nan

combined = pd.concat([pry_sub[KEEP], tum_sub[KEEP]], ignore_index=True)
combined["label"] = combined["label"].astype(int)

combined.to_csv(OUT, index=False)
print(f"\n✅ Saved → {OUT}")
print(f"   Shape  : {combined.shape}")
print(f"   Classes: {combined['traffic_class'].value_counts().to_dict()}")
print(f"   VPs    : {combined['vantage_point'].value_counts().to_dict()}")
print(f"   Missing: {combined[ALL_FEAT_COLS].isnull().sum().sum()} cells")
