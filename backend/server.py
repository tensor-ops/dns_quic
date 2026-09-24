#!/usr/bin/env python3
"""
Encrypted DNS Dataset — Backend API
=====================================
FastAPI server with SQLite persistence and Machine Learning engine.

Database: dataset.db (SQLite, auto-created on startup)
Tables  : Canonical dataset tables (dataset, packets, flows, etc.)

Endpoints:
  GET    /api/status                        — Health check & database stats
  GET    /api/tables                        — List all tables & row counts
  GET    /api/tables/{table}/rows           — Get paginated/filtered rows
  POST   /api/tables/{table}/rows           — Append a new row
  PUT    /api/tables/{table}/rows/{rowid}   — Update a row by rowid
  DELETE /api/tables/{table}/rows/{rowid}   — Delete a row by rowid
  POST   /api/tables/upload                 — Upload a CSV to create/append a table
  GET    /api/tables/{table}/export         — Export table as CSV download
  GET    /api/models/available              — List supported ML models & feature tables
  POST   /api/models/train                  — Train & evaluate a model (Random Forest / XGBoost)
  POST   /api/models/compare                — Head-to-head comparison
  POST   /api/models/pipeline               — Train -> Validate -> Test pipeline runner

Usage:
  python server.py               # From backend/
  npm run dev                    # From backend/
  npm run backend                # From root
"""

import csv
import io
import os
import sqlite3
import sys
import time
from contextlib import asynccontextmanager, contextmanager
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from xgboost import XGBClassifier

# ---------------------------------------------------------------------------
# Config & Paths
# ---------------------------------------------------------------------------

PROJECT_ROOT      = Path(__file__).resolve().parent.parent
DATASET_DIR       = PROJECT_ROOT / "dataset"
FRONTEND_DATA_DIR = PROJECT_ROOT / "frontend" / "public" / "data"
DB_PATH           = PROJECT_ROOT / "backend" / "dataset.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

# Dataset CSV files to seed on startup
SEED_FILES = [
    ("dataset",               DATASET_DIR / "dataset.csv"),
    ("packets",               DATASET_DIR / "packets.csv"),
    ("flows",                 DATASET_DIR / "flows" / "flows.csv"),
    ("full_features",         DATASET_DIR / "features" / "full_features.csv"),
    ("fingerprint_features",  DATASET_DIR / "features" / "fingerprint_features.csv"),
    ("early_packets",         DATASET_DIR / "features" / "early_packets.csv"),
    ("metadata_captures",     DATASET_DIR / "metadata" / "captures.csv"),
    ("metadata_experiments",  DATASET_DIR / "metadata" / "experiments.csv"),
    ("metadata_networks",     DATASET_DIR / "metadata" / "networks.csv"),
    ("splits_train",          DATASET_DIR / "splits" / "train.csv"),
    ("splits_validation",     DATASET_DIR / "splits" / "validation.csv"),
    ("splits_test",           DATASET_DIR / "splits" / "test.csv"),
]

# ---------------------------------------------------------------------------
# Database Helpers
# ---------------------------------------------------------------------------

@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def _safe_table_name(name: str) -> str:
    """Sanitize table name to prevent SQL injection."""
    clean = "".join(c if c.isalnum() or c == "_" else "_" for c in name.strip().lower())
    while "__" in clean:
        clean = clean.replace("__", "_")
    return clean.strip("_") or "dataset"


def _safe_col_name(name: str) -> str:
    """Sanitize column name to standard SQL-safe snake_case."""
    clean = "".join(c if c.isalnum() or c == "_" else "_" for c in name.strip().lower())
    while "__" in clean:
        clean = clean.replace("__", "_")
    return clean.strip("_") or "col"


def _infer_column_type(series: pd.Series) -> str:
    if pd.api.types.is_integer_dtype(series):
        return "INTEGER"
    if pd.api.types.is_float_dtype(series):
        return "REAL"
    return "TEXT"


