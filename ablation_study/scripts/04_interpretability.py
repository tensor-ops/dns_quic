#!/usr/bin/env python3
"""
04_interpretability.py
───────────────────────
SHAP analysis on the compact feature set using XGBoost.

Outputs:
  • shap_summary_bar.png
  • shap_beeswarm.png
  • shap_class_waterfall/  (one PNG per class)
  • shap_values.csv
"""

import os, warnings, yaml
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import xgboost as xgb
import shap
from sklearn.model_selection import train_test_split

warnings.filterwarnings("ignore")

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA    = os.path.join(ROOT, "ablation_study", "data", "flow_features_combined.csv")
REPORTS = os.path.join(ROOT, "ablation_study", "reports")
WFALL   = os.path.join(REPORTS, "shap_class_waterfall")
os.makedirs(WFALL, exist_ok=True)

with open(os.path.join(ROOT, "ablation_study", "data", "feature_groups.yaml")) as f:
    cfg = yaml.safe_load(f)

GROUPS    = {name: info["columns"] for name, info in cfg["feature_groups"].items()}
ALL_FEAT  = [c for cols in GROUPS.values() for c in cols]
CLASS_MAP = cfg["classes"]   # DOH→0, …
CLASS_NAMES = {v:k for k,v in CLASS_MAP.items()}

# Load compact feature set if available
compact_path = os.path.join(REPORTS, "compact_feature_set.txt")
if os.path.exists(compact_path):
    compact_feats = []
    with open(compact_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                compact_feats.append(line.split()[0])
    print(f"Using compact feature set ({len(compact_feats)} features)")
else:
    compact_feats = ALL_FEAT
    print("Using full feature set (compact_feature_set.txt not found)")

# ── Load data ────────────────────────────────────────────────────────────
df = pd.read_csv(DATA)
avail = [f for f in compact_feats if f in df.columns]
df[avail] = df[avail].fillna(0)
X = df[avail].values
y = df["label"].values

Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, stratify=y, random_state=42)

# ── Train XGBoost ────────────────────────────────────────────────────────
print("[XGB] Training on compact feature set …")
model = xgb.XGBClassifier(n_estimators=300, max_depth=6, learning_rate=0.1,
                            eval_metric="mlogloss", random_state=42,
                            n_jobs=-1, verbosity=0)
model.fit(Xtr, ytr)
acc = (model.predict(Xte) == yte).mean()
print(f"  Test accuracy: {acc:.4f}")

# ── SHAP ─────────────────────────────────────────────────────────────────
print("[SHAP] Computing SHAP values (may take a minute) …")
explainer = shap.TreeExplainer(model)
shap_vals = explainer.shap_values(Xte)   # shape: (n_samples, n_features, n_classes) or list

# XGBoost multi-class SHAP: list of arrays length n_classes
if isinstance(shap_vals, list):
    # shape = (n_classes, n_samples, n_features)
    shap_arr = np.stack(shap_vals, axis=2)   # → (n_samples, n_features, n_classes)
else:
    shap_arr = shap_vals

# Mean |SHAP| per feature across all classes
mean_abs_shap = np.abs(shap_arr).mean(axis=(0,2)) if shap_arr.ndim == 3 else np.abs(shap_arr).mean(axis=0)

shap_importance = pd.DataFrame({
    "feature": avail,
    "mean_abs_shap": mean_abs_shap,
}).sort_values("mean_abs_shap", ascending=False).reset_index(drop=True)
shap_importance.to_csv(os.path.join(REPORTS, "shap_values.csv"), index=False)

# ── Plot 1: Summary Bar ───────────────────────────────────────────────────
GROUP_COLORS = {
    "packet_flow": "#2563EB",
    "timing":      "#16A34A",
    "direction":   "#DC2626",
    "burst_volume":"#D97706",
    "other":       "#6B7280",
}
grp_lookup = {f:g for g,cols in GROUPS.items() for f in cols}

top_n = min(20, len(shap_importance))
top   = shap_importance.head(top_n)
colors = [GROUP_COLORS.get(grp_lookup.get(f,"other"), "#6B7280") for f in top["feature"]]

