/**
 * Supply Chain Intelligence & Risk Analytics Dashboard Logic
 */

let appData = null;
let charts = {};

// Common Chart.js styling defaults for dark theme
Chart.defaults.color = '#9ca3af';
Chart.defaults.font.family = "'Inter', sans-serif";
Chart.defaults.plugins.legend.labels.usePointStyle = true;

document.addEventListener('DOMContentLoaded', async () => {
  setupTabs();
  await loadData();
  renderExecutiveOverview();
  renderInventoryRisk();
  renderDemandForecasting();
  renderSupplierScorecard();
});

// -----------------------------------------------------------------------------
// 1. Navigation & Tab Switching
// -----------------------------------------------------------------------------
function setupTabs() {
  const navButtons = document.querySelectorAll('.nav-item');
  const tabPanes = document.querySelectorAll('.tab-pane');
  const pageTitle = document.getElementById('page-title');
  const pageSubtitle = document.getElementById('page-subtitle');

  const titles = {
    'tab-overview': {
      title: 'Executive Supply Chain Overview',
      subtitle: 'Real-time financial performance, inventory velocity, and fulfillment health'
    },
    'tab-risk': {
      title: 'Inventory Risk & Operational Triage',
      subtitle: 'Multi-factor risk index, stock-out vulnerability detection, and working capital optimization'
    },
    'tab-forecast': {
      title: 'Demand Forecasting & Seasonality Engine',
      subtitle: 'Machine learning time-series predictions (Random Forest) and feature drivers'
    },
    'tab-suppliers': {
      title: 'Supplier Performance & Vendor Scorecard',
      subtitle: 'On-time delivery rates, fill rates, delay trends, and defect penalties'
    }
  };

  navButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      navButtons.forEach(b => b.classList.remove('active'));
      tabPanes.forEach(p => p.classList.remove('active'));

      btn.classList.add('active');
      const targetTab = btn.getAttribute('data-tab');
      document.getElementById(targetTab).classList.add('active');

      if (titles[targetTab]) {
        pageTitle.textContent = titles[targetTab].title;
        pageSubtitle.textContent = titles[targetTab].subtitle;
      }
    });
  });
}

// -----------------------------------------------------------------------------
// 2. Load JSON Data
// -----------------------------------------------------------------------------
async function loadData() {
  if (window.EMBEDDED_DASHBOARD_DATA) {
    appData = window.EMBEDDED_DASHBOARD_DATA;
    console.log('Loaded embedded dashboard data.');
    return;
  }
  try {
    const response = await fetch('dashboard_data.json');
    appData = await response.json();
    console.log('Dashboard data fetched via HTTP:', appData);
  } catch (error) {
    console.error('Failed to load dashboard_data.json:', error);
  }
}

