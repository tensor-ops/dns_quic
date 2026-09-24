# Models — QUIC Traffic Classification

## 1. Purpose

The **Models** section is responsible for running multiple machine-learning models on the extracted traffic features and comparing their results.

The main objective is not to rely on a single classifier.

Instead, we will evaluate the models used in the **base paper** and compare their performance on our dataset.

```text
Dataset
   ↓
Preprocessing
   ↓
Feature Extraction
   ↓
Train / Test Split
   ↓
Multiple ML Models
   ↓
Predictions
   ↓
Evaluation
   ↓
Model Comparison
```

---

# 2. Research Objective

Our project investigates whether encrypted DNS traffic, particularly **DoQ**, can be distinguished from encrypted web traffic such as **HTTP/3/QUIC** using observable traffic metadata.

Therefore, the model section should help answer:

> **How accurately can different machine-learning models identify DoQ traffic from encrypted QUIC/HTTP traffic?**

We will compare models using the same dataset, feature set, train/test strategy, and evaluation procedure wherever possible.

---

# 3. Base Paper Models

The first set of models should be taken from the **base paper**.

### Required process

Before implementation, verify from the base paper:

- Exact model names
- Model configuration
- Hyperparameters
- Feature set
- Train/test split
- Cross-validation strategy
- Evaluation metrics
- Preprocessing steps

The frontend/backend documentation should record the exact configuration used for reproduction.

### Model Table

| Model | From Base Paper | Configuration | Status |
|---|---|---|---|
| Model 1 | Yes | To be confirmed | Planned |
| Model 2 | Yes | To be confirmed | Planned |
| Model 3 | Yes | To be confirmed | Planned |
| Model 4 | Yes | To be confirmed | Planned |

**Important:** Do not invent model names or parameters. The final list must be taken directly from the base paper.

---

# 4. Additional Models

After reproducing the base-paper experiments, we can add additional models for comparison.

Possible candidates include:

- Random Forest
- XGBoost
- Support Vector Machine (SVM)
- Logistic Regression
- k-Nearest Neighbors (k-NN)
- Decision Tree
- Gradient Boosting
- Neural Network / MLP

These should be treated as **additional comparison models**, not replacements for the base-paper models.

The final additional-model list will depend on:

- Dataset size
- Feature count
- Computational requirements
- Base-paper methodology
- Research objective

---

# 5. Model Selection Interface

The frontend should provide a simple model-selection screen.

Example:

```text
Models

Select Dataset
[ DoQ + HTTP/3 Dataset ▼ ]

Select Features
[ All Features ▼ ]

Select Model
[ Random Forest ▼ ]

                 [ Run Model ]
```

For multiple-model experiments:

```text
Select Models

☑ Base Model 1
☑ Base Model 2
☑ Base Model 3
☑ Random Forest
☑ SVM

                 [ Run Comparison ]
```

Keep the interface simple.

---

# 6. Training

When the user starts an experiment:

```text
Dataset
   ↓
Data Validation
   ↓
Preprocessing
   ↓
Feature Selection
   ↓
Train/Test Split
   ↓
Model Training
```

The frontend should show a simple progress indicator:

```text
Training Models

✓ Dataset loaded
✓ Features prepared
● Training Random Forest
○ Training SVM
○ Training Model 3
○ Generating results
```

---

# 7. Prediction

Each model should produce predictions for the test data.

For the current research problem, the classes may include:

```text
DoQ
HTTP/3
Other QUIC
```

For binary experiments:

```text
DoQ
HTTP/3
```

The exact class configuration should be displayed for each experiment.

---

# 8. Evaluation Metrics

Every model should be evaluated using consistent metrics.

### Primary metrics

- Accuracy
- Precision
- Recall
- F1-score

### Additional metrics

Where applicable:

- ROC-AUC
- False Positive Rate
- False Negative Rate
- Confusion Matrix
- Training Time
- Prediction Time

---

# 9. Model Comparison

This is one of the most important parts of the Models section.

After all selected models finish, display a comparison table.

Example:

| Model | Accuracy | Precision | Recall | F1 |
|---|---:|---:|---:|---:|
| Base Model 1 | — | — | — | — |
| Base Model 2 | — | — | — | — |
| Random Forest | — | — | — | — |
| SVM | — | — | — | — |

The values above are placeholders only.

**Never hard-code experimental results.**

---

# 10. Visualization of Model Results

Provide simple graphs for comparing models.

## Accuracy Comparison

```text
Model Accuracy

Model 1       ███████████████
Model 2       █████████████
Random Forest ████████████████
SVM           ████████████
```

## F1-score Comparison

Use a similar bar chart.

## Confusion Matrix

Show a separate confusion matrix for the selected model.

Example:

```text
                Predicted

              DoQ   HTTP/3

Actual DoQ    950      32
Actual HTTP3   21     970
```

---

# 11. Model Details

Clicking a model should show its configuration.

Example:

```text
Random Forest

Dataset:
DoQ + HTTP/3

Features:
18

Training Samples:
38,568

Testing Samples:
9,642

Parameters:
n_estimators: 100
max_depth: ...
```

The exact parameters must come from the actual experiment configuration.

---

