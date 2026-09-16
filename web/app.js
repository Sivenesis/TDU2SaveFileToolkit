/**
 * Test Drive Unlimited 2 (TDU2) Save File Toolkit - Version 2.0.5
 * Modern client logic for 4-tab architecture, custom path management, and online mode switcher.
 */

const state = {
  activeProfile: null,
  activeSavePath: null,
  isLiveDocuments: false,
  customDir: null,
  defaultDir: null,
  saveSummary: null,
  profilesList: [],
  catalogCars: [],
  garageIslandFilter: 'all',
  garageSearchQuery: '',
  swapTargetSlot: null,
  logs: []
};

// DOM Elements Cache
const el = {};

function getAuthHeaders() {
  const token = document.querySelector('meta[name="toolkit-token"]')?.getAttribute('content') || '';
  return {
    'Content-Type': 'application/json',
    'X-Toolkit-Token': token
  };
}

document.addEventListener('DOMContentLoaded', () => {
  cacheElements();
  setupTabs();
  setupEventListeners();
  setStandbyUI();
  addLog("TDU2 Save File Toolkit v2.0.5 initialized. Scanning available save profiles...", "info");
  fetchProfiles();
  fetchCatalog();
});


function cacheElements() {
  el.topProfileName = document.getElementById('topProfileName');
  el.topBackupCount = document.getElementById('topBackupCount');
  el.profileStatusDot = document.getElementById('profileStatusDot');
  el.topOnlinePill = document.getElementById('topOnlinePill');
  el.topOnlineMode = document.getElementById('topOnlineMode');

  el.profileDropdown = document.getElementById('profileDropdown');
  el.btnLoadProfile = document.getElementById('btnLoadProfile');
  el.btnRefreshProfiles = document.getElementById('btnRefreshProfiles');
  el.btnOpenCustomPath = document.getElementById('btnOpenCustomPath');
  el.btnSpecifyPathPrompt = document.getElementById('btnSpecifyPathPrompt');
  el.activePathText = document.getElementById('activePathText');
  el.bannerPathText = document.getElementById('bannerPathText');
  el.driverBadge = document.getElementById('driverBadge');

  // Custom Path Banner & Modal
  el.customPathActiveBanner = document.getElementById('customPathActiveBanner');
  el.customPathBannerText = document.getElementById('customPathBannerText');
  el.btnResetToDefaultDocs = document.getElementById('btnResetToDefaultDocs');

  el.customPathModal = document.getElementById('customPathModal');
  el.customPathCloseBtn = document.getElementById('customPathCloseBtn');
  el.customPathCancelBtn = document.getElementById('customPathCancelBtn');
  el.customPathInput = document.getElementById('customPathInput');
  el.currentCustomPathStatus = document.getElementById('currentCustomPathStatus');
  el.btnApplyCustomPath = document.getElementById('btnApplyCustomPath');
  el.btnResetDocsInModal = document.getElementById('btnResetDocsInModal');

  // Profile Form (Tab 1)
  el.emptyProfileBanner = document.getElementById('emptyProfileBanner');
  el.profileLoadedContent = document.getElementById('profileLoadedContent');
  el.tab1ModeBadge = document.getElementById('tab1ModeBadge');
  el.tab1ModeExplanation = document.getElementById('tab1ModeExplanation');
  el.btnTab1ToggleOnline = document.getElementById('btnTab1ToggleOnline');
  el.inputMoney = document.getElementById('inputMoney');
  el.inputCasinoPoints = document.getElementById('inputCasinoPoints');
  el.moneyFormattedHint = document.getElementById('moneyFormattedHint');
  el.casinoFormattedHint = document.getElementById('casinoFormattedHint');
  el.inputLevel = document.getElementById('inputLevel');
  el.btnSaveProfile = document.getElementById('btnSaveProfile');

  // Casino Furniture (Tab 1)
  el.statCasinoFurniture = document.getElementById('statCasinoFurniture') || document.getElementById('statCasinoVip');
  el.btnUnlockCasinoFurniture = document.getElementById('btnUnlockCasinoFurniture') || document.getElementById('btnUnlockAllFurniture');
  el.statFurnCount = document.getElementById('statFurnCount');
  el.statMatsCount = document.getElementById('statMatsCount');
  el.statCasinoVip = document.getElementById('statCasinoVip');
  el.btnUnlockAllFurniture = document.getElementById('btnUnlockAllFurniture');

  // Garage (Tab 2)
  el.garageTabCount = document.getElementById('garageTabCount');
  el.garageSearchInput = document.getElementById('garageSearchInput');
  el.garageHousesContainer = document.getElementById('garageHousesContainer');
  el.countAllHouses = document.getElementById('countAllHouses');
  el.countIbizaHouses = document.getElementById('countIbizaHouses');
  el.countHawaiiHouses = document.getElementById('countHawaiiHouses');

  // Save Tools (Tab 3)
  el.btnUnpackSave = document.getElementById('btnUnpackSave');
  el.btnPackSave = document.getElementById('btnPackSave');
  el.btnCreateManualBackup = document.getElementById('btnCreateManualBackup');
  el.decryptFolderPath = document.getElementById('decryptFolderPath');
  el.backupsTotalBadge = document.getElementById('backupsTotalBadge');
  el.backupsTableBody = document.getElementById('backupsTableBody');

  // Online Mode Switcher (Tab 4)
  el.onlineProfileCountBadge = document.getElementById('onlineProfileCountBadge');
  el.onlineProfilesTableBody = document.getElementById('onlineProfilesTableBody');
  el.credModeClone = document.getElementById('credModeClone');
  el.credModeCustom = document.getElementById('credModeCustom');
  el.credCloneSelect = document.getElementById('credCloneSelect');
  el.credLoginName = document.getElementById('credLoginName');
  el.credEmail = document.getElementById('credEmail');
  el.credPassword = document.getElementById('credPassword');
  el.progSourceSelect = document.getElementById('progSourceSelect');
  el.progTargetSelect = document.getElementById('progTargetSelect');
  el.progCopyKeymap = document.getElementById('progCopyKeymap');
  el.btnExecuteCloneProg = document.getElementById('btnExecuteCloneProg');

  // Diagnostic Console
  el.consoleDrawer = document.getElementById('consoleDrawer');
  el.consoleHeader = document.getElementById('consoleHeader');
  el.consoleEntries = document.getElementById('consoleEntries');
  el.consoleCountBadge = document.getElementById('consoleCountBadge');
  el.consoleStatusDot = document.getElementById('consoleStatusDot');
  el.btnCopyConsoleLog = document.getElementById('btnCopyConsoleLog');
  el.btnClearConsoleLog = document.getElementById('btnClearConsoleLog');

  // Modals
  el.confirmModal = document.getElementById('confirmModal');
  el.modalTitle = document.getElementById('modalTitle');
  el.modalBody = document.getElementById('modalBody');
  el.modalCloseBtn = document.getElementById('modalCloseBtn');
  el.modalCancelBtn = document.getElementById('modalCancelBtn');
  el.modalConfirmBtn = document.getElementById('modalConfirmBtn');

  el.catalogModal = document.getElementById('catalogModal');
  el.catalogModalTitle = document.getElementById('catalogModalTitle');
  el.catalogModalSubtitle = document.getElementById('catalogModalSubtitle');
  el.catalogModalCloseBtn = document.getElementById('catalogModalCloseBtn');
  el.catalogCancelBtn = document.getElementById('catalogCancelBtn');
  el.catalogSearchInput = document.getElementById('catalogSearchInput');
  el.catalogBrandFilter = document.getElementById('catalogBrandFilter');
  el.catalogMatchCount = document.getElementById('catalogMatchCount');
  el.catalogList = document.getElementById('catalogList');

  el.toastContainer = document.getElementById('toastContainer');
}