def seed_table(conn: sqlite3.Connection, table_name: str, csv_path: Path, force_reload: bool = False) -> int:
    """Create or refresh table from CSV. Return row count loaded."""
    resolved_path = csv_path
    if not resolved_path.exists():
        fallback = FRONTEND_DATA_DIR / csv_path.name
        if fallback.exists():
            resolved_path = fallback
        else:
            return 0

    df = pd.read_csv(resolved_path)
    df.columns = [_safe_col_name(c) for c in df.columns]
    df = df.fillna("")

    # Check if table already exists
    existing = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (table_name,),
    ).fetchone()

    if existing and not force_reload:
        current_count = conn.execute(f'SELECT COUNT(*) FROM "{table_name}"').fetchone()[0]
        if current_count == len(df) and current_count > 0:
            return current_count
        # Count mismatch with updated canonical file: drop and refresh
        conn.execute(f'DROP TABLE "{table_name}"')

    # Build CREATE TABLE statement
    col_defs = ["_rowid_ INTEGER PRIMARY KEY AUTOINCREMENT"]
    for col in df.columns:
        dtype = _infer_column_type(df[col])
        col_defs.append(f'"{col}" {dtype}')

    create_sql = f'CREATE TABLE IF NOT EXISTS "{table_name}" ({", ".join(col_defs)})'
    conn.execute(create_sql)

    # Insert rows
    cols = [f'"{c}"' for c in df.columns]
    placeholders = ", ".join(["?"] * len(df.columns))
    insert_sql = f'INSERT INTO "{table_name}" ({", ".join(cols)}) VALUES ({placeholders})'

    for row in df.itertuples(index=False):
        conn.execute(insert_sql, list(row))

    return len(df)


def seed_database():
    """Seed all canonical dataset CSV files into SQLite on startup."""
    with get_db() as conn:
        for table_name, csv_path in SEED_FILES:
            safe_name = _safe_table_name(table_name)
            count = seed_table(conn, safe_name, csv_path)
            if count > 0:
                print(f"  ✓ {safe_name:<30} {count:>6} rows")
            else:
                # Silent skip for non-existent legacy sub-files
                pass


# ---------------------------------------------------------------------------
# FastAPI Application & Lifespan
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"\n{'='*55}")
    print(f"  Encrypted DNS Dataset Backend  →  SQLite: {DB_PATH.name}")
    print(f"{'='*55}")
    print("  Seeding canonical datasets...")
    seed_database()
    print(f"{'='*55}\n")
    yield

app = FastAPI(
    title="Encrypted DNS Dataset API",
    description="SQLite-backed REST API for the Encrypted DNS Traffic Fingerprinting Dataset",
    version="1.0.0",
    docs_url="/docs",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# System & Table Management Routes
# ---------------------------------------------------------------------------

@app.get("/api/status", summary="Get database health and info")
def get_status():
    with get_db() as conn:
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        ).fetchall()
        total_rows = sum(
            conn.execute(f'SELECT COUNT(*) FROM "{r["name"]}"').fetchone()[0]
            for r in tables
        )
    return {
        "status": "connected",
        "engine": "SQLite 3",
        "database": DB_PATH.name,
        "database_path": str(DB_PATH),
        "total_tables": len(tables),
        "total_rows": total_rows,
    }


@app.get("/api/tables", summary="List all dataset tables")
def list_tables():
    with get_db() as conn:
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
        ).fetchall()
        result = []
        for row in tables:
            name = row["name"]
            count = conn.execute(f'SELECT COUNT(*) FROM "{name}"').fetchone()[0]
            pragma = conn.execute(f'PRAGMA table_info("{name}")').fetchall()
            cols = [
                r[1] for r in pragma
                if r[1] != "_rowid_"
            ]
            result.append({
                "table": name,
                "row_count": count,
                "columns": cols,
                "col_count": len(cols),
            })
    return {"tables": result, "database": DB_PATH.name}


