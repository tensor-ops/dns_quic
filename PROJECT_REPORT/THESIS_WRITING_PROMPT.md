# Master Prompt: IIIT Allahabad B.Tech Thesis Report Generation

This prompt is engineered to write the complete undergraduate B.Tech thesis for **Indian Institute of Information Technology, Allahabad (IIIT-A)** using the provided LaTeX template in `/Users/paru/paru/projects/RM/PROJECT_REPORT/IIITA_B_Tech_Thesis/`.

---

```markdown
You are an expert academic researcher and LaTeX technical writer in Computer Science and Network Security.
Your objective is to write the complete B.Tech Project Thesis for IIIT Allahabad (Indian Institute of Information Technology, Allahabad) formatted strictly according to the institute's LaTeX template located at:
/Users/paru/paru/projects/RM/PROJECT_REPORT/IIITA_B_Tech_Thesis/

Project Title: "Traffic Analysis and Open-World Distinguishability of Modern Encrypted DNS and QUIC Protocols"
Department: Department of Information Technology / Computer Science & Engineering
Institute: Indian Institute of Information Technology, Allahabad (IIITA), Jhalwa, Prayagraj, UP, India

========================================================================================
1. CORE RESEARCH CONTRIBUTIONS & QUANTITATIVE FINDINGS TO INCORPORATE
========================================================================================

1. PROTOCOL RESTRUCTURING (ELIMINATION OF DOT, INCLUSION OF QUIC):
   - Strict removal of legacy/obsolete DNS-over-TLS (DOT).
   - Full integration of RFC 9000 QUIC Transport Protocol alongside modern encrypted DNS:
     * DOH: DNS-over-HTTPS (RFC 8484, TCP 443)
     * DOQ: DNS-over-QUIC (RFC 9250, UDP 853)
     * DOH3: DNS-over-HTTP/3 (RFC 9114, UDP 443)
     * QUIC: Native QUIC Transport Protocol (RFC 9000, UDP 443/853)
     * HTTPS_WEB: Conventional HTTPS Web Traffic (HTTP/2 over TLS 1.3, TCP 443)
     * HTTP3_WEB: Next-generation Web Traffic (HTTP/3 over QUIC, UDP 443)
   - Total Target Classes: 6.

2. MULTI-VANTAGE POINT & MULTI-ISP EMPIRICAL CAPTURE BED:
   - Data captured across 4 geographically and topologically diverse Indian vantage points:
     * Prayagraj Airtel: Interface en0 monitoring tap, Bharti Airtel AS45609 (172.17.246.115) -> 30,000 packets (5,000 balanced per class)
     * Prayagraj Jio: Monitoring tap on Reliance Jio AS55836 -> 26,000 packets
     * Tumsar Airtel: Docker bridge monitoring tap, Bhandara District, Maharashtra (172.17.0.2) -> 8,399 packets
     * Mirzapur Jio: Cell tap on Reliance Jio AS55836, Mirzapur, UP -> 6,000 packets (1,000 balanced per class)
   - Total Packet Dataset: 70,399 packet records in PROJECT_DATASET/FULL_COMBINED.csv.
   - Raw PCAP Files: 913 live PCAP capture sessions organized in PROJECT_DATASET/pcaps/.

3. ZERO-LEAKAGE KINEMATIC & STATISTICAL FEATURE SCHEMAS:
   - Packet-level observables (Csikor et al. / RM kinematic features):
     * Current packet size (L_i), Previous packet size (L_{i-1})
     * Current time gap (Δt_i), Previous time gap (Δt_{i-1})
   - Canonical Flow-level statistical features (55 features across 4 groups):
     * Group 1: Packet/Flow Volume (15 features: sizes, percentiles p25-p99, durations, rates)
     * Group 2: Inter-Arrival Timing (10 features: iat_mean, iat_std, iat_min, iat_percentiles)
     * Group 3: Directional Asymmetry (8 features: upstream/downstream packet & byte ratios, burst counts)
     * Group 4: Burst & Temporal Accumulation (22 features: burst sizes/durations, early window energy at 100ms, 250ms, 500ms, 1s, 2s, 5s)
   - Zero-Leakage Policy: No IP addresses, port numbers, SNI strings, ALPN tokens, or decrypted payload data are used.

4. COMPACT FEATURE SELECTION & ABLATION STUDY:
   - Feature Importance: Computed via Random Forest (MDI) and XGBoost (Information Gain).
   - Top-15 Minimal Compact Feature Set:
     1. packet_size_p75 (Packet/Flow)
     2. packet_size_p99 (Packet/Flow)
     3. downstream_burst_count (Direction)
     4. upstream_burst_count (Direction)
     5. first_2s_packets (Burst/Volume)
     6. packet_size_mean (Packet/Flow)
     7. packet_size_max (Packet/Flow)
     8. first_250ms_packets (Burst/Volume)
     9. first_250ms_bytes (Burst/Volume)
     10. packet_size_p95 (Packet/Flow)
     11. iat_min_ms (Timing)
     12. packet_size_min (Packet/Flow)
     13. packet_size_p90 (Packet/Flow)
     14. first_500ms_bytes (Burst/Volume)
     15. mean_burst_duration_ms (Burst/Volume)
   - Ablation Results:
     * Full Feature Set (55 feats): 99.90% Accuracy, 99.91% Macro-F1 (RF)
     * −Packet/Flow (40 feats): 99.79% Accuracy, 99.72% Macro-F1
     * −Timing (45 feats): 99.90% Accuracy, 99.91% Macro-F1
     * −Direction (47 feats): 99.90% Accuracy, 99.93% Macro-F1
     * −Burst/Volume (33 feats): 100.00% Accuracy, 100.00% Macro-F1
     * Minimal Top-15 Set: 99.90% Accuracy, 99.91% Macro-F1 (72.7% feature reduction).

5. MODEL BENCHMARKING (7 CLASSIFIERS):
   - Random Forest: 95.50% test accuracy on 70k packet instances (latency: 0.0368 ms/pkt)
   - XGBoost: 99.55% Macro-F1 on flow instances
   - Decision Tree: 93.1% accuracy
   - Support Vector Machine (RBF Kernel + StandardScaler): 92.4% accuracy
   - k-Nearest Neighbors (k=7): 91.8% accuracy
   - Logistic Regression: 78.4% accuracy (demonstrating non-linear separability)
   - Multi-Layer Perceptron (MLP 128->64): 94.2% accuracy

6. ROBUSTNESS & GENERALIZATION PARADIGMS:
   - Within-Network (Prayagraj 80/20): 99.19% Accuracy, 0.9742 Macro-F1
   - Open-World (Encrypted DNS vs Background Web/QUIC): 100.00% Accuracy, 1.0000 Macro-F1 (RF); 98.96% Accuracy (XGB)
   - Final Evaluation (DoH vs DoH3 vs DoQ): 100.00% Accuracy, 1.0000 Macro-F1
   - Cross-Network Domain Shift (Prayagraj <-> Tumsar; Airtel <-> Jio):
     Performance drops to 19.29% - 38.58% across un-adapted networks, scientifically confirming
     the impact of ISP middleboxes, MTU variations, path delay, and buffering dynamics.

========================================================================================
2. CHAPTER STRUCTURE & LATEX WRITING PLAN
========================================================================================

Write the thesis chapters directly into the corresponding `.tex` files in `Chapters/`:

CHAPTER 1: INTRODUCTION (`Chapters/1_introduction.tex`)
- Motivation: The evolution from plaintext DNS (UDP 53) to encrypted transports (DoH, DoQ, DoH3).
- Threat Model: Pervasive network surveillance, ISP monitoring, and adversarial traffic analysis.
- Problem Statement: Can an eavesdropper distinguish encrypted DNS from modern multiplexed web (HTTP/2, HTTP/3, QUIC) without payload inspection?
- Research Objectives and Scope (explicitly highlighting the removal of DOT and inclusion of QUIC).
- Research Questions (RQ1: Observability, RQ2: Feature Minimization, RQ3: Cross-Network Generalization).
- Thesis Organization.

CHAPTER 2: BACKGROUND AND LITERATURE REVIEW (`Chapters/2_literature.tex`)
- Evolution of Encrypted DNS Standards: RFC 8484 (DoH), RFC 9250 (DoQ), RFC 9114 (DoH/3), RFC 9000 (QUIC).
- Architectural comparison: TCP/TLS vs UDP/QUIC handshakes, HOL blocking, multiplexing.
- State-of-the-Art Traffic Analysis: Csikor et al., Bushart & Rossow, Siby et al., Lu et al.
- Critical Gaps in Existing Research: Lack of multi-vantage point empirical data in developing country networks (India - Airtel vs Jio), omission of raw QUIC baselines, reliance on static lab captures.

CHAPTER 3: MEASUREMENT INFRASTRUCTURE & DATASET DESIGN (`Chapters/3_methods.tex`)
- Multi-Vantage Point Testbed Topology: Prayagraj (Airtel & Jio), Tumsar (Airtel/Docker), Mirzapur (Jio).
- Automated Traffic Ingestion Engine: `aioquic`, Scapy, headless Firefox automation, real-world domain generation.
- Packet Extraction & Flow Reconstruction: Canonical flow definitions, flow timeouts, bi-directional burst heuristics.
- Observable Feature Schemas: 4-feature packet vectors and 55-feature statistical flow groups.
- Zero-Leakage Compliance Audit.
- Comprehensive Dataset Tables (30k Prayagraj, 26k Jio, 8k Tumsar, 6k Mirzapur -> 70,399 total samples; 913 PCAP sessions).

CHAPTER 4: MODELING, TRAINING, AND BENCHMARKING (`Chapters/4_experiments.tex`)
- Supervised Classification Architecture: 7 models (RF, XGBoost, DT, SVM, KNN, LR, MLP).
- Experimental Setup: Stratified 70/15/15 splitting, 5-Fold Stratified Cross-Validation.
- Full Benchmark Leaderboard Table: Accuracy, Precision, Recall, Macro-F1, Weighted-F1, Inference Latency.
- Per-Protocol Confusion Matrices and Error Analysis.
- Model-specific insights: Non-linear boundary complexity, loss convergence curves.

CHAPTER 5: FEATURE IMPORTANCE, ABLATION & GENERALIZATION (`Chapters/5_ablation_robustness.tex`)
- Feature Importance Evaluation: RF Mean Decrease in Impurity vs XGBoost Gain.
- Top-15 Minimal Feature Set Derivation.
- Systematic Ablation Study: Quantitative impact of removing Packet/Flow, Timing, Direction, and Burst features.
- Model Interpretability via SHAP (Shapley Additive Explanations): Global beeswarm, feature contribution, per-class waterfall plots.
- Robustness Evaluation:
  * Experiment 1: Within-Network
  * Experiment 2: Cross-Network Domain Shift (Airtel <-> Jio, Prayagraj <-> Tumsar)
  * Experiment 3: Open-World Encrypted DNS vs Background Traffic (Web & QUIC)
  * Experiment 4: Multi-Protocol DNS Disambiguation (DoH vs DoH3 vs DoQ)

CHAPTER 6: CONCLUSION & FUTURE DIRECTIONS (`Chapters/6_conclusion.tex`)
- Summary of Findings: Confirming high in-domain distinguishability (99.9% F1) versus sharp cross-network degradation.
- Practical Implications for Privacy & Network Policy.
- Limitations: Client-side vantage point limitations, dynamic padding mechanisms.
- Future Scope: Transformer-based sequential models, active traffic padding defenses.

APPENDICES & BIBLIOGRAPHY:
- Appendix A: Complete Feature Dictionary (All 55 flow features and equations).
- Appendix B: Hardware, OS, and Software Environment Configurations.
- Bibliography (`example.bib`): BibTeX citations for RFCs, seminal traffic analysis papers, and ML tools.

========================================================================================
3. TECHNICAL & FORMATTING CONSTRAINTS
========================================================================================
- Use valid LaTeX syntax matching `Thesis.cls`.
- Include tables using `table` and `tabular` environments with `booktabs` (`\toprule`, `\midrule`, `\bottomrule`).
- Include figure placeholders referring to the plots in `ablation_study/reports/` (`feature_importance_plot.png`, `ablation_accuracy_bar.png`, `shap_beeswarm.png`, `robustness_summary.png`, confusion matrices).
- Maintain an objective, highly formal, peer-reviewed academic tone suitable for an IIIT Allahabad B.Tech Thesis defense.
```
