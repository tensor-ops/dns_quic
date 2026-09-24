/**
 * Encrypted DNS & QUIC Traffic Analyzer — Frontend Controller
 * ============================================================
 * Features:
 *   1. 📊 Dashboard: Summary KPI cards, traffic composition bar, database specs
 *   2. 🗄️ Dataset Management: SQLite table viewer, pagination, live search
 *   3. ✍️ Universal Manual Entry: Persistent SQLite insertions
 *   4. 📁 CSV Upload: Direct SQLite table creation / append
 *   5. 📊 Visualization Suite:
 *      - Protocol / Class Distribution (Bar chart)
 *      - Packet Length Distribution (Histogram bins)
 *      - Packet Timing Progression (Line chart)
 *      - Direction Distribution (Forward vs Backward ratio)
 *      - Interactive Traffic Class filter & graceful fallbacks
 */

import { parseCSV, toCSV, computeDatasetStats } from './csvParser.js';
import { EXISTING_DATASETS_REGISTRY } from './defaultData.js';

// Global state
const state = {
  currentView: 'dashboard', // 'dashboard' | 'dataset' | 'models'
  dbConnected: false,
  dbInfo: null,
  tables: [],
  activeTable: 'dataset',
  allActiveRows: [],        // Cached all rows of active table for visualizations & stats
  activeDataset: {
    name: '',
    headers: [],
    rows: [],
    totalRows: 0,
  },
  visFilterClass: 'ALL',
  uploadedFile: null,
  searchQuery: '',
  currentPage: 1,
  rowsPerPage: 25,
  editingRowId: null,
  isLoading: false,
  modelsState: {
    selectedModel: 'Random Forest',
    selectedTable: 'dataset',
    currentPhase: 'idle', // 'idle' | 'trained' | 'validated' | 'tested'
    trainResult: null,
    validateResult: null,
    testResult: null,
    lastCompareResult: null,
    isTraining: false,
  },
};

// DOM References
const navBtnDashboard = document.getElementById('btn-nav-dashboard');
const navBtnDataset = document.getElementById('btn-nav-dataset');
const navBtnModels = document.getElementById('btn-nav-models');
const viewDashboard = document.getElementById('view-dashboard');
const viewDataset = document.getElementById('view-dataset');
const viewModels = document.getElementById('view-models');
const btnDashJumpDataset = document.getElementById('btn-dash-jump-dataset');

const datasetSelect = document.getElementById('dataset-select');
const btnExportCsv = document.getElementById('btn-export-csv');

// Dashboard Elements
const kpiTotalVal = document.getElementById('kpi-total-val');
const kpiDoqVal = document.getElementById('kpi-doq-val');
const kpiDoqPct = document.getElementById('kpi-doq-pct');
const kpiDoh3Val = document.getElementById('kpi-doh3-val');
const kpiDoh3Pct = document.getElementById('kpi-doh3-pct');
const kpiDohVal = document.getElementById('kpi-doh-val');
const kpiDohPct = document.getElementById('kpi-doh-pct');
const kpiWebVal = document.getElementById('kpi-web-val');
const kpiWebPct = document.getElementById('kpi-web-pct');

// Visualization Elements
const filterTrafficClass = document.getElementById('filter-traffic-class');
const btnResetVisFilters = document.getElementById('btn-reset-vis-filters');
const chartProtocolDist = document.getElementById('chart-protocol-dist');
const chartLengthDist = document.getElementById('chart-length-dist');
const chartTimingDist = document.getElementById('chart-timing-dist');
const chartDirectionDist = document.getElementById('chart-direction-dist');

// Action Bar & Tabs
const tabBtns = document.querySelectorAll('.tab-btn');
const tabUpload = document.getElementById('tab-upload');
const tabManual = document.getElementById('tab-manual');

// Upload Tab
const dropzone = document.getElementById('csv-dropzone');
const fileInput = document.getElementById('csv-file-input');
const btnBrowse = document.getElementById('btn-browse-file');
const uploadInfoBox = document.getElementById('upload-info-box');
const tagFilename = document.getElementById('tag-filename');
const tagRows = document.getElementById('tag-rows');
const tagCols = document.getElementById('tag-cols');
const tagMissing = document.getElementById('tag-missing');
const btnSaveToDb = document.getElementById('btn-save-to-db');
const btnViewUploaded = document.getElementById('btn-view-uploaded');

// Manual Entry Form
const manualFileTargetDesc = document.getElementById('manual-file-target-desc');
const dynamicManualFields = document.getElementById('dynamic-manual-fields');
const btnSubmitManualRow = document.getElementById('btn-submit-manual-row');
const btnResetManualForm = document.getElementById('btn-reset-manual-form');

// Inline Add Drawer
const btnToggleInlineAdd = document.getElementById('btn-toggle-inline-add');
const inlineAddDrawer = document.getElementById('inline-add-drawer');
const inlineFieldsGrid = document.getElementById('inline-fields-grid');
const btnSaveInlineRow = document.getElementById('btn-save-inline-row');
const btnCancelInlineRow = document.getElementById('btn-cancel-inline-row');

// Main Table
const activeDatasetName = document.getElementById('active-dataset-name');
const activeDatasetDim = document.getElementById('active-dataset-dim');
const tableSearchInput = document.getElementById('table-search-input');
const paginationInfo = document.getElementById('pagination-info');
const btnPrevPage = document.getElementById('btn-prev-page');
const btnNextPage = document.getElementById('btn-next-page');
const mainTableThead = document.getElementById('main-table-thead');
const mainTableTbody = document.getElementById('main-table-tbody');

// Models & Experiments Elements (Pipeline)
const modelCardRF = document.getElementById('model-card-rf');
const modelCardXGB = document.getElementById('model-card-xgb');
const modelDatasetSelect = document.getElementById('model-dataset-select');
const splitInfoText = document.getElementById('split-info-text');

// Pipeline Stepper Elements
const pipelineStepTrain = document.getElementById('pipeline-step-train');
const pipelineStepValidate = document.getElementById('pipeline-step-validate');
const pipelineStepTest = document.getElementById('pipeline-step-test');
const stepStatusTrain = document.getElementById('step-status-train');
const stepStatusValidate = document.getElementById('step-status-validate');
const stepStatusTest = document.getElementById('step-status-test');
const btnPipelineTrain = document.getElementById('btn-pipeline-train');
const btnPipelineValidate = document.getElementById('btn-pipeline-validate');
const btnPipelineTest = document.getElementById('btn-pipeline-test');

// Phase Result Elements
const phaseCardTrain = document.getElementById('phase-card-train');
const phaseCardValidate = document.getElementById('phase-card-validate');
const phaseCardTest = document.getElementById('phase-card-test');
const phaseBadgeTrain = document.getElementById('phase-badge-train');
const phaseBadgeValidate = document.getElementById('phase-badge-validate');
const phaseBadgeTest = document.getElementById('phase-badge-test');
const phaseMetricsTrain = document.getElementById('phase-metrics-train');
const phaseMetricsValidate = document.getElementById('phase-metrics-validate');
const phaseMetricsTest = document.getElementById('phase-metrics-test');

const btnRunCompareModels = document.getElementById('btn-run-compare-models');
const modelsExecStatus = document.getElementById('models-exec-status');
const trainingProgressBox = document.getElementById('training-progress-box');
const trainingProgressText = document.getElementById('training-progress-text');
const cmModelName = document.getElementById('cm-model-name');
const confusionMatrixWrapper = document.getElementById('confusion-matrix-wrapper');
const featureImportanceWrapper = document.getElementById('feature-importance-wrapper');
const modelsComparisonPanel = document.getElementById('models-comparison-panel');
const modelsCompareBadge = document.getElementById('models-compare-badge');
const modelsCompareTbody = document.getElementById('models-compare-tbody');
const chartCompareAcc = document.getElementById('chart-compare-acc');
const chartCompareF1 = document.getElementById('chart-compare-f1');

const toastContainer = document.getElementById('toast-container');

function showToast(msg, isError = false) {
  const t = document.createElement('div');
  t.className = 'toast';
  if (isError) t.style.borderColor = 'var(--danger)';
  t.textContent = msg;
  toastContainer.appendChild(t);
  setTimeout(() => {
    t.style.opacity = '0';
    t.style.transition = 'opacity 0.25s ease';
    setTimeout(() => t.remove(), 250);
  }, 3000);
}

function escapeHtml(str) {
  if (str === null || str === undefined) return '';
  return String(str).replace(/[&<>"']/g, (m) => ({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#39;',
  }[m]));
}

// ---------------------------------------------------------------------------
// 1. Navigation & View Switching
// ---------------------------------------------------------------------------

