#!/usr/bin/env python3
"""
03_ablation_study.py
─────────────────────
Systematically remove one feature group at a time, retrain, compare.

Ablation runs:
  0. Full feature set (baseline)
  1. Remove packet_flow group
  2. Remove timing group
  3. Remove direction group
  4. Remove burst_volume group
  5. Minimal set: top-k features only (from combined importance)

Output:
  • ablation_results.csv
  • ablation_f1_heatmap.png
  • ablation_accuracy_bar.png
  • compact_feature_set.txt
"""

import os, warnings, yaml
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.metrics import f1_score, accuracy_score, classification_report
import xgboost as xgb

warnings.filterwarnings("ignore")

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA    = os.path.join(ROOT, "ablation_study", "data", "flow_features_combined.csv")
REPORTS = os.path.join(ROOT, "ablation_study", "reports")
os.makedirs(REPORTS, exist_ok=True)

with open(os.path.join(ROOT, "ablation_study", "data", "feature_groups.yaml")) as f:
    cfg = yaml.safe_load(f)

GROUPS = {name: info["columns"] for name, info in cfg["feature_groups"].items()}
ALL_FEAT = [c for cols in GROUPS.values() for c in cols]
CLASS_NAMES = {v:k for k,v in cfg["classes"].items()}
CLASS_LABELS = sorted(CLASS_NAMES.keys())

# Load importance ranking for minimal set
imp_path = os.path.join(REPORTS, "feature_importance_combined.csv")
if os.path.exists(imp_path):
    importance_df = pd.read_csv(imp_path)
    TOP_K = 15
    top_features = importance_df["feature"].head(TOP_K).tolist()
    print(f"Minimal set: top-{TOP_K} features from combined importance")
else:
    top_features = ALL_FEAT[:15]
    print("Warning: importance CSV not found, using first 15 features")

# ── Load data ────────────────────────────────────────────────────────────
df = pd.read_csv(DATA).dropna(subset=ALL_FEAT[:5])  # drop if core cols missing
df[ALL_FEAT] = df[ALL_FEAT].fillna(0)
y = df["label"].values
print(f"Loaded {len(df)} flows | Classes: {df['traffic_class'].value_counts().to_dict()}")

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

# ── Helper to train & evaluate ───────────────────────────────────────────
def evaluate(features, label=""):
    X = df[features].values
    rf  = RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1)
    xgm = xgb.XGBClassifier(n_estimators=200, max_depth=6, learning_rate=0.1,
                              eval_metric="mlogloss", random_state=42, n_jobs=-1, verbosity=0)
    results = {}
    for name, model in [("RF", rf), ("XGB", xgm)]:
        cv_res = cross_validate(model, X, y, cv=cv,
                                scoring=["accuracy","f1_macro","f1_weighted"],
                                return_train_score=False)
        results[name] = {
            "accuracy":     cv_res["test_accuracy"].mean(),
            "f1_macro":     cv_res["test_f1_macro"].mean(),
            "f1_weighted":  cv_res["test_f1_weighted"].mean(),
            "acc_std":      cv_res["test_accuracy"].std(),
            "f1_macro_std": cv_res["test_f1_macro"].std(),
        }
        print(f"  [{name}] acc={results[name]['accuracy']:.4f}  "
              f"macro-F1={results[name]['f1_macro']:.4f}  "
              f"n_features={len(features)}")

    # Also get per-class F1 (fit once on 80% split)
    from sklearn.model_selection import train_test_split
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2,
                                            stratify=y, random_state=42)
    rf.fit(Xtr, ytr)
    ypred = rf.predict(Xte)
    per_class_f1 = f1_score(yte, ypred, average=None, labels=CLASS_LABELS,
                             zero_division=0)
    results["RF"]["per_class_f1"] = per_class_f1
    return results

# ── Run ablation experiments ─────────────────────────────────────────────
experiments = {
    "Full Set":          ALL_FEAT,
    "−Packet/Flow":      [f for f in ALL_FEAT if f not in GROUPS["packet_flow"]],
    "−Timing":           [f for f in ALL_FEAT if f not in GROUPS["timing"]],
    "−Direction":        [f for f in ALL_FEAT if f not in GROUPS["direction"]],
    "−Burst/Volume":     [f for f in ALL_FEAT if f not in GROUPS["burst_volume"]],
    f"Minimal (top-{len(top_features)})": [f for f in top_features if f in df.columns],
}

rows       = []
heatmap_data = {}