// --- TAB NAVIGATION ---
function setupTabs() {
  const tabs = document.querySelectorAll('.app-tabs .tab-btn');
  tabs.forEach(btn => {
    btn.addEventListener('click', () => {
      const target = btn.dataset.tab;
      tabs.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      document.querySelectorAll('.tab-pane').forEach(pane => {
        pane.classList.toggle('active', pane.id === target);
      });

      if (target === 'tab-online-switch') {
        renderOnlineSwitcherTab(state.profilesList);
      }
    });
  });
}


// --- EVENT LISTENERS ---
function setupEventListeners() {
  // Profile Load
  if (el.btnLoadProfile) {
    el.btnLoadProfile.addEventListener('click', () => {
      const selectedPath = el.profileDropdown.value;
      if (!selectedPath) {
        showToast("Please select a profile from the dropdown first.", "error");
        return;
      }
      loadProfile(selectedPath);
    });
  }

  if (el.btnRefreshProfiles) {
    el.btnRefreshProfiles.addEventListener('click', fetchProfiles);
  }

  // Custom Savegame Path Modal Listeners
  if (el.btnOpenCustomPath) el.btnOpenCustomPath.addEventListener('click', openCustomPathModal);
  if (el.btnSpecifyPathPrompt) el.btnSpecifyPathPrompt.addEventListener('click', openCustomPathModal);
  if (el.customPathCloseBtn) el.customPathCloseBtn.addEventListener('click', closeCustomPathModal);
  if (el.customPathCancelBtn) el.customPathCancelBtn.addEventListener('click', closeCustomPathModal);
  if (el.btnApplyCustomPath) el.btnApplyCustomPath.addEventListener('click', () => applyCustomPath());
  if (el.btnResetDocsInModal) el.btnResetDocsInModal.addEventListener('click', resetToDefaultDocuments);
  if (el.btnResetToDefaultDocs) el.btnResetToDefaultDocs.addEventListener('click', resetToDefaultDocuments);

  // Tab 1 Online Mode Quick Toggle
  if (el.btnTab1ToggleOnline) el.btnTab1ToggleOnline.addEventListener('click', handleTab1ToggleOnline);

  // Tab 4 Credential Mode Radios
  if (el.credModeClone) el.credModeClone.addEventListener('change', updateCredInputs);
  if (el.credModeCustom) el.credModeCustom.addEventListener('change', updateCredInputs);

  // Tab 4 Progression Transfer
  if (el.btnExecuteCloneProg) el.btnExecuteCloneProg.addEventListener('click', executeProgressionTransfer);

  // Profile Form Hints
  if (el.inputMoney) {
    el.inputMoney.addEventListener('input', (e) => {
      const val = Number(e.target.value) || 0;
      el.moneyFormattedHint.textContent = `$${val.toLocaleString()}`;
    });
  }

  if (el.inputCasinoPoints) {
    el.inputCasinoPoints.addEventListener('input', (e) => {
      const val = Number(e.target.value) || 0;
      el.casinoFormattedHint.textContent = `${val.toLocaleString()} Cp`;
    });
  }

  // Save Profile Changes
  if (el.btnSaveProfile) {
    el.btnSaveProfile.addEventListener('click', saveProfileChanges);
  }

  // Unlock Casino Furniture
  const unlockCasinoBtn = el.btnUnlockCasinoFurniture || el.btnUnlockAllFurniture;
  if (unlockCasinoBtn) {
    unlockCasinoBtn.addEventListener('click', () => {
      showConfirmModal(
        "Unlock Casino Furniture?",
        "This will unlock the exclusive Casino furniture in your save.<br><br>A timestamped backup will automatically be saved to <strong>Backups/</strong>.",
        executeUnlockCasinoFurniture
      );
    });
  }

  // Garage Filters
  document.querySelectorAll('.island-filters .filter-pill').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.island-filters .filter-pill').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      state.garageIslandFilter = btn.dataset.island;
      renderGarageShowroom();
    });
  });

  if (el.garageSearchInput) {
    el.garageSearchInput.addEventListener('input', (e) => {
      state.garageSearchQuery = e.target.value.toLowerCase().trim();
      renderGarageShowroom();
    });
  }

  // Save Manipulation Operations (Tab 3)
  if (el.btnUnpackSave) el.btnUnpackSave.addEventListener('click', executeUnpackSave);
  if (el.btnPackSave) el.btnPackSave.addEventListener('click', executePackSave);
  if (el.btnCreateManualBackup) el.btnCreateManualBackup.addEventListener('click', executeManualBackup);

  // Diagnostic Console Controls
  if (el.consoleHeader) {
    el.consoleHeader.addEventListener('click', (e) => {
      if (e.target.closest('.btn')) return;
      el.consoleDrawer.classList.toggle('collapsed');
    });
  }
  if (el.btnCopyConsoleLog) el.btnCopyConsoleLog.addEventListener('click', copyConsoleLogs);
  if (el.btnClearConsoleLog) el.btnClearConsoleLog.addEventListener('click', clearConsoleLogs);

  // Modals Close Listeners
  if (el.modalCloseBtn) el.modalCloseBtn.addEventListener('click', hideConfirmModal);
  if (el.modalCancelBtn) el.modalCancelBtn.addEventListener('click', hideConfirmModal);
  if (el.catalogModalCloseBtn) el.catalogModalCloseBtn.addEventListener('click', closeCatalogModal);
  if (el.catalogCancelBtn) el.catalogCancelBtn.addEventListener('click', closeCatalogModal);

  // Catalog Filters
  if (el.catalogSearchInput) {
    el.catalogSearchInput.addEventListener('input', renderCatalogList);
  }
  if (el.catalogBrandFilter) {
    el.catalogBrandFilter.addEventListener('change', renderCatalogList);
  }
}

// --- DIAGNOSTIC LOGGER & CONSOLE ---
function addLog(message, type = 'info') {
  const timestamp = new Date().toLocaleTimeString();
  const entry = { timestamp, message, type };
  state.logs.push(entry);

  if (el.consoleEntries) {
    const div = document.createElement('div');
    div.className = `console-entry ${type}`;
    div.innerHTML = `<span class="timestamp">[${timestamp}]</span> <span class="prefix">&gt;&gt;</span> ${escapeHtml(message)}`;
    el.consoleEntries.appendChild(div);
    el.consoleEntries.scrollTop = el.consoleEntries.scrollHeight;
  }

  if (el.consoleCountBadge) {
    el.consoleCountBadge.textContent = `${state.logs.length} events`;
  }

  if (type === 'error' && el.consoleStatusDot) {
    el.consoleStatusDot.classList.add('has-error');
  }
}

function copyConsoleLogs() {
  const text = state.logs.map(l => `[${l.timestamp}] [${l.type.toUpperCase()}] ${l.message}`).join('\n');
  navigator.clipboard.writeText(text).then(() => {
    showToast("Diagnostic log copied to clipboard for developer report.", "success");
  }).catch(() => {
    showToast("Failed to copy log automatically. Please select text manually.", "error");
  });
}

function clearConsoleLogs() {
  state.logs = [];
  if (el.consoleEntries) el.consoleEntries.innerHTML = '';
  if (el.consoleCountBadge) el.consoleCountBadge.textContent = '0 events';
  if (el.consoleStatusDot) el.consoleStatusDot.classList.remove('has-error');
  addLog("Console cleared.", "info");
}

// --- CONFIRM MODAL ---
let confirmCallback = null;

