/**
 * ScamRadar — Client-Side Controller
 * Single-Page Architecture, AI Checker, SQLite Sync, Leaflet Map, and Community Alerts.
 */

// Application State
const AppState = {
  activeTab: 'dashboard-view',
  stats: null,
  reports: [],
  alerts: [],
  map: null,
  markersLayer: null,
  mapFilter: 'All',
  currentAnalysis: null
};

// Examples Dataset
const EXAMPLES = {
  electricity: "Your electricity connection will be disconnected today. Pay ₹2,500 immediately using the following link to avoid service interruption: http://bit.ly/ts-power-bill",
  job: "Amazon Part-Time Hiring: Earn ₹3,000 to ₹8,000 daily working from home just 1 hour per day by reviewing products. Contact HR on Telegram @amazon_career_tasks. Security deposit ₹500 required.",
  delivery: "India Post alert: Your consignment parcel IN894038 could not be delivered due to incomplete street address. Please update your address and pay ₹25 redelivery fee at http://post-redeliver.top",
  bank: "Dear SBI Customer, your YONO account has been blocked today due to pending KYC verification. Click http://sbi-kyc-update.xyz to update PAN immediately and resume banking services."
};

// ================= INITIALIZATION =================
document.addEventListener('DOMContentLoaded', () => {
  setupNavigation();
  setupChecker();
  setupReportForm();
  setupMap();
  setupSettings();

  // Initial Data Fetch
  fetchDashboardStats();
  fetchCommunityAlerts();
  fetchReports();
});

// ================= NAVIGATION SYSTEM =================
function setupNavigation() {
  // Desktop Nav Buttons
  document.querySelectorAll('.nav-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const tabId = btn.getAttribute('data-tab');
      switchView(tabId);
    });
  });

  // Mobile Nav Buttons
  document.querySelectorAll('.m-nav-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const tabId = btn.getAttribute('data-tab');
      switchView(tabId);
    });
  });

  // Brand logo click -> Dashboard
  document.getElementById('nav-brand').addEventListener('click', () => switchView('dashboard-view'));

  // Quick Action Buttons
  document.getElementById('btn-quick-check').addEventListener('click', () => switchView('checker-view'));
  document.getElementById('btn-hero-check').addEventListener('click', () => switchView('checker-view'));
  document.getElementById('btn-hero-map').addEventListener('click', () => switchView('map-view'));
  document.getElementById('btn-dashboard-report').addEventListener('click', () => switchView('report-view'));
  document.getElementById('btn-view-all-alerts').addEventListener('click', () => switchView('alerts-view'));
  document.getElementById('btn-cancel-report').addEventListener('click', () => switchView('dashboard-view'));
}

function switchView(tabId) {
  if (!tabId) return;
  AppState.activeTab = tabId;

  // Toggle View Panels
  document.querySelectorAll('.view-panel').forEach(panel => {
    panel.classList.remove('active');
  });
  const targetPanel = document.getElementById(tabId);
  if (targetPanel) targetPanel.classList.add('active');

  // Update Desktop Nav Active State
  document.querySelectorAll('.nav-btn').forEach(btn => {
    btn.classList.toggle('active', btn.getAttribute('data-tab') === tabId);
  });

  // Update Mobile Nav Active State
  document.querySelectorAll('.m-nav-btn').forEach(btn => {
    btn.classList.toggle('active', btn.getAttribute('data-tab') === tabId);
  });

  // Window scroll to top
  window.scrollTo({ top: 0, behavior: 'smooth' });

  // Map Resize Fix when entering Map Tab
  if (tabId === 'map-view' && AppState.map) {
    setTimeout(() => {
      AppState.map.invalidateSize();
    }, 150);
  }
}

