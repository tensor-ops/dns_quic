/**
 * Robust Client-Side CSV Parser & Analytics Engine
 */

export function parseCSV(text) {
  if (!text || !text.trim()) {
    return { headers: [], rows: [] };
  }

  const lines = [];
  let cur = '';
  let inQuotes = false;

  for (let i = 0; i < text.length; i++) {
    const char = text[i];
    const next = text[i + 1];

    if (char === '"') {
      if (inQuotes && next === '"') {
        cur += '"';
        i++;
      } else {
        inQuotes = !inQuotes;
      }
    } else if ((char === '\r' && next === '\n') || (char === '\n' && !inQuotes)) {
      if (char === '\r' && next === '\n') i++;
      lines.push(cur);
      cur = '';
    } else {
      cur += char;
    }
  }
  if (cur.trim()) lines.push(cur);

  if (lines.length === 0) return { headers: [], rows: [] };

  const parseLine = (line) => {
    const row = [];
    let field = '';
    let inQ = false;
    for (let i = 0; i < line.length; i++) {
      const c = line[i];
      const n = line[i + 1];
      if (c === '"') {
        if (inQ && n === '"') {
          field += '"';
          i++;
        } else {
          inQ = !inQ;
        }
      } else if (c === ',' && !inQ) {
        row.push(field.trim());
        field = '';
      } else {
        field += c;
      }
    }
    row.push(field.trim());
    return row;
  };

  const rawHeaders = parseLine(lines[0]);
  const headers = rawHeaders.map((h, idx) => h.replace(/^["']|["']$/g, '').trim() || `col_${idx + 1}`);

  const rows = [];
  for (let i = 1; i < lines.length; i++) {
    const rawLine = lines[i].trim();
    if (!rawLine) continue;
    const values = parseLine(rawLine);
    const rowObj = {};
    headers.forEach((h, idx) => {
      let val = values[idx] !== undefined ? values[idx] : '';
      val = val.replace(/^["']|["']$/g, '').trim();
      // Auto-cast numbers if valid
      if (val !== '' && !isNaN(val) && !isNaN(parseFloat(val))) {
        val = Number(val);
      }
      rowObj[h] = val;
    });
    rows.push(rowObj);
  }

  return { headers, rows };
}

export function toCSV(rows, headers) {
  if (!rows || rows.length === 0) return '';
  const hdrs = headers || Object.keys(rows[0]);
  const escapeVal = (val) => {
    if (val === null || val === undefined) return '';
    const s = String(val);
    if (s.includes(',') || s.includes('"') || s.includes('\n')) {
      return `"${s.replace(/"/g, '""')}"`;
    }
    return s;
  };

  const headerLine = hdrs.map(escapeVal).join(',');
  const rowLines = rows.map((r) => hdrs.map((h) => escapeVal(r[h])).join(','));
  return [headerLine, ...rowLines].join('\n');
}

export function computeDatasetStats(rows, headers) {
  const rowCount = rows ? rows.length : 0;
  const colCount = headers ? headers.length : 0;

  if (rowCount === 0) {
    return {
      rowCount: 0,
      colCount: 0,
      missingCount: 0,
      missingPct: 0,
      protocolDist: {},
      colSummary: {},
    };
  }

  let missingCount = 0;
  const colMissing = {};
  headers.forEach((h) => (colMissing[h] = 0));

  rows.forEach((r) => {
    headers.forEach((h) => {
      const v = r[h];
      if (v === '' || v === null || v === undefined || v === 'NaN' || Number.isNaN(v)) {
        missingCount++;
        colMissing[h]++;
      }
    });
  });

  const totalCells = rowCount * colCount;
  const missingPct = totalCells > 0 ? ((missingCount / totalCells) * 100).toFixed(2) : 0;

  // Protocol / Class distribution
  const protoCol = headers.find((h) =>
    ['protocol', 'transport_protocol', 'traffic_class', 'class', 'label'].includes(h.toLowerCase())
  );

  const protocolDist = {};
  if (protoCol) {
    rows.forEach((r) => {
      const key = String(r[protoCol] || 'Unknown').trim();
      protocolDist[key] = (protocolDist[key] || 0) + 1;
    });
  }

  return {
    rowCount,
    colCount,
    missingCount,
    missingPct,
    protocolCol: protoCol || null,
    protocolDist,
    colMissing,
  };
}