@app.get("/api/tables/{table}/rows", summary="Get paginated rows from a table")
def get_rows(
    table: str,
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=25, ge=1, le=500),
    search: str = Query(default=""),
):
    safe = _safe_table_name(table)
    with get_db() as conn:
        exists = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (safe,)
        ).fetchone()
        if not exists:
            raise HTTPException(status_code=404, detail=f"Table '{safe}' not found")

        pragma = conn.execute(f'PRAGMA table_info("{safe}")').fetchall()
        cols = [r[1] for r in pragma if r[1] != "_rowid_"]

        offset = (page - 1) * per_page
        if cols and search.strip():
            where_clauses = [f'CAST("{c}" AS TEXT) LIKE ?' for c in cols]
            where_sql = " OR ".join(where_clauses)
            params_filter = [f"%{search.strip()}%"] * len(cols)
            count_sql = f'SELECT COUNT(*) FROM "{safe}" WHERE {where_sql}'
            rows_sql  = f'SELECT _rowid_, * FROM "{safe}" WHERE {where_sql} LIMIT ? OFFSET ?'
            total = conn.execute(count_sql, params_filter).fetchone()[0]
            rows  = conn.execute(rows_sql, params_filter + [per_page, offset]).fetchall()
        else:
            total = conn.execute(f'SELECT COUNT(*) FROM "{safe}"').fetchone()[0]
            rows  = conn.execute(
                f'SELECT _rowid_, * FROM "{safe}" LIMIT ? OFFSET ?', (per_page, offset)
            ).fetchall()

        return {
            "table": safe,
            "columns": cols,
            "total": total,
            "page": page,
            "per_page": per_page,
            "rows": [dict(r) for r in rows],
        }


@app.post("/api/tables/{table}/rows", summary="Append a new row to a table")
def add_row(table: str, payload: dict[str, Any]):
    safe = _safe_table_name(table)
    with get_db() as conn:
        exists = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (safe,)
        ).fetchone()
        if not exists:
            raise HTTPException(status_code=404, detail=f"Table '{safe}' not found")

        pragma = conn.execute(f'PRAGMA table_info("{safe}")').fetchall()
        cols = [r[1] for r in pragma if r[1] != "_rowid_"]

        # Support matching case-insensitively or snake_cased
        col_map = {c.lower(): c for c in cols}
        valid = {}
        for k, v in payload.items():
            k_clean = _safe_col_name(k)
            if k_clean in col_map:
                valid[col_map[k_clean]] = v

        if not valid:
            raise HTTPException(status_code=422, detail="No valid columns provided")

        col_str = ", ".join(f'"{c}"' for c in valid)
        placeholders = ", ".join(["?"] * len(valid))
        cursor = conn.execute(
            f'INSERT INTO "{safe}" ({col_str}) VALUES ({placeholders})',
            list(valid.values()),
        )
        new_rowid = cursor.lastrowid
        new_row = conn.execute(
            f'SELECT _rowid_, * FROM "{safe}" WHERE _rowid_=?', (new_rowid,)
        ).fetchone()
        return {"inserted": True, "row": dict(new_row)}


@app.put("/api/tables/{table}/rows/{rowid}", summary="Update a row by rowid")
def update_row(table: str, rowid: int, payload: dict[str, Any]):
    safe = _safe_table_name(table)
    with get_db() as conn:
        exists = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (safe,)
        ).fetchone()
        if not exists:
            raise HTTPException(status_code=404, detail=f"Table '{safe}' not found")

        pragma = conn.execute(f'PRAGMA table_info("{safe}")').fetchall()
        cols = [r[1] for r in pragma if r[1] != "_rowid_"]

        col_map = {c.lower(): c for c in cols}
        valid = {}
        for k, v in payload.items():
            k_clean = _safe_col_name(k)
            if k_clean in col_map:
                valid[col_map[k_clean]] = v

        if not valid:
            raise HTTPException(status_code=422, detail="No valid columns provided")

        set_clause = ", ".join(f'"{c}" = ?' for c in valid)
        conn.execute(
            f'UPDATE "{safe}" SET {set_clause} WHERE _rowid_ = ?',
            [*valid.values(), rowid],
        )
        updated_row = conn.execute(
            f'SELECT _rowid_, * FROM "{safe}" WHERE _rowid_=?', (rowid,)
        ).fetchone()
        if not updated_row:
            raise HTTPException(status_code=404, detail=f"Row {rowid} not found")
        return {"updated": True, "row": dict(updated_row)}