for exp_name, feat_list in experiments.items():
    feat_list = [f for f in feat_list if f in df.columns]
    print(f"\n── {exp_name} ({len(feat_list)} features) ─────────")
    res = evaluate(feat_list, exp_name)
    for model, metrics in res.items():
        if model == "RF" and "per_class_f1" in metrics:
            heatmap_data[exp_name] = metrics["per_class_f1"]
        rows.append({
            "experiment":   exp_name,
            "model":        model,
            "n_features":   len(feat_list),
            "accuracy":     metrics.get("accuracy", np.nan),
            "f1_macro":     metrics.get("f1_macro", np.nan),
            "f1_weighted":  metrics.get("f1_weighted", np.nan),
            "acc_std":      metrics.get("acc_std", np.nan),
            "f1_macro_std": metrics.get("f1_macro_std", np.nan),
        })

results_df = pd.DataFrame(rows)
results_df.to_csv(os.path.join(REPORTS, "ablation_results.csv"), index=False)

# ── Plot 1: Accuracy bar chart ────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(14, 6))
fig.suptitle("Ablation Study — Remove Feature Group → Compare Performance", fontweight="bold")

for ax, metric in zip(axes, ["accuracy", "f1_macro"]):
    yerr_col = "acc_std" if "acc" in metric else "f1_macro_std"
    for model, color in [("RF","#2563EB"),("XGB","#16A34A")]:
        sub = results_df[results_df["model"] == model]
        bars = ax.bar(
            [x + (0 if model=="RF" else 0.35) for x in range(len(sub))],
            sub[metric].values, width=0.35,
            color=color, alpha=0.85, label=model,
            yerr=sub[yerr_col].values,
            capsize=3
        )
    ax.set_xticks([x+0.175 for x in range(len(experiments))])
    ax.set_xticklabels(list(experiments.keys()), rotation=20, ha="right", fontsize=8)
    ax.set_ylabel(metric.replace("_"," ").title())
    ax.set_title(metric.replace("_"," ").title())
    ax.set_ylim(0.5, 1.02)
    ax.legend()
    ax.axhline(y=results_df[(results_df["experiment"]=="Full Set")&
                              (results_df["model"]=="RF")][metric].values[0],
               color="red", linestyle="--", alpha=0.5, label="Full-set RF")
    ax.grid(axis="y", linestyle="--", alpha=0.3)

plt.tight_layout()
plt.savefig(os.path.join(REPORTS, "ablation_accuracy_bar.png"), dpi=150, bbox_inches="tight")
plt.close()

# ── Plot 2: Per-class F1 heatmap ──────────────────────────────────────────
hm_df = pd.DataFrame(heatmap_data, index=[CLASS_NAMES[i] for i in CLASS_LABELS]).T
fig, ax = plt.subplots(figsize=(10, 5))
sns.heatmap(hm_df, annot=True, fmt=".3f", cmap="YlGn", vmin=0.5, vmax=1.0,
            linewidths=0.5, ax=ax, cbar_kws={"shrink":0.7})
ax.set_title("Per-Class F1 Score — Ablation Study (Random Forest)", fontweight="bold")
ax.set_ylabel("Experiment")
ax.set_xlabel("Class")
plt.tight_layout()
plt.savefig(os.path.join(REPORTS, "ablation_f1_heatmap.png"), dpi=150, bbox_inches="tight")
plt.close()

# ── Save compact feature set ──────────────────────────────────────────────
# Pick features whose removal caused the least drop AND are in top importance
compact_path = os.path.join(REPORTS, "compact_feature_set.txt")
with open(compact_path, "w") as f:
    f.write("# Compact Feature Set — Selected from Ablation + Importance Analysis\n")
    f.write(f"# Top-{len(top_features)} features (combined RF+XGB importance rank)\n\n")
    for feat in top_features:
        grp = next((g for g,cols in GROUPS.items() if feat in cols), "other")
        f.write(f"{feat}  # group={grp}\n")

print(f"\n✅ Ablation complete — results saved to {REPORTS}/")
print(f"   ablation_results.csv")
print(f"   ablation_accuracy_bar.png")
print(f"   ablation_f1_heatmap.png")
print(f"   compact_feature_set.txt  ({len(top_features)} features)")

print("\n── Ablation Summary ─────────────────────────────────────────────")
pivot = results_df[results_df["model"]=="RF"][["experiment","n_features","accuracy","f1_macro"]].copy()
pivot = pivot.set_index("experiment")
print(pivot.round(4).to_string())
