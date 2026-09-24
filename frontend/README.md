# Encrypted DNS & QUIC Traffic Analyzer — Frontend

A research-oriented frontend for analyzing and visualizing encrypted DNS traffic (`DoQ`, `DoH3`, `DoH`) alongside multiplexed web traffic (`HTTP/3 Web`, `HTTPS Web`), adhering to the 5-class traffic classification schema and SQLite database persistence.

---

## Architecture & Scope

```text
Frontend (http://localhost:5173)
│
├── 📊 Dashboard
│   ├── Summary KPI Cards (Total Flows, Packets, DoQ, DoH3, DoH, Web Traffic)
│   ├── Traffic Class Composition Overview
│   └── Database Health & Storage Status (SQLite 3)
│
└── 🗄️ Dataset Management
    ├── 📁 Upload Dataset (CSV upload, drag-and-drop, validation, direct DB persistence)
    ├── ✍️ Manual Row-wise Entry (packet sequence creation for any table)
    ├── 📋 Existing Datasets (SQLite database tables)
    ├── 👁️ Dataset Preview (search, filter, pagination, inline CRUD)
    └── 📊 Visualization Suite:
        ├── 1. Traffic Class / Protocol Distribution (Bar chart)
        ├── 2. Packet Length Distribution (Histogram bins)
        ├── 3. Packet Timing / Progression (Line chart)
        └── 4. Direction Distribution (Forward → vs Backward ←)
```

---

## Canonical 5-Class Traffic Taxonomy

The dataset captures encrypted DNS protocols alongside background web traffic:

| Class | Protocol Family | Transport | Port | Description |
|---|---|---|---|---|
| **`DOQ`** | DNS over QUIC | UDP / QUIC | 853 / 784 | Encrypted DNS over QUIC transport |
| **`DOH3`** | DNS over HTTP/3 | UDP / QUIC | 443 | Encrypted DNS queries over HTTP/3 |
| **`DOH`** | DNS over HTTPS | TCP / TLS | 443 | Classic DNS over HTTPS over TLS |
| **`HTTP3_WEB`** | HTTP/3 Web | UDP / QUIC | 443 | Web browsing traffic over HTTP/3 |
| **`HTTPS_WEB`** | HTTPS Web | TCP / TLS | 443 | Web browsing traffic over TLS/TCP |

---

# 1. 📊 Dashboard

The dashboard provides an instant high-level overview of the currently loaded dataset and SQLite database.

### Summary KPI Cards

- **Total Packets / Records**: Total sequence count currently in the database
- **DoQ Traffic**: Count of DNS over QUIC packets/flows
- **DoH3 Traffic**: Count of DNS over HTTP/3 packets/flows
- **DoH Traffic**: Count of classic DNS over HTTPS packets/flows
- **Web Traffic**: Combined HTTP/3 Web + HTTPS Web background traffic
- **Database Status**: Engine (`SQLite 3`), database file (`dataset.db`), and total tables

### Visual Summary

- **Traffic Composition Bar**: Visual proportion breakdown across the 5 traffic classes
- **Dataset Information**: Active table dimensions, total size, and network conditions

---

# 2. 🗄️ Dataset Management

## 2.1 Upload Dataset

Supports:
- CSV upload with drag-and-drop & file picker
- Automatic header inspection & statistics calculation (row count, column count, missing values)
- **Direct Database Persistence**: One-click **"Save to SQLite DB"** (`POST /api/tables/upload`) to create or append tables in `backend/dataset.db`
- **Local Preview**: Option to preview without saving to database

## 2.2 Manual Row-wise Data Entry

Allows researchers to curate wire-level packet records manually, applicable to **all database tables**.

### Canonical Packet Schema Fields