# 12. Base Paper Reproduction

A dedicated experiment should reproduce the methodology of the base paper as closely as possible.

The reproduction record should contain:

```text
Base Paper Reproduction

Dataset:
[Dataset name]

Features:
[Feature set]

Models:
[Models from paper]

Train/Test:
[Split used in paper]

Preprocessing:
[Method used]

Evaluation:
[Metrics used]

                [ Run Reproduction ]
```

Then compare:

```text
Base Paper Result     Our Result
──────────────────────────────────
Accuracy              Accuracy
Precision             Precision
Recall                Recall
F1                    F1
```

This allows us to clearly distinguish:

1. **Results reported by the base paper**
2. **Our reproduced results**
3. **Our new experiments**

---

# 13. Our Extended Experiments

After reproducing the base paper, we can extend the experiments to our research question.

### Experiment A — Base-paper reproduction

```text
Base Paper Dataset
        ↓
Base Paper Features
        ↓
Base Paper Models
        ↓
Reproduced Results
```

### Experiment B — DoQ vs HTTP/3

```text
DoQ + HTTP/3
      ↓
Traffic Features
      ↓
Multiple Models
      ↓
Classification Results
```

### Experiment C — DoQ vs Other QUIC

```text
DoQ + Other QUIC
      ↓
Traffic Features
      ↓
Multiple Models
      ↓
Classification Results
```

### Experiment D — Multi-class Classification

```text
DoQ
HTTP/3
Other QUIC
   ↓
Multiple Models
   ↓
Multi-class Results
```

### Experiment E — Generalization

If suitable datasets are available:

```text
Training Dataset
      ↓
      Model
      ↓
Different/Test Dataset
      ↓
Generalization Performance
```

This experiment can be particularly useful for evaluating whether the classifier is learning general traffic characteristics rather than dataset-specific patterns.

---

# 14. Feature Importance

For models that support feature importance, display the most influential traffic features.

Example:

```text
Feature Importance

Flow Duration       █████████████
Packet Count        ███████████
Mean Packet Length  █████████
Mean IAT            ███████
Byte Ratio          █████
```

Possible features include:

- Flow duration
- Packet count
- Total bytes
- Mean packet length
- Packet-length variance
- Inter-arrival time
- Forward packet count
- Backward packet count
- Forward/backward byte ratio

Only display features that actually exist in the processed dataset.

---

# 15. Avoiding Data Leakage

This is an important research requirement.

The pipeline must ensure that:

```text
Training Data
     ↓
Fit preprocessing
     ↓
Train model

Test Data
     ↓
Use already-fitted preprocessing
     ↓
Evaluate model
```

The test set must not influence training or feature preprocessing.

If cross-validation is used, preprocessing should be performed correctly within the validation procedure.

---

# 16. Reproducibility

Every experiment should store:

- Dataset name/version
- Number of records
- Feature set
- Selected model
- Model parameters
- Train/test split
- Random seed
- Preprocessing method
- Evaluation metrics
- Timestamp
- Result

Example:

```text
Experiment ID: EXP-001

Dataset: doq_quic_dataset
Features: All
Model: Random Forest
Split: 80/20
Random Seed: 42

Accuracy: ...
Precision: ...
Recall: ...
F1: ...
```

This makes our experiments reproducible and easier to explain in the final report.

---

# 17. Recommended Frontend Structure

```text
Models
│
├── Model Selection
│
├── Base Paper Models
│
├── Additional Models
│
├── Run Experiment
│
├── Model Results
│
├── Model Comparison
│
├── Confusion Matrix
│
└── Feature Importance
```

---

# 18. Current Implementation Scope

For the first implementation, build only:

```text
Models
│
├── Select Dataset
├── Select Model
├── Run Model
├── Show Accuracy
├── Show Precision
├── Show Recall
├── Show F1
└── Compare Models
```

Later add:

- Base-paper reproduction
- Hyperparameter controls
- Confusion matrices
- Feature importance
- ROC curves
- Experiment history
- Generalization experiments

---

# 19. Important Rule

The model section must clearly separate:

### Base Paper

Models and methodology reproduced from the original research.

### Our Work

New models, experiments, datasets, comparisons, and analysis added for our project.

This distinction is important for the research report because it makes clear what is **reproduction** and what is **our contribution**.

---

# 20. Final Research Pipeline

The complete planned workflow is:

```text
                    DATASET
                       │
                       ▼
               DATA PREPROCESSING
                       │
                       ▼
              FEATURE EXTRACTION
                       │
                       ▼
                TRAIN / TEST
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
      Base Model 1  Base Model 2  Base Model N
          │            │            │
          └────────────┼────────────┘
                       ▼
                ADDITIONAL MODELS
                       │
                       ▼
                MODEL PREDICTION
                       │
                       ▼
                 EVALUATION
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
       Accuracy     Precision      F1
                       │
                       ▼
                MODEL COMPARISON
                       │
                       ▼
             DoQ vs HTTP/3 Analysis
```

---

## Development Principle

The frontend should make the machine-learning process understandable:

**Choose Dataset → Choose Model → Run → View Results → Compare**

The backend will handle the actual training and evaluation.

The frontend should only present the process and results clearly.