// ================= AI SCAM CHECKER =================
function setupChecker() {
  const textInput = document.getElementById('scam-text-input');
  const clearBtn = document.getElementById('btn-clear-input');
  const analyzeBtn = document.getElementById('btn-run-analysis');
  const errorBox = document.getElementById('checker-error-box');

  // Example Buttons
  document.getElementById('btn-example-electricity').addEventListener('click', () => {
    textInput.value = EXAMPLES.electricity;
    hideCheckerError();
  });
  document.getElementById('btn-example-job').addEventListener('click', () => {
    textInput.value = EXAMPLES.job;
    hideCheckerError();
  });
  document.getElementById('btn-example-delivery').addEventListener('click', () => {
    textInput.value = EXAMPLES.delivery;
    hideCheckerError();
  });
  document.getElementById('btn-example-bank').addEventListener('click', () => {
    textInput.value = EXAMPLES.bank;
    hideCheckerError();
  });

  clearBtn.addEventListener('click', () => {
    textInput.value = '';
    resetCheckerResults();
    hideCheckerError();
  });

  analyzeBtn.addEventListener('click', () => {
    const text = textInput.value.trim();
    if (!text) {
      showCheckerError("Please paste or type a suspicious message to analyze.");
      return;
    }
    hideCheckerError();
    runAIAnalysis(text);
  });

  // Report this scam button from analysis card
  document.getElementById('btn-report-this-scam').addEventListener('click', () => {
    if (AppState.currentAnalysis) {
      prefillReportForm(AppState.currentAnalysis);
      switchView('report-view');
    }
  });

  // Check another message button
  document.getElementById('btn-check-another').addEventListener('click', () => {
    resetCheckerResults();
    textInput.value = '';
    textInput.focus();
  });
}

async function runAIAnalysis(text) {
  const loadingState = document.getElementById('checker-loading-state');
  const stepText = document.getElementById('loading-step-text');
  const resultsCard = document.getElementById('analysis-results-card');
  const analyzeBtn = document.getElementById('btn-run-analysis');

  resultsCard.style.display = 'none';
  loadingState.style.display = 'flex';
  analyzeBtn.disabled = true;

  // Staged loading progression for realistic user feedback
  stepText.textContent = "Analyzing message...";
  await sleep(350);
  stepText.textContent = "Checking scam patterns...";
  await sleep(350);
  stepText.textContent = "Identifying red flags...";
  await sleep(300);

  try {
    const response = await fetch('/api/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text })
    });

    const result = await response.json();

    if (!response.ok || !result.success) {
      showCheckerError(result.error || "Analysis failed. Please try again.");
      return;
    }

    AppState.currentAnalysis = {
      ...result.data,
      originalText: text
    };

    renderAnalysisResults(result.data);

  } catch (err) {
    showCheckerError("Could not connect to ScamRadar analysis server. Please verify the backend is running.");
  } finally {
    loadingState.style.display = 'none';
    analyzeBtn.disabled = false;
  }
}

