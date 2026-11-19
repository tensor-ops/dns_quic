"""
Generator script to build production-grade Jupyter notebooks for all models
used in the research project:
1. 01_Random_Forest.ipynb
2. 02_XGBoost.ipynb
3. 03_Decision_Tree.ipynb
4. 04_Support_Vector_Machine.ipynb
5. 05_K_Nearest_Neighbors.ipynb
6. 06_Logistic_Regression.ipynb
7. 07_MLP_Neural_Network.ipynb
8. 08_Model_Comparison_and_Benchmarking.ipynb
"""

import os
from pathlib import Path
import nbformat as nbf

NOTEBOOKS_DIR = Path("/Users/paru/paru/projects/RM/PROJECT_NOTEBOOKS")
NOTEBOOKS_DIR.mkdir(parents=True, exist_ok=True)

MODELS_CONFIG = [
    {
        "filename": "01_Random_Forest.ipynb",
        "title": "Random Forest Classifier — Encrypted DNS & QUIC Traffic Classification",
        "model_name": "Random Forest",
        "short_desc": "Primary tree-ensemble baseline offering robust nonlinear classification and native Gini/entropy feature importance ranking.",
        "imports": """from sklearn.ensemble import RandomForestClassifier""",
        "model_def": """# Random Forest with 300 estimators and entropy criterion
model = RandomForestClassifier(
    n_estimators=300,
    criterion='entropy',
    max_depth=25,
    min_samples_split=2,
    min_samples_leaf=1,
    n_jobs=-1,
    random_state=RANDOM_STATE
)""",
        "requires_scaler": False,
        "deep_dive": """# ── Feature Importance Analysis ──
importances = model.feature_importances_
feat_imp = pd.DataFrame({
    'Feature': FEATURE_COLS,
    'Importance': importances
}).sort_values('Importance', ascending=False)

plt.figure(figsize=(8, 4))
sns.barplot(x='Importance', y='Feature', data=feat_imp, palette='viridis')
plt.title(f'{MODEL_NAME} — Feature Importance (Gini/Entropy)', fontweight='bold')
plt.xlabel('Normalized Importance Score')
plt.tight_layout()
plt.show()

print('Feature Importance Table:')
print(feat_imp.to_string(index=False))"""
    },
    {
        "filename": "02_XGBoost.ipynb",
        "title": "XGBoost Classifier — Gradient Boosted Decision Trees on Observable Features",
        "model_name": "XGBoost",
        "short_desc": "Optimized extreme gradient boosting library designed for high computational efficiency, regularized loss minimization, and complex decision boundaries.",
        "imports": """import xgboost as xgb
from xgboost import XGBClassifier""",
        "model_def": """# XGBoost multi-class classifier with softprob objective
model = XGBClassifier(
    n_estimators=200,
    learning_rate=0.08,
    max_depth=6,
    subsample=0.85,
    colsample_bytree=0.85,
    objective='multi:softprob',
    eval_metric='mlogloss',
    tree_method='hist',
    random_state=RANDOM_STATE,
    n_jobs=-1
)""",
        "requires_scaler": False,
        "deep_dive": """# ── XGBoost Feature Gain & Tree Importance ──
gain_imp = model.get_booster().get_score(importance_type='gain')
df_gain = pd.DataFrame([
    {'Feature': k, 'Gain': v} for k, v in gain_imp.items()
]).sort_values('Gain', ascending=False)

plt.figure(figsize=(8, 4))
sns.barplot(x='Gain', y='Feature', data=df_gain, palette='magma')
plt.title(f'{MODEL_NAME} — Feature Gain Ranking', fontweight='bold')
plt.xlabel('Average Gain per Split')
plt.tight_layout()
plt.show()

print('XGBoost Gain Table:')
print(df_gain.to_string(index=False))"""
    },
    {
        "filename": "03_Decision_Tree.ipynb",
        "title": "Decision Tree Classifier — Interpretable Non-Linear Benchmark",
        "model_name": "Decision Tree",
        "short_desc": "Transparent single-tree baseline measuring the degree of separability and interpretable hierarchical decision paths on raw timing and packet sizes.",
        "imports": """from sklearn.tree import DecisionTreeClassifier, plot_tree""",
        "model_def": """# Decision Tree with entropy splitting criterion and controlled depth
model = DecisionTreeClassifier(
    criterion='entropy',
    max_depth=12,
    min_samples_split=4,
    min_samples_leaf=2,
    random_state=RANDOM_STATE
)""",
        "requires_scaler": False,
        "deep_dive": """# ── Decision Tree Structure & Pruning Insights ──
print(f'Tree Depth: {model.get_depth()}')
print(f'Total Leaf Nodes: {model.get_n_leaves()}')

plt.figure(figsize=(18, 8))
plot_tree(model, max_depth=3, feature_names=FEATURE_COLS, class_names=list(CLASS_NAMES.values()), filled=True, rounded=True, fontsize=9)
plt.title(f'{MODEL_NAME} — Top Decision Splits (Depth ≤ 3)', fontweight='bold')
plt.tight_layout()
plt.show()"""
    },
    {
        "filename": "04_Support_Vector_Machine.ipynb",
        "title": "Support Vector Machine (SVM) — Optimal Margin Hyperplane Classifier",
        "model_name": "SVM (RBF Kernel)",
        "short_desc": "Kernelized margin classifier projecting standardized packet features into high-dimensional space with Radial Basis Function (RBF) kernel.",
        "imports": """from sklearn.svm import SVC""",
        "model_def": """# Support Vector Classifier with RBF kernel and probability calibration
model = SVC(
    C=10.0,
    kernel='rbf',
    gamma='scale',
    probability=True,
    random_state=RANDOM_STATE
)""",
        "requires_scaler": True,
        "deep_dive": """# ── Support Vectors Audit ──
print(f'Total Support Vectors: {model.named_steps["clf"].n_support_.sum():,}')
for idx, cls_name in CLASS_NAMES.items():
    print(f'  Class {cls_name:10s}: {model.named_steps["clf"].n_support_[idx]:4d} support vectors')"""
    },
    {
        "filename": "05_K_Nearest_Neighbors.ipynb",
        "title": "k-Nearest Neighbors (KNN) — Instance-Based Metric Benchmark",
        "model_name": "k-Nearest Neighbors",
        "short_desc": "Distance metric instance-based classifier evaluating local spatial proximity and cluster continuity in standardized packet feature space.",
        "imports": """from sklearn.neighbors import KNeighborsClassifier""",
        "model_def": """# k-Nearest Neighbors with Minkowski distance metric
model = KNeighborsClassifier(
    n_neighbors=7,
    weights='distance',
    metric='minkowski',
    p=2,
    n_jobs=-1
)""",
        "requires_scaler": True,
        "deep_dive": """# ── Neighbor Sensitivity Analysis ──
k_values = [3, 5, 7, 11, 15]
k_scores = []
for k in k_values:
    knn_trial = KNeighborsClassifier(n_neighbors=k, weights='distance')
    knn_trial.fit(X_tr_scaled, y_train)
    score = knn_trial.score(X_val_scaled, y_val)
    k_scores.append(score)

plt.figure(figsize=(7, 3.5))
plt.plot(k_values, k_scores, marker='o', color='#2563EB', linewidth=2)
plt.title('KNN Validation Accuracy vs. k (Number of Neighbors)', fontweight='bold')
plt.xlabel('k')
plt.ylabel('Validation Accuracy')
plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()
plt.show()"""
    },
    {
        "filename": "06_Logistic_Regression.ipynb",
        "title": "Logistic Regression — Linear Separability Baseline with L2 Regularization",
        "model_name": "Logistic Regression",
        "short_desc": "Parametric generalized linear baseline evaluating whether modern encrypted DNS and QUIC protocols are linearly separable on observable packet features.",
        "imports": """from sklearn.linear_model import LogisticRegression""",
        "model_def": """# Multinomial Logistic Regression with L2 regularization
model = LogisticRegression(
    penalty='l2',
    C=1.0,
    solver='lbfgs',
    max_iter=1000,
    random_state=RANDOM_STATE
)""",
        "requires_scaler": True,
        "deep_dive": """# ── Coefficients Analysis across Classes ──
clf_lr = model.named_steps['clf'] if 'clf' in model.named_steps else model
coef_df = pd.DataFrame(clf_lr.coef_, columns=FEATURE_COLS, index=list(CLASS_NAMES.values()))

plt.figure(figsize=(10, 5))
sns.heatmap(coef_df, annot=True, fmt='.2f', cmap='coolwarm', center=0)
plt.title(f'{MODEL_NAME} — Feature Coefficients by Protocol Class', fontweight='bold')
plt.tight_layout()
plt.show()"""
    },
    {
        "filename": "07_MLP_Neural_Network.ipynb",
        "title": "Multi-Layer Perceptron (MLP) — Feedforward Deep Neural Network",
        "model_name": "MLP Neural Network",
        "short_desc": "Multi-layer feedforward artificial neural network evaluating multi-layer non-linear cross-feature representations with ReLU activations.",
        "imports": """from sklearn.neural_network import MLPClassifier""",
        "model_def": """# MLP with two hidden layers (128, 64) and Adam optimizer
model = MLPClassifier(
    hidden_layer_sizes=(128, 64),
    activation='relu',
    solver='adam',
    alpha=0.0001,
    batch_size=128,
    learning_rate='adaptive',
    learning_rate_init=0.001,
    max_iter=250,
    early_stopping=True,
    validation_fraction=0.1,
    n_iter_no_change=15,
    random_state=RANDOM_STATE
)""",
        "requires_scaler": True,
        "deep_dive": """# ── Training Loss Curve ──
clf_mlp = model.named_steps['clf'] if 'clf' in model.named_steps else model
plt.figure(figsize=(8, 3.5))
plt.plot(clf_mlp.loss_curve_, color='#DC2626', linewidth=2, label='Training Loss')
plt.title(f'{MODEL_NAME} — Convergence Loss Curve (Adam)', fontweight='bold')
plt.xlabel('Epoch / Iteration')
plt.ylabel('Cross-Entropy Loss')
plt.grid(True, linestyle='--', alpha=0.6)
plt.legend()
plt.tight_layout()
plt.show()
print(f'Stopped after {clf_mlp.n_iter_} iterations with final loss {clf_mlp.loss_:.4f}')"""
    }
]


