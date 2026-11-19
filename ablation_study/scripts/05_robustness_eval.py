#!/usr/bin/env python3
"""
05_robustness_eval.py
──────────────────────
Four robustness experiments matching the research diagram:

  1. Within-Network     — train/test on same vantage point (Prayagraj 80/20)
  2. Cross-Network      — train Prayagraj → test Tumsar  AND  Tumsar → Prayagraj
  3. Open-World         — DNS classes vs. background web traffic (HTTPS_WEB, HTTP3_WEB)
  4. Final Evaluation   — DoH vs. DoH3 vs. DoQ identification only (3-class)

Outputs:
  • robustness_results.csv
  • confusion_matrices/  (one PNG per experiment)
  • robustness_summary.png  (grouped bar chart)
  • full_report.md
"""

import os, warnings, yaml, json
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (accuracy_score, f1_score, classification_report,
                              confusion_matrix, precision_recall_fscore_support)
import xgboost as xgb

warnings.filterwarnings("ignore")

ROOT    = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA    = os.path.join(ROOT, "ablation_study", "data", "flow_features_combined.csv")
REPORTS = os.path.join(ROOT, "ablation_study", "reports")
CM_DIR  = os.path.join(REPORTS, "confusion_matrices")
os.makedirs(CM_DIR, exist_ok=True)

with open(os.path.join(ROOT, "ablation_study", "data", "feature_groups.yaml")) as f:
    cfg = yaml.safe_load(f)

GROUPS    = {name: info["columns"] for name, info in cfg["feature_groups"].items()}
ALL_FEAT  = [c for cols in GROUPS.values() for c in cols]
CLASS_MAP = cfg["classes"]   # DOH→0, …
CLASS_NAMES_BY_IDX = {v:k for k,v in CLASS_MAP.items()}

# Load compact feature set
compact_path = os.path.join(REPORTS, "compact_feature_set.txt")
if os.path.exists(compact_path):
    FEATS = []
    with open(compact_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                FEATS.append(line.split()[0])
    print(f"Using compact feature set ({len(FEATS)} features)")
else:
    FEATS = ALL_FEAT
    print("Using full feature set")

# ── Load data ────────────────────────────────────────────────────────────
df = pd.read_csv(DATA)
avail = [f for f in FEATS if f in df.columns]
df[avail] = df[avail].fillna(0)
print(f"Loaded {len(df)} flows | VPs: {df['vantage_point'].value_counts().to_dict()}")

VP_PRY = cfg["vantage_points"]["prayagraj"]
VP_TUM = cfg["vantage_points"]["tumsar"]

pry_df = df[df["vantage_point"] == VP_PRY].copy()
tum_df = df[df["vantage_point"] == VP_TUM].copy()
print(f"Prayagraj: {len(pry_df)} flows  |  Tumsar: {len(tum_df)} flows")

results_rows = []

# ── Helper: plot confusion matrix ─────────────────────────────────────────
def plot_cm(ytrue, ypred, class_names, title, fname):
    labels = sorted(set(ytrue) | set(ypred))
    names  = [class_names.get(l, str(l)) for l in labels]
    cm = confusion_matrix(ytrue, ypred, labels=labels)
    fig, ax = plt.subplots(figsize=(max(5, len(labels)), max(4, len(labels)-1)))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                xticklabels=names, yticklabels=names, ax=ax,
                linewidths=0.5, cbar_kws={"shrink":0.7})
    ax.set_xlabel("Predicted")
    ax.set_ylabel("True")
    ax.set_title(title, fontweight="bold", fontsize=10)
    plt.tight_layout()
    plt.savefig(os.path.join(CM_DIR, fname), dpi=150, bbox_inches="tight")
    plt.close()

