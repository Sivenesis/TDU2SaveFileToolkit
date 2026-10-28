/**
 * Test Drive Unlimited 2 (TDU2) Save File Toolkit - Version 3.0.4
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
  progressionState: null,
  activeProgSubtab: 'overview',
  activeCasinoFilter: 'all',
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
  addLog("TDU2 Save File Toolkit v3.0.4 initialized. Scanning available save profiles...", "info");
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
  el.btnSaveProfile = document.getElementById('btnSaveProfile');
  el.inputDriverName = document.getElementById('inputDriverName');
  el.driverNameCapBadge = document.getElementById('driverNameCapBadge');
  el.inputOdometerKms = document.getElementById('inputOdometerKms');
  el.inputHaircuts = document.getElementById('inputHaircuts');
  el.inputCurrentCar = document.getElementById('inputCurrentCar');
  el.inputHasBeenMillionaire = document.getElementById('inputHasBeenMillionaire');

  // Raw Tree Editor (Tab 6)
  el.rawTreeContainer = document.getElementById('rawTreeContainer');
  el.rawTreeSearchInput = document.getElementById('rawTreeSearchInput');
  el.btnRawTreeSearch = document.getElementById('btnRawTreeSearch');
  el.btnRawTreeReset = document.getElementById('btnRawTreeReset');
  el.rawSearchResults = document.getElementById('rawSearchResults');
  el.rawSearchResultsList = document.getElementById('rawSearchResultsList');
  el.btnCloseSearchResults = document.getElementById('btnCloseSearchResults');
  el.rawSearchCount = document.getElementById('rawSearchCount');
  el.rawInspectorPanel = document.getElementById('rawInspectorPanel');
  el.rawInspectorEmpty = document.getElementById('rawInspectorEmpty');
  el.rawInspectorContent = document.getElementById('rawInspectorContent');
  el.rawInspectorKindBadge = document.getElementById('rawInspectorKindBadge');
  el.rawMetaName = document.getElementById('rawMetaName');
  el.rawMetaType = document.getElementById('rawMetaType');
  el.rawMetaOffset = document.getElementById('rawMetaOffset');
  el.rawMetaBounds = document.getElementById('rawMetaBounds');
  el.rawMetaPath = document.getElementById('rawMetaPath');
  el.rawScalarEditBlock = document.getElementById('rawScalarEditBlock');
  el.rawNodeInput = document.getElementById('rawNodeInput');
  el.rawNodeInputLabel = document.getElementById('rawNodeInputLabel');
  el.rawNodeInputHint = document.getElementById('rawNodeInputHint');
  el.btnApplyNodeValue = document.getElementById('btnApplyNodeValue');
  el.rawContainerBlock = document.getElementById('rawContainerBlock');
  el.rawChildCount = document.getElementById('rawChildCount');
  el.rawChildrenTableBody = document.getElementById('rawChildrenTableBody');

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
  el.btnRefreshBackups = document.getElementById('btnRefreshBackups');
  el.backupSearchInput = document.getElementById('backupSearchInput');

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

  // Customization Modal
  el.customizationModal = document.getElementById('customizationModal');
  el.customizationModalTitle = document.getElementById('customizationModalTitle');
  el.customizationModalSubtitle = document.getElementById('customizationModalSubtitle');
  el.customizationModalCloseBtn = document.getElementById('customizationModalCloseBtn');
  el.customizationCancelBtn = document.getElementById('customizationCancelBtn');
  el.customizationApplyBtn = document.getElementById('customizationApplyBtn');
  el.customizationModalBody = document.getElementById('customizationModalBody');

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
      } else if (target === 'tab-progression') {
        renderProgressionTab();
      } else if (target === 'tab-save-tools') {
        fetchBackups();
      } else if (target === 'tab-raw-tree') {
        loadRawTreeRoot();
      } else if (target === 'tab-profile') {
        if (state.activeProfile) {
          if (el.emptyProfileBanner) {
            el.emptyProfileBanner.classList.add('hidden');
            el.emptyProfileBanner.style.display = 'none';
          }
          if (el.profileLoadedContent) el.profileLoadedContent.style.display = 'grid';
        } else {
          if (el.emptyProfileBanner) {
            el.emptyProfileBanner.classList.remove('hidden');
            el.emptyProfileBanner.style.display = '';
          }
          if (el.profileLoadedContent) el.profileLoadedContent.style.display = 'none';
        }
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

  initProgressionTabListeners();

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

  // Save Manipulation Operations (Tab 4: Backup Manager)
  if (el.btnUnpackSave) el.btnUnpackSave.addEventListener('click', executeUnpackSave);
  if (el.btnPackSave) el.btnPackSave.addEventListener('click', executePackSave);
  if (el.btnCreateManualBackup) el.btnCreateManualBackup.addEventListener('click', executeManualBackup);
  if (el.btnRefreshBackups) el.btnRefreshBackups.addEventListener('click', fetchBackups);
  if (el.backupSearchInput) {
    el.backupSearchInput.addEventListener('input', (e) => {
      state.backupSearchQuery = e.target.value;
      renderBackupsTable(state.currentBackupsList || []);
    });
  }

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

  // Customization Modal Listeners
  if (el.customizationModalCloseBtn) el.customizationModalCloseBtn.addEventListener('click', closeCustomizationModal);
  if (el.customizationCancelBtn) el.customizationCancelBtn.addEventListener('click', closeCustomizationModal);
  if (el.customizationApplyBtn) el.customizationApplyBtn.addEventListener('click', executeCustomization);

  // Catalog Filters
  if (el.catalogSearchInput) {
    el.catalogSearchInput.addEventListener('input', renderCatalogList);
  }
  if (el.catalogBrandFilter) {
    el.catalogBrandFilter.addEventListener('change', renderCatalogList);
  }

  // Raw Tree Editor Controls (Tab 6)
  if (el.btnApplyNodeValue) el.btnApplyNodeValue.addEventListener('click', applyRawNodeValue);
  if (el.btnRawTreeSearch) el.btnRawTreeSearch.addEventListener('click', searchRawTree);
  if (el.rawTreeSearchInput) {
    el.rawTreeSearchInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') searchRawTree();
    });
  }
  if (el.btnRawTreeReset) {
    el.btnRawTreeReset.addEventListener('click', () => {
      if (el.rawTreeSearchInput) el.rawTreeSearchInput.value = '';
      if (el.rawSearchResults) el.rawSearchResults.style.display = 'none';
      loadRawTreeRoot();
    });
  }
  if (el.btnCloseSearchResults) {
    el.btnCloseSearchResults.addEventListener('click', () => {
      if (el.rawSearchResults) el.rawSearchResults.style.display = 'none';
    });
  }
  if (el.inputDriverName) {
    el.inputDriverName.addEventListener('input', (e) => {
      if (el.driverNameCapBadge && state.saveSummary) {
        const curLen = e.target.value.length;
        const maxCap = state.saveSummary.name_capacity || curLen;
        el.driverNameCapBadge.textContent = `${curLen} / ${maxCap} bytes`;
      }
    });
  }

  // Global backdrop click to dismiss modals
  document.querySelectorAll('.modal-overlay').forEach(overlay => {
    overlay.addEventListener('click', (e) => {
      if (e.target === overlay) {
        overlay.classList.remove('active');
      }
    });
  });

  // Escape key to dismiss any active modal
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      document.querySelectorAll('.modal-overlay.active').forEach(m => m.classList.remove('active'));
    }
  });
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
  if (el.emptyProfileBanner) {
    el.emptyProfileBanner.classList.remove('hidden');
    el.emptyProfileBanner.style.display = '';
  }
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

  const emptyProgBanner = document.getElementById('emptyProgressionBanner');
  const progWrap = document.getElementById('progressionContentWrap');
  if (emptyProgBanner) {
    emptyProgBanner.classList.remove('hidden');
    emptyProgBanner.style.display = '';
  }
  if (progWrap) progWrap.style.display = 'none';
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
  if (el.emptyProfileBanner) {
    el.emptyProfileBanner.classList.add('hidden');
    el.emptyProfileBanner.style.display = 'none';
  }
  if (el.profileLoadedContent) el.profileLoadedContent.style.display = 'grid';

  const emptyProgBanner = document.getElementById('emptyProgressionBanner');
  const progWrap = document.getElementById('progressionContentWrap');
  if (emptyProgBanner) {
    emptyProgBanner.classList.add('hidden');
    emptyProgBanner.style.display = 'none';
  }
  if (progWrap) progWrap.style.display = 'block';
  fetchProgressionState();

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

  if (el.inputDriverName) el.inputDriverName.value = summary.driver_name || '';
  if (el.driverNameCapBadge) {
    const curLen = (summary.driver_name || '').length;
    const maxCap = summary.name_capacity || curLen;
    el.driverNameCapBadge.textContent = `${curLen} / ${maxCap} bytes`;
  }
  if (el.inputOdometerKms) el.inputOdometerKms.value = summary.odometer_kms || 0;
  if (el.inputHaircuts) el.inputHaircuts.value = summary.haircuts || 0;
  if (el.inputCurrentCar) el.inputCurrentCar.value = summary.current_car || 0;
  if (el.inputHasBeenMillionaire) el.inputHasBeenMillionaire.checked = Boolean(summary.has_been_millionaire);

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
    casino_points: Math.min(2147483648, Math.max(0, Number(el.inputCasinoPoints.value) || 0)),
    driver_name: el.inputDriverName ? el.inputDriverName.value.trim() : undefined,
    odometer_kms: el.inputOdometerKms ? Number(el.inputOdometerKms.value) || 0 : undefined,
    haircuts: el.inputHaircuts ? Number(el.inputHaircuts.value) || 0 : undefined,
    current_car: el.inputCurrentCar ? Number(el.inputCurrentCar.value) || 0 : undefined,
    has_been_millionaire: el.inputHasBeenMillionaire ? Boolean(el.inputHasBeenMillionaire.checked) : undefined
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
      const houseMatches = house.name.toLowerCase().includes(q) ||
        house.island.toLowerCase().includes(q) ||
        (house.internal_display && house.internal_display.toLowerCase().includes(q)) ||
        (house.spot_name && house.spot_name.toLowerCase().includes(q));
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

    const internalBadgeHtml = house.internal_display
      ? `<span class="house-internal-id" title="Internal Residence ID & Spot Code">${escapeHtml(house.internal_display)}</span>`
      : (house.spot_name ? `<span class="house-internal-id" title="Internal Spot Code">${escapeHtml(house.spot_name)}</span>` : '');

    houseEl.innerHTML = `
      <div class="house-header">
        <div class="house-title-wrap">
          <div>
            <div class="house-name-text">
              <span>${escapeHtml(house.name)}</span>
              ${internalBadgeHtml}
            </div>
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

          <!-- Official Customization Badges -->
          <div class="car-custom-badges">
            <div class="custom-badge" title="Official Factory Paint: ${escapeHtml(car.color_name || 'Factory Stock')}">
              <span class="custom-badge-icon">
                <svg viewBox="0 0 24 24" width="10" height="10" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z"/></svg>
              </span>
              <span class="custom-badge-cat">PAINT</span>
              <span class="custom-badge-val">${escapeHtml(car.color_name || 'Factory Stock')}</span>
            </div>
            <div class="custom-badge" title="Official Factory Rims: ${escapeHtml(car.rim_name || 'Standard Wheels')}">
              <span class="custom-badge-icon">
                <svg viewBox="0 0 24 24" width="10" height="10" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="3"/><line x1="12" y1="2" x2="12" y2="9"/><line x1="12" y1="15" x2="12" y2="22"/><line x1="2" y1="12" x2="9" y2="12"/><line x1="15" y1="12" x2="22" y2="12"/></svg>
              </span>
              <span class="custom-badge-cat">RIMS</span>
              <span class="custom-badge-val">${escapeHtml(car.rim_name || 'Standard Wheels')}</span>
            </div>
            <div class="custom-badge" title="Official Interior Trim: ${escapeHtml(car.interior_name || 'Standard Trim')}">
              <span class="custom-badge-icon">
                <svg viewBox="0 0 24 24" width="10" height="10" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 18v3h16v-3"/><path d="M7 14h10"/><path d="M5 14a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v6a2 2 0 0 1-2 2"/></svg>
              </span>
              <span class="custom-badge-cat">TRIM</span>
              <span class="custom-badge-val">${escapeHtml(car.interior_name || 'Standard Trim')}</span>
            </div>
          </div>
        </div>

        <!-- Tuning Drawer -->
        <div class="car-tuning-drawer">
          <div class="tuning-drawer-header">
            <span class="tuning-drawer-title">Tuning & Performance</span>
            <div class="quick-stage-group">
              <span class="quick-stage-label">Stage:</span>
              <div class="quick-stage-stack">
                <div class="quick-stage-buttons">
                  ${[0, 1, 2, 3, 4].map(stg => `<button class="btn btn-xs ${stg === 4 ? 'btn-gold' : 'btn-secondary'} btn-quick-stage" data-stage="${stg}">S${stg}</button>`).join('')}
                </div>
                <button class="btn btn-xs btn-gold btn-max-tune">Max All (Lvl 4)</button>
              </div>
            </div>
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
            <button class="btn btn-xs btn-secondary btn-customize-toggle" title="Customize exterior paint, wheels/rims, and interior trim">
              Options
            </button>
            <button class="btn btn-xs btn-secondary btn-tune-toggle">
              Tune
            </button>
            <button class="btn btn-xs btn-gold btn-swap-model">
              Swap Model
            </button>
            <button class="btn btn-xs btn-danger-subtle btn-clear-slot" title="Empty this slot and reset to unassigned">
              Empty
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

      // Quick Stage Buttons (0-4)
      card.querySelectorAll('.btn-quick-stage').forEach(btn => {
        btn.addEventListener('click', () => {
          const stage = Number(btn.dataset.stage);
          executeSetUpgrades(car.index, stage, car.name);
        });
      });

      // Clear Slot Button
      const clearBtn = card.querySelector('.btn-clear-slot');
      if (clearBtn) {
        clearBtn.addEventListener('click', () => {
          executeClearSlot(car.index, car.name);
        });
      }

      // Customize Options Button
      const customizeBtn = card.querySelector('.btn-customize-toggle');
      if (customizeBtn) {
        customizeBtn.addEventListener('click', () => {
          openCustomizationModal(car, house.name, house.internal_display);
        });
      }

      // Swap Model Button
      const swapBtn = card.querySelector('.btn-swap-model');
      if (swapBtn) {
        swapBtn.addEventListener('click', () => {
          openCatalogModal(car.index, car.name, house.name, house.internal_display);
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
async function executeSetUpgrades(slotIndex, stage, carName) {
  addLog(`Setting Stage ${stage} upgrades on Slot #${slotIndex + 1} (${carName})...`, "info");
  try {
    const res = await fetch('/api/set-upgrades', {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ slot: slotIndex, stage: stage })
    });
    const data = await res.json();
    if (!data.success) throw new Error(data.error);

    state.saveSummary = data.summary;
    updateUI(state.saveSummary);

    addLog(`[UPGRADE SUCCESS] ${data.message}`, "success");
    if (data.backup_path) {
      addLog(`Safety backup created: ${data.backup_path}`, "info");
    }
    showToast(`Slot #${slotIndex + 1} upgraded to Stage ${stage}!`, "success");
  } catch (err) {
    addLog(`Upgrade failed: ${err.message}`, "error");
    showToast(`Upgrade Error: ${err.message}`, "error");
  }
}

function executeClearSlot(slotIndex, carName) {
  showConfirmModal(
    `Empty Garage Slot #${slotIndex + 1}?`,
    `Are you sure you want to empty <strong>${escapeHtml(carName)}</strong> from Slot #${slotIndex + 1}?<br><br>The slot will be cleared and reset to an unassigned state. An automatic backup will be created.`,
    async () => {
      addLog(`Emptying Garage Slot #${slotIndex + 1} (${carName})...`, "info");
      try {
        const res = await fetch('/api/clear-slot', {
          method: 'POST',
          headers: getAuthHeaders(),
          body: JSON.stringify({ slot: slotIndex })
        });
        const data = await res.json();
        if (!data.success) throw new Error(data.error);

        state.saveSummary = data.summary;
        updateUI(state.saveSummary);

        addLog(`[SLOT CLEARED] ${data.message}`, "success");
        if (data.backup_path) {
          addLog(`Safety backup created: ${data.backup_path}`, "info");
        }
        showToast(`Slot #${slotIndex + 1} emptied successfully!`, "success");
      } catch (err) {
        addLog(`Clear slot failed: ${err.message}`, "error");
        showToast(`Clear Error: ${err.message}`, "error");
      }
    }
  );
}

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

function openCatalogModal(slotIndex, currentCarName, houseName, houseInternal) {
  state.swapTargetSlot = Number(slotIndex);
  if (el.catalogModalTitle) el.catalogModalTitle.textContent = `Swap Vehicle Model (Slot #${slotIndex + 1})`;
  if (el.catalogModalSubtitle) {
    const houseStr = houseInternal ? `${houseName || 'Garage'} • ${houseInternal}` : (houseName || 'Garage');
    el.catalogModalSubtitle.textContent = `Target: Slot #${slotIndex + 1} • Currently: ${currentCarName} (${houseStr})`;
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

  const BLOCKED_ARCHETYPES = [2005, 2006, 2015];

  filtered.forEach(car => {
    const isBlocked = BLOCKED_ARCHETYPES.includes(Number(car.archetype));
    const item = document.createElement('div');
    item.className = `catalog-item ${isBlocked ? 'catalog-item-blocked' : ''}`;
    item.innerHTML = `
      <div>
        <div class="catalog-item-header">
          <span class="catalog-item-brand">${escapeHtml(car.brand)}</span>
          <span class="catalog-item-arch">#${car.archetype}</span>
          ${isBlocked ? '<span class="badge badge-blocked">Crash Hazard (Blocked)</span>' : ''}
        </div>
        <div class="catalog-item-title">${escapeHtml(car.name)}</div>
        <div class="catalog-item-specs">
          <span>${car.power_bhp ? car.power_bhp + ' BHP' : '--'}</span>
          <span>${car.top_speed ? Math.round(car.top_speed) + ' km/h' : '--'}</span>
          <span>${car.acceleration ? car.acceleration.toFixed(1) + 's' : '--'}</span>
        </div>
        <div class="catalog-item-options-line">
          ${isBlocked
            ? '<span class="opt-fixed-badge" style="color:var(--accent-red,#ef4444);">Ambient traffic AI vehicle - No cockpit assets</span>'
            : (car.has_options 
              ? `<span class="opt-avail-badge">${car.colors_count} Colors • ${car.rims_count} Wheels</span>` 
              : `<span class="opt-fixed-badge">Fixed Specification</span>`)}
        </div>
      </div>
      <button class="catalog-item-btn ${isBlocked ? 'btn-disabled' : ''}" ${isBlocked ? 'disabled title="Ambient AI vehicle without cockpit assets. Blocked to prevent crash."' : ''}>
        ${isBlocked ? 'Swap Blocked' : 'Swap to this Vehicle'}
      </button>
    `;

    if (!isBlocked) {
      item.querySelector('.catalog-item-btn').addEventListener('click', () => {
        executeCatalogSwap(state.swapTargetSlot, car.archetype, car.name);
      });
    }

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

// --- VEHICLE OPTIONS & CUSTOMIZATION MODAL ---
function openCustomizationModal(car, houseName, houseInternal) {
  state.customizeTargetCar = car;
  if (!car) return;

  const slotNum = car.index + 1;
  const brandDisplay = car.brand ? `${car.brand} ` : '';
  const fullName = `${brandDisplay}${car.name || ('Archetype #' + car.archetype)}`;

  if (el.customizationModalTitle) {
    el.customizationModalTitle.textContent = `Customize Vehicle Options (Slot #${slotNum})`;
  }
  if (el.customizationModalSubtitle) {
    const houseStr = houseInternal ? `${houseName || 'Garage'} • ${houseInternal}` : (houseName || 'Garage');
    el.customizationModalSubtitle.textContent = `${fullName} • Bay #${car.bay} (${houseStr})`;
  }

  // Locate car options from catalog
  const carEntry = state.catalogCars.find(c => Number(c.archetype) === Number(car.archetype));
  renderCustomizationBody(car, carEntry);

  if (el.customizationModal) el.customizationModal.classList.add('active');
}

function closeCustomizationModal() {
  if (el.customizationModal) el.customizationModal.classList.remove('active');
  state.customizeTargetCar = null;
}

function renderCustomizationBody(car, carEntry) {
  if (!el.customizationModalBody) return;
  el.customizationModalBody.innerHTML = '';

  const hasOptions = carEntry && carEntry.has_options;
  const colors = (carEntry && carEntry.colors) || [];
  const rims = (carEntry && carEntry.rims) || [];

  if (!hasOptions && colors.length === 0 && rims.length === 0) {
    // Fixed specification vehicle
    el.customizationModalBody.innerHTML = `
      <div class="fixed-spec-banner">
        <div class="fixed-spec-header">
          <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
            <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
          </svg>
          <h4>Factory Fixed Specification</h4>
        </div>
        <p>
          This vehicle model (Archetype #${car.archetype}) is a fixed factory specification in Test Drive Unlimited 2 (e.g. Police cruiser, wreck reward, or unique race-spec vehicle) with no official dealership options.
        </p>
        <div class="fixed-spec-details">
          <div class="spec-detail-item">
            <span class="spec-detail-label">Exterior:</span>
            <span class="spec-detail-val">Factory Standard Livery</span>
          </div>
          <div class="spec-detail-item">
            <span class="spec-detail-label">Wheels:</span>
            <span class="spec-detail-val">Factory Standard Wheels</span>
          </div>
          <div class="spec-detail-item">
            <span class="spec-detail-label">Interior:</span>
            <span class="spec-detail-val">Factory Standard Trim</span>
          </div>
        </div>
      </div>
    `;
    if (el.customizationApplyBtn) el.customizationApplyBtn.style.display = 'none';
    return;
  }

  if (el.customizationApplyBtn) el.customizationApplyBtn.style.display = 'inline-flex';

  // Notice banner about trim and interior options being dependent on selected factory color
  const noticeBanner = document.createElement('div');
  noticeBanner.className = 'customization-notice-banner';
  noticeBanner.innerHTML = `
    <div class="notice-icon">
      <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="12" r="10"></circle>
        <line x1="12" y1="16" x2="12" y2="12"></line>
        <line x1="12" y1="8" x2="12.01" y2="8"></line>
      </svg>
    </div>
    <div class="notice-text">
      <strong>Factory Compatibility Notice:</strong> Some trim and interior styling options are only available when certain official exterior colors are selected.
    </div>
  `;
  el.customizationModalBody.appendChild(noticeBanner);

  // Build 3 distinct sections
  const container = document.createElement('div');
  container.className = 'customization-sections-grid';

  // Current active indices
  const currentPaintIdx = Number(car.paint_indice || 0);
  const currentRimIdx = Number(car.rim_indice || 0);
  const currentInteriorIdx = Number(car.interior_indice || 0);

  // SECTION 1: EXTERIOR COLOR
  const sec1 = document.createElement('div');
  sec1.className = 'custom-section-card';
  sec1.innerHTML = `
    <div class="custom-section-header">
      <div class="sec-title-wrap">
        <span class="sec-num-badge">1</span>
        <div>
          <span class="sec-title">Official Car Color</span>
          <span class="sec-subtitle">Manufacturer Exterior Paint</span>
        </div>
      </div>
      <span class="badge ${colors.length > 0 ? '' : 'badge-dim'}">${colors.length} Available</span>
    </div>
    <div class="custom-section-body">
      ${colors.length > 0 ? `
        <div class="form-group">
          <label for="customPaintSelect">Select Official Color:</label>
          <select id="customPaintSelect" class="custom-select">
            ${colors.map(col => `
              <option value="${col.index}" ${col.index === currentPaintIdx ? 'selected' : ''}>
                ${escapeHtml(col.name)} ${col.price > 0 ? `(+$${col.price.toLocaleString()})` : '(Included)'}
              </option>
            `).join('')}
          </select>
        </div>
      ` : `
        <div class="option-unavailable-box">
          <span>No alternate factory colors available for this model (Factory Fixed).</span>
        </div>
      `}
    </div>
  `;
  container.appendChild(sec1);

  // SECTION 2: WHEELS / RIMS
  const sec2 = document.createElement('div');
  sec2.className = 'custom-section-card';
  sec2.innerHTML = `
    <div class="custom-section-header">
      <div class="sec-title-wrap">
        <span class="sec-num-badge">2</span>
        <div>
          <span class="sec-title">Official Wheels & Rims</span>
          <span class="sec-subtitle">Manufacturer Wheel Specifications</span>
        </div>
      </div>
      <span class="badge ${rims.length > 0 ? '' : 'badge-dim'}">${rims.length} Available</span>
    </div>
    <div class="custom-section-body">
      ${rims.length > 0 ? `
        <div class="form-group">
          <label for="customRimSelect">Select Official Wheels:</label>
          <select id="customRimSelect" class="custom-select">
            ${rims.map(r => {
              const diaStr = r.diameter_front ? `${r.diameter_front}"` : '';
              return `
                <option value="${r.index}" ${r.index === currentRimIdx ? 'selected' : ''}>
                  ${escapeHtml(r.name)} ${diaStr ? `(${diaStr})` : ''} ${r.price > 0 ? `(+$${r.price.toLocaleString()})` : '(Standard)'}
                </option>
              `;
            }).join('')}
          </select>
        </div>
      ` : `
        <div class="option-unavailable-box">
          <span>Standard manufacturer wheels (Factory Fixed).</span>
        </div>
      `}
    </div>
  `;
  container.appendChild(sec2);

  // SECTION 3: INTERIOR / TRIM COLOR
  const sec3 = document.createElement('div');
  sec3.className = 'custom-section-card';
  sec3.innerHTML = `
    <div class="custom-section-header">
      <div class="sec-title-wrap">
        <span class="sec-num-badge">3</span>
        <div>
          <span class="sec-title">Official Trim & Interior</span>
          <span class="sec-subtitle">Upholstery & Dashboard Styling</span>
        </div>
      </div>
      <span class="badge" id="interiorCountBadge">-- Available</span>
    </div>
    <div class="custom-section-body" id="interiorSectionBody">
      <!-- Populated dynamically based on selected color -->
    </div>
  `;
  container.appendChild(sec3);

  el.customizationModalBody.appendChild(container);

  // Dynamic Interior Options Update Function
  function refreshInteriors(selectedColorIdx, targetIntIdx = null) {
    const intBody = document.getElementById('interiorSectionBody');
    const countBadge = document.getElementById('interiorCountBadge');
    if (!intBody) return;

    let availableInts = [];
    if (colors.length > 0) {
      const activeColor = colors.find(c => c.index === Number(selectedColorIdx)) || colors[0];
      availableInts = (activeColor && activeColor.interiors) || [];
    }

    if (countBadge) countBadge.textContent = `${availableInts.length} Available`;

    if (!availableInts.length) {
      intBody.innerHTML = `
        <div class="option-unavailable-box">
          <span>Standard factory interior (No alternate trim for this color).</span>
        </div>
      `;
      return;
    }

    const currentMatch = targetIntIdx !== null ? targetIntIdx : currentInteriorIdx;
    let selectedExists = availableInts.some(i => i.index === currentMatch);
    const chosenIdx = selectedExists ? currentMatch : availableInts[0].index;

    intBody.innerHTML = `
      <div class="form-group">
        <label for="customInteriorSelect">Select Interior Trim:</label>
        <select id="customInteriorSelect" class="custom-select">
          ${availableInts.map(i => `
            <option value="${i.index}" ${i.index === chosenIdx ? 'selected' : ''}>
              ${escapeHtml(i.name)} ${i.price > 0 ? `(+$${i.price.toLocaleString()})` : '(Included)'}
            </option>
          `).join('')}
        </select>
      </div>
    `;
  }

  // Initial population of interiors
  const initialPaint = colors.length > 0 ? currentPaintIdx : 0;
  refreshInteriors(initialPaint, currentInteriorIdx);

  // Color change listener to re-populate compatible interiors
  const paintSelect = document.getElementById('customPaintSelect');
  if (paintSelect) {
    paintSelect.addEventListener('change', (e) => {
      refreshInteriors(Number(e.target.value), null);
    });
  }
}

async function executeCustomization() {
  const car = state.customizeTargetCar;
  if (!car) return;

  const paintSelect = document.getElementById('customPaintSelect');
  const rimSelect = document.getElementById('customRimSelect');
  const interiorSelect = document.getElementById('customInteriorSelect');

  const paintIdx = paintSelect ? Number(paintSelect.value) : Number(car.paint_indice || 0);
  const rimIdx = rimSelect ? Number(rimSelect.value) : Number(car.rim_indice || 0);
  const interiorIdx = interiorSelect ? Number(interiorSelect.value) : Number(car.interior_indice || 0);

  if (el.customizationApplyBtn) {
    el.customizationApplyBtn.disabled = true;
    el.customizationApplyBtn.textContent = 'Applying...';
  }

  addLog(`Applying customization to Slot #${car.index + 1} (${car.name}): Paint #${paintIdx}, Rim #${rimIdx}, Interior #${interiorIdx}...`, "info");

  try {
    const res = await fetch('/api/customize-car', {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({
        slot: car.index,
        paint_indice: paintIdx,
        rim_indice: rimIdx,
        interior_indice: interiorIdx
      })
    });
    const data = await res.json();
    if (!data.success) throw new Error(data.error);

    state.saveSummary = data.summary;
    updateUI(state.saveSummary);

    addLog(`[CUSTOMIZATION SUCCESS] ${data.message}`, "success");
    if (data.backup_path) {
      addLog(`Safety backup created: ${data.backup_path}`, "info");
    }
    showToast(`Customization applied to Slot #${car.index + 1}!`, "success");
    closeCustomizationModal();
  } catch (err) {
    addLog(`Customization failed: ${err.message}`, "error");
    showToast(`Customization Error: ${err.message}`, "error");
  } finally {
    if (el.customizationApplyBtn) {
      el.customizationApplyBtn.disabled = false;
      el.customizationApplyBtn.textContent = 'Apply Customization';
    }
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

async function fetchBackups() {
  if (!state.activeProfile) return;
  try {
    const res = await fetch('/api/backups', { headers: getAuthHeaders() });
    const data = await res.json();
    if (data.success && data.backups) {
      if (el.backupsTotalBadge) el.backupsTotalBadge.textContent = `${data.count} Backups`;
      if (el.topBackupCount) el.topBackupCount.textContent = data.count;
      state.currentBackupsList = data.backups;
      renderBackupsTable(data.backups);
    }
  } catch (err) {
    console.error("Failed fetching backups:", err);
  }
}

function renderBackupsTable(backups) {
  if (!el.backupsTableBody) return;
  el.backupsTableBody.innerHTML = '';

  state.currentBackupsList = backups || [];

  if (!backups || !backups.length) {
    el.backupsTableBody.innerHTML = '<tr><td colspan="6" class="table-empty">No backups recorded for this profile yet. Click &quot;Create Timestamped Backup&quot; to make one.</td></tr>';
    return;
  }

  const query = (state.backupSearchQuery || '').toLowerCase().trim();
  const filtered = query
    ? backups.filter(b => b.filename.toLowerCase().includes(query) || (b.operation || '').toLowerCase().includes(query))
    : backups;

  if (!filtered.length) {
    el.backupsTableBody.innerHTML = '<tr><td colspan="6" class="table-empty">No backups matching filter query.</td></tr>';
    return;
  }

  filtered.forEach(b => {
    const tr = document.createElement('tr');

    let targetType = 'DATA';
    let targetClass = 'badge-target-data';
    const fnUpper = b.filename.toUpperCase();
    if (fnUpper.includes('_OPTIONS_') || fnUpper.includes('OPTIONS')) {
      targetType = 'OPTIONS';
      targetClass = 'badge-target-options';
    } else if (fnUpper.includes('_KEYMAP_') || fnUpper.includes('KEYMAP')) {
      targetType = 'KEYMAP';
      targetClass = 'badge-target-keymap';
    }

    let opDisplay = b.operation || 'AutoBackup';
    opDisplay = opDisplay.replace(/_/g, ' ');

    tr.innerHTML = `
      <td><span class="badge ${targetClass}">${targetType}</span></td>
      <td><span class="op-tag">${escapeHtml(opDisplay)}</span></td>
      <td class="backup-filename-cell"><code>${escapeHtml(b.filename)}</code></td>
      <td class="backup-date-cell">${escapeHtml(b.timestamp)}</td>
      <td class="backup-size-cell">${escapeHtml(b.size_formatted)}</td>
      <td class="backup-action-cell">
        <button class="btn btn-xs btn-primary btn-restore-row" title="Restore save from this backup">Restore</button>
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


// ==============================================================================
// TAB 2: PROGRESSION EDITOR LOGIC & RENDERING
// ==============================================================================

function initProgressionTabListeners() {
  // Sub-Navigation Tabs
  const subnavBtns = document.querySelectorAll('.prog-subnav-btn');
  subnavBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      subnavBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const subtabKey = btn.dataset.subtab || 'overview';
      state.activeProgSubtab = subtabKey;

      document.querySelectorAll('.prog-subpanel').forEach(p => p.classList.remove('active'));
      const targetPanelId = `progPanel${subtabKey.charAt(0).toUpperCase() + subtabKey.slice(1)}`;
      const targetPanel = document.getElementById(targetPanelId);
      if (targetPanel) {
        targetPanel.classList.add('active');
      }

      renderProgressionTab();
    });
  });

  // Casino Subnav Filter Pills
  const casinoFilterPills = document.querySelectorAll('.casino-subnav .subnav-pill');
  casinoFilterPills.forEach(pill => {
    pill.addEventListener('click', () => {
      casinoFilterPills.forEach(p => p.classList.remove('active'));
      pill.classList.add('active');
      state.activeCasinoFilter = pill.dataset.casinofilter || 'all';
      renderProgressionCasinoTab();
    });
  });

  // Global Presets
  const btnMaxAll = document.getElementById('btnProgMaxAll');
  if (btnMaxAll) {
    btnMaxAll.addEventListener('click', () => {
      showConfirmModal(
        "Fulfill All Objectives (Global Level 73)?",
        "This will unlock all 60 base game levels across Competition, Discovery, Collection, and Social, plus all 146 Casino Island objectives for Casino Level 10 (Ace of Casino).<br><br>A safety backup will be created before saving.",
        () => applyProgressionPreset('max_all')
      );
    });
  }

  const btnMaxCasino = document.getElementById('btnProgMaxCasino');
  if (btnMaxCasino) {
    btnMaxCasino.addEventListener('click', () => {
      showConfirmModal(
        "Fulfill All Casino Island Objectives?",
        "This will complete all 15 casino sections, reach Casino Level 10, and grant VIP & Ace of Casino status.<br><br>A safety backup will be created before saving.",
        () => applyProgressionPreset('max_casino')
      );
    });
  }

  const btnResetAll = document.getElementById('btnProgResetAll');
  if (btnResetAll) {
    btnResetAll.addEventListener('click', () => {
      showConfirmModal(
        "Reset All Progression Objectives?",
        "This will reset all progress scores and objective achievements back to baseline (Level 0).<br><br>A safety backup will be created before saving.",
        () => applyProgressionPreset('reset_all')
      );
    });
  }

  // Skill Preset Buttons
  const mapSkillBtn = (btnId, type, skill) => {
    const b = document.getElementById(btnId);
    if (b) {
      b.addEventListener('click', () => applyProgressionPreset(type, skill));
    }
  };

  mapSkillBtn('btnMaxCompetition', 'max_skill', 'competition');
  mapSkillBtn('btnResetCompetition', 'reset_skill', 'competition');
  mapSkillBtn('btnMaxDiscovery', 'max_skill', 'discovery');
  mapSkillBtn('btnResetDiscovery', 'reset_skill', 'discovery');
  mapSkillBtn('btnMaxCollection', 'max_skill', 'collection');
  mapSkillBtn('btnResetCollection', 'reset_skill', 'collection');
  mapSkillBtn('btnMaxSocial', 'max_skill', 'social');
  mapSkillBtn('btnResetSocial', 'reset_skill', 'social');

  // Casino Subpanel Preset Buttons
  const btnMaxCasSub = document.getElementById('btnMaxCasinoSubpanel');
  if (btnMaxCasSub) {
    btnMaxCasSub.addEventListener('click', () => applyProgressionPreset('max_casino'));
  }
  const btnResetCasSub = document.getElementById('btnResetCasinoSubpanel');
  if (btnResetCasSub) {
    btnResetCasSub.addEventListener('click', () => applyProgressionPreset('reset_casino'));
  }
}

async function fetchProgressionState() {
  if (!state.activeProfile) return;
  try {
    const res = await fetch('/api/progression/state', {
      headers: getAuthHeaders()
    });
    const data = await res.json();
    if (data.success && data.state) {
      state.progressionState = data.state;
      renderProgressionTab();
    }
  } catch (err) {
    console.error("Error fetching progression state:", err);
  }
}

async function setProgressionObjective(objId, val) {
  try {
    const res = await fetch('/api/progression/set-objective', {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ id: objId, value: val })
    });
    const data = await res.json();
    if (!data.success) throw new Error(data.error);

    state.progressionState = data.state;
    renderProgressionTab();
    showToast(`Objective updated: ${objId}`, "success");
  } catch (err) {
    showToast(`Failed updating objective: ${err.message}`, "error");
    fetchProgressionState();
  }
}

async function applyProgressionPreset(type, target = null) {
  addLog(`Applying progression preset '${type}' ${target ? `for ${target}` : ''}...`, "info");
  try {
    const res = await fetch('/api/progression/preset', {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ type, target })
    });
    const data = await res.json();
    if (!data.success) throw new Error(data.error);

    state.progressionState = data.state;
    renderProgressionTab();

    // If global level updated, synchronize top driver badge
    if (data.state && data.state.overview && el.driverBadge && state.saveSummary) {
      el.driverBadge.textContent = `Driver: ${state.saveSummary.driver_name} (Level ${data.state.overview.global_level})`;
    }

    addLog(data.message || "Preset applied successfully.", "success");
    showToast(data.message || "Preset applied successfully.", "success");
  } catch (err) {
    addLog(`Preset failed: ${err.message}`, "error");
    showToast(`Preset Error: ${err.message}`, "error");
  }
}

function renderProgressionTab() {
  const emptyProgBanner = document.getElementById('emptyProgressionBanner');
  const progWrap = document.getElementById('progressionContentWrap');

  if (!state.activeProfile || !state.progressionState) {
    if (emptyProgBanner) {
      emptyProgBanner.classList.remove('hidden');
      emptyProgBanner.style.display = '';
    }
    if (progWrap) progWrap.style.display = 'none';
    return;
  }

  if (emptyProgBanner) {
    emptyProgBanner.classList.add('hidden');
    emptyProgBanner.style.display = 'none';
  }
  if (progWrap) progWrap.style.display = 'block';

  const st = state.progressionState;
  const ov = st.overview;
  if (!ov) return;

  // Header Global Level Hero
  const progGlobalLevel = document.getElementById('progGlobalLevel');
  if (progGlobalLevel) {
    progGlobalLevel.textContent = ov.global_level;
  }

  // Active Subpanel Rendering
  const currentSubtab = state.activeProgSubtab || 'overview';
  if (currentSubtab === 'overview') {
    renderProgressionOverview();
  } else if (currentSubtab === 'competition') {
    renderProgressionSkillTab('competition', 'competitionSections', 'compHeaderPts');
  } else if (currentSubtab === 'discovery') {
    renderProgressionSkillTab('discovery', 'discoverySections', 'discHeaderPts');
  } else if (currentSubtab === 'collection') {
    renderProgressionSkillTab('collection', 'collectionSections', 'collHeaderPts');
  } else if (currentSubtab === 'social') {
    renderProgressionSkillTab('social', 'socialSections', 'socHeaderPts');
  } else if (currentSubtab === 'casino') {
    renderProgressionCasinoTab();
  }
}

function renderProgressionOverview() {
  const ov = state.progressionState?.overview;
  if (!ov) return;

  const setTxt = (id, val) => {
    const e = document.getElementById(id);
    if (e) e.textContent = val;
  };

  setTxt('progVitalProfileName', ov.profile_name || state.activeProfile || '--');
  setTxt('progVitalGlobalLevel', `Level ${ov.global_level}`);
  setTxt('progVitalMoney', `$${Number(ov.money || 0).toLocaleString()}`);
  setTxt('progVitalCars', ov.cars_owned || 0);
  setTxt('progVitalHouses', ov.houses_owned || 0);
  setTxt('progVitalClubRank', `Rank ${ov.club_rank || 0}`);

  // Base Skills Summary Meters
  const skills = ov.skills;
  if (skills) {
    // Competition
    const comp = skills.competition;
    setTxt('compLevelBadge', `Lvl ${comp.level} / ${comp.max_level}`);
    setTxt('compPointsVal', `${comp.points.toLocaleString()} / ${comp.max_points.toLocaleString()} pts`);
    const compBar = document.getElementById('compProgressBar');
    if (compBar) compBar.style.width = `${comp.percent}%`;

    // Discovery
    const disc = skills.discovery;
    setTxt('discLevelBadge', `Lvl ${disc.level} / ${disc.max_level}`);
    setTxt('discPointsVal', `${disc.points.toLocaleString()} / ${disc.max_points.toLocaleString()} pts`);
    const discBar = document.getElementById('discProgressBar');
    if (discBar) discBar.style.width = `${disc.percent}%`;

    // Collection
    const coll = skills.collection;
    setTxt('collLevelBadge', `Lvl ${coll.level} / ${coll.max_level}`);
    setTxt('collPointsVal', `${coll.points.toLocaleString()} / ${coll.max_points.toLocaleString()} pts`);
    const collBar = document.getElementById('collProgressBar');
    if (collBar) collBar.style.width = `${coll.percent}%`;

    // Social
    const soc = skills.social;
    setTxt('socLevelBadge', `Lvl ${soc.level} / ${soc.max_level}`);
    setTxt('socPointsVal', `${soc.points.toLocaleString()} / ${soc.max_points.toLocaleString()} pts`);
    const socBar = document.getElementById('socProgressBar');
    if (socBar) socBar.style.width = `${soc.percent}%`;
  }

  // Casino Island Summary
  const casSum = ov.casino_summary;
  if (casSum) {
    setTxt('vitalCasinoLevel', `Lvl ${casSum.level} / ${casSum.max_level}`);
    setTxt('vitalCasinoPoints', `${casSum.points.toLocaleString()} / ${casSum.max_points.toLocaleString()} (${casSum.percent}%)`);

    const distEl = document.getElementById('vitalCasinoDistinction');
    if (distEl) {
      if (casSum.is_ace) distEl.textContent = 'Ace of Casino';
      else if (casSum.is_vip) distEl.textContent = 'VIP Member';
      else distEl.textContent = 'Standard Member';
    }

    const vipBadge = document.getElementById('casinoVipBadge');
    if (vipBadge) {
      vipBadge.className = `badge ${casSum.is_vip ? 'badge-vip active' : 'badge-locked'}`;
      vipBadge.textContent = casSum.is_vip ? 'VIP Active' : 'VIP Locked';
    }

    const aceBadge = document.getElementById('casinoAceBadge');
    if (aceBadge) {
      aceBadge.className = `badge ${casSum.is_ace ? 'badge-ace active' : 'badge-locked'}`;
      aceBadge.textContent = casSum.is_ace ? 'Ace Active' : 'Ace Locked';
    }
  }

  const casSkills = ov.casino_skills;
  if (casSkills) {
    if (casSkills.competition) {
      const c = casSkills.competition;
      setTxt('casCompLevelBadge', `Lvl ${c.level} / ${c.max_level}`);
      setTxt('casCompPointsVal', `${c.points.toLocaleString()} / ${c.max_points.toLocaleString()} pts`);
      const bar = document.getElementById('casCompProgressBar');
      if (bar) bar.style.width = `${c.percent}%`;
    }
    if (casSkills.discovery) {
      const d = casSkills.discovery;
      setTxt('casDiscLevelBadge', `Lvl ${d.level} / ${d.max_level}`);
      setTxt('casDiscPointsVal', `${d.points.toLocaleString()} / ${d.max_points.toLocaleString()} pts`);
      const bar = document.getElementById('casDiscProgressBar');
      if (bar) bar.style.width = `${d.percent}%`;
    }
    if (casSkills.collection) {
      const c = casSkills.collection;
      setTxt('casCollLevelBadge', `Lvl ${c.level} / ${c.max_level}`);
      setTxt('casCollPointsVal', `${c.points.toLocaleString()} / ${c.max_points.toLocaleString()} pts`);
      const bar = document.getElementById('casCollProgressBar');
      if (bar) bar.style.width = `${c.percent}%`;
    }
    if (casSkills.social) {
      const s = casSkills.social;
      setTxt('casSocLevelBadge', `Lvl ${s.level} / ${s.max_level}`);
      setTxt('casSocPointsVal', `${s.points.toLocaleString()} / ${s.max_points.toLocaleString()} pts`);
      const bar = document.getElementById('casSocProgressBar');
      if (bar) bar.style.width = `${s.percent}%`;
    }
  }

  // Roads Discovery Table
  renderRoadsTable(ov.roads_summary);
}

function renderRoadsTable(roadsSummary) {
  const tbody = document.getElementById('roadsTableBody');
  if (!tbody || !roadsSummary) return;

  const areaNames = [
    { area: "Ibiza Area 1", island: "Ibiza" },
    { area: "Ibiza Area 2", island: "Ibiza" },
    { area: "Hawaii Area 1", island: "Hawaii" },
    { area: "Hawaii Area 2", island: "Hawaii" },
    { area: "Hawaii Area 3", island: "Hawaii" },
    { area: "Hawaii Area 4", island: "Hawaii" },
  ];

  tbody.innerHTML = '';
  const unlocked = roadsSummary.unlocked || [];
  const totals = roadsSummary.total || [];

  areaNames.forEach((item, idx) => {
    const u = unlocked[idx] || 0;
    const t = totals[idx] || 0;
    const pct = t > 0 ? ((u / t) * 100).toFixed(1) : 0;
    const isFull = Number(pct) >= 100;

    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td><strong>${escapeHtml(item.area)}</strong></td>
      <td>${escapeHtml(item.island)}</td>
      <td>${u}</td>
      <td>${t}</td>
      <td><strong>${pct}%</strong></td>
      <td>
        <span class="badge ${isFull ? 'badge-online' : 'badge-dim'}">
          ${isFull ? '100% Complete' : 'In Progress'}
        </span>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

function renderProgressionSkillTab(skillKey, containerId, headerInfoId) {
  const st = state.progressionState;
  if (!st || !st.skills) return;

  const skillData = st.skills[skillKey];
  const container = document.getElementById(containerId);
  const headerInfo = document.getElementById(headerInfoId);
  if (!skillData || !container) return;

  const skillMeta = st.overview?.skills?.[skillKey];
  if (skillMeta && headerInfo) {
    headerInfo.textContent = `Level ${skillMeta.level} / ${skillMeta.max_level} • ${skillMeta.points.toLocaleString()} / ${skillMeta.max_points.toLocaleString()} pts (${skillMeta.percent}%)`;
  }

  container.innerHTML = '';

  Object.values(skillData.sections || {}).forEach(sec => {
    const secBox = document.createElement('div');
    secBox.className = 'section-box';

    let secEarned = 0;
    let secTotal = 0;
    (sec.objectives || []).forEach(o => {
      secEarned += o.earned_points || 0;
      secTotal += o.points || 0;
    });

    const secHeader = document.createElement('div');
    secHeader.className = 'section-header';
    secHeader.innerHTML = `
      <div class="sec-title-wrap">
        <span class="section-title">${escapeHtml(sec.name)}</span>
        <span class="section-summary-tag">${secEarned.toLocaleString()} / ${secTotal.toLocaleString()} pts</span>
      </div>
      <div class="section-actions">
        <button class="btn btn-xs btn-primary btn-max-sec">Max Section</button>
        <button class="btn btn-xs btn-secondary btn-reset-sec">Reset</button>
      </div>
    `;

    secHeader.querySelector('.btn-max-sec').addEventListener('click', () => {
      applyProgressionPreset('max_section', sec.id);
    });
    secHeader.querySelector('.btn-reset-sec').addEventListener('click', () => {
      applyProgressionPreset('reset_section', sec.id);
    });

    const secBody = document.createElement('div');
    secBody.className = 'section-body';

    const grid = document.createElement('div');
    grid.className = 'objectives-grid';

    (sec.objectives || []).forEach(obj => {
      const item = document.createElement('div');
      item.className = `objective-item ${obj.completed ? 'completed' : ''}`;

      const left = document.createElement('div');
      left.className = 'objective-left';

      const cb = document.createElement('input');
      cb.type = 'checkbox';
      cb.className = 'objective-checkbox';
      cb.checked = Boolean(obj.completed);
      cb.addEventListener('change', (e) => {
        setProgressionObjective(obj.id, e.target.checked);
      });

      const info = document.createElement('div');
      info.className = 'objective-info';

      const name = document.createElement('span');
      name.className = 'objective-name';
      name.textContent = obj.name;

      const tags = document.createElement('div');
      tags.className = 'objective-tags';
      tags.innerHTML = `
        <span class="tag-island">${escapeHtml(obj.island || 'Global')}</span>
        <span class="tag-points">+${obj.points} pts</span>
      `;

      info.appendChild(name);
      info.appendChild(tags);

      left.appendChild(cb);
      left.appendChild(info);

      const right = document.createElement('div');
      right.className = 'objective-right';

      if (obj.type === 'counter' || obj.type === 'counter_linear') {
        const input = document.createElement('input');
        input.type = 'number';
        input.className = 'counter-input';
        input.value = obj.current_value;
        input.min = 0;
        input.max = Math.max(obj.target_value * 2, 100);
        input.addEventListener('change', (e) => {
          setProgressionObjective(obj.id, parseInt(e.target.value) || 0);
        });
        right.appendChild(input);
      }

      item.appendChild(left);
      item.appendChild(right);
      grid.appendChild(item);
    });

    secBody.appendChild(grid);
    secBox.appendChild(secHeader);
    secBox.appendChild(secBody);
    container.appendChild(secBox);
  });
}

function renderProgressionCasinoTab() {
  const st = state.progressionState;
  if (!st || !st.casino_skills) return;

  const casinoSkills = st.casino_skills;
  const container = document.getElementById('casinoSectionsContainer');
  const headerInfo = document.getElementById('casinoHeaderPts');
  if (!container) return;

  const casSum = st.overview?.casino_summary;
  if (casSum && headerInfo) {
    headerInfo.textContent = `Level ${casSum.level} / ${casSum.max_level} • ${casSum.points.toLocaleString()} / ${casSum.max_points.toLocaleString()} pts (${casSum.percent}%)`;
  }

  container.innerHTML = '';
  const filter = state.activeCasinoFilter || 'all';

  Object.entries(casinoSkills).forEach(([skillKey, skillData]) => {
    if (filter !== 'all' && filter !== skillKey) {
      return;
    }

    const skillGroup = document.createElement('div');
    skillGroup.className = 'casino-skill-group';

    const skillMeta = st.overview?.casino_skills?.[skillKey];
    const skillHeader = document.createElement('div');
    skillHeader.className = 'casino-skill-group-header';
    skillHeader.innerHTML = `
      <div class="sec-title-wrap">
        <span class="casino-skill-title">${escapeHtml(skillData.name)}</span>
        <span class="badge">Lvl ${skillMeta ? skillMeta.level : 0} / ${skillData.max_level}</span>
        <span class="skill-pts">${skillMeta ? skillMeta.points.toLocaleString() : 0} / ${skillData.max_points.toLocaleString()} pts</span>
      </div>
      <div class="skill-actions">
        <button class="btn btn-xs btn-primary btn-max-cas-sk">Max ${escapeHtml(skillData.name)}</button>
        <button class="btn btn-xs btn-secondary btn-reset-cas-sk">Reset</button>
      </div>
    `;

    skillHeader.querySelector('.btn-max-cas-sk').addEventListener('click', () => {
      applyProgressionPreset('max_casino_skill', skillKey);
    });
    skillHeader.querySelector('.btn-reset-cas-sk').addEventListener('click', () => {
      applyProgressionPreset('reset_casino_skill', skillKey);
    });

    skillGroup.appendChild(skillHeader);

    Object.values(skillData.sections || {}).forEach(sec => {
      const secBox = document.createElement('div');
      secBox.className = 'section-box';

      let secEarned = 0;
      let secTotal = 0;
      (sec.objectives || []).forEach(o => {
        secEarned += o.earned_points || 0;
        secTotal += o.points || 0;
      });

      const secHeader = document.createElement('div');
      secHeader.className = 'section-header';
      secHeader.innerHTML = `
        <div class="sec-title-wrap">
          <span class="section-title">${escapeHtml(sec.name)}</span>
          <span class="section-summary-tag">${secEarned.toLocaleString()} / ${secTotal.toLocaleString()} pts</span>
        </div>
        <div class="section-actions">
          <button class="btn btn-xs btn-secondary btn-max-cas-sec">Max Section</button>
          <button class="btn btn-xs btn-secondary btn-reset-cas-sec">Reset</button>
        </div>
      `;

      secHeader.querySelector('.btn-max-cas-sec').addEventListener('click', () => {
        applyProgressionPreset('max_casino_section', sec.id);
      });
      secHeader.querySelector('.btn-reset-cas-sec').addEventListener('click', () => {
        applyProgressionPreset('reset_casino_section', sec.id);
      });

      const secBody = document.createElement('div');
      secBody.className = 'section-body';

      const grid = document.createElement('div');
      grid.className = 'objectives-grid';

      (sec.objectives || []).forEach(obj => {
        const item = document.createElement('div');
        item.className = `objective-item ${obj.completed ? 'completed' : ''}`;

        const left = document.createElement('div');
        left.className = 'objective-left';

        const cb = document.createElement('input');
        cb.type = 'checkbox';
        cb.className = 'objective-checkbox';
        cb.checked = Boolean(obj.completed);
        cb.addEventListener('change', (e) => {
          setProgressionObjective(obj.id, e.target.checked);
        });

        const info = document.createElement('div');
        info.className = 'objective-info';

        const name = document.createElement('span');
        name.className = 'objective-name';
        name.textContent = obj.name;

        const tags = document.createElement('div');
        tags.className = 'objective-tags';
        tags.innerHTML = `
          <span class="tag-island tag-casino">Casino Island</span>
          <span class="tag-points">+${obj.points} pts</span>
          ${obj.target_value > 1 ? `<span class="tag-progress">${obj.current_value} / ${obj.target_value}</span>` : ''}
        `;

        info.appendChild(name);
        info.appendChild(tags);

        left.appendChild(cb);
        left.appendChild(info);

        const right = document.createElement('div');
        right.className = 'objective-right';

        if (obj.target_value > 1 && obj.type !== 'prog_bool' && obj.type !== 'vip_access' && obj.type !== 'prog_two_cars') {
          const input = document.createElement('input');
          input.type = 'number';
          input.className = 'counter-input';
          input.value = obj.current_value;
          input.min = 0;
          input.max = Math.max(obj.target_value * 2, 100);
          input.addEventListener('change', (e) => {
            setProgressionObjective(obj.id, parseInt(e.target.value) || 0);
          });
          right.appendChild(input);
        }

        item.appendChild(left);
        item.appendChild(right);
        grid.appendChild(item);
      });

      secBody.appendChild(grid);
      secBox.appendChild(secHeader);
      secBox.appendChild(secBody);
      skillGroup.appendChild(secBox);
    });

    container.appendChild(skillGroup);
  });
}

// ==========================================
// --- RAW TREE EDITOR (TAB 6) LOGIC ---
// ==========================================

async function loadRawTreeRoot() {
  if (!el.rawTreeContainer) return;
  if (!state.activeProfile) {
    el.rawTreeContainer.innerHTML = `
      <div class="empty-state-banner">
        <div class="empty-icon">
          <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
        </div>
        <div class="empty-text">
          <strong>No Save Profile Loaded:</strong> Please load a save profile to explore and mutate the raw XMBF node hierarchy.
        </div>
      </div>
    `;
    return;
  }

  el.rawTreeContainer.innerHTML = '<div class="tree-loading">Loading root nodes...</div>';
  try {
    const res = await fetch('/api/raw-tree');
    const data = await res.json();
    if (!data.success) throw new Error(data.error);

    el.rawTreeContainer.innerHTML = '';
    const rootNodes = data.children || [];
    if (!rootNodes.length) {
      el.rawTreeContainer.innerHTML = '<div style="padding: 1.5rem; color: var(--text-dim);">No root nodes found in savefile.</div>';
      return;
    }

    const treeList = document.createElement('div');
    treeList.className = 'tree-nodes-list';
    rootNodes.forEach(child => {
      treeList.appendChild(createTreeNodeElement(child));
    });
    el.rawTreeContainer.appendChild(treeList);
    addLog(`Loaded ${rootNodes.length} top-level XMBF nodes into Raw Tree Editor.`, "info");
  } catch (err) {
    el.rawTreeContainer.innerHTML = `<div class="tree-error">Failed loading raw tree: ${escapeHtml(err.message)}</div>`;
    addLog(`Raw tree load error: ${err.message}`, "error");
  }
}

function createTreeNodeElement(nodeInfo) {
  const nodeEl = document.createElement('div');
  nodeEl.className = 'tree-node';
  nodeEl.dataset.path = nodeInfo.path;

  const row = document.createElement('div');
  row.className = 'tree-node-row';

  const expander = document.createElement('button');
  expander.className = 'tree-expander';
  if (nodeInfo.is_container) {
    expander.innerHTML = '<svg viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg>';
  } else {
    expander.classList.add('leaf');
    expander.innerHTML = '<span class="tree-bullet">•</span>';
  }

  const icon = document.createElement('span');
  icon.className = 'tree-icon';
  icon.innerHTML = nodeInfo.is_container
    ? '<svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>'
    : '<svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>';

  const label = document.createElement('span');
  label.className = 'tree-label';
  label.textContent = nodeInfo.name;

  const badge = document.createElement('span');
  badge.className = `tree-badge type-${(nodeInfo.type || 'unknown').toLowerCase()}`;
  badge.textContent = nodeInfo.type;

  row.appendChild(expander);
  row.appendChild(icon);
  row.appendChild(label);
  row.appendChild(badge);

  if (!nodeInfo.is_container && nodeInfo.value !== null && nodeInfo.value !== undefined) {
    const valPreview = document.createElement('span');
    valPreview.className = 'tree-val-preview';
    valPreview.textContent = String(nodeInfo.value);
    row.appendChild(valPreview);
  } else if (nodeInfo.is_container && nodeInfo.child_count !== undefined) {
    const countPreview = document.createElement('span');
    countPreview.className = 'tree-count-preview';
    countPreview.textContent = `(${nodeInfo.child_count} children)`;
    row.appendChild(countPreview);
  }

  nodeEl.appendChild(row);

  let childrenContainer = null;
  let isExpanded = false;

  if (nodeInfo.is_container) {
    expander.addEventListener('click', (e) => {
      e.stopPropagation();
      if (!isExpanded) {
        if (!childrenContainer) {
          childrenContainer = document.createElement('div');
          childrenContainer.className = 'tree-node-children';
          nodeEl.appendChild(childrenContainer);
          loadContainerChildren(nodeInfo.path, childrenContainer, expander);
        } else {
          childrenContainer.style.display = 'block';
        }
        expander.classList.add('open');
        isExpanded = true;
      } else {
        if (childrenContainer) childrenContainer.style.display = 'none';
        expander.classList.remove('open');
        isExpanded = false;
      }
    });
  }

  row.addEventListener('click', () => {
    document.querySelectorAll('.tree-node-row.selected').forEach(r => r.classList.remove('selected'));
    row.classList.add('selected');
    inspectNode(nodeInfo);
  });

  return nodeEl;
}

async function loadContainerChildren(parentPath, containerEl, expanderBtn) {
  containerEl.innerHTML = '<div class="tree-loading-inline">Loading...</div>';
  try {
    const res = await fetch(`/api/raw-tree?path=${encodeURIComponent(parentPath)}`);
    const data = await res.json();
    if (!data.success) throw new Error(data.error);

    containerEl.innerHTML = '';
    const children = data.children || [];
    if (!children.length) {
      containerEl.innerHTML = '<div class="tree-empty-inline">Empty container</div>';
      return;
    }
    children.forEach(child => {
      containerEl.appendChild(createTreeNodeElement(child));
    });
  } catch (err) {
    containerEl.innerHTML = `<div class="tree-error-inline">${escapeHtml(err.message)}</div>`;
  }
}

function inspectNode(nodeInfo) {
  state.selectedRawNode = nodeInfo;
  if (!el.rawInspectorPanel) return;

  if (el.rawInspectorEmpty) el.rawInspectorEmpty.style.display = 'none';
  if (el.rawInspectorContent) el.rawInspectorContent.style.display = 'flex';

  if (el.rawInspectorKindBadge) {
    el.rawInspectorKindBadge.textContent = nodeInfo.is_container ? 'CONTAINER' : 'LEAF SCALAR';
    el.rawInspectorKindBadge.className = `inspector-kind-badge ${nodeInfo.is_container ? 'badge-container' : 'badge-scalar'}`;
  }

  if (el.rawMetaName) el.rawMetaName.textContent = nodeInfo.name;
  if (el.rawMetaType) el.rawMetaType.textContent = nodeInfo.type;
  if (el.rawMetaOffset) el.rawMetaOffset.textContent = nodeInfo.offset !== undefined ? `0x${nodeInfo.offset.toString(16).toUpperCase()} (${nodeInfo.offset})` : '--';
  if (el.rawMetaPath) el.rawMetaPath.textContent = nodeInfo.path || nodeInfo.name;

  if (el.rawMetaBounds) {
    if (nodeInfo.min_val !== undefined && nodeInfo.max_val !== undefined) {
      el.rawMetaBounds.textContent = `[${nodeInfo.min_val} ... ${nodeInfo.max_val}]`;
    } else if (nodeInfo.capacity !== undefined) {
      el.rawMetaBounds.textContent = `Max length: ${nodeInfo.capacity} bytes`;
    } else {
      el.rawMetaBounds.textContent = 'None';
    }
  }

  if (nodeInfo.is_container) {
    if (el.rawScalarEditBlock) el.rawScalarEditBlock.style.display = 'none';
    if (el.rawContainerBlock) el.rawContainerBlock.style.display = 'block';
    if (el.rawChildCount) el.rawChildCount.textContent = `${nodeInfo.child_count || 0} child nodes`;

    if (el.rawChildrenTableBody) {
      el.rawChildrenTableBody.innerHTML = '';
      (nodeInfo.children || []).forEach(c => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td><strong>${escapeHtml(c.name)}</strong></td>
          <td><span class="badge badge-subtle">${escapeHtml(c.type)}</span></td>
          <td>${c.is_container ? `<em>${c.child_count || 0} items</em>` : escapeHtml(String(c.value !== null && c.value !== undefined ? c.value : ''))}</td>
        `;
        tr.style.cursor = 'pointer';
        tr.addEventListener('click', () => {
          inspectNode(c);
        });
        el.rawChildrenTableBody.appendChild(tr);
      });
    }
  } else {
    if (el.rawContainerBlock) el.rawContainerBlock.style.display = 'none';
    if (el.rawScalarEditBlock) el.rawScalarEditBlock.style.display = 'block';

    if (el.rawNodeInputLabel) el.rawNodeInputLabel.textContent = `Node Value (${nodeInfo.type})`;
    if (el.rawNodeInput) {
      el.rawNodeInput.value = nodeInfo.value !== null && nodeInfo.value !== undefined ? nodeInfo.value : '';
      if (nodeInfo.type === 'bool') {
        el.rawNodeInput.placeholder = 'true / false or 1 / 0';
      } else if (nodeInfo.type.startsWith('int') || nodeInfo.type.startsWith('uint') || nodeInfo.type === 'float') {
        el.rawNodeInput.placeholder = 'Numeric value';
      } else {
        el.rawNodeInput.placeholder = 'String value';
      }
    }

    if (el.rawNodeInputHint) {
      if (nodeInfo.min_val !== undefined && nodeInfo.max_val !== undefined) {
        el.rawNodeInputHint.textContent = `Valid range: ${nodeInfo.min_val} to ${nodeInfo.max_val}`;
      } else if (nodeInfo.capacity !== undefined) {
        el.rawNodeInputHint.textContent = `In-place string limit: cannot exceed ${nodeInfo.capacity} bytes`;
      } else {
        el.rawNodeInputHint.textContent = 'In-place byte mutation with validation';
      }
    }
  }
}

async function applyRawNodeValue() {
  if (!state.selectedRawNode) {
    showToast("Please select a leaf node first.", "error");
    return;
  }
  const node = state.selectedRawNode;
  if (node.is_container) {
    showToast("Cannot set value on a container node.", "error");
    return;
  }

  const rawVal = el.rawNodeInput?.value ?? '';
  let parsedVal = rawVal;

  if (node.type === 'bool') {
    const s = String(rawVal).toLowerCase().trim();
    parsedVal = (s === 'true' || s === '1' || s === 'yes');
  } else if (node.type.startsWith('int') || node.type.startsWith('uint')) {
    parsedVal = parseInt(rawVal, 10);
    if (isNaN(parsedVal)) {
      showToast("Please enter a valid integer.", "error");
      return;
    }
  } else if (node.type === 'float') {
    parsedVal = parseFloat(rawVal);
    if (isNaN(parsedVal)) {
      showToast("Please enter a valid float.", "error");
      return;
    }
  }

  addLog(`Mutating raw node '${node.path}' in-place...`, "info");
  try {
    const res = await fetch('/api/raw-node/set', {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ path: node.path, value: parsedVal })
    });
    const data = await res.json();
    if (!data.success) throw new Error(data.error);

    node.value = parsedVal;
    if (data.summary) {
      state.saveSummary = data.summary;
      updateUI(state.saveSummary);
    }

    const rowEl = document.querySelector(`.tree-node[data-path="${node.path}"] .tree-val-preview`);
    if (rowEl) rowEl.textContent = String(parsedVal);

    addLog(`[RAW MUTATION SUCCESS] ${data.message}`, "success");
    showToast(`Updated '${node.name}' to ${parsedVal}!`, "success");
  } catch (err) {
    addLog(`Raw mutation failed: ${err.message}`, "error");
    showToast(`Mutation Error: ${err.message}`, "error");
  }
}

async function searchRawTree() {
  const query = el.rawTreeSearchInput?.value?.trim();
  if (!query) {
    showToast("Please enter a search query.", "info");
    return;
  }

  addLog(`Searching XMBF raw tree for '${query}'...`, "info");
  if (el.rawSearchResults) el.rawSearchResults.style.display = 'block';
  if (el.rawSearchResultsList) el.rawSearchResultsList.innerHTML = '<div style="padding: 1rem; color: var(--text-dim);">Searching 30,000+ nodes...</div>';

  try {
    const res = await fetch(`/api/raw-tree?search=${encodeURIComponent(query)}`);
    const data = await res.json();
    if (!data.success) throw new Error(data.error);

    const matches = data.matches || [];
    if (el.rawSearchCount) el.rawSearchCount.textContent = matches.length;

    if (!matches.length) {
      if (el.rawSearchResultsList) el.rawSearchResultsList.innerHTML = '<div style="padding: 1rem; color: var(--text-dim);">No nodes matched your query.</div>';
      return;
    }

    if (el.rawSearchResultsList) {
      el.rawSearchResultsList.innerHTML = '';
      matches.forEach(m => {
        const item = document.createElement('div');
        item.className = 'search-result-item';
        item.innerHTML = `
          <div class="result-top">
            <span class="result-name">${escapeHtml(m.name)}</span>
            <span class="badge ${m.is_container ? 'badge-container' : 'badge-scalar'}">${escapeHtml(m.type)}</span>
          </div>
          <div class="result-path">${escapeHtml(m.path)}</div>
          ${!m.is_container && m.value !== null && m.value !== undefined ? `<div class="result-value">Value: <code>${escapeHtml(String(m.value))}</code></div>` : ''}
        `;
        item.addEventListener('click', () => {
          inspectNode(m);
        });
        el.rawSearchResultsList.appendChild(item);
      });
    }

    addLog(`Found ${matches.length} raw node matches for '${query}'.`, "success");
  } catch (err) {
    if (el.rawSearchResultsList) el.rawSearchResultsList.innerHTML = `<div class="tree-error">${escapeHtml(err.message)}</div>`;
    addLog(`Raw search failed: ${err.message}`, "error");
  }
}