function setupViewNavigation() {
  function switchView(target) {
    state.currentView = target;
    navBtnDashboard.classList.toggle('active', target === 'dashboard');
    navBtnDataset.classList.toggle('active', target === 'dataset');
    if (navBtnModels) navBtnModels.classList.toggle('active', target === 'models');

    viewDashboard.style.display = target === 'dashboard' ? 'flex' : 'none';
    viewDataset.style.display = target === 'dataset' ? 'flex' : 'none';
    if (viewModels) viewModels.style.display = target === 'models' ? 'flex' : 'none';

    if (target === 'dashboard') {
      renderDashboard();
      renderVisualizations();
    } else if (target === 'dataset') {
      renderMainTable();
    } else if (target === 'models') {
      onModelsViewActivated();
    }
  }

  navBtnDashboard.addEventListener('click', () => switchView('dashboard'));
  navBtnDataset.addEventListener('click', () => switchView('dataset'));
  if (navBtnModels) {
    navBtnModels.addEventListener('click', () => switchView('models'));
  }
  btnDashJumpDataset.addEventListener('click', () => switchView('dataset'));
}

// ---------------------------------------------------------------------------
// 2. Database Connection & Table Registry
// ---------------------------------------------------------------------------

async function checkDatabaseConnection() {
  try {
    const res = await fetch('/api/status');
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    state.dbConnected = true;
    state.dbInfo = data;
    return true;
  } catch (err) {
    console.warn('Database backend not available, falling back to local mode:', err.message);
    state.dbConnected = false;
    return false;
  }
}

async function loadTableList() {
  datasetSelect.innerHTML = '';

  if (state.dbConnected) {
    try {
      const res = await fetch('/api/tables');
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      state.tables = data.tables || [];

      state.tables.forEach((t) => {
        const opt = document.createElement('option');
        opt.value = t.table;
        opt.textContent = `🗄️ ${t.table} (${t.row_count.toLocaleString()} rows • ${t.col_count} cols)`;
        datasetSelect.appendChild(opt);
      });

      if (modelDatasetSelect) {
        modelDatasetSelect.innerHTML = '';
        state.tables.forEach((t) => {
          const opt = document.createElement('option');
          opt.value = t.table;
          opt.textContent = `${t.table} (${t.row_count.toLocaleString()} rows)`;
          modelDatasetSelect.appendChild(opt);
        });
      }

      if (state.tables.length > 0) {
        const initialTable = state.tables.some((t) => t.table === 'dataset') ? 'dataset' : state.tables[0].table;
        datasetSelect.value = initialTable;
        if (modelDatasetSelect) {
          modelDatasetSelect.value = initialTable;
          state.modelsState.selectedTable = initialTable;
        }
        await selectDatabaseTable(initialTable);
      }
      return;
    } catch (err) {
      console.error('Failed to load tables list from SQLite:', err);
      showToast('Failed to fetch tables from database', true);
    }
  }

  // Fallback to static registry
  EXISTING_DATASETS_REGISTRY.forEach((ds) => {
    const opt = document.createElement('option');
    opt.value = ds.id;
    opt.textContent = `${ds.name} (~${ds.rowsHint} rows)`;
    datasetSelect.appendChild(opt);
  });
  await loadFallbackDataset('dataset');
}

// ---------------------------------------------------------------------------
// 3. Fetching Table Data & Visual Cache
// ---------------------------------------------------------------------------