function showConfirmModal(title, text, onProceed) {
  if (el.modalTitle) el.modalTitle.textContent = title;
  if (el.modalBody) el.modalBody.innerHTML = text;
  confirmCallback = onProceed;
  if (el.confirmModal) el.confirmModal.classList.add('active');

  if (el.modalConfirmBtn) {
    el.modalConfirmBtn.onclick = () => {
      const cb = confirmCallback;
      hideConfirmModal();
      if (cb) cb();
    };
  }
}

function hideConfirmModal() {
  if (el.confirmModal) el.confirmModal.classList.remove('active');
  confirmCallback = null;
}

// --- TOASTS ---
function showToast(message, type = 'info') {
  if (!el.toastContainer) return;
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.textContent = message;
  el.toastContainer.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    setTimeout(() => toast.remove(), 200);
  }, 4000);
}

// --- STANDBY EMPTY STATE UI ---
function setStandbyUI() {
  if (el.emptyProfileBanner) el.emptyProfileBanner.classList.remove('hidden');
  if (el.profileLoadedContent) el.profileLoadedContent.style.display = 'none';
  if (el.topProfileName) el.topProfileName.textContent = 'None';
  if (el.profileStatusDot) el.profileStatusDot.classList.add('standby');
  if (el.topOnlineMode) {
    el.topOnlineMode.textContent = '--';
    el.topOnlineMode.className = 'val mode-tag-pill';
  }
  if (el.tab1ModeBadge) {
    el.tab1ModeBadge.textContent = 'OFFLINE';
    el.tab1ModeBadge.className = 'mode-tag-badge mode-badge-offline';
  }
  if (el.topBackupCount) el.topBackupCount.textContent = '0';
  if (el.garageTabCount) el.garageTabCount.textContent = '0';
  if (el.activePathText) el.activePathText.textContent = "No profile selected. Choose a profile from the dropdown and click 'Load Profile'.";
  if (el.bannerPathText) el.bannerPathText.textContent = "Documents\\Eden Games\\Test Drive Unlimited 2\\savegame";
  if (el.garageHousesContainer) {
    el.garageHousesContainer.innerHTML = `
      <div class="empty-state-banner">
        <div class="empty-icon">
          <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
        </div>
        <div class="empty-text">
          <strong>No Save Profile Loaded:</strong> Please select your save profile from the dropdown above and click <strong>Load Profile</strong> to view and edit owned houses and vehicles.
        </div>
      </div>
    `;
  }
}

// --- CUSTOM PATH MODAL & MANAGEMENT ---
function openCustomPathModal() {
  if (el.customPathInput) {
    el.customPathInput.value = state.customDir || '';
  }
  if (el.currentCustomPathStatus) {
    if (state.customDir) {
      el.currentCustomPathStatus.textContent = `Active custom folder: ${state.customDir}`;
    } else {
      el.currentCustomPathStatus.textContent = `Current default: ${state.defaultDir || 'Documents\\Eden Games\\Test Drive Unlimited 2\\savegame'}`;
    }
  }
  if (el.customPathModal) el.customPathModal.classList.add('active');
}

function closeCustomPathModal() {
  if (el.customPathModal) el.customPathModal.classList.remove('active');
}

async function applyCustomPath(pathValue) {
  const target = (pathValue !== undefined ? pathValue : (el.customPathInput ? el.customPathInput.value : '')).trim();
  if (!target) {
    showToast("Please enter a path to your savegame or profile folder.", "error");
    return;
  }
  addLog(`Setting custom save path: ${target}...`, "info");
  try {
    const res = await fetch('/api/save-directory', {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ directory: target })
    });
    const data = await res.json();
    if (!data.success) throw new Error(data.error);

    closeCustomPathModal();
    state.customDir = data.custom_dir;
    state.profilesList = data.profiles || [];
    renderProfileDropdown(state.profilesList);
    renderOnlineSwitcherTab(state.profilesList);
    updateCustomPathUI();

    addLog(data.message, "success");
    showToast(data.message, "success");
  } catch (err) {
    addLog(`Custom path error: ${err.message}`, "error");
    showToast(`Path Error: ${err.message}`, "error");
  }
}

async function resetToDefaultDocuments() {
  addLog("Resetting save path to default Documents folder...", "info");
  try {
    const res = await fetch('/api/save-directory', {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ reset: true })
    });
    const data = await res.json();
    if (!data.success) throw new Error(data.error);

    closeCustomPathModal();
    state.customDir = null;
    state.profilesList = data.profiles || [];
    renderProfileDropdown(state.profilesList);
    renderOnlineSwitcherTab(state.profilesList);
    updateCustomPathUI();

    addLog("Reset to standard Documents directory.", "info");
    showToast("Reset to default Documents directory.", "success");
  } catch (err) {
    addLog(`Reset error: ${err.message}`, "error");
    showToast(`Reset Error: ${err.message}`, "error");
  }
}

function updateCustomPathUI() {
  if (state.customDir) {
    if (el.customPathActiveBanner) el.customPathActiveBanner.style.display = 'flex';
    if (el.customPathBannerText) el.customPathBannerText.textContent = state.customDir;
  } else {
    if (el.customPathActiveBanner) el.customPathActiveBanner.style.display = 'none';
  }
}

// --- PROFILE SCANNING & LOADING ---
async function fetchProfiles() {
  try {
    const res = await fetch('/api/profiles');
    const data = await res.json();
    if (!data.success) throw new Error(data.error);

    state.profilesList = data.profiles || [];
    state.customDir = data.custom_dir;
    state.defaultDir = data.default_dir;

    renderProfileDropdown(state.profilesList);
    renderOnlineSwitcherTab(state.profilesList);
    updateCustomPathUI();

    if (data.decrypt_dir && el.decryptFolderPath) {
      el.decryptFolderPath.textContent = data.decrypt_dir;
    }
    const locNote = state.customDir ? `custom path (${state.customDir})` : 'Documents & local folders';
    addLog(`Found ${state.profilesList.length} save profile(s) across ${locNote}.`, "info");
  } catch (err) {
    addLog(`Failed scanning profiles: ${err.message}`, "error");
    showToast(`Scan Error: ${err.message}`, "error");
  }
}

function renderProfileDropdown(profiles) {
  if (!el.profileDropdown) return;
  el.profileDropdown.innerHTML = '<option value="">-- Select a Save Profile --</option>';

  if (!profiles.length) {
    const opt = document.createElement('option');
    opt.value = "";
    opt.textContent = "No TDU2 profiles found (Use 'Custom Path...' if saves are elsewhere)";
    el.profileDropdown.appendChild(opt);
    return;
  }

  profiles.forEach(p => {
    const opt = document.createElement('option');
    opt.value = p.path;
    opt.textContent = p.display_name;
    el.profileDropdown.appendChild(opt);
  });
  el.profileDropdown.value = "";
}

async function loadProfile(targetPath) {
  addLog(`Loading save profile from: ${targetPath}...`, "info");
  try {
    const res = await fetch('/api/load', {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ path: targetPath })
    });
    const data = await res.json();
    if (!data.success) throw new Error(data.error);

    state.saveSummary = data.summary;
    state.activeProfile = data.summary.profile_name;
    state.activeSavePath = data.summary.source_path;
    state.isLiveDocuments = data.summary.is_live_documents;

    updateUI(state.saveSummary);
    addLog(`Loaded profile '${state.saveSummary.driver_name}' (Money: $${state.saveSummary.money.toLocaleString()})`, "success");
    showToast(`Loaded ${state.saveSummary.driver_name}!`, "success");
  } catch (err) {
    addLog(`Failed loading save file: ${err.message}`, "error");
    showToast(`Load Error: ${err.message}`, "error");
  }
}