@app.delete("/api/tables/{table}/rows/{rowid}", summary="Delete a row by rowid")
def delete_row(table: str, rowid: int):
    safe = _safe_table_name(table)
    with get_db() as conn:
        exists = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (safe,)
        ).fetchone()
        if not exists:
            raise HTTPException(status_code=404, detail=f"Table '{safe}' not found")

        result = conn.execute(f'DELETE FROM "{safe}" WHERE _rowid_=?', (rowid,))
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail=f"Row {rowid} not found")
        return {"deleted": True, "rowid": rowid}


@app.post("/api/tables/upload", summary="Upload a CSV to create or append a table")
async def upload_csv(
    file: UploadFile = File(...),
    table_name: str = Query(default=""),
):
    if not (file.filename and file.filename.lower().endswith(".csv")):
        raise HTTPException(status_code=422, detail="Only CSV files are accepted")

    content = await file.read()
    decoded = content.decode("utf-8-sig", errors="replace")
    reader = csv.DictReader(io.StringIO(decoded))
    headers = reader.fieldnames
    if not headers:
        raise HTTPException(status_code=422, detail="CSV has no headers")

    rows_data = list(reader)
    if not rows_data:
        raise HTTPException(status_code=422, detail="CSV has no data rows")

    safe_table = _safe_table_name(table_name or Path(file.filename).stem)

    with get_db() as conn:
        df = pd.DataFrame(rows_data)
        df.columns = [_safe_col_name(c) for c in df.columns]

        # Infer numeric types for clean database storage
        for c in df.columns:
            converted = pd.to_numeric(df[c], errors="ignore")
            df[c] = converted

        existing = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (safe_table,)
        ).fetchone()

        if not existing:
            col_defs = ["_rowid_ INTEGER PRIMARY KEY AUTOINCREMENT"]
            for col in df.columns:
                dtype = _infer_column_type(df[col])
                col_defs.append(f'"{col}" {dtype}')
            conn.execute(f'CREATE TABLE "{safe_table}" ({", ".join(col_defs)})')

        safe_cols = list(df.columns)
        col_str = ", ".join(f'"{c}"' for c in safe_cols)
        placeholders = ", ".join(["?"] * len(safe_cols))
        for _, row in df.iterrows():
            conn.execute(
                f'INSERT INTO "{safe_table}" ({col_str}) VALUES ({placeholders})',
                [row[c] for c in safe_cols],
            )

        total = conn.execute(f'SELECT COUNT(*) FROM "{safe_table}"').fetchone()[0]

    return {
        "table": safe_table,
        "rows_inserted": len(rows_data),
        "total_rows": total,
        "columns": list(df.columns),
    }


