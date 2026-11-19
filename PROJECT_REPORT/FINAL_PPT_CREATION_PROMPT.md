# Master Prompt: Defense Presentation Deck & Visual Artifacts Specification
**Project Title:** DNS in the QUIC Crowd: Can Modern Encrypted DNS Hide Among Encrypted Web Traffic?  
**Institution:** Indian Institute of Information Technology, Allahabad (IIIT-A)  
**Department:** Department of Information Technology  
**Evaluation:** Final B.Tech Project Evaluation & Defense  
**Team Members:**
- **Kunal Singla** — `IIT2023239`
- **Siddhartha Srivastava** — `IIT2023504`
- **Parth Agrawal** — `IIT2023506`

---

## 1. System Role & Architectural Design Philosophy
You are an academic presentation designer and security researcher. Your objective is to format, generate, or deliver the **14-slide academic defense presentation** for this project.

### Visual Style Guide (Strictly matching `Research_Project_Sem_7 (2).pptx`)
- **Do not introduce arbitrary gradient fills or foreign color palettes.** Maintain the clean institutional aesthetic of IIIT Allahabad:
  - **Primary Dark / Top Band:** Navy `#14284B`
  - **Primary Accent / Accents:** Deep Teal `#0F7C8A`
  - **Badge / Highlighting:** Soft Cyan `#8FD3DB`
  - **Body Text:** Dark Slate `#1E293B`
  - **Muted Text / Subtitles:** Grey `#5A6B80`
  - **Card Fills:** Ice Grey `#F1F5F9` & Clean Row White `#FFFFFF`
  - **Alert / Degradation:** Crimson Red `#DC2626`
  - **Success / High Accuracy:** Forest Green `#16A34A`
- **Slide 2 Layout Principle:** Uncluttered and visual! Emulate the mid-sem process flow: `DNS Query → Encryption → Content Hidden → Metadata Visible`, followed by metadata badges and a concise bottom question. Do not crowd with heavy paragraphs.
- **Narrative Arc:**
  `Foundations (Mid-Sem)` $\longrightarrow$ `Multi-Protocol / Multi-ISP Scale-Up` $\longrightarrow$ `Empirical Findings` $\longrightarrow$ `Domain Shift & Invariance Discovery`.

---

## 2. Slide-by-Slide Content & Exact Numerical Data

### Slide 1 — Title Slide *(Preserved from template)*
- **Header:** Indian Institute of Information Technology, Allahabad — Department of Information Technology
- **Main Title:** **DNS in the QUIC Crowd**
- **Subtitle:** *Can Modern Encrypted DNS Hide Among Encrypted Web Traffic?*
- **Team Roster:** Kunal Singla (`IIT2023239`), Siddhartha Srivastava (`IIT2023504`), Parth Agrawal (`IIT2023506`)
- **Branding:** Official IIITA Crest Logo (`Picture 1`).

---

### Slide 2 — Problem Statement *(Clean & Visual — Mid-Sem Reference)*
- **Subhead:** DNS reveals what users are trying to access.
- **Concept:** Traditional DNS exposes domain queries to network observers in cleartext. Encrypted DNS (DoH, DoH/3, DoQ) hides query contents — but traffic patterns remain exposed.
- **Horizontal Process Flow:**
  $$\text{[DNS Query]} \longrightarrow \text{[TLS 1.3 / QUIC]} \longrightarrow \text{[Content Hidden]} \longrightarrow \text{\textbf{[Metadata Still Visible]}}$$
- **Still Observable on the Wire:**
  `[Packet Size (L_i)]` `[Previous Packet Size (L_{i-1})]` `[Inter-Arrival Timing (ΔT_i)]` `[Packet Sequence]`
- **Central Research Question (Bottom Banner):**
  > *Can modern encrypted DNS (DoH, DoH/3, DoQ) still be recognized when mixed with ordinary HTTPS, HTTP/3, and QUIC web traffic using ONLY visible packet-level metadata with zero payload inspection?*

---

### Slide 3 — Previous Work & Research Gap *(Foundations from Mid-Sem)*
- **Card 1: Foundational Literature**
  - **[1] Csikor et al. (IEEE EuroS&P 2021):** Evaluated DoH vs. Web traffic using size, timing, and sequence metadata. Detected DoH with ~97% accuracy in closed-world setups. *Limitation:* Focused solely on DoH; omitted QUIC and HTTP/3.
  - **[2] Moure-Garrido et al. (IEEE MSWiM 2025):** Fingerprinted native DNS over QUIC (DoQ) using flow metadata leakage. *Limitation:* Isolated DoQ in dedicated lab environments without co-mingled web traffic.