// --- UPDATE UI DASHBOARDS ---
function updateUI(summary) {
  if (!summary) return;

  // Unhide profile content and hide empty banner
  if (el.emptyProfileBanner) el.emptyProfileBanner.classList.add('hidden');
  if (el.profileLoadedContent) el.profileLoadedContent.style.display = 'grid';

  // Header Status
  if (el.topProfileName) el.topProfileName.textContent = summary.driver_name;
  if (el.profileStatusDot) el.profileStatusDot.classList.remove('standby');
  if (el.activePathText) el.activePathText.textContent = summary.source_path;
  if (el.bannerPathText) el.bannerPathText.textContent = summary.source_path;
  if (el.driverBadge) el.driverBadge.textContent = `Driver: ${summary.driver_name} (Level ${summary.overall_level})`;

  // Online Mode Header Pill & Tab 1 Widget
  const onlineStatus = summary.online_status || { is_online: false, mode_label: 'OFFLINE' };
  const isOnline = Boolean(onlineStatus.is_online);

  if (el.topOnlineMode) {
    el.topOnlineMode.textContent = isOnline ? 'ONLINE' : 'OFFLINE';
    el.topOnlineMode.className = `val mode-tag-pill ${isOnline ? 'online' : 'offline'}`;
  }

  if (el.tab1ModeBadge) {
    el.tab1ModeBadge.textContent = isOnline ? 'ONLINE' : 'OFFLINE';
    el.tab1ModeBadge.className = `mode-tag-badge ${isOnline ? 'mode-badge-online' : 'mode-badge-offline'}`;
  }

  if (el.tab1ModeExplanation) {
    el.tab1ModeExplanation.textContent = isOnline
      ? `Online profile (Server Nickname: ${onlineStatus.login_name || summary.driver_name}${onlineStatus.email ? `, Email: ${onlineStatus.email}` : ''}).`
      : 'Single-player offline profile. Game runs offline without multiplayer server login prompts.';
  }

  if (el.btnTab1ToggleOnline) {
    el.btnTab1ToggleOnline.textContent = isOnline ? 'Switch to Offline Mode' : 'Switch to Online Mode';
  }

  // Tab 1: Profile Form
  if (el.inputMoney) el.inputMoney.value = summary.money;
  if (el.moneyFormattedHint) el.moneyFormattedHint.textContent = `$${summary.money.toLocaleString()}`;

  if (el.inputCasinoPoints) el.inputCasinoPoints.value = summary.casino_points;
  if (el.casinoFormattedHint) el.casinoFormattedHint.textContent = `${summary.casino_points.toLocaleString()} Cp`;

  if (el.inputLevel) el.inputLevel.value = `Level ${summary.overall_level}`;

  // Casino Furniture status
  const furn = summary.furniture || {};
  const isCasinoFurnUnlocked = Boolean(furn.casino_vip_unlocked || furn.casino_furniture_unlocked);
  if (el.statCasinoFurniture) {
    el.statCasinoFurniture.textContent = isCasinoFurnUnlocked ? 'Unlocked' : 'Locked';
    el.statCasinoFurniture.className = `stat-mini-val ${isCasinoFurnUnlocked ? 'stat-val-unlocked' : 'stat-val-locked'}`;
  }
  if (el.statCasinoVip) el.statCasinoVip.textContent = isCasinoFurnUnlocked ? 'Unlocked' : 'Locked';
  if (el.statFurnCount) el.statFurnCount.textContent = `${furn.unlocked_count || 0} / 383`;
  if (el.statMatsCount) el.statMatsCount.textContent = `${furn.materials_unlocked || 0} / 61`;

  // Tab 2: Garage
  if (el.garageTabCount) el.garageTabCount.textContent = summary.garage.count;
  renderGarageShowroom();

  // Tab 3: Backups
  const backups = summary.backups || { count: 0, list: [] };
  if (el.topBackupCount) el.topBackupCount.textContent = backups.count;
  if (el.backupsTotalBadge) el.backupsTotalBadge.textContent = `${backups.count} Backups`;
  renderBackupsTable(backups.list);
}