| Field | Type | Example | Description |
|---|---|---|---|
| `flow_id` | String | `flow_doq_001` | Unique flow identifier |
| `capture_id` | String | `cap_doq_wifi_001` | Pcap capture session ID |
| `traffic_class` | String | `DOQ` | One of `DOQ`, `DOH3`, `DOH`, `HTTP3_WEB`, `HTTPS_WEB` |
| `label` | Integer | `3` | Numeric class label (0 to 4) |
| `packet_index` | Integer | `0` | 0-based sequential packet index |
| `timestamp` | Float | `0.00245` | Relative packet arrival time (seconds) |
| `direction` | String | `F` | `F` (Forward: Client → Server) or `B` (Backward: Server → Client) |
| `packet_size` | Integer | `1250` | Total wire packet length in bytes |
| `payload_size` | Integer | `1200` | Transport layer payload in bytes |
| `iat` | Float | `0.0012` | Inter-arrival time from preceding packet |
| `transport_protocol` | String | `QUIC` | `QUIC` (UDP) or `TCP` |
| `tcp_flags` | String | `ACK` | TCP flags (empty for QUIC) |
| `quic_packet_type` | String | `1-RTT` | QUIC frame/packet type |

### Required Actions

- `+ Add Row Directly` (Inline drawer above table)
- `✍️ Add Row to Active File` (Dedicated Tab form)
- Inline row editing (`✏️` → `✓`) persisting via `PUT /api/tables/{table}/rows/{rowid}`
- Inline row deletion (`✕`) persisting via `DELETE /api/tables/{table}/rows/{rowid}`

---

# 3. 👁️ Dataset Preview

The primary spreadsheet-style table view provides:
- **Active Table Metadata**: Displaying `${rowCount} rows × ${colCount} columns`
- **Instant Search / Filter**: Live filtering across all columns
- **Server-Side Pagination**: Navigate pages (`‹`, `›`) with configurable rows per page
- **Direction Pills**: Directional indicators (`→` Forward, `←` Backward)
- **Export**: `📥 Export CSV` direct download from SQLite (`GET /api/tables/{table}/export`)

---

# 4. 📊 Visualization Suite

A dedicated visualization suite renders data-driven charts directly from the active dataset.

### Recommended Initial Visualization Set

| # | Visualization | Data Field | Chart Type | Purpose |
|---|---|---|---|---|
| 1 | **Traffic Class Distribution** | `traffic_class` / `transport_protocol` | Bar Chart | Understand dataset composition across DoQ, DoH3, DoH, HTTP3, HTTPS |
| 2 | **Packet Length Distribution** | `packet_size` / `payload_size` | Histogram | Analyze wire packet size patterns (e.g. 0-200B, 200-500B, 500-1000B, 1000-1500B) |
| 3 | **Packet Timing Progression** | `timestamp` / `iat` | Line Chart | Inspect packet arrival intervals, bursts, and transmission timing |
| 4 | **Direction Distribution** | `direction` | Distribution Bar | Measure Forward (`→`) vs Backward (`←`) traffic asymmetry |

### Interactive Visualization Controls

- **Traffic Class Filter**: `[ All ▼ ]`, `[ DOQ ]`, `[ DOH3 ]`, `[ DOH ]`, `[ HTTP3_WEB ]`, `[ HTTPS_WEB ]`
- **Reset Filters**: One-click restore to full dataset view
- **Missing Data Handling**: If a dataset lacks specific fields (e.g. metadata tables lacking packet lengths), a clean notice is shown:
  ```text
  ⚠ Packet length data is not available in this dataset.
  ```

---

# 5. 🗄️ Database & API Backend (`backend/`)

- **Database**: SQLite 3 at `backend/dataset.db`
- **FastAPI Server**: Running on `http://localhost:8001`
- **Endpoints**:
  - `GET /api/status`: Engine stats, database path, table count, total rows
  - `GET /api/tables`: List of tables with schemas & row counts
  - `GET /api/tables/{table}/rows`: Paginated and searchable records
  - `POST /api/tables/{table}/rows`: Insert row into SQLite
  - `PUT /api/tables/{table}/rows/{rowid}`: Update row in SQLite
  - `DELETE /api/tables/{table}/rows/{rowid}`: Delete row from SQLite
  - `POST /api/tables/upload`: Upload CSV into SQLite table
  - `GET /api/tables/{table}/export`: Stream CSV download
