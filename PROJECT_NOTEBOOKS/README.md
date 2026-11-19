# Research Project Model Notebooks

**Directory:** `/Users/paru/paru/projects/RM/PROJECT_NOTEBOOKS`  
**Focus:** Supervised Training, Validation, and Testing of Encrypted DNS & QUIC Classifiers  
**Target Protocols (6):** `DOH`, `DOQ`, `DOH3`, `QUIC`, `HTTPS_WEB`, `HTTP3_WEB` (DOT protocol removed)  
**Zero-Leakage Feature Set:** Observable Kinematic Features (`Current packet size`, `Previous packet size`, `Current time gap`, `Previous time gap`)

---

## 1. Notebook Inventory & Models

| Notebook File | Model Architecture | Key Characteristics & Role |
|---|---|---|
| [`01_Random_Forest.ipynb`](01_Random_Forest.ipynb) | **Random Forest** (`RandomForestClassifier`) | 300 estimators, entropy criterion; primary nonlinear ensemble baseline with native Gini/entropy feature importance. |
| [`02_XGBoost.ipynb`](02_XGBoost.ipynb) | **XGBoost** (`XGBClassifier`) | Extreme gradient boosting with softprob objective, subsampling, and feature gain tree analysis. |
| [`03_Decision_Tree.ipynb`](03_Decision_Tree.ipynb) | **Decision Tree** (`DecisionTreeClassifier`) | Single-tree benchmark offering visual hierarchical decision boundaries and threshold inspection. |
| [`04_Support_Vector_Machine.ipynb`](04_Support_Vector_Machine.ipynb) | **Support Vector Machine (SVM)** (`SVC`) | Maximum margin hyperplane classifier with Radial Basis Function (RBF) kernel and feature scaling. |
| [`05_K_Nearest_Neighbors.ipynb`](05_K_Nearest_Neighbors.ipynb) | **k-Nearest Neighbors (KNN)** (`KNeighborsClassifier`) | Instance-based distance metric benchmark ($k=7$) evaluating local manifold continuity and sensitivity. |
| [`06_Logistic_Regression.ipynb`](06_Logistic_Regression.ipynb) | **Logistic Regression** (`LogisticRegression`) | Multinomial generalized linear baseline assessing linear separability of modern encrypted traffic. |
| [`07_MLP_Neural_Network.ipynb`](07_MLP_Neural_Network.ipynb) | **Multi-Layer Perceptron (MLP)** (`MLPClassifier`) | Deep feedforward neural network (128 → 64 hidden nodes), ReLU activation, Adam optimizer, early stopping. |
| [`08_Model_Comparison_and_Benchmarking.ipynb`](08_Model_Comparison_and_Benchmarking.ipynb) | **Master Model Benchmark** (All 7 Models) | Head-to-head evaluation on identical splits, generating performance leaderboards and latency plots. |

---

## 2. Standardized Workflow in Every Notebook

Each individual model notebook follows a rigorous scientific workflow:
1. **Environment Setup & Reproducibility:** Fixed random seed (`RANDOM_STATE = 42`) and inline visualization styling.
2. **Data Ingestion:** Reads the consolidated dataset from `../PROJECT_DATASET/FULL_COMBINED_WITH_METADATA.csv` (70,399 samples across Prayagraj Airtel, Prayagraj Jio, Tumsar Airtel, and Mirzapur Jio).
3. **Audit & Zero-Leakage Check:** Confirms the 6 classes are present, verifies zero missing values, and strictly selects only the 4 observable packet features.
4. **Stratified Data Partitioning:**
   - **Train Set (70%):** Model fitting.
   - **Validation Set (15%):** Hyperparameter tuning & internal checkpointing.
   - **Holdout Test Set (15%):** Unseen test set for final reporting.
5. **5-Fold Stratified Cross-Validation:** Validates model variance across 5 training folds ($K=5$).
6. **Validation Evaluation:** Verifies generalization on the $15\%$ validation set.
7. **Test Evaluation:** Computes final Test Accuracy, Precision, Recall, Macro-F1, Weighted-F1, and per-packet inference latency.
8. **Visual Confusion Matrix:** Normalized heatmap showing prediction vs actual distributions.
9. **Model-Specific Deep Dive:**
   - RF: Feature importance bar chart
   - XGB: Feature gain ranking
   - DT: Decision tree visual plot (depth $\le 3$)
   - SVM: Support vector audit per class
   - KNN: Sensitivity curve across $k \in [3, 5, 7, 11, 15]$
   - LR: Feature coefficient heatmap across all 6 classes
   - MLP: Epoch loss convergence curve
10. **Cross-Network Domain Shift Evaluation:** Evaluates robustness when trained on Airtel and tested on Jio.
11. **Model Persistence:** Serializes the trained model pipeline via `joblib` into `saved_models/`.

---

## 3. How to Run

Open any notebook in Jupyter Lab, Jupyter Notebook, or VS Code / Cursor:
```bash
jupyter lab /Users/paru/paru/projects/RM/PROJECT_NOTEBOOKS
```
To run all cells head-to-head across all 7 models, open [`08_Model_Comparison_and_Benchmarking.ipynb`](08_Model_Comparison_and_Benchmarking.ipynb).