@app.get("/api/tables/{table}/export", summary="Export table as CSV download")
def export_table(table: str):
    safe = _safe_table_name(table)
    with get_db() as conn:
        exists = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (safe,)
        ).fetchone()
        if not exists:
            raise HTTPException(status_code=404, detail=f"Table '{safe}' not found")

        pragma = conn.execute(f'PRAGMA table_info("{safe}")').fetchall()
        cols = [r[1] for r in pragma if r[1] != "_rowid_"]
        col_select = ", ".join(f'"{c}"' for c in cols)
        rows = conn.execute(f'SELECT {col_select} FROM "{safe}"').fetchall()

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(cols)
    for row in rows:
        writer.writerow(list(row))

    buf.seek(0)
    return StreamingResponse(
        iter([buf.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{safe}.csv"'},
    )


# ---------------------------------------------------------------------------
# Machine Learning Engine
# ---------------------------------------------------------------------------

SUPPORTED_MODELS = [
    "Random Forest",
    "XGBoost",
]

CANONICAL_CLASSES = ["DOH", "DOH3", "DOQ", "HTTP3_WEB", "HTTPS_WEB"]


class TrainModelRequest(BaseModel):
    model_name: str = Field(default="Random Forest")
    table_name: str = Field(default="packets")
    test_size: float = Field(default=0.3, ge=0.1, le=0.5)
    random_state: int = Field(default=42)


class CompareModelsRequest(BaseModel):
    table_name: str = Field(default="packets")
    models: list[str] = Field(default_factory=lambda: SUPPORTED_MODELS)
    test_size: float = Field(default=0.3, ge=0.1, le=0.5)
    random_state: int = Field(default=42)


class PipelineRequest(BaseModel):
    model_name: str = Field(default="Random Forest")
    table_name: str = Field(default="packets")
    phase: str = Field(default="train")  # 'train' | 'validate' | 'test'
    random_state: int = Field(default=42)


def get_classifier_instance(name: str):
    if name == "Random Forest":
        return RandomForestClassifier(n_estimators=100, random_state=42)
    elif name == "XGBoost":
        return XGBClassifier(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=6,
            random_state=42,
            eval_metric="mlogloss",
        )
    else:
        raise ValueError(f"Unknown model name: {name}")


def load_feature_matrix(conn: sqlite3.Connection, table_name: str):
    safe = _safe_table_name(table_name)
    df = pd.read_sql_query(f'SELECT * FROM "{safe}"', conn)
    if len(df) == 0:
        raise HTTPException(status_code=400, detail=f"Table '{safe}' is empty")

    target_col = None
    for cand in ["traffic_class", "traffic", "protocol", "label"]:
        if cand in df.columns:
            target_col = cand
            break

    if not target_col:
        raise HTTPException(status_code=400, detail=f"No target classification column found in '{safe}'")

    y = df[target_col].astype(str)

    exclude = {
        "_rowid_", "flow_id", "capture_id", "label", "traffic_class",
        "traffic", "split", "scenario_id", "repetition_id", "capture_date",
        "device_id", "network_id", "capture_file", "environment", "target",
    }

    if "direction" in df.columns:
        df["direction_num"] = df["direction"].map(lambda d: 1 if str(d).upper() in ["F", "→", "CLIENT"] else 0)
        exclude.add("direction")

    if "transport_protocol" in df.columns:
        df["proto_num"] = df["transport_protocol"].map(lambda p: 1 if "QUIC" in str(p).upper() else 0)
        exclude.add("transport_protocol")

    # Clean and convert numeric-like columns
    for c in df.columns:
        if c not in exclude and not pd.api.types.is_numeric_dtype(df[c]):
            num_c = pd.to_numeric(df[c], errors="coerce")
            if num_c.notna().sum() > 0.5 * len(df):
                df[c] = num_c

    feature_cols = [
        c for c in df.columns
        if c not in exclude and pd.api.types.is_numeric_dtype(df[c])
    ]

    if not feature_cols:
        raise HTTPException(status_code=400, detail=f"No numeric features found in table '{safe}'")

    X = df[feature_cols].replace([np.inf, -np.inf], np.nan).fillna(0)
    return X, y, feature_cols


@app.get("/api/models/available", summary="List available models and feature tables")
def list_available_models():
    with get_db() as conn:
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
        ).fetchall()
        feature_tables = [
            r["name"] for r in tables
            if any(k in r["name"] for k in ["dataset", "features", "packets", "flows", "splits"])
        ]

    return {
        "models": SUPPORTED_MODELS,
        "recommended_tables": feature_tables or ["dataset", "packets", "early_packets"],
        "classes": CANONICAL_CLASSES,
    }


@app.post("/api/models/train", summary="Train and evaluate a single model")
def train_model(req: TrainModelRequest):
    with get_db() as conn:
        X, y, feature_cols = load_feature_matrix(conn, req.table_name)

    # Check class distribution and stratifiability
    class_counts = y.value_counts()
    n_classes = len(class_counts)
    can_stratify = (class_counts.min() >= 2) and (int(len(X) * req.test_size) >= n_classes)

    # Perform split
    if len(X) >= 6 and can_stratify:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=req.test_size,
            random_state=req.random_state,
            stratify=y,
        )
    elif len(X) >= 4:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=req.test_size,
            random_state=req.random_state,
            shuffle=True,
        )
    else:
        X_train, X_test, y_train, y_test = X, X, y, y

    # Label encoding: Fit on y_train so classes are ALWAYS contiguous 0..K-1 for XGBoost
    all_classes = sorted(list(set(y_train.unique()) | set(y_test.unique())))
    le_train = LabelEncoder()
    y_train_enc = le_train.fit_transform(y_train)

    # Scale features
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)

    # Train model
    model = get_classifier_instance(req.model_name)
    t0 = time.perf_counter()
    model.fit(X_train_s, y_train_enc)
    train_time_ms = round((time.perf_counter() - t0) * 1000, 2)

    # Predict & Evaluate
    preds_enc = model.predict(X_test_s)
    preds = le_train.inverse_transform(preds_enc)

    acc = float(accuracy_score(y_test, preds))
    prec = float(precision_score(y_test, preds, average="macro", zero_division=0))
    rec = float(recall_score(y_test, preds, average="macro", zero_division=0))
    f1 = float(f1_score(y_test, preds, average="macro", zero_division=0))
    cm = confusion_matrix(y_test, preds, labels=all_classes).tolist()

    # Feature importances
    feature_importances = []
    if hasattr(model, "feature_importances_"):
        imps = model.feature_importances_
        sorted_indices = np.argsort(imps)[::-1]
        for idx in sorted_indices[:12]:
            feature_importances.append({
                "feature": feature_cols[idx],
                "importance": round(float(imps[idx]), 4),
            })

    metrics_dict = {
        "accuracy": round(acc, 4),
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "f1": round(f1, 4),
        "f1_score": round(f1, 4),
        "train_time_ms": train_time_ms,
        "training_time_ms": train_time_ms,
    }

    cm_dict = {
        "matrix": cm,
        "classes": all_classes,
    }

    return {
        "model_name": req.model_name,
        "category": "Classifier",
        "table_name": req.table_name,
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "feature_count": len(feature_cols),
        "features": feature_cols,
        "classes": all_classes,
        "accuracy": round(acc, 4),
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "f1": round(f1, 4),
        "training_time_ms": train_time_ms,
        "metrics": metrics_dict,
        "confusion_matrix": cm_dict,
        "dataset_info": {
            "train_samples": len(X_train),
            "test_samples": len(X_test),
            "features_used": len(feature_cols),
            "classes": all_classes,
        },
        "feature_importances": feature_importances,
    }


