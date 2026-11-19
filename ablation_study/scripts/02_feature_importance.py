#!/usr/bin/env python3
"""
02_feature_importance.py
─────────────────────────
Train RF + XGBoost on the full feature set.
Outputs:
  • feature_importance_rf.csv
  • feature_importance_xgb.csv
  • feature_importance_plot.png
"""

import os, warnings, yaml
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.preprocessing import LabelEncoder
import xgboost as xgb

warnings.filterwarnings("ignore")

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA    = os.path.join(ROOT, "ablation_study", "data", "flow_features_combined.csv")
REPORTS = os.path.join(ROOT, "ablation_study", "reports")
os.makedirs(REPORTS, exist_ok=True)

with open(os.path.join(ROOT, "ablation_study", "data", "feature_groups.yaml")) as f:
    cfg = yaml.safe_load(f)

GROUP_MAP = {}
ALL_FEAT  = []
for grp_name, grp_info in cfg["feature_groups"].items():
    for col in grp_info["columns"]:
        GROUP_MAP[col] = grp_name
        ALL_FEAT.append(col)

# ── Load data ────────────────────────────────────────────────────────────
df = pd.read_csv(DATA).dropna(subset=ALL_FEAT)
print(f"Loaded {len(df)} flows | Classes: {df['traffic_class'].value_counts().to_dict()}")

X = df[ALL_FEAT].fillna(0).values
y = df["label"].values
class_names = {v:k for k,v in cfg["classes"].items()}

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

# ── Random Forest ────────────────────────────────────────────────────────
print("\n[RF] Training …")
rf = RandomForestClassifier(n_estimators=300, max_depth=None,
                             min_samples_leaf=2, random_state=42, n_jobs=-1)
rf_scores = cross_val_score(rf, X, y, cv=cv, scoring="f1_macro")
rf.fit(X, y)
rf_imp = pd.DataFrame({"feature": ALL_FEAT,
                        "importance": rf.feature_importances_,
                        "group": [GROUP_MAP.get(f,"other") for f in ALL_FEAT]
                       }).sort_values("importance", ascending=False).reset_index(drop=True)
rf_imp["rank"] = rf_imp.index + 1
rf_imp.to_csv(os.path.join(REPORTS, "feature_importance_rf.csv"), index=False)
print(f"  5-fold macro-F1: {rf_scores.mean():.4f} ± {rf_scores.std():.4f}")
print(f"  Top-10 features:\n{rf_imp[['rank','feature','group','importance']].head(10).to_string(index=False)}")

# ── XGBoost ──────────────────────────────────────────────────────────────
print("\n[XGB] Training …")
xgb_model = xgb.XGBClassifier(n_estimators=300, max_depth=6, learning_rate=0.1,
                                use_label_encoder=False, eval_metric="mlogloss",
                                random_state=42, n_jobs=-1, verbosity=0)
xgb_scores = cross_val_score(xgb_model, X, y, cv=cv, scoring="f1_macro")
xgb_model.fit(X, y)
xgb_imp = pd.DataFrame({"feature": ALL_FEAT,
                          "importance": xgb_model.feature_importances_,
                          "group": [GROUP_MAP.get(f,"other") for f in ALL_FEAT]
                         }).sort_values("importance", ascending=False).reset_index(drop=True)
xgb_imp["rank"] = xgb_imp.index + 1
xgb_imp.to_csv(os.path.join(REPORTS, "feature_importance_xgb.csv"), index=False)
print(f"  5-fold macro-F1: {xgb_scores.mean():.4f} ± {xgb_scores.std():.4f}")
print(f"  Top-10 features:\n{xgb_imp[['rank','feature','group','importance']].head(10).to_string(index=False)}")

# ── Combined importance (average rank) ───────────────────────────────────
merged = rf_imp[["feature","group"]].copy()
merged["rf_imp"]  = rf_imp["importance"]
merged["xgb_imp"] = xgb_imp.set_index("feature").loc[merged["feature"], "importance"].values
merged["avg_imp"] = (merged["rf_imp"] + merged["xgb_imp"]) / 2
merged = merged.sort_values("avg_imp", ascending=False).reset_index(drop=True)
merged["combined_rank"] = merged.index + 1
merged.to_csv(os.path.join(REPORTS, "feature_importance_combined.csv"), index=False)

# ── Plot ──────────────────────────────────────────────────────────────────
GROUP_COLORS = {
    "packet_flow": "#2563EB",
    "timing":      "#16A34A",
    "direction":   "#DC2626",
    "burst_volume":"#D97706",
    "other":       "#6B7280",
}

top20 = merged.head(20)
colors = [GROUP_COLORS.get(g, "#6B7280") for g in top20["group"]]

fig, axes = plt.subplots(1, 2, figsize=(16, 8))
fig.suptitle("Feature Importance — RF vs XGBoost (Top 20)", fontsize=14, fontweight="bold")

for ax, (model_name, imp_col) in zip(axes, [("Random Forest","rf_imp"),("XGBoost","xgb_imp")]):
    vals  = top20[imp_col].values
    feats = top20["feature"].values
    bars  = ax.barh(range(20), vals[::-1], color=colors[::-1])
    ax.set_yticks(range(20))
    ax.set_yticklabels(feats[::-1], fontsize=8)
    ax.set_xlabel("Importance")
    ax.set_title(model_name)
    ax.grid(axis="x", linestyle="--", alpha=0.4)

# Legend
from matplotlib.patches import Patch
legend_elements = [Patch(facecolor=c, label=g.replace("_"," ").title())
                   for g,c in GROUP_COLORS.items() if g != "other"]
fig.legend(handles=legend_elements, loc="lower center", ncol=4, fontsize=9, title="Feature Group")
plt.tight_layout(rect=[0,0.06,1,1])
plt.savefig(os.path.join(REPORTS, "feature_importance_plot.png"), dpi=150, bbox_inches="tight")
plt.close()

print(f"\n✅ Saved reports to {REPORTS}")
print(f"   feature_importance_rf.csv, feature_importance_xgb.csv,")
print(f"   feature_importance_combined.csv, feature_importance_plot.png")
print(f"\n── Baseline (Full Feature Set) ──────────────────────────────────")
print(f"   RF  macro-F1 (5-fold): {rf_scores.mean():.4f} ± {rf_scores.std():.4f}")
print(f"   XGB macro-F1 (5-fold): {xgb_scores.mean():.4f} ± {xgb_scores.std():.4f}")

# Save baseline scores for downstream scripts
pd.DataFrame({
    "model": ["RF","XGBoost"],
    "cv_f1_mean": [rf_scores.mean(), xgb_scores.mean()],
    "cv_f1_std":  [rf_scores.std(),  xgb_scores.std()],
    "feature_set": ["full","full"],
}).to_csv(os.path.join(REPORTS, "baseline_scores.csv"), index=False)