async function selectDatabaseTable(tableName, page = 1) {
  state.activeTable = tableName;
  state.currentPage = page;
  state.editingRowId = null;
  state.isLoading = true;

  try {
    // 1. Fetch paginated table rows for the main view
    const params = new URLSearchParams({
      page: String(state.currentPage),
      per_page: String(state.rowsPerPage),
      search: state.searchQuery || '',
    });

    const res = await fetch(`/api/tables/${encodeURIComponent(tableName)}/rows?${params}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();

    state.activeDataset = {
      name: tableName,
      headers: data.columns || [],
      rows: data.rows || [],
      totalRows: data.total,
    };

    // 2. Fetch full sample for visualizations (up to 500 rows)
    const fullRes = await fetch(`/api/tables/${encodeURIComponent(tableName)}/rows?page=1&per_page=500`);
    if (fullRes.ok) {
      const fullData = await fullRes.json();
      state.allActiveRows = fullData.rows || [];
    } else {
      state.allActiveRows = data.rows || [];
    }

    updateDatasetDimensions();
    renderDynamicManualForm();
    renderMainTable();
    renderVisualizations();
    renderDashboard();
  } catch (err) {
    console.error('Error fetching table rows:', err);
    showToast(`Failed to fetch records from table "${tableName}"`, true);
  } finally {
    state.isLoading = false;
  }
}

async function loadFallbackDataset(dsId) {
  const meta = EXISTING_DATASETS_REGISTRY.find((d) => d.id === dsId);
  if (!meta) return;

  try {
    const resp = await fetch(meta.url);
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    const text = await resp.text();
    const parsed = parseCSV(text);

    state.activeTable = null;
    state.activeDataset = {
      name: meta.name,
      headers: parsed.headers,
      rows: parsed.rows,
      totalRows: parsed.rows.length,
    };
    state.allActiveRows = parsed.rows;
    state.currentPage = 1;
    state.editingRowId = null;

    updateDatasetDimensions();
    renderDynamicManualForm();
    renderMainTable();
    renderVisualizations();
    renderDashboard();
  } catch (err) {
    console.error(err);
    showToast(`Failed to load ${meta.name}`, true);
  }
}

function updateDatasetDimensions() {
  if (!state.activeDataset) return;
  activeDatasetName.textContent = state.activeDataset.name;
  const count = state.dbConnected ? state.activeDataset.totalRows : state.activeDataset.rows.length;
  activeDatasetDim.textContent = `${count.toLocaleString()} rows × ${state.activeDataset.headers.length} columns`;
}

// ---------------------------------------------------------------------------
// 4. 📊 Dashboard Implementation
// ---------------------------------------------------------------------------

function renderDashboard() {
  const rows = state.allActiveRows || [];
  const total = rows.length;

  kpiTotalVal.textContent = (state.activeDataset.totalRows || total).toLocaleString();

  if (total === 0) {
    kpiDoqVal.textContent = '0';
    kpiDoqPct.textContent = '0% of traffic';
    kpiDoh3Val.textContent = '0';
    kpiDoh3Pct.textContent = '0% of traffic';
    kpiDohVal.textContent = '0';
    kpiDohPct.textContent = '0% of traffic';
    kpiWebVal.textContent = '0';
    kpiWebPct.textContent = '0% of traffic';
    return;
  }

  // Count classes
  let doqCount = 0;
  let doh3Count = 0;
  let dohCount = 0;
  let webCount = 0;
  let otherCount = 0;

  rows.forEach((r) => {
    const cls = String(r.traffic_class || r.traffic || r.protocol || r.label || '').toUpperCase();
    if (cls.includes('DOQ')) {
      doqCount++;
    } else if (cls.includes('DOH3') || cls.includes('HTTP3_DNS') || cls.includes('DOH-3')) {
      doh3Count++;
    } else if (cls.includes('DOH')) {
      dohCount++;
    } else if (cls.includes('WEB') || cls.includes('HTTP')) {
      webCount++;
    } else {
      otherCount++;
    }
  });

  const pct = (c) => (total > 0 ? ((c / total) * 100).toFixed(1) : '0');

  kpiDoqVal.textContent = doqCount.toLocaleString();
  kpiDoqPct.textContent = `${pct(doqCount)}% of traffic`;

  kpiDoh3Val.textContent = doh3Count.toLocaleString();
  kpiDoh3Pct.textContent = `${pct(doh3Count)}% of traffic`;

  kpiDohVal.textContent = dohCount.toLocaleString();
  kpiDohPct.textContent = `${pct(dohCount)}% of traffic`;

  kpiWebVal.textContent = webCount.toLocaleString();
  kpiWebPct.textContent = `${pct(webCount)}% of traffic`;
}

// ---------------------------------------------------------------------------
// 5. 📊 Visualization Suite (Section 4 & 10 of README)
// ---------------------------------------------------------------------------

function setupVisualizationControls() {
  filterTrafficClass.addEventListener('change', (e) => {
    state.visFilterClass = e.target.value;
    renderVisualizations();
  });

  btnResetVisFilters.addEventListener('click', () => {
    state.visFilterClass = 'ALL';
    filterTrafficClass.value = 'ALL';
    renderVisualizations();
  });
}

function getVisFilteredRows() {
  const rows = state.allActiveRows || [];
  if (state.visFilterClass === 'ALL') return rows;
  return rows.filter((r) => {
    const cls = String(r.traffic_class || r.traffic || r.protocol || '').toUpperCase();
    return cls.includes(state.visFilterClass);
  });
}

function renderVisualizations() {
  const rows = getVisFilteredRows();

  renderChart1ProtocolDist(rows);
  renderChart2PacketLengthDist(rows);
  renderChart3TimingProgression(rows);
  renderChart4DirectionDist(rows);
}

// 5.1 Protocol / Class Distribution (Bar Chart)
function renderChart1ProtocolDist(rows) {
  if (!rows || rows.length === 0) {
    chartProtocolDist.innerHTML = '<div class="chart-missing-notice">No records match the current filter.</div>';
    return;
  }

  // Count classes
  const counts = {};
  rows.forEach((r) => {
    const cls = r.traffic_class || r.traffic || r.transport_protocol || r.protocol || 'Unknown';
    counts[cls] = (counts[cls] || 0) + 1;
  });

  const entries = Object.entries(counts).sort((a, b) => b[1] - a[1]);
  if (entries.length === 0) {
    chartProtocolDist.innerHTML = '<div class="chart-missing-notice">⚠ Protocol / Class data is not available.</div>';
    return;
  }

  const maxVal = Math.max(...entries.map((e) => e[1])) || 1;
  const colors = {
    DOQ: '#06b6d4',
    DOH3: '#8b5cf6',
    DOH: '#10b981',
    HTTP3_WEB: '#f59e0b',
    HTTPS_WEB: '#3b82f6',
    QUIC: '#06b6d4',
    TCP: '#3b82f6',
  };

  const barHeight = 24;
  const gap = 12;
  const svgHeight = entries.length * (barHeight + gap) + 20;

  let barsHtml = '';
  entries.forEach(([label, count], i) => {
    const y = i * (barHeight + gap) + 10;
    const barWidth = Math.max(12, Math.round((count / maxVal) * 230));
    const color = colors[label.toUpperCase()] || '#06b6d4';
    const pct = ((count / rows.length) * 100).toFixed(1);

    barsHtml += `
      <g class="bar-group">
        <text x="10" y="${y + 16}" fill="#94a3b8" font-size="11" font-family="'JetBrains Mono', monospace">${label}</text>
        <rect x="110" y="${y}" width="${barWidth}" height="${barHeight}" rx="4" fill="${color}" opacity="0.85">
          <title>${label}: ${count} records (${pct}%)</title>
        </rect>
        <text x="${118 + barWidth}" y="${y + 16}" fill="#f1f5f9" font-size="11" font-family="'JetBrains Mono', monospace" font-weight="600">${count} (${pct}%)</text>
      </g>
    `;
  });

  chartProtocolDist.innerHTML = `
    <svg viewBox="0 0 420 ${svgHeight}" preserveAspectRatio="xMinYMin meet">
      ${barsHtml}
    </svg>
  `;
}

// 5.2 Packet Length Distribution (Histogram Bins)
function renderChart2PacketLengthDist(rows) {
  if (!rows || rows.length === 0) {
    chartLengthDist.innerHTML = '<div class="chart-missing-notice">No records match the current filter.</div>';
    return;
  }

  // Check if packet_size or length exists
  const hasLength = rows.some((r) => r.current_packet_size !== undefined || r.packet_size !== undefined || r.payload_size !== undefined || r.length !== undefined || r.len !== undefined);
  if (!hasLength) {
    chartLengthDist.innerHTML = '<div class="chart-missing-notice">⚠ Packet length data is not available in this dataset.</div>';
    return;
  }

  // 5 Bins: <200B, 200-500B, 500-1000B, 1000-1400B, >1400B
  const bins = [
    { label: '<200B', min: 0, max: 200, count: 0 },
    { label: '200-500B', min: 200, max: 500, count: 0 },
    { label: '500-1KB', min: 500, max: 1000, count: 0 },
    { label: '1K-1.4KB', min: 1000, max: 1400, count: 0 },
    { label: '>1.4KB', min: 1400, max: Infinity, count: 0 },
  ];

  rows.forEach((r) => {
    const sz = Number(r.current_packet_size ?? r.packet_size ?? r.payload_size ?? r.length ?? r.len);
    if (!isNaN(sz) && sz >= 0) {
      for (const b of bins) {
        if (sz >= b.min && sz < b.max) {
          b.count++;
          break;
        }
      }
    }
  });

  const maxCount = Math.max(...bins.map((b) => b.count)) || 1;
  const chartHeight = 120;
  const colWidth = 48;
  const gap = 16;
  const startX = 25;

  let colsHtml = '';
  bins.forEach((b, i) => {
    const x = startX + i * (colWidth + gap);
    const h = Math.max(4, Math.round((b.count / maxCount) * chartHeight));
    const y = 140 - h;
    const pct = ((b.count / rows.length) * 100).toFixed(1);

    colsHtml += `
      <g>
        <text x="${x + colWidth / 2}" y="${y - 6}" text-anchor="middle" fill="#cbd5e1" font-size="10" font-family="'JetBrains Mono', monospace" font-weight="600">${b.count}</text>
        <rect x="${x}" y="${y}" width="${colWidth}" height="${h}" rx="3" fill="#8b5cf6" opacity="0.85">
          <title>${b.label}: ${b.count} packets (${pct}%)</title>
        </rect>
        <text x="${x + colWidth / 2}" y="156" text-anchor="middle" fill="#94a3b8" font-size="10" font-family="'JetBrains Mono', monospace">${b.label}</text>
      </g>
    `;
  });

  chartLengthDist.innerHTML = `
    <svg viewBox="0 0 350 170" preserveAspectRatio="xMidYMid meet">
      <line x1="15" y1="140" x2="335" y2="140" stroke="rgba(255,255,255,0.1)" stroke-width="1" />
      ${colsHtml}
    </svg>
  `;
}

// 5.3 Packet Arrival Timing Progression (Line Chart)
function renderChart3TimingProgression(rows) {
  if (!rows || rows.length === 0) {
    chartTimingDist.innerHTML = '<div class="chart-missing-notice">No records match the current filter.</div>';
    return;
  }

  const hasTiming = rows.some((r) => r.current_time_gap !== undefined || r.timestamp !== undefined || r.relative_time !== undefined || r.iat !== undefined || r.time !== undefined);
  if (!hasTiming) {
    chartTimingDist.innerHTML = '<div class="chart-missing-notice">⚠ Packet timing data is not available in this dataset.</div>';
    return;
  }

  // Sample up to 30 points to display clean timing curve
  const validTiming = rows
    .map((r, i) => ({
      idx: i,
      t: Number(r.current_time_gap ?? r.timestamp ?? r.relative_time ?? r.iat ?? i * 0.01),
      sz: Number(r.current_packet_size ?? r.packet_size ?? r.length ?? 500),
    }))
    .filter((d) => !isNaN(d.t))
    .slice(0, 35);

  if (validTiming.length < 2) {
    chartTimingDist.innerHTML = '<div class="chart-missing-notice">Not enough timing points to draw progression.</div>';
    return;
  }

  const maxT = Math.max(...validTiming.map((d) => d.t)) || 1;
  const minT = Math.min(...validTiming.map((d) => d.t)) || 0;
  const rangeT = maxT - minT || 1;

  const w = 340;
  const h = 110;
  const padX = 25;
  const padY = 20;

  const points = validTiming.map((d, i) => {
    const x = padX + (i / (validTiming.length - 1)) * (w - 2 * padX);
    const normY = (d.t - minT) / rangeT;
    const y = h + padY - normY * h;
    return `${x.toFixed(1)},${y.toFixed(1)}`;
  });

  const pathD = `M ${points.join(' L ')}`;
  const areaD = `M ${points[0]} L ${points.join(' L ')} L ${points[points.length - 1].split(',')[0]},${h + padY} L ${points[0].split(',')[0]},${h + padY} Z`;

  chartTimingDist.innerHTML = `
    <svg viewBox="0 0 350 160" preserveAspectRatio="xMidYMid meet">
      <defs>
        <linearGradient id="timingGrad" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stop-color="#10b981" stop-opacity="0.35"/>
          <stop offset="100%" stop-color="#10b981" stop-opacity="0.0"/>
        </linearGradient>
      </defs>
      <line x1="${padX}" y1="${h + padY}" x2="${w - padX}" y2="${h + padY}" stroke="rgba(255,255,255,0.1)" />
      <path d="${areaD}" fill="url(#timingGrad)"/>
      <path d="${pathD}" fill="none" stroke="#10b981" stroke-width="2" stroke-linecap="round"/>
      <text x="${padX}" y="152" fill="#94a3b8" font-size="10" font-family="'JetBrains Mono', monospace">T0: ${minT.toFixed(3)}s</text>
      <text x="${w - padX}" y="152" text-anchor="end" fill="#94a3b8" font-size="10" font-family="'JetBrains Mono', monospace">Tend: ${maxT.toFixed(3)}s</text>
    </svg>
  `;
}

// 5.4 Direction Distribution (Forward vs Backward Ratio)
function renderChart4DirectionDist(rows) {
  if (!rows || rows.length === 0) {
    chartDirectionDist.innerHTML = '<div class="chart-missing-notice">No records match the current filter.</div>';
    return;
  }

  const hasDir = rows.some((r) => r.direction !== undefined || r.dir !== undefined);
  if (!hasDir) {
    chartDirectionDist.innerHTML = '<div class="chart-missing-notice">⚠ Direction data is not available in this dataset.</div>';
    return;
  }

  let fwd = 0;
  let bwd = 0;
  rows.forEach((r) => {
    const d = String(r.direction ?? r.dir ?? '').toUpperCase();
    if (d === 'F' || d === '→' || d.startsWith('FWD') || d === 'CLIENT') fwd++;
    else if (d === 'B' || d === '←' || d.startsWith('BWD') || d === 'SERVER') bwd++;
  });

  const totalDir = fwd + bwd;
  if (totalDir === 0) {
    chartDirectionDist.innerHTML = '<div class="chart-missing-notice">⚠ No explicit direction values found.</div>';
    return;
  }

  const fwdPct = ((fwd / totalDir) * 100).toFixed(1);
  const bwdPct = ((bwd / totalDir) * 100).toFixed(1);

  chartDirectionDist.innerHTML = `
    <div style="width: 100%; display: flex; flex-direction: column; gap: 0.9rem; padding: 0.5rem 1rem;">
      <div style="display: flex; justify-content: space-between; font-size: 0.78rem;">
        <span style="color: #67e8f9; font-weight: 600;">Forward (→ Client)</span>
        <span style="color: #fcd34d; font-weight: 600;">Backward (← Server)</span>
      </div>

      <div style="height: 24px; display: flex; border-radius: 999px; overflow: hidden; background: rgba(0,0,0,0.3); border: 1px solid var(--border); padding: 2px;">
        <div style="width: ${fwdPct}%; background: #06b6d4; height: 100%; border-radius: 999px 0 0 999px;" title="Forward: ${fwd} (${fwdPct}%)"></div>
        <div style="width: ${bwdPct}%; background: #f59e0b; height: 100%; border-radius: 0 999px 999px 0;" title="Backward: ${bwd} (${bwdPct}%)"></div>
      </div>

      <div style="display: flex; justify-content: space-between; font-family: var(--font-mono); font-size: 0.85rem;">
        <span style="color: #fff; font-weight: 700;">${fwd} packets <span style="font-size: 0.72rem; color: #67e8f9;">(${fwdPct}%)</span></span>
        <span style="color: #fff; font-weight: 700;">${bwd} packets <span style="font-size: 0.72rem; color: #fcd34d;">(${bwdPct}%)</span></span>
      </div>
    </div>
  `;
}

// ---------------------------------------------------------------------------
// 6. Main Dataset Table View & Spreadsheet Actions
// ---------------------------------------------------------------------------

function renderMainTable() {
  const { headers, rows, totalRows } = state.activeDataset;

  // Thead
  mainTableThead.innerHTML = '';
  const hTr = document.createElement('tr');
  const thIdx = document.createElement('th');
  thIdx.style.width = '42px';
  thIdx.textContent = '#';
  hTr.appendChild(thIdx);

  headers.forEach((h) => {
    const th = document.createElement('th');
    th.textContent = h;
    hTr.appendChild(th);
  });

  const thActions = document.createElement('th');
  thActions.style.width = '75px';
  thActions.style.textAlign = 'right';
  thActions.textContent = 'Actions';
  hTr.appendChild(thActions);

  mainTableThead.appendChild(hTr);

  // Pagination calculation
  const total = state.dbConnected ? totalRows : getLocalFilteredRows().length;
  const page = state.currentPage;
  const perPage = state.rowsPerPage;
  const start = total === 0 ? 0 : (page - 1) * perPage + 1;
  const end = Math.min(page * perPage, total);

  paginationInfo.textContent = total > 0 ? `${start}–${end} of ${total.toLocaleString()}` : '0 of 0';
  btnPrevPage.disabled = page <= 1;
  btnNextPage.disabled = end >= total;

  // Tbody
  mainTableTbody.innerHTML = '';
  const displayRows = state.dbConnected ? rows : getLocalPaginatedRows();

  if (displayRows.length === 0) {
    mainTableTbody.innerHTML = `<tr><td colspan="${headers.length + 2}" style="text-align:center; color: var(--text-dim); padding: 3rem;">No records found. Click "+ Add Row Directly" to add a new record.</td></tr>`;
    return;
  }

  displayRows.forEach((r, idx) => {
    const rowId = r._rowid_ !== undefined ? r._rowid_ : idx;
    const isEditing = state.editingRowId === rowId;

    const tr = document.createElement('tr');
    if (isEditing) tr.className = 'editing-row';

    const tdIdx = document.createElement('td');
    tdIdx.style.color = 'var(--text-dim)';
    tdIdx.textContent = start + idx;
    tr.appendChild(tdIdx);

    headers.forEach((h) => {
      const td = document.createElement('td');
      const val = r[h];

      if (isEditing) {
        td.innerHTML = `<input type="text" class="edit-cell-input" data-col="${h}" value="${val !== undefined && val !== null ? String(val) : ''}" />`;
      } else {
        if (h.toLowerCase() === 'direction' || h.toLowerCase() === 'dir') {
          const isF = String(val).toUpperCase() === 'F' || val === '→';
          td.innerHTML = `<span class="pill-dir ${isF ? 'pill-fwd' : 'pill-bwd'}">${isF ? '→' : '←'}</span>`;
        } else {
          td.textContent = val !== undefined && val !== null && val !== '' ? val : '—';
        }
      }
      tr.appendChild(td);
    });

    const tdAct = document.createElement('td');
    tdAct.style.textAlign = 'right';

    if (isEditing) {
      tdAct.innerHTML = `
        <div class="row-actions">
          <button class="btn-action save btn-save-edit" data-rowid="${rowId}" data-idx="${idx}" title="Save to Database">✓</button>
          <button class="btn-action btn-cancel-edit" title="Cancel">✕</button>
        </div>
      `;
    } else {
      tdAct.innerHTML = `
        <div class="row-actions">
          <button class="btn-action btn-edit-row" data-rowid="${rowId}" data-idx="${idx}" title="Edit in SQLite">✏️</button>
          <button class="btn-action del btn-del-row" data-rowid="${rowId}" data-idx="${idx}" title="Delete from SQLite">✕</button>
        </div>
      `;
    }
    tr.appendChild(tdAct);
    mainTableTbody.appendChild(tr);
  });

  attachRowActionListeners();
}

function getLocalFilteredRows() {
  const rows = state.activeDataset.rows || [];
  const q = state.searchQuery.toLowerCase().trim();
  if (!q) return rows;
  return rows.filter((r) => Object.values(r).some((v) => String(v).toLowerCase().includes(q)));
}

function getLocalPaginatedRows() {
  const filtered = getLocalFilteredRows();
  const start = (state.currentPage - 1) * state.rowsPerPage;
  return filtered.slice(start, start + state.rowsPerPage);
}

// ---------------------------------------------------------------------------
// 7. Inline CRUD Handlers (Edit, Save, Delete)
// ---------------------------------------------------------------------------

function attachRowActionListeners() {
  mainTableTbody.querySelectorAll('.btn-edit-row').forEach((btn) => {
    btn.addEventListener('click', (e) => {
      const rowId = e.currentTarget.dataset.rowid;
      state.editingRowId = isNaN(rowId) ? rowId : Number(rowId);
      renderMainTable();
    });
  });

  mainTableTbody.querySelectorAll('.btn-cancel-edit').forEach((btn) => {
    btn.addEventListener('click', () => {
      state.editingRowId = null;
      renderMainTable();
    });
  });

  mainTableTbody.querySelectorAll('.btn-save-edit').forEach((btn) => {
    btn.addEventListener('click', async (e) => {
      const rowId = e.currentTarget.dataset.rowid;
      const idx = Number(e.currentTarget.dataset.idx);
      const tr = e.currentTarget.closest('tr');
      const inputs = tr.querySelectorAll('.edit-cell-input');

      const updatedPayload = {};
      inputs.forEach((inp) => {
        const col = inp.dataset.col;
        let val = inp.value.trim();
        if (val !== '' && !isNaN(val)) val = Number(val);
        updatedPayload[col] = val !== '' ? val : null;
      });

      if (state.dbConnected && state.activeTable) {
        try {
          const res = await fetch(`/api/tables/${encodeURIComponent(state.activeTable)}/rows/${rowId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(updatedPayload),
          });
          if (!res.ok) {
            const errJson = await res.json().catch(() => ({}));
            throw new Error(errJson.detail || `HTTP ${res.status}`);
          }
          showToast(`Row #${rowId} updated in SQLite database`);
          state.editingRowId = null;
          await selectDatabaseTable(state.activeTable, state.currentPage);
          return;
        } catch (err) {
          console.error('Failed to update SQLite row:', err);
          showToast(`Failed to update in database: ${err.message}`, true);
          return;
        }
      }

      Object.assign(state.activeDataset.rows[idx], updatedPayload);
      state.editingRowId = null;
      renderMainTable();
      renderVisualizations();
      renderDashboard();
      showToast('Row updated (local in-memory)');
    });
  });

  mainTableTbody.querySelectorAll('.btn-del-row').forEach((btn) => {
    btn.addEventListener('click', async (e) => {
      const rowId = e.currentTarget.dataset.rowid;
      const idx = Number(e.currentTarget.dataset.idx);

      if (state.dbConnected && state.activeTable) {
        try {
          const res = await fetch(`/api/tables/${encodeURIComponent(state.activeTable)}/rows/${rowId}`, {
            method: 'DELETE',
          });
          if (!res.ok) {
            const errJson = await res.json().catch(() => ({}));
            throw new Error(errJson.detail || `HTTP ${res.status}`);
          }
          showToast(`Row #${rowId} permanently deleted from SQLite database`);
          state.editingRowId = null;
          await checkDatabaseConnection();
          await selectDatabaseTable(state.activeTable, state.currentPage);
          return;
        } catch (err) {
          console.error('Failed to delete SQLite row:', err);
          showToast(`Failed to delete row: ${err.message}`, true);
          return;
        }
      }

      state.activeDataset.rows.splice(idx, 1);
      state.activeDataset.totalRows = state.activeDataset.rows.length;
      updateDatasetDimensions();
      renderMainTable();
      renderVisualizations();
      renderDashboard();
      showToast('Row deleted');
    });
  });
}