function renderAnalysisResults(data) {
  const resultsCard = document.getElementById('analysis-results-card');
  const categoryElem = document.getElementById('result-category');
  const riskBadge = document.getElementById('result-risk-badge');
  const riskIcon = document.getElementById('result-risk-icon');
  const riskText = document.getElementById('result-risk-text');
  const scoreVal = document.getElementById('result-score-val');
  const redFlagsContainer = document.getElementById('result-red-flags');
  const whySuspicious = document.getElementById('result-why-suspicious');
  const recommendationsList = document.getElementById('result-recommendations');

  // Category & Score
  categoryElem.textContent = data.category || "Suspicious Message";
  scoreVal.textContent = data.risk_score;

  // Multi-attribute Risk Badge (Color + Icon + Text)
  riskBadge.className = 'risk-badge';
  if (data.risk_level === 'HIGH RISK') {
    riskBadge.classList.add('badge-high');
    riskIcon.textContent = '🚨';
    riskText.textContent = 'HIGH RISK';
    scoreVal.style.color = 'var(--risk-high-solid)';
  } else if (data.risk_level === 'MEDIUM RISK') {
    riskBadge.classList.add('badge-medium');
    riskIcon.textContent = '⚠️';
    riskText.textContent = 'MEDIUM RISK';
    scoreVal.style.color = 'var(--risk-medium-solid)';
  } else {
    riskBadge.classList.add('badge-watch');
    riskIcon.textContent = '👁️';
    riskText.textContent = 'WATCH';
    scoreVal.style.color = 'var(--risk-watch-solid)';
  }

  // Red Flags
  redFlagsContainer.innerHTML = '';
  if (data.red_flags && data.red_flags.length > 0) {
    data.red_flags.forEach(rf => {
      const item = document.createElement('div');
      item.className = 'red-flag-item';
      
      const snippets = rf.detected_snippets && rf.detected_snippets.length > 0
        ? ` <span style="color: #93c5fd; font-family: var(--font-mono); font-size: 0.75rem;">[Matched: ${rf.detected_snippets.join(', ')}]</span>`
        : '';

      item.innerHTML = `
        <div class="red-flag-title">${escapeHtml(rf.name)}${snippets}</div>
        <div class="red-flag-desc">${escapeHtml(rf.description)}</div>
      `;
      redFlagsContainer.appendChild(item);
    });
  } else {
    redFlagsContainer.innerHTML = `<div class="red-flag-item" style="border-left-color: var(--safe-green);">
      <div class="red-flag-title">No Critical Trigger Patterns Matched</div>
      <div class="red-flag-desc">Standard urgency and credential extortion patterns were not found.</div>
    </div>`;
  }

  // Plain-English Explanation
  whySuspicious.textContent = data.why_suspicious;

  // Recommendations Checklist
  recommendationsList.innerHTML = '';
  if (data.recommended_actions && data.recommended_actions.length > 0) {
    data.recommended_actions.forEach(action => {
      const li = document.createElement('li');
      li.textContent = action;
      recommendationsList.appendChild(li);
    });
  }

  // Reveal Results Card
  resultsCard.style.display = 'block';
  resultsCard.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function resetCheckerResults() {
  document.getElementById('analysis-results-card').style.display = 'none';
  AppState.currentAnalysis = null;
}

function showCheckerError(msg) {
  const errorBox = document.getElementById('checker-error-box');
  errorBox.textContent = msg;
  errorBox.style.display = 'block';
}

function hideCheckerError() {
  const errorBox = document.getElementById('checker-error-box');
  errorBox.style.display = 'none';
}

// ================= COMMUNITY REPORT FORM =================
function setupReportForm() {
  const form = document.getElementById('scam-report-form');
  const successBanner = document.getElementById('report-success-banner');
  const errorBanner = document.getElementById('report-error-banner');

  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const category = document.getElementById('report-category').value.trim();
    const description = document.getElementById('report-description').value.trim();
    const area = document.getElementById('report-area').value.trim();
    const privacyCheck = document.getElementById('report-privacy-confirm').checked;
    const riskLevel = document.getElementById('report-risk-level').value;
    const riskScore = document.getElementById('report-risk-score').value;

    errorBanner.style.display = 'none';
    successBanner.style.display = 'none';

    // Validation
    if (!category) {
      showReportError("Please select a scam category.");
      return;
    }
    if (!description || description.length < 10) {
      showReportError("Please provide a descriptive message (at least 10 characters).");
      return;
    }
    if (!area) {
      showReportError("Please select an approximate neighborhood.");
      return;
    }
    if (!privacyCheck) {
      showReportError("Please confirm that your submission does not contain personal passwords, OTPs, or PINs.");
      return;
    }

    const submitBtn = document.getElementById('btn-submit-report');
    submitBtn.disabled = true;
    submitBtn.textContent = "Submitting Report...";

    try {
      const response = await fetch('/api/reports', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          category,
          description,
          area,
          risk_level: riskLevel || undefined,
          risk_score: riskScore ? parseInt(riskScore) : undefined
        })
      });

      const resData = await response.json();

      if (!response.ok || !resData.success) {
        showReportError(resData.error || "Failed to submit report. Please try again.");
        return;
      }

      // Success Display
      successBanner.style.display = 'flex';
      showToast("Report added successfully. Thank you for protecting your community!", "success");
      form.reset();
      document.getElementById('report-privacy-confirm').checked = true;

      // Automatically refresh Dashboard, Map, and Alerts
      fetchDashboardStats();
      fetchReports();
      fetchCommunityAlerts();

      // Scroll to top of report container to see the confirmation banner
      successBanner.scrollIntoView({ behavior: 'smooth', block: 'center' });

    } catch (err) {
      showReportError("Network error while submitting report. Please check server connection.");
    } finally {
      submitBtn.disabled = false;
      submitBtn.innerHTML = `
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
        Submit Community Report
      `;
    }
  });
}