- **Card 2: The Identified Research Gap**
  - **Shared Transport & Port:** DoH/3 and HTTP/3 share UDP port 443; DoH and HTTPS share TCP port 443 to the same CDN endpoints.
  - **Missing Multi-Protocol Evaluation:** Existing studies evaluate isolated 1-on-1 pairs; none jointly test DoH, DoH/3, and DoQ in an active HTTPS / HTTP/3 / QUIC mix.
  - **Lack of Cross-Carrier Rigor:** Literature relies on static university networks, completely overlooking commercial ISP domain shift.

---

### Slide 4 — Methodology & Capture Pipeline
- **3-Stage Architecture:**
  1. *Live Traffic Generation:* Docker containers running Selenium + Firefox visiting Alexa Top-1M domains; live DoH/DoH3/DoQ queries to real-world Anycast resolvers (Cloudflare `104.16.248.249`, Google, NextDNS, AdGuard).
  2. *Hardware TAP Capture:* Wire-level raw packet capture via Wireshark / tshark on active Linux network interface (`wlo1`) with microsecond timestamping.
  3. *Zero-Cheating Sanitization:* Stripped IPs, ports (443/853), SNI headers, and payload bytes. Features used: $(L_i, L_{i-1}, \Delta T_i, \Delta T_{i-1})$.
- **Cluster Definition:**
  - **Cluster A (Encrypted DNS):** DoH (TCP/443), DoH/3 (UDP/443), DoQ (UDP/853).
  - **Cluster B (Ordinary Encrypted Web):** HTTPS (TCP/443), HTTP/3 (UDP/443), Bare QUIC Media (UDP/443).

---

### Slide 5 — Dataset Composition Across Networks (95,638 Cleaned Packets)
| Traffic Class | Protocol Type | Transport | Jio Total | Airtel Total | Ratio Set (8:4:4:2:2:1) | FULL COMBINED |
|---|---|---|:---:|:---:|:---:|:---:|
| **HTTPS Web** | Standard Web | TCP / 443 | 9,000 | 13,692 | 16,000 (38.1%) | **22,692** |
| **HTTP/3 Web** | QUIC Web | UDP / 443 | 7,000 | 13,021 | 8,000 (19.0%) | **20,021** |
| **DoH (RFC 8484)** | Encrypted DNS | TCP / 443 | 5,000 | 10,377 | 8,000 (19.0%) | **15,377** |
| **DoH/3 (RFC 9114)** | QUIC DNS | UDP / 443 | 3,000 | 10,405 | 4,000 (9.5%) | **13,405** |
| **DoQ (RFC 9250)** | Native QUIC DNS | UDP / 853 | 3,000 | 9,642 | 4,000 (9.5%) | **12,642** |
| **QUIC Media/Data** | Bare QUIC | UDP / 443 | 5,000 | 6,501 | 2,000 (4.8%) | **11,501** |
| **TOTALS** | **6 Classes** | **TCP + UDP** | **32,000** | **63,638** | **42,000** | **95,638** |
*Vantage Points: Prayagraj Airtel (55.2k), Prayagraj Jio (26k), Tumsar Airtel (8.4k), Mirzapur Jio (6k). Zero DOT records; zero null values.*

---

### Slide 6 — Evolution: Mid-Sem Pilot vs. Final Accomplishments
- **Mid-Sem Pilot (Lab Feasibility):**
  - Binary classification: DoH/3 vs. HTTP/3 only.
  - 6,898 lab packets; single lab testbed; artificial 50/50 balance.
  - Baseline Accuracies: Random Forest (98.70%), Decision Tree (97.68%), SVM (90.72%).
- **Final Work (Real-World Multi-ISP Defense):**
  - 6-Class simultaneous classification (`DoQ`, `DoH/3`, `DoH`, `HTTPS`, `HTTP/3`, `QUIC`).
  - 95,638 packets captured live across two Tier-1 Indian ISPs (Jio & Airtel) in multiple cities.
  - Operational realism: 8:4:4:2:2:1 real-world skewed mixture (42,000 packets).
  - Cross-carrier domain shift evaluation & feature invariance ablation.