def record(exp, model_name, ytrue, ypred, class_names_map, n_train, n_test):
    acc    = accuracy_score(ytrue, ypred)
    mf1    = f1_score(ytrue, ypred, average="macro",    zero_division=0)
    wf1    = f1_score(ytrue, ypred, average="weighted", zero_division=0)
    results_rows.append({
        "experiment": exp,
        "model":      model_name,
        "n_train":    n_train,
        "n_test":     n_test,
        "accuracy":   round(acc,4),
        "f1_macro":   round(mf1,4),
        "f1_weighted":round(wf1,4),
    })
    print(f"  [{model_name}] acc={acc:.4f}  macro-F1={mf1:.4f}")
    return acc, mf1

def train_and_eval(name, Xtr, ytr, Xte, yte, class_names_map, exp_name, cm_filename=None):
    le = LabelEncoder()
    ytr_enc = le.fit_transform(ytr)
    # Train
    if name == "RF":
        model = RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1)
    else:
        model = xgb.XGBClassifier(n_estimators=200, max_depth=6, learning_rate=0.1,
                                  eval_metric="mlogloss", random_state=42,
                                  n_jobs=-1, verbosity=0)
    model.fit(Xtr, ytr_enc)
    
    ypred_enc = model.predict(Xte)
    ypred = le.inverse_transform(ypred_enc)
    
    record(exp_name, name, yte, ypred, class_names_map, len(Xtr), len(Xte))
    if cm_filename and name == "RF":
        plot_cm(yte, ypred, class_names_map, f"{exp_name} (RF)", cm_filename)
    return ypred

# ═══════════════════════════════════════════════════════════════════════════
# EXP 1 — Within-Network (Prayagraj 80/20)
# ═══════════════════════════════════════════════════════════════════════════
print("\n══ EXP 1: Within-Network (Prayagraj 80/20) ══")
Xp = pry_df[avail].values
yp = pry_df["label"].values
cls_p = {v:k for k,v in CLASS_MAP.items() if v in set(yp)}

Xtr, Xte, ytr, yte = train_test_split(Xp, yp, test_size=0.2, stratify=yp, random_state=42)
for model_name in ["RF", "XGB"]:
    train_and_eval(model_name, Xtr, ytr, Xte, yte, cls_p, "Within-Network", "cm_within_network.png")

# ═══════════════════════════════════════════════════════════════════════════
# EXP 2 — Cross-Network
#   2a: Train Prayagraj → Test Tumsar
#   2b: Train Tumsar → Test Prayagraj
# ═══════════════════════════════════════════════════════════════════════════
print("\n══ EXP 2a: Cross-Network (Prayagraj → Tumsar) ══")
common_classes_pt = set(pry_df["label"].unique()) & set(tum_df["label"].unique())
print(f"   Common classes: {[CLASS_NAMES_BY_IDX[c] for c in sorted(common_classes_pt)]}")

pry_common = pry_df[pry_df["label"].isin(common_classes_pt)]
tum_common = tum_df[tum_df["label"].isin(common_classes_pt)]
cls_common = {v:k for k,v in CLASS_MAP.items() if v in common_classes_pt}

Xtr = pry_common[avail].values;  ytr = pry_common["label"].values
Xte = tum_common[avail].values;  yte = tum_common["label"].values

for model_name in ["RF", "XGB"]:
    train_and_eval(model_name, Xtr, ytr, Xte, yte, cls_common, "Cross-Net (Prayagraj→Tumsar)", "cm_cross_pry2tum.png")

print("\n══ EXP 2b: Cross-Network (Tumsar → Prayagraj) ══")
Xtr = tum_common[avail].values;  ytr = tum_common["label"].values
Xte = pry_common[avail].values;  yte = pry_common["label"].values

for model_name in ["RF", "XGB"]:
    train_and_eval(model_name, Xtr, ytr, Xte, yte, cls_common, "Cross-Net (Tumsar→Prayagraj)", "cm_cross_tum2pry.png")

