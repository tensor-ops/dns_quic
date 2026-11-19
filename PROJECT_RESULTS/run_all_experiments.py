"""
Master ML Experiment Runner
Runs all 7 models across 6 scenarios, saves full results to PROJECT_RESULTS/
"""
import os, sys, time, warnings, json
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns

from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import LinearSVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.metrics import (accuracy_score, precision_score, recall_score, f1_score,
                             classification_report, confusion_matrix,
                             roc_auc_score, roc_curve, auc)
from sklearn.preprocessing import LabelEncoder, label_binarize

try:
    from xgboost import XGBClassifier
    HAS_XGB = True
except ImportError:
    HAS_XGB = False
    print("WARNING: XGBoost not found, skipping")

# ─────────────────────────── PATHS ───────────────────────────
BASE        = '/Users/paru/paru/projects/RM'
PD          = f'{BASE}/PROJECT_DATASET'
RESULTS_DIR = f'{BASE}/PROJECT_RESULTS'

CLASSES = ['DOH', 'DOQ', 'DOH3', 'QUIC', 'HTTPS_WEB', 'HTTP3_WEB']
CLASS_MAP = {c: i for i, c in enumerate(CLASSES)}
CORE_COLS = ['Current packet size', 'Previous packet size',
             'Current time gap',    'Previous time gap', 'traffic_class']

RATIO_COUNTS = {          # 8:4:4:2:2:1  → total 42k
    'HTTPS_WEB' : 16000,
    'HTTP3_WEB' :  8000,
    'DOH'       :  8000,
    'DOH3'      :  4000,
    'DOQ'       :  4000,
    'QUIC'      :  2000,
}

# ─────────────────────── DATASET LOADER ──────────────────────
def load(path):
    df = pd.read_csv(path, usecols=CORE_COLS)
    df = df[df['traffic_class'].isin(CLASSES)].dropna()
    df['label'] = df['traffic_class'].map(CLASS_MAP)
    return df

def xy(df):
    feat = ['Current packet size','Previous packet size','Current time gap','Previous time gap']
    return df[feat].values, df['label'].values

# ──────────────────────── MODELS REGISTRY ────────────────────
def get_models():
    models = {
        'Random_Forest'       : RandomForestClassifier(n_estimators=200, n_jobs=-1, random_state=42),
        'Decision_Tree'       : DecisionTreeClassifier(max_depth=20, random_state=42),
        'Linear_SVM'          : CalibratedClassifierCV(LinearSVC(max_iter=3000, random_state=42)),
        'KNN'                 : KNeighborsClassifier(n_neighbors=5, n_jobs=-1, metric='euclidean'),
        'Logistic_Regression' : LogisticRegression(max_iter=1000, n_jobs=-1, random_state=42, solver='lbfgs'),
        'MLP'                 : MLPClassifier(hidden_layer_sizes=(256,128,64), max_iter=300,
                                               early_stopping=True, validation_fraction=0.1,
                                               random_state=42),
    }
    if HAS_XGB:
        models['XGBoost'] = XGBClassifier(n_estimators=200, n_jobs=-1, random_state=42,
                                           use_label_encoder=False, eval_metric='mlogloss',
                                           tree_method='hist')
    return models