// --- SAVE PROFILE CHANGES (TAB 1) ---
async function saveProfileChanges() {
  if (!state.activeSavePath) {
    showToast("No active save file loaded. Please select a profile and click Load Profile first.", "error");
    return;
  }

  const payload = {
    money: Math.min(2147483648, Math.max(0, Number(el.inputMoney.value) || 0)),
    casino_points: Math.min(2147483648, Math.max(0, Number(el.inputCasinoPoints.value) || 0))
  };

  addLog("Applying direct profile changes...", "info");

  try {
    const res = await fetch('/api/edit-profile', {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (!data.success) throw new Error(data.error);

    state.saveSummary = data.summary;
    updateUI(state.saveSummary);

    addLog(`[PROFILE SAVED] ${data.message}`, "success");
    if (data.backup_path) {
      addLog(`Safety backup created: ${data.backup_path}`, "info");
    }
    showToast("Profile changes saved successfully!", "success");
  } catch (err) {
    addLog(`Failed updating profile: ${err.message}`, "error");
    showToast(`Save Error: ${err.message}`, "error");
  }
}

// --- UNLOCK CASINO FURNITURE (TAB 1) ---
async function executeUnlockCasinoFurniture() {
  addLog("Unlocking Casino furniture...", "info");

  try {
    const res = await fetch('/api/unlock-casino-furniture', {
      method: 'POST',
      headers: getAuthHeaders()
    });
    const data = await res.json();
    if (!data.success) throw new Error(data.error);

    state.saveSummary = data.summary;
    updateUI(state.saveSummary);

    addLog(`[CASINO FURNITURE UNLOCKED] ${data.message}`, "success");
    if (data.backup_path) {
      addLog(`Safety backup created: ${data.backup_path}`, "info");
    }
    showToast("Casino furniture unlocked successfully!", "success");
  } catch (err) {
    addLog(`Casino furniture unlock failed: ${err.message}`, "error");
    showToast(`Unlock Error: ${err.message}`, "error");
  }
}

const executeUnlockFurniture = executeUnlockCasinoFurniture;

// --- GARAGE EDITOR (TAB 2) ---
function renderGarageShowroom() {
  if (!el.garageHousesContainer) return;
  if (!state.saveSummary || !state.saveSummary.garage) {
    el.garageHousesContainer.innerHTML = `
      <div class="empty-state-banner">
        <div class="empty-icon">
          <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
        </div>
        <div class="empty-text">
          <strong>No Save Profile Loaded:</strong> Please select your save profile from the dropdown above and click <strong>Load Profile</strong> to view and edit owned houses and vehicles.
        </div>
      </div>
    `;
    return;
  }
  el.garageHousesContainer.innerHTML = '';

  const houses = state.saveSummary.garage.houses || [];
  const islandFilter = state.garageIslandFilter.toLowerCase();
  const q = state.garageSearchQuery;

  let totalIbiza = 0;
  let totalHawaii = 0;
  houses.forEach(h => {
    if (h.island.toLowerCase() === 'ibiza') totalIbiza++;
    else totalHawaii++;
  });
  if (el.countAllHouses) el.countAllHouses.textContent = houses.length;
  if (el.countIbizaHouses) el.countIbizaHouses.textContent = totalIbiza;
  if (el.countHawaiiHouses) el.countHawaiiHouses.textContent = totalHawaii;

  let renderedHouseCount = 0;

  houses.forEach(house => {
    if (islandFilter !== 'all' && house.island.toLowerCase() !== islandFilter) return;

    let matchingCars = house.cars || [];
    if (q) {
      const houseMatches = house.name.toLowerCase().includes(q) || house.island.toLowerCase().includes(q);
      matchingCars = house.cars.filter(c => {
        if (houseMatches) return true;
        const carStr = `${c.brand} ${c.name} ${c.model} ${c.version} ${c.archetype}`.toLowerCase();
        return carStr.includes(q);
      });
      if (!matchingCars.length) return;
    }

    renderedHouseCount++;
    const houseEl = document.createElement('div');
    houseEl.className = 'house-section';

    houseEl.innerHTML = `
      <div class="house-header">
        <div class="house-title-wrap">
          <div>
            <div class="house-name-text">${escapeHtml(house.name)}</div>
            <div class="house-meta-badges">
              <span class="badge-island badge-island-${house.island.toLowerCase()}">${escapeHtml(house.island)}</span>
              <span class="badge">Level ${house.level}</span>
              <span class="badge">${house.slots_total}-Car Garage</span>
            </div>
          </div>
        </div>
        <div class="house-capacity-pill">
          ${house.slots_occupied} / ${house.slots_total} Vehicles Parked
        </div>
      </div>

      <div class="house-cars-grid"></div>
    `;

    const gridEl = houseEl.querySelector('.house-cars-grid');

    matchingCars.forEach(car => {
      const card = document.createElement('div');
      card.className = 'car-card';

      const brandDisplay = car.brand || 'Vehicle';
      const upg = car.upgrades || { acceleration: 0, top_speed: 0, braking: 0 };
      const accelLvl = Number(upg.acceleration || 0);
      const speedLvl = Number(upg.top_speed || 0);
      const brakeLvl = Number(upg.braking || 0);

      card.innerHTML = `
        <div class="car-card-top">
          <div class="car-header">
            <span class="car-brand-badge">${escapeHtml(brandDisplay)}</span>
            <span class="car-archetype-badge">#${car.archetype}</span>
          </div>
          <div class="car-title">${escapeHtml(car.name)}</div>
          ${car.version ? `<div class="car-version-text">${escapeHtml(car.version)}</div>` : ''}

          <div class="car-specs-grid">
            <div class="spec-box">
              <span class="spec-label">POWER</span>
              <span class="spec-val">${car.power_bhp ? car.power_bhp + ' BHP' : '--'}</span>
            </div>
            <div class="spec-box">
              <span class="spec-label">TOP SPEED</span>
              <span class="spec-val">${car.top_speed ? Math.round(car.top_speed) + ' km/h' : '--'}</span>
            </div>
            <div class="spec-box">
              <span class="spec-label">0-100 KM/H</span>
              <span class="spec-val">${car.acceleration ? car.acceleration.toFixed(1) + ' s' : '--'}</span>
            </div>
            <div class="spec-box">
              <span class="spec-label">ODOMETER</span>
              <span class="spec-val">${car.mileage ? car.mileage.toLocaleString() + ' km' : '0 km'}</span>
            </div>
          </div>

          <!-- Tuning Quick-Status Badges (Visible without opening menu) -->
          <div class="car-tuning-badges">
            <div class="tuning-badge ${accelLvl === 4 ? 'is-max' : (accelLvl > 0 ? 'is-tuned' : '')}" title="Acceleration Tuning: Level ${accelLvl}">
              <svg class="tune-icon" viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
              <span class="tune-cat">ACC</span>
              <span class="tune-val">Lvl ${accelLvl}</span>
            </div>
            <div class="tuning-badge ${speedLvl === 4 ? 'is-max' : (speedLvl > 0 ? 'is-tuned' : '')}" title="Top Speed Tuning: Level ${speedLvl}">
              <svg class="tune-icon" viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
              <span class="tune-cat">SPD</span>
              <span class="tune-val">Lvl ${speedLvl}</span>
            </div>
            <div class="tuning-badge ${brakeLvl === 4 ? 'is-max' : (brakeLvl > 0 ? 'is-tuned' : '')}" title="Braking Tuning: Level ${brakeLvl}">
              <svg class="tune-icon" viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="4"/><line x1="4.93" y1="4.93" x2="9.17" y2="9.17"/><line x1="14.83" y1="14.83" x2="19.07" y2="19.07"/></svg>
              <span class="tune-cat">BRK</span>
              <span class="tune-val">Lvl ${brakeLvl}</span>
            </div>
          </div>
        </div>

        <!-- Tuning Drawer -->
        <div class="car-tuning-drawer">
          <div class="tuning-drawer-header">
            <span class="tuning-drawer-title">Tuning & Performance</span>
            <button class="btn btn-xs btn-gold btn-max-tune">Max All (Lvl 4)</button>
          </div>

          <div class="tuning-row">
            <span class="tuning-row-label">Acceleration</span>
            <div class="tuning-pills" data-part="acceleration">
              ${[0, 1, 2, 3, 4].map(l => `<button class="tune-pill ${l === accelLvl ? (l === 4 ? 'active pill-max' : 'active') : ''}" data-lvl="${l}">${l}</button>`).join('')}
            </div>
          </div>

          <div class="tuning-row">
            <span class="tuning-row-label">Top Speed</span>
            <div class="tuning-pills" data-part="top_speed">
              ${[0, 1, 2, 3, 4].map(l => `<button class="tune-pill ${l === speedLvl ? (l === 4 ? 'active pill-max' : 'active') : ''}" data-lvl="${l}">${l}</button>`).join('')}
            </div>
          </div>

          <div class="tuning-row">
            <span class="tuning-row-label">Braking</span>
            <div class="tuning-pills" data-part="braking">
              ${[0, 1, 2, 3, 4].map(l => `<button class="tune-pill ${l === brakeLvl ? (l === 4 ? 'active pill-max' : 'active') : ''}" data-lvl="${l}">${l}</button>`).join('')}
            </div>
          </div>

          <div class="tuning-drawer-footer">
            <button class="btn btn-xs btn-secondary btn-close-tune">Close</button>
            <button class="btn btn-xs btn-primary btn-apply-tune">Apply Tuning</button>
          </div>
        </div>

        <div class="car-card-footer">
          <span class="car-slot-tag">Slot #${car.index + 1}</span>
          <div class="car-card-actions">
            <button class="btn btn-xs btn-secondary btn-tune-toggle">
              Tune
            </button>
            <button class="btn btn-xs btn-gold btn-swap-model">
              Swap Model
            </button>
          </div>
        </div>
      `;

      // Drawer Toggle
      const drawer = card.querySelector('.car-tuning-drawer');
      const tuneToggleBtn = card.querySelector('.btn-tune-toggle');
      const closeTuneBtn = card.querySelector('.btn-close-tune');

      if (tuneToggleBtn && drawer) {
        tuneToggleBtn.addEventListener('click', () => {
          drawer.classList.toggle('open');
        });
      }
      if (closeTuneBtn && drawer) {
        closeTuneBtn.addEventListener('click', () => {
          drawer.classList.remove('open');
        });
      }

      // Tuning Pills
      card.querySelectorAll('.tuning-pills').forEach(group => {
        group.querySelectorAll('.tune-pill').forEach(pill => {
          pill.addEventListener('click', () => {
            group.querySelectorAll('.tune-pill').forEach(p => p.classList.remove('active', 'pill-max'));
            const lvl = Number(pill.dataset.lvl);
            pill.classList.add('active');
            if (lvl === 4) pill.classList.add('pill-max');
          });
        });
      });

      // Max All Tune
      const maxTuneBtn = card.querySelector('.btn-max-tune');
      if (maxTuneBtn) {
        maxTuneBtn.addEventListener('click', () => {
          executeTuning(car.index, { max_tune: true }, car.name);
        });
      }

      // Apply Custom Tune
      const applyTuneBtn = card.querySelector('.btn-apply-tune');
      if (applyTuneBtn) {
        applyTuneBtn.addEventListener('click', () => {
          const a = Number(card.querySelector('.tuning-pills[data-part="acceleration"] .tune-pill.active')?.dataset.lvl || 0);
          const s = Number(card.querySelector('.tuning-pills[data-part="top_speed"] .tune-pill.active')?.dataset.lvl || 0);
          const b = Number(card.querySelector('.tuning-pills[data-part="braking"] .tune-pill.active')?.dataset.lvl || 0);
          executeTuning(car.index, { acceleration: a, top_speed: s, braking: b }, car.name);
        });
      }

      // Swap Model Button
      const swapBtn = card.querySelector('.btn-swap-model');
      if (swapBtn) {
        swapBtn.addEventListener('click', () => {
          openCatalogModal(car.index, car.name, house.name);
        });
      }

      gridEl.appendChild(card);
    });

    el.garageHousesContainer.appendChild(houseEl);
  });

  if (renderedHouseCount === 0) {
    el.garageHousesContainer.innerHTML = '<div style="text-align:center; padding: 3rem; color: var(--text-dim);">No vehicles or houses matching filter.</div>';
  }
}

// --- VEHICLE TUNING API ---
async function executeTuning(slotIndex, tunePayload, carName) {
  addLog(`Tuning Slot #${slotIndex + 1} (${carName})...`, "info");
  try {
    const res = await fetch('/api/tune-car', {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ slot: slotIndex, ...tunePayload })
    });
    const data = await res.json();
    if (!data.success) throw new Error(data.error);

    state.saveSummary = data.summary;
    updateUI(state.saveSummary);

    addLog(`[TUNING SUCCESS] ${data.message}`, "success");
    if (data.backup_path) {
      addLog(`Safety backup created: ${data.backup_path}`, "info");
    }
    showToast(`Slot #${slotIndex + 1} tuned successfully!`, "success");
  } catch (err) {
    addLog(`Tuning failed: ${err.message}`, "error");
    showToast(`Tune Error: ${err.message}`, "error");
  }
}