// ---------------------------------------------------------------------------
// 8. Dynamic Manual Entry Forms & Direct Database Insertion
// ---------------------------------------------------------------------------

function renderDynamicManualForm() {
  if (!state.activeDataset) return;
  const { headers, name } = state.activeDataset;

  manualFileTargetDesc.textContent = `Insert a new row into SQLite table "${name}":`;
  dynamicManualFields.innerHTML = '';
  inlineFieldsGrid.innerHTML = '';

  headers.forEach((h) => {
    // Form in Tab 2
    const group = document.createElement('div');
    group.className = 'entry-field-group';
    group.innerHTML = `
      <label class="entry-label" title="${h}">${h}</label>
      <input type="text" class="entry-input tab-manual-input" data-col="${h}" placeholder="${getPlaceholder(h)}" />
    `;
    dynamicManualFields.appendChild(group);

    // Inline Drawer above Table
    const inlineGroup = document.createElement('div');
    inlineGroup.className = 'entry-field-group';
    inlineGroup.innerHTML = `
      <label class="entry-label" title="${h}">${h}</label>
      <input type="text" class="entry-input inline-manual-input" data-col="${h}" placeholder="${getPlaceholder(h)}" />
    `;
    inlineFieldsGrid.appendChild(inlineGroup);
  });
}