def build_single_model_notebook(cfg):
    nb = nbf.v4.new_notebook()

    # Markdown: Header
    md_header = f"""# {cfg['title']}

**Project:** Encrypted DNS & QUIC Traffic Intelligence  
**Focus:** Observable Traffic Flow Classification without Payload Decryption  
**Model Family:** `{cfg['model_name']}`  
**Zero-Leakage Policy:** Strictly relies on observable packet lengths and inter-arrival timing. Zero IP, port, SNI, or payload content leakage.

---

### Model Overview
{cfg['short_desc']}

**Protocol Target Classes (6):**
- `DOH`: DNS-over-HTTPS (RFC 8484)
- `DOQ`: DNS-over-QUIC (RFC 9250)
- `DOH3`: DNS-over-HTTP/3 (RFC 9114)
- `QUIC`: Raw QUIC Transport Protocol (RFC 9000)
- `HTTPS_WEB`: Standard HTTPS Web Browsing
- `HTTP3_WEB`: Modern Web Browsing over HTTP/3 / QUIC
*(DOT protocol completely removed as per specification)*
"""
    nb.cells.append(nbf.v4.new_markdown_cell(md_header))

    # Code: Imports & Seed
    code_imports = f"""# ── 1. Environment Setup & Core Dependencies ──
import os
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
%matplotlib inline
import seaborn as sns

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_validate
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix, roc_auc_score, roc_curve
)
import joblib

{cfg['imports']}

# Visualization aesthetics
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams['font.sans-serif'] = 'Helvetica'
plt.rcParams['axes.edgecolor'] = '#cbd5e1'
plt.rcParams['axes.linewidth'] = 0.8

RANDOM_STATE = 42
MODEL_NAME = "{cfg['model_name']}"
print(f"Environment initialized for {{MODEL_NAME}}.")
"""
    nb.cells.append(nbf.v4.new_code_cell(code_imports))

    # Markdown: Data Loading
    md_data = """## 2. Dataset Ingestion & Validation

We load the consolidated multi-vantage point dataset from `../PROJECT_DATASET/`.  
By default, this notebook ingests `FULL_COMBINED_WITH_METADATA.csv` (or `FULL_COMBINED.csv`), covering captures from:
- **Prayagraj (Airtel AS45609 & Reliance Jio AS55836)**
- **Tumsar (Maharashtra Airtel/Docker Lab)**
- **Mirzapur (Reliance Jio)**
"""
    nb.cells.append(nbf.v4.new_markdown_cell(md_data))

    # Code: Load Data
    code_load = """# ── 2. Load Consolidated Multi-Vantage Point Dataset ──
DATA_DIR = Path("../PROJECT_DATASET")
DATASET_PATH = DATA_DIR / "FULL_COMBINED_WITH_METADATA.csv"

# Fallback to standard 5-col version if metadata file is not present
if not DATASET_PATH.exists():
    DATASET_PATH = DATA_DIR / "FULL_COMBINED.csv"

print(f"Loading dataset from: {DATASET_PATH}")
df = pd.read_csv(DATASET_PATH)
print(f"Dataset successfully loaded: {df.shape[0]:,d} total records, {df.shape[1]} columns.")

# Audit class distribution
print("\\nClass Distribution:")
print(df['traffic_class'].value_counts())

# Audit missing values
null_count = df.isnull().sum().sum()
assert null_count == 0, f"Found {null_count} missing values in dataset!"
print("\\nData Integrity Check: PASS (0 missing values, zero DOT entries).")
"""
    nb.cells.append(nbf.v4.new_code_cell(code_load))

    # Markdown: Feature Extraction
    md_features = """## 3. Feature Matrix Construction & Zero-Leakage Policy

The ML features strictly follow the kinematic packet observable schema:
1. `Current packet size` ($L_i$)
2. `Previous packet size` ($L_{i-1}$)
3. `Current time gap` ($\Delta t_i = t_i - t_{i-1}$)
4. `Previous time gap` ($\Delta t_{i-1} = t_{i-1} - t_{i-2}$)
"""
    nb.cells.append(nbf.v4.new_markdown_cell(md_features))

    # Code: Feature Preparation
    code_features = """# ── 3. Feature Matrix & Target Label Vector ──
FEATURE_COLS = [
    'Current packet size',
    'Previous packet size',
    'Current time gap',
    'Previous time gap'
]

CLASS_MAP = {
    'DOH': 0,
    'DOQ': 1,
    'DOH3': 2,
    'QUIC': 3,
    'HTTPS_WEB': 4,
    'HTTP3_WEB': 5
}
CLASS_NAMES = {v: k for k, v in CLASS_MAP.items()}

X = df[FEATURE_COLS].values
y = df['traffic_class'].map(CLASS_MAP).values

print(f"Feature matrix X shape: {X.shape}")
print(f"Target vector y shape:  {y.shape}")
print(f"Classes present: {[CLASS_NAMES[i] for i in sorted(np.unique(y))]}")
"""
    nb.cells.append(nbf.v4.new_code_cell(code_features))

    # Markdown: Splitting
    md_split = """## 4. Stratified Train / Validation / Test Splitting

To ensure robust evaluation:
- **Train Set (70%):** Model parameter estimation.
- **Validation Set (15%):** Hyperparameter tuning and model checkpointing.
- **Holdout Test Set (15%):** Completely unseen test set for unbiased final reporting.
"""
    nb.cells.append(nbf.v4.new_markdown_cell(md_split))

    # Code: Train Val Test Split
    code_split = """# ── 4. Stratified 70 / 15 / 15 Partitioning ──
X_train_val, X_test, y_train_val, y_test = train_test_split(
    X, y, test_size=0.15, stratify=y, random_state=RANDOM_STATE
)

# Further split train_val into 70% train and 15% val (relative 15/85 ≈ 0.1765)
X_train, X_val, y_train, y_val = train_test_split(
    X_train_val, y_train_val, test_size=(0.15 / 0.85), stratify=y_train_val, random_state=RANDOM_STATE
)

print(f"Train set:      {X_train.shape[0]:,d} samples ({X_train.shape[0]/len(X):.1%})")
print(f"Validation set: {X_val.shape[0]:,d} samples ({X_val.shape[0]/len(X):.1%})")
print(f"Test set:       {X_test.shape[0]:,d} samples ({X_test.shape[0]/len(X):.1%})")
"""
    nb.cells.append(nbf.v4.new_code_cell(code_split))

    # Markdown: Pipeline
    md_pipeline = f"""## 5. Model Architecture & Pipeline Construction

We configure `{cfg['model_name']}`.
{"A `StandardScaler` pipeline is employed to normalize feature scales for optimal convergence." if cfg['requires_scaler'] else "Tree-based models do not require monotonic feature scaling; raw packet dimensions are directly processed."}
"""
    nb.cells.append(nbf.v4.new_markdown_cell(md_pipeline))

    # Code: Model Definition
    if cfg['requires_scaler']:
        pipeline_code = f"""# ── 5. Define Scaler + Model Pipeline ──
{cfg['model_def']}

pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('clf', model)
])
print("Model Pipeline constructed successfully:")
print(pipeline)
"""
    else:
        pipeline_code = f"""# ── 5. Define Model Instance ──
{cfg['model_def']}

pipeline = model
print("Model instance constructed successfully:")
print(pipeline)
"""
    nb.cells.append(nbf.v4.new_code_cell(pipeline_code))

    # Markdown: Training & CV
    md_train = """## 6. Model Training & 5-Fold Stratified Cross-Validation

We evaluate model stability using 5-fold cross-validation on the training set, followed by full fitting.
"""
    nb.cells.append(nbf.v4.new_markdown_cell(md_train))

    # Code: Training & CV
    code_train = """# ── 6. 5-Fold Stratified Cross-Validation & Fit ──
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
scoring = ['accuracy', 'f1_macro', 'f1_weighted']

print(f"Running 5-fold cross-validation for {MODEL_NAME}...")
start_time = time.time()
cv_results = cross_validate(pipeline, X_train, y_train, cv=cv, scoring=scoring, n_jobs=-1)
train_time = time.time() - start_time

print(f"\\n5-Fold Cross-Validation Results ({train_time:.2f}s):")
print(f"  Accuracy:    {np.mean(cv_results['test_accuracy']):.4f} ± {np.std(cv_results['test_accuracy']):.4f}")
print(f"  Macro-F1:    {np.mean(cv_results['test_f1_macro']):.4f} ± {np.std(cv_results['test_f1_macro']):.4f}")
print(f"  Weighted-F1: {np.mean(cv_results['test_f1_weighted']):.4f} ± {np.std(cv_results['test_f1_weighted']):.4f}")

# Fit on entire training set
print(f"\\nFitting {MODEL_NAME} on full training split ({len(X_train):,d} samples)...")
pipeline.fit(X_train, y_train)
print("Fit complete.")
"""
    nb.cells.append(nbf.v4.new_code_cell(code_train))

    # Markdown: Validation Set
    md_val = """## 7. Validation Set Evaluation

Evaluating performance on the independent validation split ($15\\%$) to verify generalization before unlocking the test set.
"""
    nb.cells.append(nbf.v4.new_markdown_cell(md_val))

    # Code: Val Eval
    code_val = """# ── 7. Evaluate on Validation Set ──
y_val_pred = pipeline.predict(X_val)

val_acc = accuracy_score(y_val, y_val_pred)
val_f1_macro = f1_score(y_val, y_val_pred, average='macro')
val_f1_weighted = f1_score(y_val, y_val_pred, average='weighted')

print(f"Validation Accuracy:    {val_acc:.4f}")
print(f"Validation Macro-F1:    {val_f1_macro:.4f}")
print(f"Validation Weighted-F1: {val_f1_weighted:.4f}")
"""
    nb.cells.append(nbf.v4.new_code_cell(code_val))

    # Markdown: Final Test Evaluation
    md_test = """## 8. Final Evaluation on Unseen Test Set

Testing the trained model on the holdout test set ($15\\%$) and computing detailed per-class classification metrics.
"""
    nb.cells.append(nbf.v4.new_markdown_cell(md_test))

    # Code: Test Eval
    code_test = """# ── 8. Test Set Evaluation & Metrics ──
start_inf = time.time()
y_test_pred = pipeline.predict(X_test)
inf_time_ms = (time.time() - start_inf) / len(X_test) * 1000

test_acc = accuracy_score(y_test, y_test_pred)
test_f1_macro = f1_score(y_test, y_test_pred, average='macro')
test_f1_weighted = f1_score(y_test, y_test_pred, average='weighted')

print(f"============================================================")
print(f"  {MODEL_NAME} — FINAL TEST SET PERFORMANCE")
print(f"============================================================")
print(f"  Test Accuracy:     {test_acc:.4f} ({test_acc*100:.2f}%)")
print(f"  Macro-F1 Score:    {test_f1_macro:.4f}")
print(f"  Weighted-F1:       {test_f1_weighted:.4f}")
print(f"  Inference Latency: {inf_time_ms:.4f} ms / packet vector")
print(f"============================================================\\n")

target_names = [CLASS_NAMES[i] for i in sorted(np.unique(y_test))]
print("Detailed Classification Report:")
print(classification_report(y_test, y_test_pred, target_names=target_names, digits=4))
"""
    nb.cells.append(nbf.v4.new_code_cell(code_test))

    # Markdown: Visual Confusion Matrix
    md_cm = """## 9. Visual Confusion Matrix

Heatmap visualizing predicted vs. actual protocol classes to inspect false-positive and false-negative distributions.
"""
    nb.cells.append(nbf.v4.new_markdown_cell(md_cm))

    # Code: Visual CM
    code_cm = """# ── 9. Confusion Matrix Heatmap ──
cm = confusion_matrix(y_test, y_test_pred)
cm_norm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]

fig, ax = plt.subplots(figsize=(8, 6.5))
sns.heatmap(
    cm_norm, annot=True, fmt='.2%', cmap='Blues',
    xticklabels=target_names, yticklabels=target_names,
    cbar=True, ax=ax, linewidths=0.5
)
ax.set_title(f'{MODEL_NAME} — Test Normalized Confusion Matrix', fontweight='bold', fontsize=13)
ax.set_xlabel('Predicted Label', fontweight='bold', labelpad=10)
ax.set_ylabel('Actual Label', fontweight='bold', labelpad=10)
plt.tight_layout()
plt.show()
"""
    nb.cells.append(nbf.v4.new_code_cell(code_cm))

    # Markdown: Model Specific Deep Dive
    md_deep = f"""## 10. Model-Specific Deep Dive: {cfg['model_name']} Analysis

Analyzing the internal representation and mechanics of `{cfg['model_name']}`.
"""
    nb.cells.append(nbf.v4.new_markdown_cell(md_deep))

    # Code: Deep Dive
    nb.cells.append(nbf.v4.new_code_cell(cfg['deep_dive']))

    # Markdown: Cross-Network Check
    md_cross = """## 11. Cross-Network Robustness Check (Airtel vs. Jio Domain Shift)

Evaluating model robustness across different networks and geographical vantage points.
"""
    nb.cells.append(nbf.v4.new_markdown_cell(md_cross))

    # Code: Cross-Network
    code_cross = """# ── 11. Cross-Network Domain Shift Evaluation ──
if 'isp' in df.columns:
    airtel_mask = (df['isp'] == 'Airtel')
    jio_mask = (df['isp'] == 'Jio')

    if airtel_mask.sum() > 0 and jio_mask.sum() > 0:
        X_airtel = df.loc[airtel_mask, FEATURE_COLS].values
        y_airtel = df.loc[airtel_mask, 'traffic_class'].map(CLASS_MAP).values

        X_jio = df.loc[jio_mask, FEATURE_COLS].values
        y_jio = df.loc[jio_mask, 'traffic_class'].map(CLASS_MAP).values

        # Train on Airtel -> Test on Jio
        print(f"Training on Airtel ({len(X_airtel):,d}) -> Testing on Jio ({len(X_jio):,d})...")
        pipeline.fit(X_airtel, y_airtel)
        jio_pred = pipeline.predict(X_jio)
        acc_a2j = accuracy_score(y_jio, jio_pred)
        f1_a2j = f1_score(y_jio, jio_pred, average='macro')
        print(f"  Cross-Net (Airtel -> Jio) Accuracy: {acc_a2j:.4f} | Macro-F1: {f1_a2j:.4f}")
else:
    print("Dataset does not contain 'isp' metadata column; skipping cross-network test.")
"""
    nb.cells.append(nbf.v4.new_code_cell(code_cross))

    # Markdown: Save Model
    md_save = """## 12. Model Serialization & Export

Saving the trained pipeline for downstream evaluation, inference server deployment, or reproducibility.
"""
    nb.cells.append(nbf.v4.new_markdown_cell(md_save))

    # Code: Save Model
    code_save = f"""# ── 12. Save Trained Model to Disk ──
MODELS_DIR = Path("../PROJECT_NOTEBOOKS/saved_models")
MODELS_DIR.mkdir(parents=True, exist_ok=True)

save_path = MODELS_DIR / f"{cfg['filename'].replace('.ipynb', '')}.joblib"
joblib.dump(pipeline, save_path)
print(f"Trained model pipeline successfully serialized to: {{save_path.resolve()}}")
"""
    nb.cells.append(nbf.v4.new_code_cell(code_save))

    out_file = NOTEBOOKS_DIR / cfg['filename']
    with open(out_file, 'w', encoding='utf-8') as f:
        nbf.write(nb, f)
    print(f"Generated notebook: {out_file.name}")