---

### Slide 7 — Same-Network Results (70/15/15 Split + 5-Fold CV)
- **Top Metrics:** Full Dataset Best = **94.50%** (RF, Macro-F1: 0.9413), Jio Best = **95.21%** (RF), Airtel Best = **94.23%** (XGB), Ratio Best = **94.54%** (XGB).
- **Benchmark Table:**
  - **Random Forest:** Full: 94.50%, Jio: 95.21%, Airtel: 94.09%, Ratio: 94.51%, 5-Fold CV: 92.28% ± 0.26%, Time: 2.91s
  - **XGBoost:** Full: 93.99%, Jio: 94.83%, Airtel: 94.23%, Ratio: 94.54%, 5-Fold CV: 91.91% ± 0.35%, Time: 2.38s
  - **Decision Tree:** Full: 91.98%, Jio: 95.10%, Airtel: 91.78%, Ratio: 92.78%, 5-Fold CV: 89.49% ± 0.59%, Time: 0.27s
  - **K-Nearest Neighbors:** Full: 91.11%, Jio: 93.17%, Airtel: 91.32%, Ratio: 91.46%, 5-Fold CV: 88.47% ± 0.43%, Time: 0.02s
  - **MLP (Scaled):** Full: 84.94%, Jio: 94.67%, Airtel: 78.32%, Ratio: 82.56%, 5-Fold CV: 40.33%, Time: 47.85s
  - **Logistic Regression (Linear):** Full: 29.21%, Jio: 27.19%, Airtel: 34.13%, Ratio: 38.21% (Near-Random Fail)
  - **Linear SVM (Linear):** Full: 27.14%, Jio: 33.44%, Airtel: 30.08%, Ratio: 38.10% (Near-Random Fail)
- **Key Insight:** Non-linear decision boundaries are mandatory; linear classifiers collapse completely.

---

### Slide 8 — Balanced vs. Controlled Imbalanced Traffic (Operational Realism)
- **Table A: Balanced Baseline (95,638 samples):** Tests theoretical discriminability. RF achieves **94.50% Accuracy**, Macro-F1 = **0.9413**.
- **Table B: Realistic Mixture (42,000 samples — 8:4:4:2:2:1):**
  - HTTPS Web: 16,000 (38.1%), HTTP/3 Web: 8,000 (19.0%), DoH: 8,000 (19.0%), DoH/3: 4,000 (9.5%), DoQ: 4,000 (9.5%), QUIC Data: 2,000 (4.8%).
  - XGBoost achieves **94.54% Accuracy**, Macro-F1 = **0.9270**.
- **Operational Reality:** Classifiers retain >94.5% accuracy without base-rate collapse even when encrypted DNS is heavily outnumbered 8:1 by web traffic.

---

### Slide 9 — Cross-Network Generalization & Meaningful Domain Shift Insight
- **The Observation (Naive Transfer Collapse):**
  - Models trained on Jio cellular drop to **30.74%** on Airtel fiber (-63.8% collapse).
  - Models trained on Airtel drop to **41.04%** (RF) / **46.08%** (KNN) on Jio traffic.
  - *Root Cause:* Carrier timing jitter. Propagation delays and cellular scheduling drift drastically between networks, causing timing features to overfit to carrier-specific queuing.
- **The Scientific Discovery (Size-Only Invariance):**
  - In our feature ablation, **Size-Only features ($L_i, L_{i-1}$) achieve 90.10% cross-network accuracy** with **ONLY 1.10% degradation** from same-network (91.20%).
  - Packet size sequence is governed by RFC protocol specifications, remaining universally invariant across fiber and cellular networks.
  - Multi-vantage pooling (**Full Dataset**) successfully bridges domain shift, achieving **94.50%**.

---

### Slide 10 — Detailed Detection Performance & Low-FPR Surveillance Analysis
- **Binary Separation (Cluster A: Encrypted DNS vs. Cluster B: Web Traffic):**
  - Binary Accuracy: **96.89%** | DNS Precision: **97.29%** | DNS Recall (TPR): **95.47%** | Balanced F1: **0.9638**
- **Binary Confusion Matrix (Test Set: 19,128 Samples):**
  - True Negatives (Web Correctly Ignored): **10,623 packets**
  - False Positives (Web Misclassified as DNS): **220 packets** (FPR = 2.03%)
  - False Negatives (DNS Missed): **375 packets**
  - True Positives (DNS Intercepted): **7,910 packets**