function getPlaceholder(colName) {
  const c = colName.toLowerCase();
  if (c.includes('flow_id')) return 'flow_doq_001';
  if (c.includes('capture_id')) return 'cap_doq_001';
  if (c.includes('traffic_class')) return 'DOQ';
  if (c.includes('proto')) return 'QUIC';
  if (c.includes('ip')) return '192.168.1.100';
  if (c.includes('port')) return '853';
  if (c.includes('time')) return '0.015';
  if (c.includes('len') || c.includes('size') || c.includes('bytes')) return '1250';
  if (c.includes('dir')) return 'F';
  if (c.includes('label')) return '3';
  if (c.includes('rate')) return '24.5';
  return 'value';
}

async function insertRowIntoActiveDataset(rowPayload) {
  if (state.dbConnected && state.activeTable) {
    try {
      const res = await fetch(`/api/tables/${encodeURIComponent(state.activeTable)}/rows`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(rowPayload),
      });
      if (!res.ok) {
        const errJson = await res.json().catch(() => ({}));
        throw new Error(errJson.detail || `HTTP ${res.status}`);
      }
      const data = await res.json();
      const newRowId = data.row ? data.row._rowid_ : 'new';
      showToast(`Inserted row #${newRowId} directly into SQLite table "${state.activeTable}"`);

      await checkDatabaseConnection();
      const newTotal = state.activeDataset.totalRows + 1;
      const lastPage = Math.ceil(newTotal / state.rowsPerPage);
      await selectDatabaseTable(state.activeTable, lastPage);
      return true;
    } catch (err) {
      console.error('Failed to insert into SQLite database:', err);
      showToast(`Database insert error: ${err.message}`, true);
      return false;
    }
  }

  state.activeDataset.rows.push(rowPayload);
  state.activeDataset.totalRows = state.activeDataset.rows.length;
  state.allActiveRows.push(rowPayload);
  state.currentPage = Math.ceil(state.activeDataset.rows.length / state.rowsPerPage);
  updateDatasetDimensions();
  renderMainTable();
  renderVisualizations();
  renderDashboard();
  showToast(`Added row #${state.activeDataset.rows.length} (local in-memory)`);
  return true;
}

function setupManualEntryHandlers() {
  btnSubmitManualRow.addEventListener('click', async () => {
    if (!state.activeDataset) return;
    const inputs = dynamicManualFields.querySelectorAll('.tab-manual-input');
    const newRow = {};
    let hasAnyVal = false;

    inputs.forEach((inp) => {
      const col = inp.dataset.col;
      let val = inp.value.trim();
      if (val !== '') hasAnyVal = true;
      if (val !== '' && !isNaN(val)) val = Number(val);
      newRow[col] = val !== '' ? val : null;
    });

    if (!hasAnyVal) {
      showToast('Please enter at least one field value', true);
      return;
    }

    const ok = await insertRowIntoActiveDataset(newRow);
    if (ok) {
      inputs.forEach((inp) => (inp.value = ''));
    }
  });

  btnResetManualForm.addEventListener('click', () => {
    dynamicManualFields.querySelectorAll('.tab-manual-input').forEach((i) => (i.value = ''));
  });

  btnToggleInlineAdd.addEventListener('click', () => {
    const isHidden = inlineAddDrawer.style.display === 'none';
    inlineAddDrawer.style.display = isHidden ? 'block' : 'none';
    btnToggleInlineAdd.textContent = isHidden ? '✕ Close Form' : '+ Add Row Directly';
  });

  btnCancelInlineRow.addEventListener('click', () => {
    inlineAddDrawer.style.display = 'none';
    btnToggleInlineAdd.textContent = '+ Add Row Directly';
  });

  btnSaveInlineRow.addEventListener('click', async () => {
    if (!state.activeDataset) return;
    const inputs = inlineFieldsGrid.querySelectorAll('.inline-manual-input');
    const newRow = {};
    let hasAnyVal = false;

    inputs.forEach((inp) => {
      const col = inp.dataset.col;
      let val = inp.value.trim();
      if (val !== '') hasAnyVal = true;
      if (val !== '' && !isNaN(val)) val = Number(val);
      newRow[col] = val !== '' ? val : null;
    });

    if (!hasAnyVal) {
      showToast('Please enter at least one field value', true);
      return;
    }

    const ok = await insertRowIntoActiveDataset(newRow);
    if (ok) {
      inputs.forEach((inp) => (inp.value = ''));
      inlineAddDrawer.style.display = 'none';
      btnToggleInlineAdd.textContent = '+ Add Row Directly';
    }
  });
}

// ---------------------------------------------------------------------------
// 9. CSV Upload & Database Persistence
// ---------------------------------------------------------------------------

function setupUpload() {
  btnBrowse.addEventListener('click', (e) => {
    e.stopPropagation();
    fileInput.click();
  });

  dropzone.addEventListener('click', () => fileInput.click());

  dropzone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropzone.classList.add('dragover');
  });

  dropzone.addEventListener('dragleave', () => dropzone.classList.remove('dragover'));

  dropzone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropzone.classList.remove('dragover');
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFile(e.dataTransfer.files[0]);
    }
  });

  fileInput.addEventListener('change', (e) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFile(e.target.files[0]);
    }
  });

  btnSaveToDb.addEventListener('click', async () => {
    if (!state.uploadedFile) return;

    if (!state.dbConnected) {
      showToast('Database backend is offline. Previewing in local memory.', true);
      previewUploadedFileLocally();
      return;
    }

    try {
      showToast(`Uploading and storing "${state.uploadedFile.name}" in SQLite...`);
      const formData = new FormData();
      formData.append('file', state.uploadedFile);

      const res = await fetch('/api/tables/upload', {
        method: 'POST',
        body: formData,
      });

      if (!res.ok) {
        const errJson = await res.json().catch(() => ({}));
        throw new Error(errJson.detail || `HTTP ${res.status}`);
      }

      const data = await res.json();
      showToast(`Stored ${data.rows_inserted.toLocaleString()} rows in SQLite table "${data.table}"!`);

      await checkDatabaseConnection();
      await loadTableList();
      datasetSelect.value = data.table;
      await selectDatabaseTable(data.table, 1);
    } catch (err) {
      console.error('Failed to store CSV into SQLite:', err);
      showToast(`Upload failed: ${err.message}`, true);
    }
  });

  btnViewUploaded.addEventListener('click', () => {
    previewUploadedFileLocally();
  });
}

function handleFile(file) {
  if (!file.name.endsWith('.csv')) {
    showToast('Please upload a .csv file', true);
    return;
  }

  state.uploadedFile = file;

  const reader = new FileReader();
  reader.onload = (e) => {
    try {
      const parsed = parseCSV(e.target.result);
      if (parsed.headers.length === 0) {
        showToast('CSV file is empty', true);
        return;
      }
      const stats = computeDatasetStats(parsed.rows, parsed.headers);

      tagFilename.textContent = file.name;
      tagRows.textContent = `${stats.rowCount.toLocaleString()} rows`;
      tagCols.textContent = `${stats.colCount} cols`;
      tagMissing.textContent = `${stats.missingCount} missing`;
      uploadInfoBox.style.display = 'flex';

      showToast(`Loaded ${file.name} (${stats.rowCount.toLocaleString()} rows)`);
    } catch (err) {
      console.error(err);
      showToast('Failed to parse CSV preview', true);
    }
  };
  reader.readAsText(file);
}

