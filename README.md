# Encrypted DNS Traffic Intelligence

This project extends the existing research dataset to build a complete, reproducible machine-learning experimentation framework for encrypted DNS traffic classification.

## Directory Structure

- `dataset/`: Original and generated compact datasets.
- `Docker_dataset/`: Capturing scripts.
- `ml/`: Core ML pipeline (loaders, preprocessors, models, evaluators).
- `experiments/`: Experiment scripts (binary, multiclass, cv, open-world, ratio-analysis).
- `notebooks/`: Jupyter notebook for the experiments.
- `results/`: Contains output tables, trained models, figures, and markdown reports.

## Reproducing Experiments

To execute the entire pipeline (including all six models, cross validation, train/test ratio analysis, open-world experiment, and multiclass experiment), simply run:

```bash
bash run_all.sh
```

### Or run individually:

1. **DoH vs Web (Primary)**: `python3 experiments/train_doh_vs_web.py`
2. **Train/Test Ratio Analysis**: `python3 experiments/run_train_test_ratio.py`
3. **Cross Validation**: `python3 experiments/run_cross_validation.py`
4. **Multiclass Analysis**: `python3 experiments/train_multiclass.py`
5. **Open World Analysis**: `python3 experiments/run_open_world.py`
6. **Generate Report**: `python3 experiments/generate_report.py`

## Features

- **pkt_len (Current packet size)**
- **prev_pkt_len (Previous packet size)**
- **time_lag (Current time gap)**
- **prev_time_lag (Previous time gap)**

Models used: SVM, Decision Tree, Random Forest, AdaBoost, Gaussian Naive Bayes, Logistic Regression.