# ──────────────────── PLOTTING HELPERS ───────────────────────
def plot_confusion_matrix(cm, classes, out_path, title='Confusion Matrix'):
    fig, ax = plt.subplots(figsize=(8,6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=classes, yticklabels=classes, ax=ax)
    ax.set_xlabel('Predicted', fontsize=12)
    ax.set_ylabel('True', fontsize=12)
    ax.set_title(title, fontsize=14)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()

def plot_roc_curves(y_true, y_prob, classes, out_path, title='ROC Curves'):
    y_bin = label_binarize(y_true, classes=list(range(len(classes))))
    fig, ax = plt.subplots(figsize=(8,6))
    colors = plt.cm.tab10(np.linspace(0, 1, len(classes)))
    for i, (cls, col) in enumerate(zip(classes, colors)):
        fpr, tpr, _ = roc_curve(y_bin[:, i], y_prob[:, i])
        roc_auc = auc(fpr, tpr)
        ax.plot(fpr, tpr, color=col, lw=1.5, label=f'{cls} (AUC={roc_auc:.3f})')
    ax.plot([0,1],[0,1],'k--',lw=0.8)
    ax.set_xlabel('False Positive Rate')
    ax.set_ylabel('True Positive Rate')
    ax.set_title(title)
    ax.legend(loc='lower right', fontsize=8)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()

def plot_class_bar(report_dict, classes, out_path, title='Per-Class F1'):
    f1s = [report_dict.get(c, {}).get('f1-score', 0) for c in classes]
    fig, ax = plt.subplots(figsize=(8,4))
    bars = ax.bar(classes, f1s, color='steelblue', edgecolor='white')
    ax.bar_label(bars, fmt='%.3f', fontsize=9)
    ax.set_ylim(0, 1.1)
    ax.set_ylabel('F1 Score')
    ax.set_title(title)
    ax.tick_params(axis='x', rotation=15)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()

# ─────────────────────── CORE EVALUATOR ──────────────────────
def evaluate_model(model, model_name, scenario_name,
                   X_train, y_train, X_val, y_val, X_test, y_test,
                   do_cv=True, cv_X=None, cv_y=None):
    out_dir = f'{RESULTS_DIR}/{scenario_name}/{model_name}'
    os.makedirs(out_dir, exist_ok=True)

    # ── Train
    t0 = time.time()
    model.fit(X_train, y_train)
    train_time = time.time() - t0

    # ── Predict
    y_pred_val  = model.predict(X_val)
    y_pred_test = model.predict(X_test)

    # ── Probabilities (for ROC)
    has_proba = hasattr(model, 'predict_proba')
    y_prob_test = model.predict_proba(X_test) if has_proba else None

    # ── Metrics
    def metrics(yt, yp, split):
        return {
            'split'      : split,
            'accuracy'   : accuracy_score(yt, yp),
            'precision_macro': precision_score(yt, yp, average='macro', zero_division=0),
            'recall_macro'   : recall_score(yt, yp, average='macro', zero_division=0),
            'f1_macro'       : f1_score(yt, yp, average='macro', zero_division=0),
            'f1_weighted'    : f1_score(yt, yp, average='weighted', zero_division=0),
        }

    val_metrics  = metrics(y_val, y_pred_val, 'validation')
    test_metrics = metrics(y_test, y_pred_test, 'test')
    train_metrics = metrics(y_train, model.predict(X_train), 'train')
    train_metrics['train_time_s'] = round(train_time, 2)

    # CV — subsample to max 15k to keep it fast
    cv_mean, cv_std = None, None
    if do_cv and cv_X is not None:
        MAX_CV = 15000
        if len(cv_X) > MAX_CV:
            idx = np.random.RandomState(42).choice(len(cv_X), MAX_CV, replace=False)
            cv_X_s, cv_y_s = cv_X[idx], cv_y[idx]
        else:
            cv_X_s, cv_y_s = cv_X, cv_y
        cv_scores = cross_val_score(model, cv_X_s, cv_y_s, cv=5, scoring='accuracy', n_jobs=-1)
        cv_mean, cv_std = cv_scores.mean(), cv_scores.std()

    # ── Save metrics CSV
    rows = [train_metrics, val_metrics, test_metrics]
    if cv_mean is not None:
        rows.append({'split':'cv_5fold', 'accuracy': cv_mean, 'cv_std': cv_std})
    pd.DataFrame(rows).to_csv(f'{out_dir}/metrics.csv', index=False)

    # ── Classification report
    report = classification_report(y_test, y_pred_test,
                                   target_names=CLASSES, output_dict=False, zero_division=0)
    report_dict = classification_report(y_test, y_pred_test,
                                        target_names=CLASSES, output_dict=True, zero_division=0)
    with open(f'{out_dir}/classification_report.txt', 'w') as f:
        f.write(f"Model: {model_name}  |  Scenario: {scenario_name}\n")
        f.write(f"Train time: {train_time:.2f}s\n")
        if cv_mean: f.write(f"5-Fold CV Accuracy: {cv_mean:.4f} ± {cv_std:.4f}\n")
        f.write("\n--- TEST SET ---\n")
        f.write(report)

    # ── Confusion matrix
    cm = confusion_matrix(y_test, y_pred_test)
    pd.DataFrame(cm, index=CLASSES, columns=CLASSES).to_csv(f'{out_dir}/confusion_matrix.csv')
    plot_confusion_matrix(cm, CLASSES, f'{out_dir}/confusion_matrix.png',
                          title=f'{model_name} — {scenario_name}')

    # ── ROC
    if y_prob_test is not None:
        try:
            plot_roc_curves(y_test, y_prob_test, CLASSES,
                            f'{out_dir}/roc_curves.png',
                            title=f'{model_name} — {scenario_name} ROC')
        except Exception as e:
            print(f"  ROC plot skipped: {e}")

    # ── Per-class F1 bar
    plot_class_bar(report_dict, CLASSES, f'{out_dir}/per_class_f1.png',
                   title=f'{model_name} — {scenario_name} Per-Class F1')

    result = {
        'model'     : model_name,
        'scenario'  : scenario_name,
        'train_acc' : train_metrics['accuracy'],
        'val_acc'   : val_metrics['accuracy'],
        'test_acc'  : test_metrics['accuracy'],
        'f1_macro'  : test_metrics['f1_macro'],
        'f1_weighted': test_metrics['f1_weighted'],
        'precision_macro': test_metrics['precision_macro'],
        'recall_macro'  : test_metrics['recall_macro'],
        'train_time_s'  : round(train_time, 2),
        'cv_accuracy'   : cv_mean,
        'cv_std'        : cv_std,
    }
    print(f"    ✓ {model_name:25s}  test_acc={result['test_acc']:.4f}  f1={result['f1_macro']:.4f}  ({train_time:.1f}s)")
    return result

# ──────────────────── SCENARIO RUNNER ────────────────────────
def run_scenario(scenario_name, df, cross=False,
                 df_train_ext=None, df_test_ext=None):
    """
    cross=False → split internally (70/15/15)
    cross=True  → df_train_ext=train DF, df_test_ext=test DF (no val split needed; use 10% of train as val)
    """
    print(f"\n{'='*60}")
    print(f"SCENARIO: {scenario_name}")

    if not cross:
        X, y = xy(df)
        X_tr, X_tmp, y_tr, y_tmp = train_test_split(X, y, test_size=0.30, random_state=42, stratify=y)
        X_val, X_te, y_val, y_te = train_test_split(X_tmp, y_tmp, test_size=0.50, random_state=42, stratify=y_tmp)
        cv_X, cv_y = X, y
        print(f"  Train: {len(y_tr):,}  Val: {len(y_val):,}  Test: {len(y_te):,}")
    else:
        X_tr_full, y_tr_full = xy(df_train_ext)
        X_te, y_te           = xy(df_test_ext)
        # 10% of train as validation
        X_tr, X_val, y_tr, y_val = train_test_split(X_tr_full, y_tr_full,
                                                      test_size=0.10, random_state=42, stratify=y_tr_full)
        cv_X, cv_y = None, None
        print(f"  Train: {len(y_tr):,}  Val: {len(y_val):,}  Test: {len(y_te):,} (cross-network)")

    results = []
    for mname, model in get_models().items():
        print(f"  → {mname}")
        try:
            r = evaluate_model(model, mname, scenario_name,
                               X_tr, y_tr, X_val, y_val, X_te, y_te,
                               do_cv=(not cross), cv_X=cv_X, cv_y=cv_y)
            results.append(r)
        except Exception as e:
            print(f"    ✗ {mname} FAILED: {e}")
    return results

# ──────────────────────── MAIN ───────────────────────────────
if __name__ == '__main__':
    print("Loading datasets...")
    df_full   = load(f'{PD}/FULL_COMBINED.csv')
    df_jio    = load(f'{PD}/JIO_COMBINED.csv')
    df_airtel = load(f'{PD}/AIRTEL_COMBINED.csv')

    # Ratio dataset
    frames = []
    for cls, n in RATIO_COUNTS.items():
        sub = df_full[df_full['traffic_class'] == cls]
        if len(sub) >= n:
            frames.append(sub.sample(n, random_state=42))
        else:
            frames.append(sub)
            print(f"  WARNING: {cls} only has {len(sub)} rows, wanted {n}")
    df_ratio = pd.concat(frames, ignore_index=True).sample(frac=1, random_state=42)
    df_ratio.to_csv(f'{PD}/RATIO_DATASET.csv', index=False)
    print(f"Ratio dataset: {len(df_ratio):,} rows | {df_ratio['traffic_class'].value_counts().to_dict()}")

    print(f"\nFull: {len(df_full):,}  JIO: {len(df_jio):,}  Airtel: {len(df_airtel):,}  Ratio: {len(df_ratio):,}")

    # ── Dataset Info
    print("\nBuilding dataset info...")
    info_rows = []
    for name, df in [('FULL_COMBINED', df_full), ('JIO_COMBINED', df_jio),
                      ('AIRTEL_COMBINED', df_airtel), ('PRAYAGRAJ_JIO', load(f'{PD}/PRAYAGRAJ_JIO_COMBINED.csv')),
                      ('TUMSAR_AIRTEL', load(f'{PD}/TUMSAR_AIRTEL_COMBINED.csv')),
                      ('MIRZAPUR_JIO', load(f'{PD}/MIRZAPUR_JIO_COMBINED.csv')),
                      ('PRAYAGRAJ_AIRTEL', load(f'{PD}/PRAYAGRAJ_AIRTEL_COMBINED.csv')),
                      ('RATIO_DATASET', df_ratio)]:
        row = {'dataset': name, 'total_rows': len(df)}
        for cls in CLASSES:
            row[cls] = int((df['traffic_class'] == cls).sum())
        row['null_count'] = int(df.isnull().sum().sum())
        info_rows.append(row)
    df_info = pd.DataFrame(info_rows)
    df_info.to_csv(f'{RESULTS_DIR}/DATASET_INFO/dataset_summary.csv', index=False)

    # Pretty print
    print("\n" + df_info.to_string(index=False))

    # ── Plot dataset distribution
    fig, ax = plt.subplots(figsize=(12, 5))
    datasets = df_info[df_info['dataset'].isin(['FULL_COMBINED','JIO_COMBINED','AIRTEL_COMBINED','RATIO_DATASET'])]
    x = np.arange(len(CLASSES))
    w = 0.2
    colors = plt.cm.Set2(np.linspace(0,1,4))
    for i, (_, row) in enumerate(datasets.iterrows()):
        vals = [row[c] for c in CLASSES]
        ax.bar(x + i*w, vals, w, label=row['dataset'], color=colors[i])
    ax.set_xticks(x + 1.5*w); ax.set_xticklabels(CLASSES, rotation=15)
    ax.set_ylabel('Sample Count'); ax.set_title('Class Distribution Across Datasets')
    ax.legend(); plt.tight_layout()
    plt.savefig(f'{RESULTS_DIR}/DATASET_INFO/class_distribution.png', dpi=150)
    plt.close()

    # Vantage point distribution
    df_full_meta = pd.read_csv(f'{PD}/FULL_COMBINED_WITH_METADATA.csv')
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    df_full_meta.groupby(['vantage_point','traffic_class']).size().unstack(fill_value=0).plot(kind='bar', ax=axes[0])
    axes[0].set_title('Samples per Vantage Point × Class'); axes[0].tick_params(axis='x', rotation=25)
    df_full_meta['traffic_class'].value_counts().plot(kind='pie', ax=axes[1], autopct='%1.1f%%')
    axes[1].set_title('Overall Class Distribution (Pie)')
    plt.tight_layout()
    plt.savefig(f'{RESULTS_DIR}/DATASET_INFO/vantage_point_distribution.png', dpi=150)
    plt.close()
    print("Dataset info saved.")

    # ──────────── RUN ALL SCENARIOS ────────────
    all_results = []

    all_results += run_scenario('FULL_DATASET',   df_full)
    all_results += run_scenario('JIO_ONLY',        df_jio)
    all_results += run_scenario('AIRTEL_ONLY',     df_airtel)
    all_results += run_scenario('RATIO_DATASET',   df_ratio)
    all_results += run_scenario('CROSS_JIO_TRAIN_AIRTEL_TEST',    None, cross=True,
                                df_train_ext=df_jio,    df_test_ext=df_airtel)
    all_results += run_scenario('CROSS_AIRTEL_TRAIN_JIO_TEST',    None, cross=True,
                                df_train_ext=df_airtel, df_test_ext=df_jio)

    # ──────────── MASTER RESULTS TABLE ────────────
    df_results = pd.DataFrame(all_results)
    df_results = df_results.sort_values(['scenario','test_acc'], ascending=[True,False])
    df_results.to_csv(f'{RESULTS_DIR}/ALL_RESULTS_MASTER.csv', index=False)

    # ──────────── COMPARISON PLOTS ────────────
    scenarios_list = df_results['scenario'].unique()
    models_list    = df_results['model'].unique()

    # Heatmap: test accuracy per model per scenario
    pivot = df_results.pivot(index='model', columns='scenario', values='test_acc')
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.heatmap(pivot, annot=True, fmt='.4f', cmap='YlOrRd', vmin=0.5, vmax=1.0, ax=ax,
                linewidths=0.5)
    ax.set_title('Test Accuracy — Model × Scenario', fontsize=14)
    plt.tight_layout()
    plt.savefig(f'{RESULTS_DIR}/comparison_accuracy_heatmap.png', dpi=150)
    plt.close()

    # Heatmap: F1 macro
    pivot_f1 = df_results.pivot(index='model', columns='scenario', values='f1_macro')
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.heatmap(pivot_f1, annot=True, fmt='.4f', cmap='Blues', vmin=0.5, vmax=1.0, ax=ax,
                linewidths=0.5)
    ax.set_title('Macro F1 — Model × Scenario', fontsize=14)
    plt.tight_layout()
    plt.savefig(f'{RESULTS_DIR}/comparison_f1_heatmap.png', dpi=150)
    plt.close()

    # Bar chart per scenario
    for scenario in scenarios_list:
        sub = df_results[df_results['scenario'] == scenario].sort_values('test_acc', ascending=False)
        fig, ax = plt.subplots(figsize=(10, 5))
        x = np.arange(len(sub))
        b1 = ax.bar(x - 0.2, sub['train_acc'], 0.35, label='Train Acc', color='steelblue')
        b2 = ax.bar(x + 0.2, sub['test_acc'],  0.35, label='Test Acc',  color='coral')
        ax.bar_label(b1, fmt='%.3f', fontsize=7)
        ax.bar_label(b2, fmt='%.3f', fontsize=7)
        ax.set_xticks(x); ax.set_xticklabels(sub['model'], rotation=20, ha='right')
        ax.set_ylim(0, 1.15); ax.set_ylabel('Accuracy')
        ax.set_title(f'Train vs Test Accuracy — {scenario}')
        ax.legend(); plt.tight_layout()
        plt.savefig(f'{RESULTS_DIR}/{scenario}/train_vs_test_accuracy.png', dpi=150)
        plt.close()

    # Training time comparison
    fig, ax = plt.subplots(figsize=(12, 5))
    pivot_time = df_results.pivot(index='model', columns='scenario', values='train_time_s')
    pivot_time.plot(kind='bar', ax=ax, colormap='tab10')
    ax.set_ylabel('Training Time (s)'); ax.set_title('Training Time — All Models × Scenarios')
    ax.tick_params(axis='x', rotation=25); ax.legend(loc='upper right', fontsize=8)
    plt.tight_layout()
    plt.savefig(f'{RESULTS_DIR}/comparison_training_time.png', dpi=150)
    plt.close()

    # ──────────── PRINT FINAL SUMMARY ────────────
    print("\n" + "="*80)
    print("FINAL RESULTS SUMMARY")
    print("="*80)
    print(df_results[['scenario','model','train_acc','test_acc','f1_macro','train_time_s']].to_string(index=False))
    print(f"\n✅ All results saved to: {RESULTS_DIR}")
    print(f"   Master table: {RESULTS_DIR}/ALL_RESULTS_MASTER.csv")