function previewUploadedFileLocally() {
  if (!state.uploadedFile) return;

  const reader = new FileReader();
  reader.onload = (e) => {
    const parsed = parseCSV(e.target.result);
    state.activeTable = null;
    state.activeDataset = {
      name: state.uploadedFile.name,
      headers: parsed.headers,
      rows: parsed.rows,
      totalRows: parsed.rows.length,
    };
    state.allActiveRows = parsed.rows;
    state.currentPage = 1;
    state.editingRowId = null;

    updateDatasetDimensions();
    renderDynamicManualForm();
    renderMainTable();
    renderVisualizations();
    renderDashboard();
    showToast(`Displaying ${state.uploadedFile.name} preview`);
  };
  reader.readAsText(state.uploadedFile);
}

// ---------------------------------------------------------------------------
// 10. Table Controls (Search, Pagination, Export)
// ---------------------------------------------------------------------------

let searchDebounce = null;

function setupTableControls() {
  datasetSelect.addEventListener('change', async (e) => {
    const val = e.target.value;
    if (state.dbConnected) {
      await selectDatabaseTable(val, 1);
    } else {
      await loadFallbackDataset(val);
    }
  });

  tableSearchInput.addEventListener('input', (e) => {
    clearTimeout(searchDebounce);
    state.searchQuery = e.target.value;
    searchDebounce = setTimeout(async () => {
      state.currentPage = 1;
      if (state.dbConnected && state.activeTable) {
        await selectDatabaseTable(state.activeTable, 1);
      } else {
        renderMainTable();
      }
    }, 200);
  });

  btnPrevPage.addEventListener('click', async () => {
    if (state.currentPage > 1) {
      state.currentPage--;
      if (state.dbConnected && state.activeTable) {
        await selectDatabaseTable(state.activeTable, state.currentPage);
      } else {
        renderMainTable();
      }
    }
  });

  btnNextPage.addEventListener('click', async () => {
    const total = state.dbConnected ? state.activeDataset.totalRows : getLocalFilteredRows().length;
    if (state.currentPage * state.rowsPerPage < total) {
      state.currentPage++;
      if (state.dbConnected && state.activeTable) {
        await selectDatabaseTable(state.activeTable, state.currentPage);
      } else {
        renderMainTable();
      }
    }
  });

  if (btnExportCsv) {
    btnExportCsv.addEventListener('click', () => {
      if (state.dbConnected && state.activeTable) {
        window.location.href = `/api/tables/${encodeURIComponent(state.activeTable)}/export`;
        showToast(`Exporting "${state.activeTable}" from SQLite database...`);
        return;
      }

      if (!state.activeDataset || !state.activeDataset.rows.length) return;
      const csv = toCSV(state.activeDataset.rows, state.activeDataset.headers);
      const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = state.activeDataset.name.endsWith('.csv') ? state.activeDataset.name : `${state.activeDataset.name}.csv`;
      a.click();
      URL.revokeObjectURL(url);
      showToast(`Exported ${state.activeDataset.name}`);
    });
  }
}

function setupTabs() {
  tabBtns.forEach((btn) => {
    btn.addEventListener('click', () => {
      tabBtns.forEach((b) => b.classList.remove('active'));
      btn.classList.add('active');
      const target = btn.dataset.tab;
      if (target === 'upload') {
        tabUpload.classList.add('active');
        tabManual.classList.remove('active');
      } else {
        tabManual.classList.add('active');
        tabUpload.classList.remove('active');
      }
    });
  });
}

// ---------------------------------------------------------------------------
// 11. Machine Learning Models & 3-Phase Pipeline Suite (RF & XGBoost)
// ---------------------------------------------------------------------------

function setupModelsSection() {
  // Model selection cards click & radio changes
  if (modelCardRF) {
    modelCardRF.addEventListener('click', () => selectModel('Random Forest'));
  }
  if (modelCardXGB) {
    modelCardXGB.addEventListener('click', () => selectModel('XGBoost'));
  }

  const modelRadios = document.querySelectorAll('input[name="model_choice"]');
  modelRadios.forEach((radio) => {
    radio.addEventListener('change', (e) => {
      if (e.target.checked) {
        selectModel(e.target.value);
      }
    });
  });

  // Feature dataset select
  if (modelDatasetSelect) {
    modelDatasetSelect.addEventListener('change', (e) => {
      state.modelsState.selectedTable = e.target.value;
      resetPipeline();
      if (modelsExecStatus) {
        modelsExecStatus.textContent = `Selected dataset: ${e.target.value}. Pipeline reset.`;
      }
    });
  }

  // Pipeline phase buttons
  if (btnPipelineTrain) {
    btnPipelineTrain.addEventListener('click', () => runPipelinePhase('train'));
  }
  if (btnPipelineValidate) {
    btnPipelineValidate.addEventListener('click', () => runPipelinePhase('validate'));
  }
  if (btnPipelineTest) {
    btnPipelineTest.addEventListener('click', () => runPipelinePhase('test'));
  }

  // Head-to-head comparison button
  if (btnRunCompareModels) {
    btnRunCompareModels.addEventListener('click', () => runCompareModels());
  }

  updatePipelineStepperUI();
}

function selectModel(modelName) {
  state.modelsState.selectedModel = modelName;
  if (modelCardRF) {
    modelCardRF.classList.toggle('active', modelName === 'Random Forest');
    const radioRF = document.getElementById('radio-rf');
    if (radioRF) radioRF.checked = modelName === 'Random Forest';
  }
  if (modelCardXGB) {
    modelCardXGB.classList.toggle('active', modelName === 'XGBoost');
    const radioXGB = document.getElementById('radio-xgb');
    if (radioXGB) radioXGB.checked = modelName === 'XGBoost';
  }
  resetPipeline();
  if (modelsExecStatus) {
    modelsExecStatus.textContent = `Selected model: ${modelName}. Ready to train.`;
  }
  showToast(`Selected ${modelName}`);
}

function resetPipeline() {
  state.modelsState.currentPhase = 'idle';
  state.modelsState.trainResult = null;
  state.modelsState.validateResult = null;
  state.modelsState.testResult = null;

  // Reset badges & cards
  ['train', 'validate', 'test'].forEach((p) => {
    const badge = document.getElementById(`phase-badge-${p}`);
    if (badge) {
      badge.textContent = 'Pending';
      badge.className = 'phase-card-badge phase-pending';
    }
    const metricsRow = document.getElementById(`phase-metrics-${p}`);
    if (metricsRow) {
      metricsRow.innerHTML = `
        <div class="phase-metric"><span class="pm-val">—</span><span class="pm-label">Accuracy</span></div>
        <div class="phase-metric"><span class="pm-val">—</span><span class="pm-label">Precision</span></div>
        <div class="phase-metric"><span class="pm-val">—</span><span class="pm-label">Recall</span></div>
        <div class="phase-metric"><span class="pm-val">—</span><span class="pm-label">F1-Score</span></div>
      `;
    }
    const card = document.getElementById(`phase-card-${p}`);
    if (card) card.classList.remove('phase-active', 'phase-completed');
  });

  if (cmModelName) cmModelName.textContent = '—';
  if (confusionMatrixWrapper) {
    confusionMatrixWrapper.innerHTML = '<div class="chart-missing-notice">Run the pipeline to see the confusion matrix.</div>';
  }
  if (featureImportanceWrapper) {
    featureImportanceWrapper.innerHTML = '<div class="chart-missing-notice">Train a model to see feature importances.</div>';
  }

  updatePipelineStepperUI();
}