function prefillReportForm(analysis) {
  if (!analysis) return;
  
  const catSelect = document.getElementById('report-category');
  const descInput = document.getElementById('report-description');
  const riskLevelInput = document.getElementById('report-risk-level');
  const riskScoreInput = document.getElementById('report-risk-score');

  // Fill message text
  descInput.value = analysis.originalText || '';

  // Auto-select category if matching option exists
  for (let i = 0; i < catSelect.options.length; i++) {
    if (catSelect.options[i].value.toLowerCase() === analysis.category.toLowerCase()) {
      catSelect.selectedIndex = i;
      break;
    }
  }
  // If not exact, check substring
  if (catSelect.selectedIndex <= 0) {
    for (let i = 0; i < catSelect.options.length; i++) {
      if (analysis.category.toLowerCase().includes(catSelect.options[i].value.toLowerCase())) {
        catSelect.selectedIndex = i;
        break;
      }
    }
  }

  // Pre-fill hidden risk attributes
  riskLevelInput.value = analysis.risk_level || '';
  riskScoreInput.value = analysis.risk_score || '';

  // Hide any previous feedback
  document.getElementById('report-success-banner').style.display = 'none';
  document.getElementById('report-error-banner').style.display = 'none';
}

function showReportError(msg) {
  const errorBanner = document.getElementById('report-error-banner');
  errorBanner.textContent = msg;
  errorBanner.style.display = 'block';
}

// ================= DASHBOARD & STATS =================
async function fetchDashboardStats() {
  try {
    const response = await fetch('/api/stats');
    const result = await response.json();

    if (result.success && result.data) {
      AppState.stats = result.data;
      updateStatsUI(result.data);
    }
  } catch (err) {
    console.error("Failed to fetch dashboard stats:", err);
  }
}

function updateStatsUI(stats) {
  document.getElementById('stat-total-reports').textContent = stats.total_reports;
  document.getElementById('stat-high-risk').textContent = stats.high_risk_count;
  document.getElementById('stat-medium-risk').textContent = stats.medium_risk_count;
  document.getElementById('stat-active-alerts').textContent = stats.active_alerts_count;
  document.getElementById('header-alert-count').textContent = stats.active_alerts_count;

  // Render recent reports feed in dashboard
  const feedContainer = document.getElementById('dashboard-reports-container');
  feedContainer.innerHTML = '';

  if (stats.recent_reports && stats.recent_reports.length > 0) {
    stats.recent_reports.forEach(r => {
      const item = document.createElement('div');
      item.className = 'report-feed-item';

      const isSynthetic = r.source === 'synthetic_demo';
      const sourceTag = isSynthetic 
        ? `<span class="tag-synthetic">Synthetic Demo Data</span>` 
        : `<span class="tag-community">Community Report</span>`;

      const badgeClass = r.risk_level === 'HIGH RISK' 
        ? 'badge-high' 
        : (r.risk_level === 'MEDIUM RISK' ? 'badge-medium' : 'badge-watch');

      item.innerHTML = `
        <div class="item-top-row">
          <span class="item-category">${escapeHtml(r.category)}</span>
          <span class="risk-badge ${badgeClass}">${escapeHtml(r.risk_level)}</span>
        </div>
        <div class="item-area-badge">📍 ${escapeHtml(r.area)}</div>
        <p class="item-snippet">${escapeHtml(r.description)}</p>
        <div class="item-footer-row">
          <span>${escapeHtml(r.created_at)}</span>
          ${sourceTag}
        </div>
      `;
      feedContainer.appendChild(item);
    });
  } else {
    feedContainer.innerHTML = `<div class="loading-placeholder">No reports logged yet.</div>`;
  }
}