fig, ax = plt.subplots(figsize=(10, 7))
bars = ax.barh(range(top_n), top["mean_abs_shap"].values[::-1], color=colors[::-1])
ax.set_yticks(range(top_n))
ax.set_yticklabels(top["feature"].values[::-1], fontsize=9)
ax.set_xlabel("Mean |SHAP| value")
ax.set_title("SHAP Feature Importance — Encrypted DNS Classification\n(XGBoost, all classes)", fontweight="bold")
ax.grid(axis="x", linestyle="--", alpha=0.4)

from matplotlib.patches import Patch
legend_elements = [Patch(facecolor=c, label=g.replace("_"," ").title())
                   for g,c in GROUP_COLORS.items() if g != "other"]
ax.legend(handles=legend_elements, fontsize=8, loc="lower right")
plt.tight_layout()
plt.savefig(os.path.join(REPORTS, "shap_summary_bar.png"), dpi=150, bbox_inches="tight")
plt.close()
print("  Saved: shap_summary_bar.png")

# ── Plot 2: Beeswarm ─────────────────────────────────────────────────────
# Use average SHAP across classes for beeswarm
if shap_arr.ndim == 3:
    shap_2d = shap_arr.mean(axis=2)
else:
    shap_2d = shap_arr

Xte_df = pd.DataFrame(Xte, columns=avail)
fig, ax = plt.subplots(figsize=(10, 7))
shap.summary_plot(shap_2d, Xte_df, show=False, max_display=20,
                  plot_type="dot", color_bar=True)
plt.title("SHAP Beeswarm — Feature Impact Distribution", fontweight="bold", fontsize=12)
plt.tight_layout()
plt.savefig(os.path.join(REPORTS, "shap_beeswarm.png"), dpi=150, bbox_inches="tight")
plt.close()
print("  Saved: shap_beeswarm.png")

# ── Plot 3: Per-class waterfall (one sample per class) ────────────────────
if shap_arr.ndim == 3:
    for cls_idx in sorted(CLASS_NAMES.keys()):
        cls_name = CLASS_NAMES[cls_idx]
        # Find a correctly-classified test sample for this class
        pred = model.predict(Xte)
        mask = (yte == cls_idx) & (pred == cls_idx)
        if not mask.any():
            mask = (yte == cls_idx)
        if not mask.any():
            continue
        sample_idx = np.where(mask)[0][0]

        shap_cls = shap_arr[sample_idx, :, cls_idx]   # SHAP for this class
        base_val  = explainer.expected_value[cls_idx] if isinstance(explainer.expected_value, list) \
                    else float(explainer.expected_value)

        # Manual waterfall bar chart
        order = np.argsort(np.abs(shap_cls))[::-1][:12]
        vals  = shap_cls[order]
        feats = [avail[i] for i in order]

        fig, ax = plt.subplots(figsize=(8, 5))
        colors_w = ["#DC2626" if v>0 else "#2563EB" for v in vals]
        ax.barh(range(len(vals)), vals[::-1], color=colors_w[::-1])
        ax.set_yticks(range(len(vals)))
        ax.set_yticklabels(feats[::-1], fontsize=8)
        ax.axvline(0, color="black", linewidth=0.8)
        ax.set_xlabel("SHAP value")
        ax.set_title(f"SHAP Waterfall — Class: {cls_name}\n(sample from test set)", fontweight="bold")
        ax.grid(axis="x", linestyle="--", alpha=0.3)
        plt.tight_layout()
        plt.savefig(os.path.join(WFALL, f"shap_waterfall_{cls_name}.png"), dpi=150, bbox_inches="tight")
        plt.close()
    print(f"  Saved: shap_class_waterfall/ ({len(CLASS_NAMES)} PNGs)")

print(f"\n✅ Interpretability analysis complete → {REPORTS}")
print(f"\n── Top-10 SHAP Features ─────────────────────────────────────────")
print(shap_importance.head(10).to_string(index=False))