function updatePipelineStepperUI() {
  const phase = state.modelsState.currentPhase; // 'idle' | 'trained' | 'validated' | 'tested'
  const isTraining = state.modelsState.isTraining;

  // Train Step
  if (pipelineStepTrain && stepStatusTrain && btnPipelineTrain) {
    if (phase === 'idle') {
      pipelineStepTrain.className = 'pipeline-step active';
      stepStatusTrain.textContent = 'Ready';
      btnPipelineTrain.disabled = isTraining;
      btnPipelineTrain.className = 'btn btn-primary btn-sm';
      btnPipelineTrain.textContent = '▶ Train Model';
    } else {
      pipelineStepTrain.className = 'pipeline-step completed';
      stepStatusTrain.textContent = 'Completed ✓';
      btnPipelineTrain.disabled = isTraining;
      btnPipelineTrain.className = 'btn btn-secondary btn-sm';
      btnPipelineTrain.textContent = '↺ Re-train';
    }
  }

  // Validate Step
  if (pipelineStepValidate && stepStatusValidate && btnPipelineValidate) {
    if (phase === 'idle') {
      pipelineStepValidate.className = 'pipeline-step locked';
      stepStatusValidate.textContent = 'Locked';
      btnPipelineValidate.disabled = true;
      btnPipelineValidate.className = 'btn btn-secondary btn-sm';
      btnPipelineValidate.textContent = '▶ Validate Model';
    } else if (phase === 'trained') {
      pipelineStepValidate.className = 'pipeline-step active';
      stepStatusValidate.textContent = 'Ready';
      btnPipelineValidate.disabled = isTraining;
      btnPipelineValidate.className = 'btn btn-primary btn-sm';
      btnPipelineValidate.textContent = '▶ Validate Model';
    } else {
      pipelineStepValidate.className = 'pipeline-step completed';
      stepStatusValidate.textContent = 'Completed ✓';
      btnPipelineValidate.disabled = isTraining;
      btnPipelineValidate.className = 'btn btn-secondary btn-sm';
      btnPipelineValidate.textContent = '↺ Re-validate';
    }
  }

  // Test Step
  if (pipelineStepTest && stepStatusTest && btnPipelineTest) {
    if (phase === 'idle' || phase === 'trained') {
      pipelineStepTest.className = 'pipeline-step locked';
      stepStatusTest.textContent = 'Locked';
      btnPipelineTest.disabled = true;
      btnPipelineTest.className = 'btn btn-secondary btn-sm';
      btnPipelineTest.textContent = '▶ Test Model';
    } else if (phase === 'validated') {
      pipelineStepTest.className = 'pipeline-step active';
      stepStatusTest.textContent = 'Ready';
      btnPipelineTest.disabled = isTraining;
      btnPipelineTest.className = 'btn btn-primary btn-sm';
      btnPipelineTest.textContent = '▶ Test Model';
    } else {
      pipelineStepTest.className = 'pipeline-step completed';
      stepStatusTest.textContent = 'Completed ✓';
      btnPipelineTest.disabled = isTraining;
      btnPipelineTest.className = 'btn btn-secondary btn-sm';
      btnPipelineTest.textContent = '↺ Re-test';
    }
  }
}

function onModelsViewActivated() {
  if (state.modelsState.currentPhase === 'idle' && !state.modelsState.isTraining && !state.modelsState.trainResult) {
    if (modelsExecStatus) {
      modelsExecStatus.textContent = 'Ready: Click "Train Model" to start Phase 1';
    }
  }
}

function setPipelineBusy(isBusy, text = 'Processing pipeline...') {
  state.modelsState.isTraining = isBusy;
  if (trainingProgressBox) {
    trainingProgressBox.style.display = isBusy ? 'flex' : 'none';
  }
  if (trainingProgressText) {
    trainingProgressText.textContent = text;
  }
  if (btnPipelineTrain) btnPipelineTrain.disabled = isBusy;
  if (btnPipelineValidate) btnPipelineValidate.disabled = isBusy;
  if (btnPipelineTest) btnPipelineTest.disabled = isBusy;
  if (btnRunCompareModels) btnRunCompareModels.disabled = isBusy;
  updatePipelineStepperUI();
}

async function runPipelinePhase(phase) {
  if (state.modelsState.isTraining) return;

  const modelName = state.modelsState.selectedModel || 'Random Forest';
  const tableName = state.modelsState.selectedTable || 'dataset';
  const phaseLabel = phase === 'train' ? 'Training' : phase === 'validate' ? 'Validation' : 'Testing';

  setPipelineBusy(true, `Running ${phaseLabel} for ${modelName} on ${tableName}...`);

  try {
    const res = await fetch('/api/models/pipeline', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model_name: modelName,
        phase: phase,
        table_name: tableName,
      }),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: `HTTP ${res.status}` }));
      throw new Error(err.detail || `Server returned ${res.status}`);
    }

    const data = await res.json();

    // Advance phase state
    if (phase === 'train') {
      state.modelsState.trainResult = data;
      if (state.modelsState.currentPhase === 'idle') {
        state.modelsState.currentPhase = 'trained';
      }
    } else if (phase === 'validate') {
      state.modelsState.validateResult = data;
      if (state.modelsState.currentPhase === 'trained') {
        state.modelsState.currentPhase = 'validated';
      }
    } else if (phase === 'test') {
      state.modelsState.testResult = data;
      state.modelsState.currentPhase = 'tested';
    }

    // Render phase card
    renderPhaseResultCard(phase, data);

    // Render diagnostics
    if (cmModelName) {
      cmModelName.textContent = `${data.model_name} (${phaseLabel})`;
    }
    renderConfusionMatrix(data.confusion_matrix, data.classes);
    renderFeatureImportances(data.feature_importances, data.model_name);

    const m = data.metrics || {};
    const accPct = ((m.accuracy || 0) * 100).toFixed(1);
    const f1Pct = ((m.f1_score || 0) * 100).toFixed(1);

    if (modelsExecStatus) {
      const splitSrc = data.used_splits_tables ? 'splits tables' : 'dynamic split';
      modelsExecStatus.textContent = `✓ ${modelName} [${phaseLabel}]: Acc ${accPct}%, F1 ${f1Pct}% (${splitSrc})`;
    }
    showToast(`✓ ${phaseLabel} complete: ${accPct}% Accuracy`);
  } catch (err) {
    console.error(`Failed to run ${phase} phase:`, err);
    showToast(`Error in ${phase}: ${err.message}`, true);
    if (modelsExecStatus) {
      modelsExecStatus.textContent = `Error in ${phase}: ${err.message}`;
    }
  } finally {
    setPipelineBusy(false);
  }
}

function renderPhaseResultCard(phase, data) {
  const card = document.getElementById(`phase-card-${phase}`);
  const badge = document.getElementById(`phase-badge-${phase}`);
  const metricsRow = document.getElementById(`phase-metrics-${phase}`);

  if (card) {
    card.classList.remove('phase-active');
    card.classList.add('phase-completed');
  }

  const m = data.metrics || {};
  const acc = ((m.accuracy ?? 0) * 100).toFixed(1);
  const prec = ((m.precision ?? 0) * 100).toFixed(1);
  const rec = ((m.recall ?? 0) * 100).toFixed(1);
  const f1 = ((m.f1_score ?? 0) * 100).toFixed(1);

  if (badge) {
    badge.textContent = `${acc}% Acc`;
    badge.className = 'phase-card-badge phase-done';
  }

  if (metricsRow) {
    metricsRow.innerHTML = `
      <div class="phase-metric"><span class="pm-val">${acc}%</span><span class="pm-label">Accuracy</span></div>
      <div class="phase-metric"><span class="pm-val">${prec}%</span><span class="pm-label">Precision</span></div>
      <div class="phase-metric"><span class="pm-val">${rec}%</span><span class="pm-label">Recall</span></div>
      <div class="phase-metric"><span class="pm-val" style="color: #22d3ee;">${f1}%</span><span class="pm-label">F1-Score</span></div>
    `;
  }
}

async function runCompareModels() {
  if (state.modelsState.isTraining) return;

  const tableName = state.modelsState.selectedTable || 'dataset';

  setPipelineBusy(true, `Comparing Random Forest vs XGBoost on ${tableName}...`);

  try {
    const res = await fetch('/api/models/compare', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        table_name: tableName,
        models: ['Random Forest', 'XGBoost'],
        test_size: 0.3,
      }),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: `HTTP ${res.status}` }));
      throw new Error(err.detail || `Server returned ${res.status}`);
    }

    const data = await res.json();
    state.modelsState.lastCompareResult = data;

    if (modelsComparisonPanel) {
      modelsComparisonPanel.style.display = 'block';
    }

    renderComparisonResults(data);

    if (modelsExecStatus) {
      modelsExecStatus.textContent = `✓ Head-to-head comparison complete for Random Forest vs XGBoost`;
    }
    showToast(`✓ Model comparison completed`);
  } catch (err) {
    console.error('Failed to compare models:', err);
    showToast(`Comparison error: ${err.message}`, true);
    if (modelsExecStatus) {
      modelsExecStatus.textContent = `Comparison error: ${err.message}`;
    }
  } finally {
    setPipelineBusy(false);
  }
}