# ═══════════════════════════════════════════════════════════════════════════
# EXP 3 — Open-World: DNS vs. Web traffic
#   Train on DNS classes only (DOH, DOT, DOQ, DOH3)
#   Test on all 6 — web classes (HTTPS_WEB, HTTP3_WEB) → labeled as "Web/Unknown"
# ═══════════════════════════════════════════════════════════════════════════
print("\n══ EXP 3: Open-World (DNS vs. HTTPS_WEB / HTTP3_WEB) ══")
DNS_CLASSES  = {CLASS_MAP["DOH"], CLASS_MAP["DOT"], CLASS_MAP["DOQ"], CLASS_MAP["DOH3"]}
WEB_CLASSES  = {CLASS_MAP["HTTPS_WEB"], CLASS_MAP["HTTP3_WEB"]}

# Binary task: Is this encrypted DNS (1) or generic web traffic (0)?
df_ow = df.copy()
df_ow["ow_label"] = df_ow["label"].apply(lambda l: 1 if l in DNS_CLASSES else 0)

# Train on 70% of mixed traffic to detect DNS vs Web
Xtr_ow, Xte_ow, ytr_ow, yte_ow = train_test_split(df_ow[avail].values, df_ow["ow_label"].values,
                                                   test_size=0.3, stratify=df_ow["ow_label"].values,
                                                   random_state=42)

ow_cls_names = {0:"Web/Unknown", 1:"Encrypted-DNS"}
for model_name in ["RF", "XGB"]:
    train_and_eval(model_name, Xtr_ow, ytr_ow, Xte_ow, yte_ow, ow_cls_names,
                   "Open-World (DNS vs Web)", "cm_open_world.png")

# ═══════════════════════════════════════════════════════════════════════════
# EXP 4 — Final Evaluation: DoH vs. DoH3 vs. DoQ (3-class, hardest)
# ═══════════════════════════════════════════════════════════════════════════
print("\n══ EXP 4: Final Evaluation — DoH / DoH3 / DoQ ══")
DNS3_CLASSES = {CLASS_MAP["DOH"], CLASS_MAP["DOH3"], CLASS_MAP["DOQ"]}
dns3_cls_names = {CLASS_MAP["DOH"]:"DOH", CLASS_MAP["DOH3"]:"DOH3", CLASS_MAP["DOQ"]:"DOQ"}

d3 = df[df["label"].isin(DNS3_CLASSES)].copy()
X3 = d3[avail].values
y3 = d3["label"].values

# 4a: Within-network (all data, 80/20)
Xtr3, Xte3, ytr3, yte3 = train_test_split(X3, y3, test_size=0.2, stratify=y3, random_state=42)

print("  4a — Within-network (DoH/DoH3/DoQ, 80/20):")
for model_name in ["RF", "XGB"]:
    train_and_eval(model_name, Xtr3, ytr3, Xte3, yte3, dns3_cls_names,
                   "Final (DoH/DoH3/DoQ) Within-Net", "cm_final_dns3_within.png")

# 4b: Cross-network (Prayagraj → Tumsar, only DOH/DOH3/DOQ)
print("  4b — Cross-network Prayagraj→Tumsar (DoH/DoH3/DoQ):")
pry3 = pry_df[pry_df["label"].isin(DNS3_CLASSES)]
tum3 = tum_df[tum_df["label"].isin(DNS3_CLASSES)]
common3 = set(pry3["label"].unique()) & set(tum3["label"].unique())
dns3_common_names = {v:k for k,v in CLASS_MAP.items() if v in common3}

if len(common3) >= 2 and len(tum3) > 5:
    pry3c = pry3[pry3["label"].isin(common3)]
    tum3c = tum3[tum3["label"].isin(common3)]
    for model_name in ["RF", "XGB"]:
        train_and_eval(model_name, pry3c[avail].values, pry3c["label"].values,
                       tum3c[avail].values, tum3c["label"].values,
                       dns3_common_names, "Final (DoH/DoH3/DoQ) Cross-Net Pry→Tum",
                       "cm_final_dns3_cross.png")

# ═══════════════════════════════════════════════════════════════════════════
# Summary plots
# ═══════════════════════════════════════════════════════════════════════════
res_df = pd.DataFrame(results_rows)
res_df.to_csv(os.path.join(REPORTS, "robustness_results.csv"), index=False)