// --- VEHICLE CATALOG & SWAP MODAL ---
async function fetchCatalog() {
  try {
    const res = await fetch('/api/cars-catalog');
    const data = await res.json();
    if (data.success && data.cars) {
      state.catalogCars = data.cars;
      populateBrandFilter(data.cars);
      addLog(`Loaded ${data.cars.length} vehicles into swap catalog.`, "info");
    }
  } catch (err) {
    addLog(`Warning: Could not fetch vehicle catalog: ${err.message}`, "warn");
  }
}

function populateBrandFilter(cars) {
  if (!el.catalogBrandFilter) return;
  const brands = Array.from(new Set(cars.map(c => c.brand).filter(Boolean))).sort();
  el.catalogBrandFilter.innerHTML = '<option value="">All Brands (359 Vehicles)</option>';
  brands.forEach(b => {
    const opt = document.createElement('option');
    opt.value = b;
    opt.textContent = `${b} (${cars.filter(c => c.brand === b).length})`;
    el.catalogBrandFilter.appendChild(opt);
  });
}

function openCatalogModal(slotIndex, currentCarName, houseName) {
  state.swapTargetSlot = Number(slotIndex);
  if (el.catalogModalTitle) el.catalogModalTitle.textContent = `Swap Vehicle Model (Slot #${slotIndex + 1})`;
  if (el.catalogModalSubtitle) {
    el.catalogModalSubtitle.textContent = `Target: Slot #${slotIndex + 1} • Currently: ${currentCarName} (${houseName})`;
  }
  if (el.catalogSearchInput) el.catalogSearchInput.value = '';
  if (el.catalogBrandFilter) el.catalogBrandFilter.value = '';
  renderCatalogList();
  if (el.catalogModal) el.catalogModal.classList.add('active');
}

function closeCatalogModal() {
  if (el.catalogModal) el.catalogModal.classList.remove('active');
}

function renderCatalogList() {
  if (!el.catalogList) return;
  el.catalogList.innerHTML = '';

  const q = (el.catalogSearchInput?.value || '').toLowerCase().trim();
  const selectedBrand = el.catalogBrandFilter?.value || '';

  const filtered = state.catalogCars.filter(c => {
    if (selectedBrand && c.brand !== selectedBrand) return false;
    if (!q) return true;
    const searchStr = `${c.brand} ${c.name} ${c.model} ${c.version} ${c.archetype}`.toLowerCase();
    return searchStr.includes(q);
  });

  if (el.catalogMatchCount) el.catalogMatchCount.textContent = filtered.length;

  if (!filtered.length) {
    el.catalogList.innerHTML = '<div style="grid-column: 1/-1; text-align:center; padding: 2rem; color: var(--text-dim);">No vehicles found matching search.</div>';
    return;
  }

  filtered.forEach(car => {
    const item = document.createElement('div');
    item.className = 'catalog-item';
    item.innerHTML = `
      <div>
        <div class="catalog-item-header">
          <span class="catalog-item-brand">${escapeHtml(car.brand)}</span>
          <span class="catalog-item-arch">#${car.archetype}</span>
        </div>
        <div class="catalog-item-title">${escapeHtml(car.name)}</div>
        <div class="catalog-item-specs">
          <span>${car.power_bhp ? car.power_bhp + ' BHP' : '--'}</span>
          <span>${car.top_speed ? Math.round(car.top_speed) + ' km/h' : '--'}</span>
          <span>${car.acceleration ? car.acceleration.toFixed(1) + 's' : '--'}</span>
        </div>
      </div>
      <button class="catalog-item-btn">
        Swap to this Vehicle
      </button>
    `;

    item.querySelector('.catalog-item-btn').addEventListener('click', () => {
      executeCatalogSwap(state.swapTargetSlot, car.archetype, car.name);
    });

    el.catalogList.appendChild(item);
  });
}

async function executeCatalogSwap(slotIndex, newArchetype, newCarName) {
  closeCatalogModal();
  addLog(`Swapping Garage Slot #${slotIndex + 1} to ${newCarName} (Arch #${newArchetype})...`, "info");

  try {
    const res = await fetch('/api/swap-car-catalog', {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ slot: slotIndex, new_archetype: newArchetype })
    });
    const data = await res.json();
    if (!data.success) throw new Error(data.error);

    state.saveSummary = data.summary;
    updateUI(state.saveSummary);

    addLog(`[SWAP SUCCESS] ${data.message}`, "success");
    if (data.backup_path) {
      addLog(`Safety backup created: ${data.backup_path}`, "info");
    }
    showToast(`Slot #${slotIndex + 1} is now ${newCarName}!`, "success");
  } catch (err) {
    addLog(`Car swap failed: ${err.message}`, "error");
    showToast(`Swap Error: ${err.message}`, "error");
  }
}

// --- SAVE FILES MANIPULATION (TAB 3) ---
async function executeUnpackSave() {
  if (!state.activeSavePath) {
    showToast("No active save file loaded. Please load a profile first.", "error");
    return;
  }
  addLog("Unpacking DATA, KEYMAP, and OPTIONS containers into decrypt/ folder in Toolkit root...", "info");

  try {
    const res = await fetch('/api/unpack', {
      method: 'POST',
      headers: getAuthHeaders()
    });
    const data = await res.json();
    if (!data.success) throw new Error(data.error);

    addLog(`[UNPACK SUCCESS] ${data.message}`, "success");
    if (data.decrypt_dir) {
      addLog(`Decrypted Destination Folder: ${data.decrypt_dir}`, "info");
      if (el.decryptFolderPath) el.decryptFolderPath.textContent = data.decrypt_dir;
    }
    if (data.unpacked_files && data.unpacked_files.length) {
      addLog(`Unpacked ${data.unpacked_files.length} files: ${data.unpacked_files.join(', ')}`, "info");
    }
    showToast(`Save files unpacked to decrypt/ folder (${data.unpacked_count || 3} containers)!`, "success");
  } catch (err) {
    addLog(`Unpack failed: ${err.message}`, "error");
    showToast(`Unpack Error: ${err.message}`, "error");
  }
}