// ================= INTERACTIVE SCAM MAP =================
function setupMap() {
  const mapCanvas = document.getElementById('scam-leaflet-map');
  if (!mapCanvas || typeof L === 'undefined') return;

  // Center on Hyderabad coordinates [17.3850, 78.4867]
  AppState.map = L.map('scam-leaflet-map', {
    center: [17.4100, 78.4300],
    zoom: 12,
    zoomControl: true
  });

  // OpenStreetMap Dark/Standard Tiles
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 18,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
  }).addTo(AppState.map);

  AppState.markersLayer = L.layerGroup().addTo(AppState.map);

  // Setup Risk Filter Buttons
  document.querySelectorAll('.filter-pill').forEach(pill => {
    pill.addEventListener('click', () => {
      document.querySelectorAll('.filter-pill').forEach(p => p.classList.remove('active'));
      pill.classList.add('active');
      AppState.mapFilter = pill.getAttribute('data-filter');
      renderMapMarkers();
    });
  });
}

async function fetchReports() {
  try {
    const response = await fetch('/api/reports?limit=150');
    const result = await response.json();

    if (result.success && result.data) {
      AppState.reports = result.data;
      renderMapMarkers();
    }
  } catch (err) {
    console.error("Failed to load map reports:", err);
  }
}

function renderMapMarkers() {
  if (!AppState.map || !AppState.markersLayer) return;

  AppState.markersLayer.clearLayers();

  const filtered = AppState.reports.filter((r, idx) => {
    if (AppState.mapFilter === 'All') return true;
    if (AppState.mapFilter === 'Recent') return idx < 5;
    return r.risk_level === AppState.mapFilter;
  });

  filtered.forEach(r => {
    if (!r.latitude || !r.longitude) return;

    let pinClass = 'pin-watch';
    let iconChar = '👁️';
    let badgeClass = 'badge-watch';

    if (r.risk_level === 'HIGH RISK') {
      pinClass = 'pin-high';
      iconChar = '!';
      badgeClass = 'badge-high';
    } else if (r.risk_level === 'MEDIUM RISK') {
      pinClass = 'pin-medium';
      iconChar = '▲';
      badgeClass = 'badge-medium';
    }

    const customIcon = L.divIcon({
      className: 'custom-leaflet-pin',
      html: `<div class="custom-pin ${pinClass}">${iconChar}</div>`,
      iconSize: [32, 32],
      iconAnchor: [16, 16],
      popupAnchor: [0, -18]
    });

    const isSynthetic = r.source === 'synthetic_demo';
    const tagHtml = isSynthetic
      ? `<span class="tag-synthetic">Synthetic Demo Data</span>`
      : `<span class="tag-community">Community Report</span>`;

    const popupContent = `
      <div class="map-popup-card">
        <div class="popup-top">
          <span class="popup-category">${escapeHtml(r.category)}</span>
          <span class="risk-badge ${badgeClass}">${escapeHtml(r.risk_level)}</span>
        </div>
        <div class="popup-area">📍 Approx. Locality: <strong>${escapeHtml(r.area)}</strong></div>
        <p class="popup-desc">${escapeHtml(r.description)}</p>
        <div class="popup-footer">
          <span>${escapeHtml(r.created_at)}</span>
          ${tagHtml}
        </div>
      </div>
    `;

    const marker = L.marker([r.latitude, r.longitude], { icon: customIcon });
    marker.bindPopup(popupContent);
    AppState.markersLayer.addLayer(marker);
  });
}

// ================= COMMUNITY ALERTS =================
async function fetchCommunityAlerts() {
  try {
    const response = await fetch('/api/alerts');
    const result = await response.json();

    if (result.success && result.data) {
      AppState.alerts = result.data;
      renderAlertsUI(result.data);
    }
  } catch (err) {
    console.error("Failed to load community alerts:", err);
  }
}