@app.post("/api/models/compare", summary="Train and compare Random Forest vs XGBoost")
def compare_models(req: CompareModelsRequest):
    with get_db() as conn:
        X, y, feature_cols = load_feature_matrix(conn, req.table_name)

    class_counts = y.value_counts()
    n_classes = len(class_counts)
    can_stratify = (class_counts.min() >= 2) and (int(len(X) * req.test_size) >= n_classes)

    if len(X) >= 6 and can_stratify:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=req.test_size,
            random_state=req.random_state,
            stratify=y,
        )
    elif len(X) >= 4:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=req.test_size,
            random_state=req.random_state,
            shuffle=True,
        )
    else:
        X_train, X_test, y_train, y_test = X, X, y, y

    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)

    all_classes = sorted(list(set(y_train.unique()) | set(y_test.unique())))
    le_train = LabelEncoder()
    y_train_enc = le_train.fit_transform(y_train)

    results = []
    models_to_run = req.models or SUPPORTED_MODELS

    for m_name in models_to_run:
        try:
            clf = get_classifier_instance(m_name)
            t0 = time.perf_counter()
            clf.fit(X_train_s, y_train_enc)
            train_time_ms = round((time.perf_counter() - t0) * 1000, 2)

            preds_enc = clf.predict(X_test_s)
            preds = le_train.inverse_transform(preds_enc)

            acc = float(accuracy_score(y_test, preds))
            prec = float(precision_score(y_test, preds, average="macro", zero_division=0))
            rec = float(recall_score(y_test, preds, average="macro", zero_division=0))
            f1 = float(f1_score(y_test, preds, average="macro", zero_division=0))
            cm = confusion_matrix(y_test, preds, labels=all_classes).tolist()

            feature_importances = []
            if hasattr(clf, "feature_importances_"):
                imps = clf.feature_importances_
                sorted_indices = np.argsort(imps)[::-1]
                for idx in sorted_indices[:10]:
                    feature_importances.append({
                        "feature": feature_cols[idx],
                        "importance": round(float(imps[idx]), 4),
                    })

            metrics_dict = {
                "accuracy": round(acc, 4),
                "precision": round(prec, 4),
                "recall": round(rec, 4),
                "f1": round(f1, 4),
                "f1_score": round(f1, 4),
                "train_time_ms": train_time_ms,
                "training_time_ms": train_time_ms,
            }

            cm_dict = {
                "matrix": cm,
                "classes": all_classes,
            }

            results.append({
                "model_name": m_name,
                "category": "Classifier",
                "accuracy": round(acc, 4),
                "precision": round(prec, 4),
                "recall": round(rec, 4),
                "f1": round(f1, 4),
                "training_time_ms": train_time_ms,
                "metrics": metrics_dict,
                "confusion_matrix": cm_dict,
                "classes": all_classes,
                "feature_importances": feature_importances,
            })
        except Exception as e:
            results.append({
                "model_name": m_name,
                "category": "Classifier",
                "error": str(e),
                "accuracy": 0.0,
                "precision": 0.0,
                "recall": 0.0,
                "f1": 0.0,
            })

    results.sort(key=lambda r: r.get("accuracy", 0), reverse=True)

    return {
        "table_name": req.table_name,
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "feature_count": len(feature_cols),
        "classes": all_classes,
        "results": results,
    }


