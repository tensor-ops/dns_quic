# Encrypted DNS Traffic Intelligence
## Feature Importance, Ablation & Robustness — Full Report

**Generated:** 2026-11-19  |  **Dataset:** 36,928 packet-level records → 957 flows across Prayagraj & Tumsar

Protocols: DOH, DOQ, DOH3, QUIC, HTTPS_WEB, HTTP3_WEB (DOT removed and replaced with QUIC)

---

## 1. Feature Groups Used

| Group | Features | Count |
|---|---|---|
| **Packet Flow** | packet_count, byte_count, duration_ms, packets_per_sec … | 15 |
| **Timing** | iat_mean_ms, iat_std_ms, iat_min_ms, iat_max_ms … | 10 |
| **Direction** | upstream_packets, downstream_packets, packet_direction_ratio, upstream_bytes … | 8 |
| **Burst Volume** | burst_count, mean_burst_size, maximum_burst_size, minimum_burst_size … | 22 |

---

## 2. Robustness Results

| experiment                             | model   |   n_train |   n_test |   accuracy |   f1_macro |
|:---------------------------------------|:--------|----------:|---------:|-----------:|-----------:|
| Within-Network                         | RF      |       496 |      124 |     0.9919 |     0.9742 |
| Within-Network                         | XGB     |       496 |      124 |     0.9839 |     0.9266 |
| Cross-Net (Prayagraj→Tumsar)           | RF      |       620 |      337 |     0.1929 |     0.1412 |
| Cross-Net (Prayagraj→Tumsar)           | XGB     |       620 |      337 |     0.3858 |     0.341  |
| Cross-Net (Tumsar→Prayagraj)           | RF      |       337 |      620 |     0.3548 |     0.1457 |
| Cross-Net (Tumsar→Prayagraj)           | XGB     |       337 |      620 |     0.3613 |     0.1391 |
| Open-World (DNS vs Web)                | RF      |       669 |      288 |     1      |     1      |
| Open-World (DNS vs Web)                | XGB     |       669 |      288 |     0.9896 |     0.9869 |
| Final (DoH/DoH3/DoQ) Within-Net        | RF      |       211 |       53 |     1      |     1      |
| Final (DoH/DoH3/DoQ) Within-Net        | XGB     |       211 |       53 |     1      |     1      |
| Final (DoH/DoH3/DoQ) Cross-Net Pry→Tum | RF      |        55 |      209 |     0.2297 |     0.1689 |
| Final (DoH/DoH3/DoQ) Cross-Net Pry→Tum | XGB     |        55 |      209 |     0.2297 |     0.1596 |

---

## 3. Key Findings

See companion plots:
- `feature_importance_plot.png` — RF vs XGBoost rankings
- `ablation_accuracy_bar.png` — group ablation results
- `ablation_f1_heatmap.png` — per-class F1 drop per group removed
- `shap_summary_bar.png` — SHAP feature importance
- `shap_beeswarm.png` — SHAP value distribution
- `robustness_summary.png` — all 4 robustness experiments
- `confusion_matrices/` — per-experiment confusion matrices