async function executePackSave() {
  if (!state.activeSavePath) {
    showToast("No active save file loaded. Please load a profile first.", "error");
    return;
  }

  showConfirmModal(
    "Pack Decrypted Files to Game-Ready Save?",
    "This will read <strong>DATA.json</strong> (along with <strong>KEYMAP.json</strong> and <strong>OPTIONS.json</strong> if present) from the <strong>decrypt/</strong> folder, compile them into binary XMBF, and re-encrypt them into game-ready saves with authentic DES-CBC and Eden-SHA1 signatures.<br><br>• Your live game save will be safely updated.<br>• Timestamped safety backups are automatically archived in <strong>Backups/</strong>.<br>• An offline game-ready copy is placed in <strong>decrypt/game_ready/</strong>.",
    async () => {
      addLog("Compiling and encrypting decrypted files from decrypt/ into game-ready save...", "info");
      try {
        const res = await fetch('/api/pack', {
          method: 'POST',
          headers: getAuthHeaders(),
          body: JSON.stringify({ install_to_live: true })
        });
        const data = await res.json();
        if (!data.success) throw new Error(data.error);

        if (data.summary) {
          state.saveSummary = data.summary;
          updateUI(state.saveSummary);
        }

        addLog(`[PACK SUCCESS] ${data.message}`, "success");
        if (data.game_ready_dir) {
          addLog(`Game-ready copy exported: ${data.game_ready_dir}`, "info");
        }
        if (data.backup_path) {
          addLog(`Safety backup created: ${data.backup_path}`, "info");
        }
        showToast("Save files packed and installed successfully!", "success");
      } catch (err) {
        addLog(`Pack failed: ${err.message}`, "error");
        showToast(`Pack Error: ${err.message}`, "error");
      }
    }
  );
}

async function executeManualBackup() {
  if (!state.activeSavePath) {
    showToast("No active save file loaded.", "error");
    return;
  }
  addLog("Creating manual timestamped backup in Backups/...", "info");

  try {
    const res = await fetch('/api/create-backup', {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ label: "Manual" })
    });
    const data = await res.json();
    if (!data.success) throw new Error(data.error);

    addLog(`[BACKUP SUCCESS] ${data.message}`, "success");
    addLog(`Saved at: ${data.backup_path}`, "info");
    renderBackupsTable(data.backups || []);
    showToast("Manual backup created successfully!", "success");
  } catch (err) {
    addLog(`Backup creation failed: ${err.message}`, "error");
    showToast(`Backup Error: ${err.message}`, "error");
  }
}

function renderBackupsTable(backups) {
  if (!el.backupsTableBody) return;
  el.backupsTableBody.innerHTML = '';

  if (!backups || !backups.length) {
    el.backupsTableBody.innerHTML = '<tr><td colspan="5" class="table-empty">No backups recorded for this profile yet.</td></tr>';
    return;
  }

  backups.forEach(b => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${escapeHtml(b.filename)}</td>
      <td><span class="op-tag">${escapeHtml(b.operation)}</span></td>
      <td>${escapeHtml(b.timestamp)}</td>
      <td>${escapeHtml(b.size_formatted)}</td>
      <td>
        <button class="btn btn-xs btn-secondary btn-restore-row">Restore</button>
      </td>
    `;

    tr.querySelector('.btn-restore-row').addEventListener('click', () => {
      showConfirmModal(
        `Restore Backup: ${b.filename}?`,
        `This will restore your active save file from <strong>${b.filename}</strong>.<br><br>A safety backup of the current save will be preserved before restoring.`,
        () => executeRestoreBackup(b.path)
      );
    });

    el.backupsTableBody.appendChild(tr);
  });
}

async function executeRestoreBackup(backupPath) {
  addLog(`Restoring save from backup: ${backupPath}...`, "info");
  try {
    const res = await fetch('/api/restore-backup', {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ backup_path: backupPath })
    });
    const data = await res.json();
    if (!data.success) throw new Error(data.error);

    state.saveSummary = data.summary;
    updateUI(state.saveSummary);

    addLog(`[RESTORE SUCCESS] ${data.message}`, "success");
    showToast("Save file restored from backup successfully!", "success");
  } catch (err) {
    addLog(`Restore failed: ${err.message}`, "error");
    showToast(`Restore Error: ${err.message}`, "error");
  }
}

// --- UTILITIES ---
function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

// --- ONLINE MODE SWITCHER & PROGRESSION TRANSFER (TAB 4) ---
function updateCredInputs() {
  const isClone = el.credModeClone ? el.credModeClone.checked : true;
  if (el.credCloneSelect) el.credCloneSelect.disabled = !isClone;
  if (el.credLoginName) el.credLoginName.disabled = isClone;
  if (el.credEmail) el.credEmail.disabled = isClone;
  if (el.credPassword) el.credPassword.disabled = isClone;
}

function renderOnlineSwitcherTab(profiles) {
  if (!el.onlineProfilesTableBody) return;
  const list = profiles || [];

  if (el.onlineProfileCountBadge) {
    el.onlineProfileCountBadge.textContent = `${list.length} Profile${list.length === 1 ? '' : 's'}`;
  }

  // Populate Dropdowns: Clone Credentials, Source Progression, Target Progression
  const prevCloneVal = el.credCloneSelect?.value;
  const prevSrcVal = el.progSourceSelect?.value;
  const prevTgtVal = el.progTargetSelect?.value;

  if (el.credCloneSelect) {
    el.credCloneSelect.innerHTML = '<option value="">-- Select a profile to clone credentials from --</option>';
  }
  if (el.progSourceSelect) {
    el.progSourceSelect.innerHTML = '<option value="">-- Select Source Profile --</option>';
  }
  if (el.progTargetSelect) {
    el.progTargetSelect.innerHTML = '<option value="">-- Select Target Online Profile --</option>';
  }

  list.forEach(p => {
    const st = p.online_status || {};
    const isOnline = (p.is_online !== undefined) ? Boolean(p.is_online) : Boolean(st.is_online);
    const nick = p.login_name || st.login_name || '';
    const email = p.email || st.email || '';
    const credHint = (nick || email) ? ` • ${nick || email}` : ' • No Stored Nick';

    if (el.credCloneSelect) {
      const opt = document.createElement('option');
      opt.value = p.profile_name;
      opt.textContent = `${p.profile_name} (${isOnline ? 'Online' : 'Offline'}${credHint})`;
      el.credCloneSelect.appendChild(opt);
    }
    if (el.progSourceSelect) {
      const opt = document.createElement('option');
      opt.value = p.profile_name;
      opt.textContent = `${p.profile_name} (${isOnline ? 'Online' : 'Offline'})`;
      el.progSourceSelect.appendChild(opt);
    }
    if (el.progTargetSelect) {
      const opt = document.createElement('option');
      opt.value = p.profile_name;
      opt.textContent = `${p.profile_name} (${isOnline ? 'Online' : 'Offline'})`;
      el.progTargetSelect.appendChild(opt);
    }
  });

  if (prevCloneVal && el.credCloneSelect) el.credCloneSelect.value = prevCloneVal;
  if (prevSrcVal && el.progSourceSelect) el.progSourceSelect.value = prevSrcVal;
  if (prevTgtVal && el.progTargetSelect) el.progTargetSelect.value = prevTgtVal;

  updateCredInputs();

  // Populate Profiles Table
  el.onlineProfilesTableBody.innerHTML = '';
  if (!list.length) {
    el.onlineProfilesTableBody.innerHTML = '<tr><td colspan="6" class="table-empty">No TDU2 profiles found in active directory.</td></tr>';
    return;
  }

  list.forEach(p => {
    const st = p.online_status || {};
    const isOnline = (p.is_online !== undefined) ? Boolean(p.is_online) : Boolean(st.is_online);

    // ProfileList.dat Flag with color-coded badge
    let regText = '<span style="color:var(--text-dim);">N/A</span>';
    if (st.registry_online === true || p.reg_flag === '0xFF (Online)') {
      regText = '<span class="mode-tag-badge mode-badge-online">0xFF (Online)</span>';
    } else if (st.registry_online === false || p.reg_flag === '0x00 (Offline)') {
      regText = '<span class="mode-tag-badge mode-badge-offline">0x00 (Offline)</span>';
    } else if (p.reg_flag && p.reg_flag !== 'Not Registered') {
      regText = `<code>${escapeHtml(p.reg_flag)}</code>`;
    } else if (isOnline) {
      regText = '<span class="mode-tag-badge mode-badge-online">0xFF (Online)</span>';
    } else if (isOnline === false) {
      regText = '<span class="mode-tag-badge mode-badge-offline">0x00 (Offline)</span>';
    }

    // OPTIONS Container Flag with color-coded badge
    let optText = '<span style="color:var(--text-dim);">N/A</span>';
    if (st.options_online === true || p.options_flag === true) {
      optText = '<span class="mode-tag-badge mode-badge-online">True (Online)</span>';
    } else if (st.options_online === false || p.options_flag === false) {
      optText = '<span class="mode-tag-badge mode-badge-offline">False (Offline)</span>';
    } else if (p.options_flag && p.options_flag !== 'Unknown') {
      optText = `<code>${escapeHtml(String(p.options_flag))}</code>`;
    } else if (isOnline) {
      optText = '<span class="mode-tag-badge mode-badge-online">True (Online)</span>';
    } else if (isOnline === false) {
      optText = '<span class="mode-tag-badge mode-badge-offline">False (Offline)</span>';
    }

    // Saved credentials display
    const loginName = p.login_name || st.login_name;
    const email = p.email || st.email;
    let credsDisplay = '<span style="color:var(--text-dim);">None</span>';
    if (loginName || email) {
      credsDisplay = `<strong>${escapeHtml(loginName || 'Anonymous')}</strong>${email ? `<br><small style="color:var(--text-dim);">${escapeHtml(email)}</small>` : ''}`;
    }

    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td><strong>${escapeHtml(p.profile_name)}</strong></td>
      <td>
        <span class="mode-tag-badge ${isOnline ? 'mode-badge-online' : 'mode-badge-offline'}">
          ${isOnline ? 'ONLINE' : 'OFFLINE'}
        </span>
      </td>
      <td>${regText}</td>
      <td>${optText}</td>
      <td>${credsDisplay}</td>
      <td>
        <button class="btn btn-xs ${isOnline ? 'btn-secondary' : 'btn-primary'} btn-switch-action" data-profile="${escapeHtml(p.profile_name)}" data-target="${isOnline ? 'offline' : 'online'}">
          ${isOnline ? 'Switch to Offline' : 'Switch to Online'}
        </button>
      </td>
    `;

    const switchBtn = tr.querySelector('.btn-switch-action');
    if (switchBtn) {
      switchBtn.addEventListener('click', () => {
        const targetOnline = switchBtn.dataset.target === 'online';
        executeSwitchProfile(p.profile_name, targetOnline);
      });
    }

    el.onlineProfilesTableBody.appendChild(tr);
  });
}