@app.post("/api/models/pipeline", summary="Run a Train → Validate → Test pipeline phase")
def run_pipeline(req: PipelineRequest):
    """Execute a single phase of the ML pipeline (train, validate, or test)."""
    if req.model_name not in SUPPORTED_MODELS:
        raise HTTPException(status_code=400, detail=f"Model must be one of: {SUPPORTED_MODELS}")

    if req.phase not in ("train", "validate", "test"):
        raise HTTPException(status_code=400, detail="Phase must be 'train', 'validate', or 'test'")

    with get_db() as conn:
        use_splits_tables = False
        if req.table_name in ("splits", "splits_train", "predefined_splits"):
            has_splits = True
            for split_table in ["splits_train", "splits_validation", "splits_test"]:
                exists = conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                    (split_table,),
                ).fetchone()
                if not exists:
                    has_splits = False
                    break
                row_count = conn.execute(f'SELECT COUNT(*) FROM "{split_table}"').fetchone()[0]
                if row_count == 0:
                    has_splits = False
                    break
            if has_splits:
                use_splits_tables = True

        if use_splits_tables:
            X_train, y_train, feature_cols = load_feature_matrix(conn, "splits_train")
            X_val, y_val, _ = load_feature_matrix(conn, "splits_validation")
            X_test, y_test, _ = load_feature_matrix(conn, "splits_test")

            common_cols = [c for c in feature_cols if c in X_val.columns and c in X_test.columns]
            if not common_cols:
                raise HTTPException(status_code=400, detail="No common numeric features across splits")
            X_train = X_train[common_cols]
            X_val = X_val[common_cols]
            X_test = X_test[common_cols]
            feature_cols = common_cols
        else:
            X_full, y_full, feature_cols = load_feature_matrix(conn, req.table_name)
            class_counts = y_full.value_counts()
            n_classes = len(class_counts)
            can_stratify = (class_counts.min() >= 3) and (int(len(X_full) * 0.2) >= n_classes)

            if len(X_full) >= 6:
                X_trainval, X_test, y_trainval, y_test = train_test_split(
                    X_full, y_full,
                    test_size=0.2,
                    random_state=req.random_state,
                    stratify=y_full if can_stratify else None,
                )
                tv_counts = y_trainval.value_counts()
                can_strat2 = (tv_counts.min() >= 2) and (int(len(X_trainval) * 0.25) >= len(tv_counts))
                X_train, X_val, y_train, y_val = train_test_split(
                    X_trainval, y_trainval,
                    test_size=0.25,
                    random_state=req.random_state,
                    stratify=y_trainval if can_strat2 else None,
                )
            else:
                X_train, X_val, X_test = X_full, X_full, X_full
                y_train, y_val, y_test = y_full, y_full, y_full

    all_classes = sorted(list(set(y_train.unique()) | set(y_val.unique()) | set(y_test.unique())))
    le_train = LabelEncoder()
    y_train_enc = le_train.fit_transform(y_train)

    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_val_s = scaler.transform(X_val)
    X_test_s = scaler.transform(X_test)

    clf = get_classifier_instance(req.model_name)
    t0 = time.perf_counter()
    clf.fit(X_train_s, y_train_enc)
    train_time_ms = round((time.perf_counter() - t0) * 1000, 2)

    if req.phase == "train":
        X_eval_s, y_eval = X_train_s, y_train
        eval_samples = len(y_train)
    elif req.phase == "validate":
        X_eval_s, y_eval = X_val_s, y_val
        eval_samples = len(y_val)
    else:  # test
        X_eval_s, y_eval = X_test_s, y_test
        eval_samples = len(y_test)

    preds_enc = clf.predict(X_eval_s)
    preds = le_train.inverse_transform(preds_enc)

    acc = float(accuracy_score(y_eval, preds))
    prec = float(precision_score(y_eval, preds, average="macro", zero_division=0))
    rec = float(recall_score(y_eval, preds, average="macro", zero_division=0))
    f1 = float(f1_score(y_eval, preds, average="macro", zero_division=0))
    cm = confusion_matrix(y_eval, preds, labels=all_classes).tolist()

    feature_importances = []
    if hasattr(clf, "feature_importances_"):
        imps = clf.feature_importances_
        sorted_indices = np.argsort(imps)[::-1]
        for idx in sorted_indices[:12]:
            feature_importances.append({
                "feature": feature_cols[idx],
                "importance": round(float(imps[idx]), 4),
            })

    return {
        "model_name": req.model_name,
        "phase": req.phase,
        "table_name": req.table_name,
        "used_splits_tables": use_splits_tables,
        "train_samples": len(y_train),
        "validation_samples": len(y_val),
        "test_samples": len(y_test),
        "eval_samples": eval_samples,
        "feature_count": len(feature_cols),
        "features": feature_cols,
        "classes": all_classes,
        "metrics": {
            "accuracy": round(acc, 4),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1_score": round(f1, 4),
            "train_time_ms": train_time_ms,
        },
        "confusion_matrix": {
            "matrix": cm,
            "classes": all_classes,
        },
        "feature_importances": feature_importances,
        "dataset_info": {
            "train_samples": len(y_train),
            "validation_samples": len(y_val),
            "test_samples": len(y_test),
            "features_used": len(feature_cols),
            "classes": all_classes,
        },
    }


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    backend_dir = Path(__file__).resolve().parent
    if str(backend_dir) not in sys.path:
        sys.path.insert(0, str(backend_dir))
    import uvicorn
    port = int(os.environ.get("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)