// -----------------------------------------------------------------------------
// 3. Tab 1: Executive Overview
// -----------------------------------------------------------------------------
function renderExecutiveOverview() {
  if (!appData) return;
  const exec = appData.executive;

  // Monthly Revenue & Profit Chart
  const ctxMonthly = document.getElementById('chart-monthly-trend').getContext('2d');
  charts.monthly = new Chart(ctxMonthly, {
    type: 'line',
    data: {
      labels: exec.monthly_trend.labels,
      datasets: [
        {
          label: 'Gross Revenue ($M)',
          data: exec.monthly_trend.revenue,
          borderColor: '#3b82f6',
          backgroundColor: 'rgba(59, 130, 246, 0.1)',
          fill: true,
          tension: 0.35,
          borderWidth: 2.5
        },
        {
          label: 'Gross Profit ($M)',
          data: exec.monthly_trend.profit,
          borderColor: '#10b981',
          backgroundColor: 'transparent',
          borderDash: [5, 5],
          tension: 0.35,
          borderWidth: 2
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: 'index', intersect: false },
      scales: {
        x: { grid: { color: 'rgba(55, 65, 81, 0.4)' } },
        y: { grid: { color: 'rgba(55, 65, 81, 0.4)' }, title: { display: true, text: 'INR Crores (₹ Cr)' } }
      }
    }
  });

  // Health Donut
  const ctxHealth = document.getElementById('chart-health-donut').getContext('2d');
  const healthLabels = Object.keys(exec.health_counts);
  const healthValues = Object.values(exec.health_counts);
  charts.health = new Chart(ctxHealth, {
    type: 'doughnut',
    data: {
      labels: healthLabels,
      datasets: [{
        data: healthValues,
        backgroundColor: ['#10b981', '#f59e0b', '#ef4444', '#8b5cf6'],
        borderWidth: 0
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { position: 'bottom' } }
    }
  });

  // Category Breakdown Bar
  const ctxCat = document.getElementById('chart-category-sales').getContext('2d');
  charts.category = new Chart(ctxCat, {
    type: 'bar',
    data: {
      labels: exec.category_breakdown.labels,
      datasets: [{
        label: 'Revenue (₹ Cr)',
        data: exec.category_breakdown.data,
        backgroundColor: ['#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#06b6d4'],
        borderRadius: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { grid: { display: false } },
        y: { grid: { color: 'rgba(55, 65, 81, 0.4)' }, title: { display: true, text: 'Revenue (₹ Cr)' } }
      }
    }
  });

  // Warehouse Breakdown Horizontal Bar
  const ctxWh = document.getElementById('chart-warehouse-sales').getContext('2d');
  charts.warehouse = new Chart(ctxWh, {
    type: 'bar',
    data: {
      labels: exec.warehouse_breakdown.labels,
      datasets: [{
        label: 'Fulfillment (₹ Cr)',
        data: exec.warehouse_breakdown.data,
        backgroundColor: '#6366f1',
        borderRadius: 6
      }]
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { grid: { color: 'rgba(55, 65, 81, 0.4)' }, title: { display: true, text: 'Fulfilled (₹ Cr)' } },
        y: { grid: { display: false } }
      }
    }
  });
}

// -----------------------------------------------------------------------------
// 4. Tab 2: Inventory Risk & Triage
// -----------------------------------------------------------------------------
function renderInventoryRisk() {
  if (!appData) return;
  const inv = appData.inventory;
  const records = inv.records;

  // Scatter Chart: Stock vs Lead Time Demand
  const ctxScatter = document.getElementById('chart-risk-scatter').getContext('2d');
  const scatterPoints = records.slice(0, 300).map(r => ({
    x: r.current_closing_stock,
    y: r.forecast_demand_lead_time,
    r: Math.min(14, Math.max(4, r.current_inventory_value / 2500)),
    record: r
  }));

  charts.scatter = new Chart(ctxScatter, {
    type: 'bubble',
    data: {
      datasets: [{
        label: 'SKU Risk Points',
        data: scatterPoints,
        backgroundColor: scatterPoints.map(p => {
          if (p.record.risk_category === 'Critical') return 'rgba(239, 68, 68, 0.75)';
          if (p.record.risk_category === 'High') return 'rgba(249, 115, 22, 0.75)';
          if (p.record.risk_category === 'Medium') return 'rgba(234, 179, 8, 0.75)';
          return 'rgba(16, 185, 129, 0.75)';
        })
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: (ctx) => {
              const rec = ctx.raw.record;
              return `${rec.product_id} (${rec.product_name}) - Score: ${rec.inventory_risk_score} [${rec.risk_category}]`;
            }
          }
        }
      },
      scales: {
        x: { grid: { color: 'rgba(55, 65, 81, 0.4)' }, title: { display: true, text: 'Current Available Stock (Units)' } },
        y: { grid: { color: 'rgba(55, 65, 81, 0.4)' }, title: { display: true, text: 'Forecast Demand During Lead Time (Units)' } }
      }
    }
  });

  // Table population & filters
  const tableBody = document.getElementById('risk-table-body');
  const searchInput = document.getElementById('search-input');
  const filterRisk = document.getElementById('filter-risk');
  const filterWarehouse = document.getElementById('filter-warehouse');

  function updateTable() {
    const q = searchInput.value.toLowerCase();
    const rFilter = filterRisk.value;
    const wFilter = filterWarehouse.value;

    const filtered = records.filter(r => {
      const matchSearch = r.product_id.toLowerCase().includes(q) || r.product_name.toLowerCase().includes(q) || r.category.toLowerCase().includes(q);
      const matchRisk = (rFilter === 'ALL') || (r.risk_category === rFilter);
      const matchWh = (wFilter === 'ALL') || (r.warehouse_id === wFilter);
      return matchSearch && matchRisk && matchWh;
    });

    tableBody.innerHTML = '';
    filtered.slice(0, 50).forEach(row => {
      const tr = document.createElement('tr');
      const badgeClass = row.risk_category === 'Critical' ? 'red-badge' : (row.risk_category === 'High' ? 'amber-badge' : (row.risk_category === 'Medium' ? 'yellow-badge' : 'green-badge'));
      tr.innerHTML = `
        <td><strong>${row.product_id}</strong></td>
        <td>${row.product_name}</td>
        <td>${row.category}</td>
        <td>${row.warehouse_id}</td>
        <td>${row.current_closing_stock.toLocaleString()}</td>
        <td>${row.forecast_demand_lead_time}</td>
        <td>${row.days_of_inventory}d</td>
        <td><strong>${row.inventory_risk_score}</strong></td>
        <td><span class="kpi-badge ${badgeClass}">${row.risk_category}</span></td>
        <td>${row.recommended_action}</td>
      `;
      tableBody.appendChild(tr);
    });

    document.getElementById('table-record-count').textContent = `Showing top ${Math.min(50, filtered.length)} of ${filtered.length} matching SKU-Warehouse combinations`;
  }

  searchInput.addEventListener('input', updateTable);
  filterRisk.addEventListener('change', updateTable);
  filterWarehouse.addEventListener('change', updateTable);
  updateTable();
}

// -----------------------------------------------------------------------------
// 5. Tab 3: Demand Forecasting
// -----------------------------------------------------------------------------
function renderDemandForecasting() {
  if (!appData) return;
  const fc = appData.forecasting;

  // Actual vs Predicted Line Chart
  const ctxFc = document.getElementById('chart-forecast-series').getContext('2d');
  charts.forecast = new Chart(ctxFc, {
    type: 'line',
    data: {
      labels: fc.sample_comparison.dates,
      datasets: [
        {
          label: 'Actual Units Sold',
          data: fc.sample_comparison.actual,
          borderColor: '#1e293b',
          backgroundColor: '#374151',
          borderWidth: 2
        },
        {
          label: 'Random Forest Forecast',
          data: fc.sample_comparison.predicted,
          borderColor: '#38bdf8',
          borderDash: [4, 4],
          borderWidth: 2
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: { grid: { color: 'rgba(55, 65, 81, 0.4)' } },
        y: { grid: { color: 'rgba(55, 65, 81, 0.4)' }, title: { display: true, text: 'Units / Day' } }
      }
    }
  });

  // Feature Importance Horizontal Bar
  const ctxFeat = document.getElementById('chart-feature-importance').getContext('2d');
  charts.features = new Chart(ctxFeat, {
    type: 'bar',
    data: {
      labels: fc.feature_importance.labels,
      datasets: [{
        label: 'Importance %',
        data: fc.feature_importance.data,
        backgroundColor: '#8b5cf6',
        borderRadius: 6
      }]
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { grid: { color: 'rgba(55, 65, 81, 0.4)' }, title: { display: true, text: 'Feature Weight (%)' } },
        y: { grid: { display: false } }
      }
    }
  });
}

// -----------------------------------------------------------------------------
// 6. Tab 4: Supplier Scorecard
// -----------------------------------------------------------------------------
function renderSupplierScorecard() {
  if (!appData) return;
  const supList = appData.suppliers.records;
  const tbody = document.getElementById('supplier-table-body');
  tbody.innerHTML = '';

  supList.sort((a, b) => b.supplier_risk_score - a.supplier_risk_score).forEach(s => {
    const tr = document.createElement('tr');
    const badgeClass = s.supplier_risk_score > 70 ? 'red-badge' : (s.supplier_risk_score > 40 ? 'amber-badge' : 'green-badge');
    tr.innerHTML = `
      <td><strong>${s.supplier_id}</strong></td>
      <td>${s.supplier_name}</td>
      <td>${s.supplier_region}</td>
      <td>${s.supplier_type}</td>
      <td><strong>${s.on_time_delivery_rate_pct}%</strong></td>
      <td>${s.avg_delay_days} days</td>
      <td>${s.fill_rate_pct}%</td>
      <td>${s.defect_rate_pct}%</td>
      <td><strong>${s.supplier_risk_score}</strong></td>
      <td><span class="kpi-badge ${badgeClass}">${s.supplier_rating}</span></td>
    `;
    tbody.appendChild(tr);
  });
}