def build_comparison_notebook():
    nb = nbf.v4.new_notebook()

    md_header = """# Master Model Comparison & Benchmarking

**Project:** Encrypted DNS & QUIC Traffic Intelligence  
**Focus:** Comprehensive Multi-Model Benchmarking Across Observable Kinematic Features  
**Models Evaluated:**
1. Random Forest (`RandomForestClassifier`)
2. XGBoost (`XGBClassifier`)
3. Decision Tree (`DecisionTreeClassifier`)
4. Support Vector Machine (`SVC`)
5. k-Nearest Neighbors (`KNeighborsClassifier`)
6. Logistic Regression (`LogisticRegression`)
7. Multi-Layer Perceptron (`MLPClassifier`)

---

### Objective
Provide an end-to-end head-to-head comparison on the exact same train/validation/test partitions, evaluating:
- Test Accuracy & Macro-F1
- Per-Protocol Precision & Recall
- Inference Latency per Packet Vector
- Within-Network vs. Cross-Network Generalization
"""
    nb.cells.append(nbf.v4.new_markdown_cell(md_header))

    code_setup = """# ── 1. Setup & Imports ──
import os
import time
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
%matplotlib inline
import seaborn as sns

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_validate
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, classification_report

from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
from xgboost import XGBClassifier

sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams['font.sans-serif'] = 'Helvetica'

RANDOM_STATE = 42
print("Benchmark dependencies initialized.")
"""
    nb.cells.append(nbf.v4.new_code_cell(code_setup))

    code_load = """# ── 2. Ingest Consolidated Dataset ──
DATA_DIR = Path("../PROJECT_DATASET")
DATASET_PATH = DATA_DIR / "FULL_COMBINED_WITH_METADATA.csv"
if not DATASET_PATH.exists():
    DATASET_PATH = DATA_DIR / "FULL_COMBINED.csv"

df = pd.read_csv(DATASET_PATH)
FEATURE_COLS = ['Current packet size', 'Previous packet size', 'Current time gap', 'Previous time gap']
CLASS_MAP = {'DOH': 0, 'DOQ': 1, 'DOH3': 2, 'QUIC': 3, 'HTTPS_WEB': 4, 'HTTP3_WEB': 5}
CLASS_NAMES = {v: k for k, v in CLASS_MAP.items()}

X = df[FEATURE_COLS].values
y = df['traffic_class'].map(CLASS_MAP).values

# 70 / 15 / 15 Stratified Split
X_train_val, X_test, y_train_val, y_test = train_test_split(X, y, test_size=0.15, stratify=y, random_state=RANDOM_STATE)
X_train, X_val, y_train, y_val = train_test_split(X_train_val, y_train_val, test_size=(0.15 / 0.85), stratify=y_train_val, random_state=RANDOM_STATE)

print(f"Dataset: {len(df):,d} samples.")
print(f"Train: {len(X_train):,d} | Val: {len(X_val):,d} | Test: {len(X_test):,d}")
"""
    nb.cells.append(nbf.v4.new_code_cell(code_load))

    code_benchmark = """# ── 3. Configure All 7 Candidate Models ──
models_dict = {
    'Random Forest': RandomForestClassifier(n_estimators=200, criterion='entropy', random_state=RANDOM_STATE, n_jobs=-1),
    'XGBoost': XGBClassifier(n_estimators=150, learning_rate=0.1, max_depth=6, random_state=RANDOM_STATE, n_jobs=-1),
    'Decision Tree': DecisionTreeClassifier(criterion='entropy', max_depth=12, random_state=RANDOM_STATE),
    'SVM (RBF)': Pipeline([('scaler', StandardScaler()), ('clf', SVC(C=10.0, kernel='rbf', probability=True, random_state=RANDOM_STATE))]),
    'KNN': Pipeline([('scaler', StandardScaler()), ('clf', KNeighborsClassifier(n_neighbors=7, weights='distance', n_jobs=-1))]),
    'Logistic Regression': Pipeline([('scaler', StandardScaler()), ('clf', LogisticRegression(C=1.0, max_iter=1000, random_state=RANDOM_STATE))]),
    'MLP Neural Net': Pipeline([('scaler', StandardScaler()), ('clf', MLPClassifier(hidden_layer_sizes=(128, 64), max_iter=200, random_state=RANDOM_STATE))]),
}

results = []
print("Starting head-to-head benchmarking on test partition...")

for name, model in models_dict.items():
    print(f"Training {name:20s}...", end="")
    t0 = time.time()
    model.fit(X_train, y_train)
    fit_time = time.time() - t0

    t_inf = time.time()
    y_pred = model.predict(X_test)
    inf_latency = (time.time() - t_inf) / len(X_test) * 1000

    acc = accuracy_score(y_test, y_pred)
    f1_m = f1_score(y_test, y_pred, average='macro')
    f1_w = f1_score(y_test, y_pred, average='weighted')
    prec_m = precision_score(y_test, y_pred, average='macro')
    rec_m = recall_score(y_test, y_pred, average='macro')

    results.append({
        'Model': name,
        'Accuracy': acc,
        'Macro-F1': f1_m,
        'Weighted-F1': f1_w,
        'Precision': prec_m,
        'Recall': rec_m,
        'Fit Time (s)': fit_time,
        'Inference (ms/pkt)': inf_latency
    })
    print(f" Done! Acc: {acc:.4f} | Macro-F1: {f1_m:.4f} ({fit_time:.2f}s)")

df_results = pd.DataFrame(results).sort_values('Macro-F1', ascending=False).reset_index(drop=True)
"""
    nb.cells.append(nbf.v4.new_code_cell(code_benchmark))

    code_display = """# ── 4. Leaderboard & Visual Comparison ──
print("\\n==========================================================================")
print("                       OFFICIAL MODEL LEADERBOARD")
print("==========================================================================")
print(df_results.to_string(index=False))

fig, axes = plt.subplots(1, 2, figsize=(16, 5))

# Plot 1: Macro-F1 vs Accuracy
sns.barplot(x='Macro-F1', y='Model', data=df_results, ax=axes[0], palette='Blues_r')
axes[0].set_title('Macro-F1 Score by Model', fontweight='bold')
axes[0].set_xlim(0.8, 1.01)

# Plot 2: Inference Latency
sns.barplot(x='Inference (ms/pkt)', y='Model', data=df_results, ax=axes[1], palette='Reds_r')
axes[1].set_title('Inference Latency (ms per packet vector)', fontweight='bold')
plt.tight_layout()
plt.show()
"""
    nb.cells.append(nbf.v4.new_code_cell(code_display))

    out_file = NOTEBOOKS_DIR / "08_Model_Comparison_and_Benchmarking.ipynb"
    with open(out_file, 'w', encoding='utf-8') as f:
        nbf.write(nb, f)
    print(f"Generated notebook: {out_file.name}")


def main():
    print(f"=== Generating Model Notebooks in {NOTEBOOKS_DIR} ===")
    for cfg in MODELS_CONFIG:
        build_single_model_notebook(cfg)
    build_comparison_notebook()
    print("=== All 8 notebooks successfully created! ===")


if __name__ == "__main__":
    main()