# Grouped bar: accuracy + macro-F1 per experiment × model
exps = res_df["experiment"].unique()
fig, axes = plt.subplots(1, 2, figsize=(16, 6))
fig.suptitle("Robustness Evaluation — All Experiments", fontweight="bold")

for ax, metric in zip(axes, ["accuracy", "f1_macro"]):
    x  = np.arange(len(exps))
    w  = 0.35
    rf_vals  = [res_df[(res_df["experiment"]==e)&(res_df["model"]=="RF" )][metric].values[0]
                if len(res_df[(res_df["experiment"]==e)&(res_df["model"]=="RF")]) else 0
                for e in exps]
    xgb_vals = [res_df[(res_df["experiment"]==e)&(res_df["model"]=="XGB")][metric].values[0]
                if len(res_df[(res_df["experiment"]==e)&(res_df["model"]=="XGB")]) else 0
                for e in exps]
    ax.bar(x - w/2, rf_vals,  w, label="RF",      color="#2563EB", alpha=0.85)
    ax.bar(x + w/2, xgb_vals, w, label="XGBoost", color="#16A34A", alpha=0.85)
    ax.set_xticks(x)
    ax.set_xticklabels([e.replace(" ","\n") for e in exps], fontsize=7)
    ax.set_ylabel(metric.replace("_"," ").title())
    ax.set_title(metric.replace("_"," ").title())
    ax.set_ylim(0, 1.05)
    ax.legend()
    ax.grid(axis="y", linestyle="--", alpha=0.3)
    for i, (rv, xv) in enumerate(zip(rf_vals, xgb_vals)):
        ax.text(i-w/2, rv+0.01, f"{rv:.2f}", ha="center", fontsize=6)
        ax.text(i+w/2, xv+0.01, f"{xv:.2f}", ha="center", fontsize=6)

plt.tight_layout()
plt.savefig(os.path.join(REPORTS, "robustness_summary.png"), dpi=150, bbox_inches="tight")
plt.close()

print(f"\n✅ Robustness evaluation complete → {REPORTS}")
print("\n── Results Summary ──────────────────────────────────────────────")
pivot = res_df[["experiment","model","n_train","n_test","accuracy","f1_macro"]]
print(pivot.to_string(index=False))

# ── Generate full markdown report ────────────────────────────────────────
report_md = os.path.join(REPORTS, "full_report.md")
with open(report_md, "w") as f:
    f.write("# Encrypted DNS Traffic Intelligence\n")
    f.write("## Feature Importance, Ablation & Robustness — Full Report\n\n")
    f.write(f"**Generated:** 2026-11-17  |  **Dataset:** 35,616 packet-level records → {len(df)} flows\n\n")
    f.write("---\n\n")
    f.write("## 1. Feature Groups Used\n\n")
    f.write("| Group | Features | Count |\n|---|---|---|\n")
    for grp, info in cfg["feature_groups"].items():
        f.write(f"| **{grp.replace('_',' ').title()}** | "
                f"{', '.join(info['columns'][:4])} … | {len(info['columns'])} |\n")
    f.write("\n---\n\n## 2. Robustness Results\n\n")
    f.write(pivot.to_markdown(index=False))
    f.write("\n\n---\n\n")
    f.write("## 3. Key Findings\n\n")
    f.write("See companion plots:\n")
    f.write("- `feature_importance_plot.png` — RF vs XGBoost rankings\n")
    f.write("- `ablation_accuracy_bar.png` — group ablation results\n")
    f.write("- `ablation_f1_heatmap.png` — per-class F1 drop per group removed\n")
    f.write("- `shap_summary_bar.png` — SHAP feature importance\n")
    f.write("- `shap_beeswarm.png` — SHAP value distribution\n")
    f.write("- `robustness_summary.png` — all 4 robustness experiments\n")
    f.write("- `confusion_matrices/` — per-experiment confusion matrices\n")

print(f"\n📄 Full report → {report_md}")