function renderAlertsUI(alerts) {
  // 1. Render in Dashboard widget
  const dashContainer = document.getElementById('dashboard-alerts-container');
  dashContainer.innerHTML = '';

  if (alerts && alerts.length > 0) {
    alerts.slice(0, 4).forEach(alert => {
      const item = document.createElement('div');
      item.className = 'alert-feed-item';

      const badgeClass = alert.risk_level === 'HIGH RISK' ? 'badge-high' : 'badge-medium';

      item.innerHTML = `
        <div class="item-top-row">
          <span class="item-category">${escapeHtml(alert.title)}</span>
          <span class="risk-badge ${badgeClass}">${escapeHtml(alert.risk_level)}</span>
        </div>
        <div class="item-area-badge">📍 ${escapeHtml(alert.area)} &bull; ${alert.report_count} Reports</div>
        <p class="item-snippet">${escapeHtml(alert.message)}</p>
        <div class="item-footer-row">
          <span style="color: #93c5fd;">💡 Action: ${escapeHtml(alert.recommended_action)}</span>
        </div>
      `;
      dashContainer.appendChild(item);
    });
  } else {
    dashContainer.innerHTML = `<div class="loading-placeholder">No clustered alerts active at this moment.</div>`;
  }

  // 2. Render in Full Alerts Page
  const fullContainer = document.getElementById('full-alerts-list');
  fullContainer.innerHTML = '';

  if (alerts && alerts.length > 0) {
    alerts.forEach(alert => {
      const card = document.createElement('div');
      card.className = 'alert-card-detailed';

      const badgeClass = alert.risk_level === 'HIGH RISK' ? 'badge-high' : 'badge-medium';

      card.innerHTML = `
        <div>
          <div class="alert-card-header">
            <h3 class="alert-card-title">${escapeHtml(alert.title)}</h3>
            <span class="risk-badge ${badgeClass}">${escapeHtml(alert.risk_level)}</span>
          </div>
          <div class="item-area-badge" style="margin: 0.5rem 0;">📍 ${escapeHtml(alert.area)} &bull; ${alert.report_count} clustered reports</div>
          <p class="alert-card-message">${escapeHtml(alert.message)}</p>
        </div>
        <div class="alert-card-action">
          <strong>Safety Guidance:</strong> ${escapeHtml(alert.recommended_action)}
        </div>
        <div class="alert-card-footer">
          <span>Last updated: ${escapeHtml(alert.updated_at)}</span>
          <span class="tag-synthetic">Community Threat Intelligence</span>
        </div>
      `;
      fullContainer.appendChild(card);
    });
  } else {
    fullContainer.innerHTML = `<div class="loading-placeholder">No active community alerts.</div>`;
  }
}

// ================= SETTINGS =================
function setupSettings() {
  const saveBtn = document.getElementById('btn-save-settings');
  const refreshAlertsBtn = document.getElementById('btn-refresh-alerts');
  const feedback = document.getElementById('settings-save-feedback');

  // Load existing settings
  fetch('/api/settings')
    .then(r => r.json())
    .then(res => {
      if (res.success && res.data) {
        if (res.data.primary_area) document.getElementById('pref-area').value = res.data.primary_area;
        if (res.data.alert_sensitivity) document.getElementById('pref-sensitivity').value = res.data.alert_sensitivity;
      }
    })
    .catch(() => {});

  saveBtn.addEventListener('click', async () => {
    const primary_area = document.getElementById('pref-area').value;
    const alert_sensitivity = document.getElementById('pref-sensitivity').value;

    try {
      const res = await fetch('/api/settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ primary_area, alert_sensitivity })
      });
      const data = await res.json();
      if (data.success) {
        feedback.style.display = 'block';
        showToast("Preferences saved successfully!", "success");
        setTimeout(() => { feedback.style.display = 'none'; }, 3000);
      }
    } catch (e) {
      showToast("Failed to save preferences.", "error");
    }
  });

  refreshAlertsBtn.addEventListener('click', () => {
    fetchCommunityAlerts();
    showToast("Community alerts refreshed.", "success");
  });
}

// ================= UTILITIES =================
function showToast(message, type = 'success') {
  const container = document.getElementById('toast-container');
  if (!container) return;

  const toast = document.createElement('div');
  toast.className = `toast ${type === 'success' ? 'toast-success' : 'toast-error'}`;
  toast.innerHTML = `
    <span>${type === 'success' ? '✓' : '⚠️'}</span>
    <span>${escapeHtml(message)}</span>
  `;

  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(10px)';
    toast.style.transition = 'all 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}