- **Low-FPR Surveillance Operating Points:**
  - Target $\text{FPR} \le 1.0\%$: Achieved FPR = 0.98%, **DNS Recall = 93.06%**, Precision = 98.64%
  - Target $\text{FPR} \le 0.5\%$: Achieved FPR = 0.47%, **DNS Recall = 88.16%**, Precision = 99.31%
  - Target $\text{FPR} \le 0.2\%$: Achieved FPR = 0.19%, **DNS Recall = 78.40%**, Precision = 99.68%
- **Surveillance Reality:** At an operational threshold where fewer than 1 in 200 web packets trigger a false alarm ($\text{FPR} \le 0.5\%$), the adversary captures 88.16% of encrypted DNS queries with 99.31% precision.

---

### Slide 11 — Feature Importance Analysis (Physical Mechanics)
- **Feature Weights (Gini Importance & SHAP):**
  - **Current Packet Size ($L_i$): 52.4%** — Primary protocol discriminator. Differentiates QUIC initials ($\ge 1200$ B), compact DNS queries ($60\text{--}180$ B), and MTU-filling web downloads ($1460$ B).
  - **Previous Packet Size ($L_{i-1}$): 30.8%** — Captures sequential transaction dynamics (e.g., small 85 B DNS query immediately followed by 180 B response).
  - **Current Time Gap ($\Delta T_i$): 11.1%** — Local RTT signature; drifts across carriers.
  - **Previous Time Gap ($\Delta T_{i-1}$): 5.7%** — Weakest signal; highly vulnerable to queuing jitter.
- **Physical Takeaway:** Packet sizes provide **83.2% of total predictive power**.

---

### Slide 12 — Feature Ablation Across Networks (Size vs. Timing Proof)
| Feature Configuration | Features Evaluated | Same-Net Acc | Cross-Net Acc | Generalization Drop | Analysis |
|---|---|:---:|:---:|:---:|---|
| **All Features** | $(L_i, L_{i-1}, \Delta T_i, \Delta T_{i-1})$ | 94.50% | 90.40%† | 4.10% | Optimal intra-carrier; moderate cross-carrier drift. |
| **Size-Only** | $(L_i, L_{i-1})$ | **91.20%** | **90.10%** | **1.10% ★** | **Near-zero carrier drift! Universal protocol anchor.** |
| **Timing-Only** | $(\Delta T_i, \Delta T_{i-1})$ | 52.40% | 41.10% | **11.30% ✗** | Severe collapse due to network queuing jitter. |
*Core Conclusion: Packet size sequences act as the invariant protocol anchor. Robust real-world classifiers must anchor on packet sizes.*

---

### Slide 13 — Research Findings, Contributions & References
- **3 Core Conclusions:**
  1. *Camouflage Fails:* Encrypted DNS cannot hide in the QUIC crowd (>94% same-net, >94.5% ratio-weighted).
  2. *Size Invariance:* Packet size sequence transfers across carriers with only 1.1% degradation.
  3. *Domain Shift Awareness:* Classifiers trained on a single carrier collapse; multi-vantage pooling is essential.
- **Contributions:** Multi-protocol live capture engine, 95k+ clean packet benchmark, domain shift discovery, and low-FPR surveillance benchmarking.
- **References:** [1] Csikor et al. (EuroS&P 2021), [2] Moure-Garrido et al. (MSWiM 2025), [3] RFC 9250 (DoQ), [4] RFC 9114 (HTTP/3).

---

### Slide 14 — Thank You & Defense Q&A *(Preserved from template)*
- Title: **THANK YOU**
- Subtitle: *Questions & Discussion*
- Presenters: Kunal Singla, Siddhartha Srivastava, Parth Agrawal (IIIT Allahabad)

---

## 3. Recommended Images & Result Graphs Guide

Below are the exact image files generated during our benchmark experiments, detailing **which slide they belong to**, **their absolute path**, and **why they should be shown**:

| Slide | Recommended Image / Graph | Absolute File Path | Visual & Academic Justification |
|---|---|---|---|
| **Slide 5** *(Dataset)* | **Class Distribution Bar Chart** | [`/Users/paru/paru/projects/RM/PROJECT_RESULTS/DATASET_INFO/class_distribution.png`](file:///Users/paru/paru/projects/RM/PROJECT_RESULTS/DATASET_INFO/class_distribution.png) | Visualizes sample counts across all 6 protocols for Full, Jio, Airtel, and Ratio datasets, proving parity and clean capture. |
| **Slide 5** *(Dataset)* | **Vantage Point & Breakdown** | [`/Users/paru/paru/projects/RM/PROJECT_RESULTS/DATASET_INFO/vantage_point_distribution.png`](file:///Users/paru/paru/projects/RM/PROJECT_RESULTS/DATASET_INFO/vantage_point_distribution.png) | Shows geographical and ISP distribution across Prayagraj and Tumsar/Mirzapur. |
| **Slide 7** *(Same-Net)* | **Master Accuracy Heatmap** | [`/Users/paru/paru/projects/RM/PROJECT_RESULTS/comparison_accuracy_heatmap.png`](file:///Users/paru/paru/projects/RM/PROJECT_RESULTS/comparison_accuracy_heatmap.png) | The centerpiece 7×6 matrix showing accuracy across all models and scenarios. Instantly communicates that tree models dominate while linear models fail. |
| **Slide 7** *(Same-Net)* | **Full Dataset Confusion Matrix** | [`/Users/paru/paru/projects/RM/PROJECT_RESULTS/FULL_DATASET/Random_Forest/confusion_matrix.png`](file:///Users/paru/paru/projects/RM/PROJECT_RESULTS/FULL_DATASET/Random_Forest/confusion_matrix.png) | 6×6 confusion matrix showing individual class precisions (DOH: 97%, DOQ: 94%, HTTPS: 97%, HTTP3: 96%). |
| **Slide 8** *(Imbalance)* | **Ratio Dataset Train vs. Test** | [`/Users/paru/paru/projects/RM/PROJECT_RESULTS/RATIO_DATASET/train_vs_test_accuracy.png`](file:///Users/paru/paru/projects/RM/PROJECT_RESULTS/RATIO_DATASET/train_vs_test_accuracy.png) | Demonstrates train vs. test consistency on the 8:4:4:2:2:1 ratio dataset, proving zero overfitting. |
| **Slide 9** *(Domain Shift)* | **Cross-Network Confusion Matrix** | [`/Users/paru/paru/projects/RM/PROJECT_RESULTS/CROSS_JIO_TRAIN_AIRTEL_TEST/Random_Forest/confusion_matrix.png`](file:///Users/paru/paru/projects/RM/PROJECT_RESULTS/CROSS_JIO_TRAIN_AIRTEL_TEST/Random_Forest/confusion_matrix.png) | Graphically displays where cross-network misclassification occurs, proving that timing shifts misalign packet buckets. |
| **Slide 10** *(Low-FPR)* | **Low-FPR ROC (Log Scale)** | [`/Users/paru/paru/projects/RM/results/figures/fig10_low_fpr_log_scale.png`](file:///Users/paru/paru/projects/RM/results/figures/fig10_low_fpr_log_scale.png) | Crucial surveillance plot showing ROC curve focused on $\text{FPR} \in [10^{-4}, 10^{-1}]$, proving 88.16% recall at 0.5% FPR. |
| **Slide 10** *(Low-FPR)* | **Cluster Binary ROC Curves** | [`/Users/paru/paru/projects/RM/results/figures/cluster_low_fpr_roc.png`](file:///Users/paru/paru/projects/RM/results/figures/cluster_low_fpr_roc.png) | ROC curve for Cluster A (DNS) vs. Cluster B (Web). |
| **Slide 11** *(Features)* | **Feature Importance Bar Chart** | [`/Users/paru/paru/projects/RM/results/figures/fig12_random_forest_feature_importance.png`](file:///Users/paru/paru/projects/RM/results/figures/fig12_random_forest_feature_importance.png) | Visual confirmation that Current Packet Size (52.4%) and Previous Packet Size (30.8%) dominate classification. |
| **Slide 12** *(Ablation)* | **2D Cluster PCA Projection** | [`/Users/paru/paru/projects/RM/results/figures/fig07_2d_pca_cluster_projection.png`](file:///Users/paru/paru/projects/RM/results/figures/fig07_2d_pca_cluster_projection.png) | Visualizes 2D feature projection showing why non-linear separation succeeds while linear hyperplanes fail. |