function renderComparisonResults(compareData) {
  if (!compareData || !compareData.results || compareData.results.length === 0) {
    return;
  }

  // Sort by F1 descending, then accuracy
  const sorted = [...compareData.results].sort((a, b) => {
    const f1A = a.metrics ? a.metrics.f1_score : -1;
    const f1B = b.metrics ? b.metrics.f1_score : -1;
    if (f1B !== f1A) return f1B - f1A;
    return (b.metrics?.accuracy || 0) - (a.metrics?.accuracy || 0);
  });

  if (modelsCompareBadge) {
    modelsCompareBadge.textContent = `${sorted.length} Models Evaluated`;
  }

  // Populate comparison table
  if (modelsCompareTbody) {
    let tbodyHtml = '';
    sorted.forEach((item, idx) => {
      const rank = idx + 1;
      const rankBadgeClass = rank === 1 ? 'rank-1' : 'rank-2';
      const rankIcon = rank === 1 ? '🥇' : '🥈';

      const m = item.metrics;
      const accStr = m ? `${(m.accuracy * 100).toFixed(1)}%` : '—';
      const precStr = m ? `${(m.precision * 100).toFixed(1)}%` : '—';
      const recStr = m ? `${(m.recall * 100).toFixed(1)}%` : '—';
      const f1Str = m ? `${(m.f1_score * 100).toFixed(1)}%` : '—';
      const timeStr = m ? `${m.train_time_ms.toFixed(1)} ms` : '—';

      tbodyHtml += `
        <tr style="cursor: pointer;" title="Click to inspect this model's diagnostics" data-model-name="${escapeHtml(item.model_name)}">
          <td><span class="rank-badge ${rankBadgeClass}">${rankIcon}</span></td>
          <td><strong>${escapeHtml(item.model_name)}</strong></td>
          <td style="text-align: right; font-weight: 600; color: #fff;">${accStr}</td>
          <td style="text-align: right; color: #cbd5e1;">${precStr}</td>
          <td style="text-align: right; color: #cbd5e1;">${recStr}</td>
          <td style="text-align: right; font-weight: 700; color: #22d3ee;">${f1Str}</td>
          <td style="text-align: right; font-family: var(--font-mono); color: var(--text-dim);">${timeStr}</td>
        </tr>
      `;
    });
    modelsCompareTbody.innerHTML = tbodyHtml;

    // Attach row click listeners to inspect that model
    const rows = modelsCompareTbody.querySelectorAll('tr');
    rows.forEach((tr) => {
      tr.addEventListener('click', () => {
        const mName = tr.getAttribute('data-model-name');
        const found = sorted.find((s) => s.model_name === mName);
        if (found && !found.error) {
          if (cmModelName) cmModelName.textContent = `${found.model_name} (Comparison)`;
          renderConfusionMatrix(found.confusion_matrix, found.classes);
          renderFeatureImportances(found.feature_importances, found.model_name);
          showToast(`Inspecting diagnostics for ${found.model_name}`);
        }
      });
    });
  }

  // Render SVG Comparison Bar Charts
  renderSvgMetricComparisonChart(chartCompareAcc, sorted, 'accuracy', 'Accuracy');
  renderSvgMetricComparisonChart(chartCompareF1, sorted, 'f1_score', 'F1-Score');
}

function renderConfusionMatrix(cm, fallbackClasses = []) {
  if (!confusionMatrixWrapper) return;

  let matrix = null;
  let classes = fallbackClasses || [];

  if (Array.isArray(cm)) {
    matrix = cm;
  } else if (cm && Array.isArray(cm.matrix)) {
    matrix = cm.matrix;
    classes = cm.classes || classes;
  }

  if (!matrix || matrix.length === 0 || !classes || classes.length === 0) {
    confusionMatrixWrapper.innerHTML = '<div class="chart-missing-notice">Confusion matrix data is unavailable for this run.</div>';
    return;
  }

  let html = '<table class="cm-table">';
  html += '<thead><tr>';
  html += '<th class="cm-corner">Actual \\ Pred</th>';
  classes.forEach((cls) => {
    html += `<th>${escapeHtml(cls)}</th>`;
  });
  html += '</tr></thead>';
  html += '<tbody>';

  matrix.forEach((row, rIdx) => {
    const actualCls = classes[rIdx] || `C${rIdx}`;
    html += '<tr>';
    html += `<th style="text-align: left; font-family: var(--font-mono);">${escapeHtml(actualCls)}</th>`;

    const rowTotal = row.reduce((a, b) => a + b, 0) || 1;

    row.forEach((val, cIdx) => {
      let cellClass = 'cm-cell-empty';
      let title = `Actual: ${actualCls}, Pred: ${classes[cIdx]}: ${val}`;
      let style = '';

      if (rIdx === cIdx) {
        cellClass = 'cm-cell-diag';
        const alpha = Math.min(0.85, 0.2 + 0.65 * (val / rowTotal));
        style = `background: rgba(16, 185, 129, ${alpha.toFixed(2)});`;
      } else if (val > 0) {
        cellClass = 'cm-cell-err';
        const alpha = Math.min(0.85, 0.2 + 0.65 * (val / rowTotal));
        style = `background: rgba(239, 68, 68, ${alpha.toFixed(2)});`;
      }

      html += `<td class="${cellClass}" style="${style}" title="${title}">${val}</td>`;
    });
    html += '</tr>';
  });

  html += '</tbody></table>';
  confusionMatrixWrapper.innerHTML = html;
}

function renderFeatureImportances(fiList, modelName = '') {
  if (!featureImportanceWrapper) return;

  if (!fiList || fiList.length === 0) {
    featureImportanceWrapper.innerHTML = `
      <div class="chart-missing-notice">
        <span>No feature importance metrics available for ${escapeHtml(modelName)}.</span>
      </div>
    `;
    return;
  }

  const topItems = fiList.slice(0, 8);
  const maxImp = Math.max(...topItems.map((item) => item.importance)) || 1;

  let html = '<div class="fi-wrapper">';
  topItems.forEach((item) => {
    const pct = Math.min(100, Math.max(2, Math.round((item.importance / maxImp) * 100)));
    const dispVal = (item.importance * 100).toFixed(1);
    html += `
      <div class="fi-item">
        <div class="fi-meta">
          <span class="fi-name">${escapeHtml(item.feature)}</span>
          <span class="fi-score">${dispVal}%</span>
        </div>
        <div class="fi-bar-track">
          <div class="fi-bar-fill" style="width: ${pct}%;"></div>
        </div>
      </div>
    `;
  });
  html += '</div>';

  featureImportanceWrapper.innerHTML = html;
}

function renderSvgMetricComparisonChart(container, modelsList, metricKey, label) {
  if (!container) return;

  const valid = modelsList.filter((m) => {
    const v = m.metrics ? m.metrics[metricKey] : m[metricKey];
    return typeof v === 'number';
  });
  if (valid.length === 0) {
    container.innerHTML = `<div class="chart-missing-notice">No metric data available for ${label}.</div>`;
    return;
  }

  const svgWidth = 420;
  const rowHeight = 32;
  const svgHeight = Math.max(100, valid.length * rowHeight + 30);
  const labelWidth = 130;
  const barMaxWidth = 220;

  let svg = `<svg viewBox="0 0 ${svgWidth} ${svgHeight}" preserveAspectRatio="xMidYMid meet">`;

  // Grid lines
  const x50 = labelWidth + barMaxWidth * 0.5;
  const x100 = labelWidth + barMaxWidth;
  svg += `<line x1="${x50}" y1="10" x2="${x50}" y2="${svgHeight - 15}" stroke="rgba(255,255,255,0.06)" stroke-dasharray="2,2" />`;
  svg += `<line x1="${x100}" y1="10" x2="${x100}" y2="${svgHeight - 15}" stroke="rgba(255,255,255,0.12)" />`;
  svg += `<text x="${x50}" y="${svgHeight - 4}" fill="#64748b" font-size="8" font-family="monospace" text-anchor="middle">50%</text>`;
  svg += `<text x="${x100}" y="${svgHeight - 4}" fill="#64748b" font-size="8" font-family="monospace" text-anchor="middle">100%</text>`;

  valid.forEach((item, i) => {
    const y = 14 + i * rowHeight;
    const val = item.metrics ? item.metrics[metricKey] : item[metricKey];
    const barWidth = Math.max(3, val * barMaxWidth);
    const color = item.model_name.includes('Random Forest') ? '#10b981' : '#f59e0b';

    // Label
    svg += `<text x="${labelWidth - 8}" y="${y + 13}" fill="#cbd5e1" font-size="10.5" font-family="sans-serif" font-weight="500" text-anchor="end">${escapeHtml(item.model_name)}</text>`;
    // Bar background
    svg += `<rect x="${labelWidth}" y="${y}" width="${barMaxWidth}" height="18" rx="4" fill="rgba(255,255,255,0.04)" />`;
    // Value bar
    svg += `<rect x="${labelWidth}" y="${y}" width="${barWidth}" height="18" rx="4" fill="${color}" opacity="0.9">
              <title>${escapeHtml(item.model_name)}: ${(val * 100).toFixed(1)}%</title>
            </rect>`;
    // Value text
    svg += `<text x="${labelWidth + barWidth + 8}" y="${y + 13}" fill="#fff" font-size="10" font-family="monospace" font-weight="600">${(val * 100).toFixed(1)}%</text>`;
  });

  svg += '</svg>';
  container.innerHTML = svg;
}

// ---------------------------------------------------------------------------
// Init
// ---------------------------------------------------------------------------

async function init() {
  setupViewNavigation();
  setupTabs();
  setupUpload();
  setupManualEntryHandlers();
  setupVisualizationControls();
  setupTableControls();
  setupModelsSection();

  await checkDatabaseConnection();
  await loadTableList();
}

document.addEventListener('DOMContentLoaded', init);