async function executeSwitchProfile(profileName, targetOnline) {
  const modeLabel = targetOnline ? 'Online' : 'Offline';
  
  let payload = {
    profile_name: profileName,
    target_online: targetOnline
  };

  if (targetOnline) {
    if (el.credModeClone && el.credModeClone.checked) {
      const cloneFrom = el.credCloneSelect?.value;
      if (cloneFrom && cloneFrom !== profileName) {
        payload.clone_from = cloneFrom;
      }
    } else {
      if (el.credLoginName?.value.trim()) payload.login = el.credLoginName.value.trim();
      if (el.credEmail?.value.trim()) payload.email = el.credEmail.value.trim();
      if (el.credPassword?.value) payload.password = el.credPassword.value;
    }
  }

  addLog(`Switching profile '${profileName}' to ${modeLabel.toUpperCase()} mode...`, "info");

  try {
    const res = await fetch('/api/switch-mode', {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (!data.success) throw new Error(data.error);

    addLog(`[MODE SWITCH SUCCESS] ${data.message}`, "success");
    showToast(data.message, "success");

    // Refresh profiles list and reload if this was the active profile
    await fetchProfiles();

    if (state.activeProfile === profileName && state.activeSavePath) {
      await loadProfile(state.activeSavePath);
    }
  } catch (err) {
    addLog(`Mode switch failed for '${profileName}': ${err.message}`, "error");
    showToast(`Switch Error: ${err.message}`, "error");
  }
}

async function executeProgressionTransfer() {
  const sourceProfile = el.progSourceSelect?.value;
  const targetProfile = el.progTargetSelect?.value;
  if (!sourceProfile) {
    showToast("Please select a Source Profile to copy progression from.", "error");
    return;
  }
  if (!targetProfile) {
    showToast("Please select a Target Online Profile to receive the progression.", "error");
    return;
  }
  if (sourceProfile === targetProfile) {
    showToast("Source and Target profiles must be different.", "error");
    return;
  }

  showConfirmModal(
    `Transfer Progression: ${sourceProfile} &rarr; ${targetProfile}?`,
    `This will clone all progression (money, owned houses, tuned vehicles, clothes, unlocked items) from <strong>${escapeHtml(sourceProfile)}</strong> into <strong>${escapeHtml(targetProfile)}</strong>.<br><br>
    • <strong>${escapeHtml(targetProfile)}'s server nickname, UUID, and DLC tokens will be 100% preserved.</strong><br>
    • Controls and steering wheel bindings (<code>KEYMAP</code>) remain safely untouched.<br>
    • Automatic safety backups of both profiles will be created in <strong>Backups/</strong> prior to transfer.`,
    async () => {
      addLog(`Initiating progression transfer from '${sourceProfile}' to '${targetProfile}'...`, "info");
      try {
        const res = await fetch('/api/clone-progression', {
          method: 'POST',
          headers: getAuthHeaders(),
          body: JSON.stringify({
            source_profile: sourceProfile,
            target_profile: targetProfile,
            copy_keymap: false
          })
        });
        const data = await res.json();
        if (!data.success) throw new Error(data.error);

        addLog(`[PROGRESSION CLONED] ${data.message}`, "success");
        showToast(data.message, "success");

        await fetchProfiles();

        if (state.activeProfile === targetProfile || state.activeProfile === sourceProfile) {
          const matchingProf = state.profilesList.find(p => p.profile_name === targetProfile);
          if (matchingProf) {
            await loadProfile(matchingProf.path);
          }
        }
      } catch (err) {
        addLog(`Progression transfer failed: ${err.message}`, "error");
        showToast(`Transfer Error: ${err.message}`, "error");
      }
    }
  );
}

function handleTab1ToggleOnline() {
  if (!state.activeProfile) {
    showToast("No active profile loaded. Please load a profile first.", "error");
    return;
  }

  const currentOnline = Boolean(state.saveSummary?.online_status?.is_online);
  const targetOnline = !currentOnline;
  const targetLabel = targetOnline ? 'Online' : 'Offline';

  showConfirmModal(
    `Switch ${state.activeProfile} to ${targetLabel} Mode?`,
    `This will update <strong>ProfileList.dat</strong> (byte 256) and <strong>OPTIONS</strong> (<code>IsOnlineEnabledProfile = ${targetOnline ? 'True' : 'False'}</code>).<br><br>
    An automatic safety backup will be archived before saving.`,
    () => {
      executeSwitchProfile(state.activeProfile, targetOnline);
    }
  );
}

