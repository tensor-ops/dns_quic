# Encrypted DNS Traffic Intelligence
## Feature Importance, Ablation & Robustness — Full Report

**Generated:** 2026-11-17  |  **Dataset:** 35,616 packet-level records → 750 flows

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
| Within-Network                         | RF      |       368 |       93 |     0.9892 |     0.9683 |
| Within-Network                         | XGB     |       368 |       93 |     0.9892 |     0.974  |
| Cross-Net (Prayagraj→Tumsar)           | RF      |       411 |      289 |     0.173  |     0.1394 |
| Cross-Net (Prayagraj→Tumsar)           | XGB     |       411 |      289 |     0.1315 |     0.083  |
| Cross-Net (Tumsar→Prayagraj)           | RF      |       289 |      411 |     0.1119 |     0.0705 |
| Cross-Net (Tumsar→Prayagraj)           | XGB     |       289 |      411 |     0.0365 |     0.0205 |
| Open-World (DNS vs Web)                | RF      |       525 |      225 |     0.9911 |     0.9909 |
| Open-World (DNS vs Web)                | XGB     |       525 |      225 |     0.9822 |     0.9818 |
| Final (DoH/DoH3/DoQ) Within-Net        | RF      |       211 |       53 |     1      |     1      |
| Final (DoH/DoH3/DoQ) Within-Net        | XGB     |       211 |       53 |     1      |     1      |
| Final (DoH/DoH3/DoQ) Cross-Net Pry→Tum | RF      |        55 |      209 |     0.2201 |     0.1608 |
| Final (DoH/DoH3/DoQ) Cross-Net Pry→Tum | XGB     |        55 |      209 |     0.4354 |     0.5056 |

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
