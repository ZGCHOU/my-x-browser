// ICANX Browser - Renderer for Advanced UI
// i18n structure moved to i18n.js and locales/

let globalSettings = { preProxies: [], subscriptions: [], mode: 'single', enablePreProxy: false };
let currentEditId = null;
let confirmCallback = null;
let currentProxyGroup = 'manual';
let inputCallback = null;
let searchText = '';
let viewMode = localStorage.getItem('icanx_view') || 'grid';
let currentFilter = 'all';
let runningProfiles = new Set();

// ============================================================================
// Initialization
// ============================================================================
async function init() {
    // Hide splash after 1.5s
    setTimeout(() => {
        const splash = document.getElementById('splash');
        if (splash) splash.classList.add('hidden');
    }, 1500);

    // Load settings
    globalSettings = await window.electronAPI.getSettings();
    if (!globalSettings.preProxies) globalSettings.preProxies = [];
    if (!globalSettings.subscriptions) globalSettings.subscriptions = [];

    // Update proxy toggle UI
    updateProxyToggle();

    // Load profiles
    await loadProfiles();

    // Check running profiles
    await updateRunningStatus();

    // Event listeners
    window.electronAPI.onProfileStatus(({ id, status }) => {
        if (status === 'running') runningProfiles.add(id);
        else runningProfiles.delete(id);
        updateRunningStatus();
        loadProfiles();
    });

    window.electronAPI.onRefreshProfiles(() => loadProfiles());
    window.electronAPI.onApiLaunchProfile((id) => launch(id));

    // Initialize dropdowns
    initCustomTimezoneDropdown('addTimezone', 'addTimezoneDropdown');
    initCustomTimezoneDropdown('editTimezone', 'editTimezoneDropdown');
    initCustomCityDropdown('addCity', 'addCityDropdown');
    initCustomCityDropdown('editCity', 'editCityDropdown');
    initCustomLanguageDropdown('addLanguage', 'addLanguageDropdown');
    initCustomLanguageDropdown('editLanguage', 'editLanguageDropdown');

    // Check for updates silently
    checkUpdatesSilent();

    // Click outside handlers
    document.addEventListener('click', (e) => {
        const importMenu = document.getElementById('importMenu');
        if (importMenu && !importMenu.contains(e.target) && !e.target.closest('[onclick="toggleImportMenu()"]')) {
            importMenu.classList.remove('active');
        }
    });
}

// ============================================================================
// Profile Loading & Rendering
// ============================================================================
async function loadProfiles() {
    try {
        const profiles = await window.electronAPI.getProfiles();
        const container = document.getElementById('profileList');
        
        // Update stats
        document.getElementById('stat-total').textContent = profiles.length;
        document.getElementById('stat-active').textContent = runningProfiles.size;

        // Filter profiles
        let filtered = profiles.filter(p => {
            const text = searchText.toLowerCase();
            return p.name.toLowerCase().includes(text) ||
                (p.tags && p.tags.some(t => t.toLowerCase().includes(text))) ||
                p.proxyStr.toLowerCase().includes(text);
        });

        // Apply status filter
        if (currentFilter === 'running') {
            filtered = filtered.filter(p => runningProfiles.has(p.id));
        } else if (currentFilter === 'stopped') {
            filtered = filtered.filter(p => !runningProfiles.has(p.id));
        }

        // Update view mode
        updateViewMode();

        // Render
        if (filtered.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                            <rect x="2" y="3" width="20" height="14" rx="2" ry="2"/>
                            <line x1="8" y1="21" x2="16" y2="21"/>
                            <line x1="12" y1="17" x2="12" y2="21"/>
                        </svg>
                    </div>
                    <h3>${searchText ? '未找到结果' : '暂无环境'}</h3>
                    <p>${searchText ? '尝试不同的搜索关键词' : '创建您的第一个浏览器环境以开始使用'}</p>
                    ${!searchText ? '<button class="btn btn-primary" onclick="openAddModal()">创建环境</button>' : ''}
                </div>
            `;
            return;
        }

        container.innerHTML = '';
        
        if (viewMode === 'grid') {
            container.className = 'profiles-container profiles-grid';
            filtered.forEach(p => {
                container.appendChild(createProfileCard(p));
            });
        } else {
            container.className = 'profiles-container profiles-list';
            filtered.forEach(p => {
                container.appendChild(createProfileRow(p));
            });
        }
    } catch (e) {
        console.error('加载环境失败：', e);
    }
}

function createProfileCard(p) {
    const fp = p.fingerprint || {};
    const screen = fp.screen || { width: 0, height: 0 };
    const isRunning = runningProfiles.has(p.id);
    const firstLetter = p.name.charAt(0).toUpperCase();
    
    let tagsHtml = '';
    if (p.tags && p.tags.length > 0) {
        tagsHtml = p.tags.slice(0, 2).map(tag => `<span class="tag" title="${escapeHtml(tag)}">${escapeHtml(tag.length > 6 ? tag.substring(0, 6) + '...' : tag)}</span>`).join('');
        if (p.tags.length > 2) tagsHtml += `<span class="tag">+${p.tags.length - 2}</span>`;
    }

    const card = document.createElement('div');
    card.className = `profile-card ${isRunning ? 'running' : ''}`;
    card.innerHTML = `
        <div class="profile-header">
            <div class="profile-identity">
                <div class="profile-avatar ${isRunning ? 'running' : ''}">${firstLetter}</div>
                <div class="profile-info">
                    <h3>${escapeHtml(p.name)}</h3>
                    <div class="profile-meta">
                        <span>${p.proxyStr.split('://')[0].toUpperCase() || 'N/A'}</span>
                        <span>•</span>
                        <span>${screen.width || 'Auto'}×${screen.height || 'Auto'}</span>
                    </div>
                </div>
            </div>
            <div class="profile-status ${isRunning ? 'running' : ''}">
                <span class="profile-status-dot"></span>
                ${isRunning ? '运行中' : '已停止'}
            </div>
        </div>
        <div class="profile-details">
            <div class="detail-item">
                <div class="detail-label">时区</div>
                <div class="detail-value">${fp.timezone || '自动'}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">语言</div>
                <div class="detail-value">${fp.language || '自动'}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">前置代理</div>
                <div class="detail-value">${p.preProxyOverride === 'default' ? '默认' : p.preProxyOverride === 'on' ? '开' : p.preProxyOverride === 'off' ? '关' : '默认'}</div>
            </div>
        </div>
        <div class="profile-tags">${tagsHtml}</div>
        <div class="profile-actions">
            <button class="btn-launch ${isRunning ? 'running' : ''}" onclick="event.stopPropagation(); toggleProfile('${p.id}')">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                    ${isRunning 
                        ? '<rect x="6" y="6" width="12" height="12" rx="2"/>' 
                        : '<polygon points="5 3 19 12 5 21 5 3"/>'
                    }
                </svg>
                ${isRunning ? '停止' : '启动'}
            </button>
            <button class="btn-action" onclick="event.stopPropagation(); openEditModal('${p.id}')">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                    <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                </svg>
            </button>
            <button class="btn-action" onclick="event.stopPropagation(); showConfirm('确定删除此环境？', () => remove('${p.id}'))">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="3 6 5 6 21 6"/>
                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                </svg>
            </button>
        </div>
    `;
    
    card.onclick = () => openEditModal(p.id);
    return card;
}

function createProfileRow(p) {
    const fp = p.fingerprint || {};
    const isRunning = runningProfiles.has(p.id);
    const firstLetter = p.name.charAt(0).toUpperCase();
    
    let tagsHtml = '';
    if (p.tags && p.tags.length > 0) {
        tagsHtml = p.tags.slice(0, 2).map(tag => `<span class="row-tag">${tag}</span>`).join('');
    }

    const row = document.createElement('div');
    row.className = `profile-row ${isRunning ? 'running' : ''}`;
    row.innerHTML = `
        <div class="row-avatar ${isRunning ? 'running' : ''}">${firstLetter}</div>
        <div class="row-info">
            <h4>${escapeHtml(p.name)}</h4>
            <div class="row-meta">${fp.timezone || '自动'} • ${fp.language || '自动'}</div>
        </div>
        <div class="row-tags">${tagsHtml}</div>
        <div class="row-status ${isRunning ? 'running' : ''}">
            <span class="profile-status-dot"></span>
            ${isRunning ? '运行中' : '已停止'}
        </div>
        <div class="row-actions">
            <button class="btn-action" onclick="event.stopPropagation(); toggleProfile('${p.id}')" title="${isRunning ? '停止' : '启动'}">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                    ${isRunning 
                        ? '<rect x="6" y="6" width="12" height="12" rx="2"/>' 
                        : '<polygon points="5 3 19 12 5 21 5 3"/>'
                    }
                </svg>
            </button>
            <button class="btn-action" onclick="event.stopPropagation(); openEditModal('${p.id}')" title="编辑">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                    <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                </svg>
            </button>
            <button class="btn-action" onclick="event.stopPropagation(); showConfirm('确定删除此环境？', () => remove('${p.id}'))" title="删除">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="3 6 5 6 21 6"/>
                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                </svg>
            </button>
        </div>
    `;
    
    row.onclick = () => openEditModal(p.id);
    return row;
}

// ============================================================================
// Profile Actions
// ============================================================================
async function toggleProfile(id) {
    if (runningProfiles.has(id)) {
        // Stop profile - for now just reload to check status
        await updateRunningStatus();
        loadProfiles();
    } else {
        await launch(id);
    }
}

async function launch(id) {
    try {
        const watermarkStyle = localStorage.getItem('icanx_watermark_style') || 'enhanced';
        const msg = await window.electronAPI.launchProfile(id, watermarkStyle);
        if (msg && msg.includes(':')) showAlert(msg);
        runningProfiles.add(id);
        updateRunningStatus();
        loadProfiles();
    } catch (e) {
        showAlert('错误：' + e.message);
    }
}

async function updateRunningStatus() {
    try {
        const runningIds = await window.electronAPI.getRunningIds();
        runningProfiles = new Set(runningIds);
        document.getElementById('stat-active').textContent = runningProfiles.size;
    } catch (e) {
        console.error('获取运行状态失败：', e);
    }
}

async function remove(id) {
    try {
        await window.electronAPI.deleteProfile(id);
        await loadProfiles();
    } catch (e) {
        showAlert('删除失败：' + e.message);
    }
}

// ============================================================================
// Modal Functions
// ============================================================================
function openAddModal() {
    document.getElementById('addName').value = '';
    document.getElementById('addProxy').value = '';
    document.getElementById('addTags').value = '';
    document.getElementById('addTimezone').value = '';
    document.getElementById('addCity').value = '';
    document.getElementById('addLanguage').value = '';
    document.getElementById('addResW').value = '';
    document.getElementById('addResH').value = '';
    document.getElementById('addPreProxyOverride').value = 'default';
    
    document.getElementById('addModal').classList.add('active');
}

function closeAddModal() {
    document.getElementById('addModal').classList.remove('active');
}

async function saveNewProfile() {
    const nameBase = document.getElementById('addName').value.trim();
    const proxyText = document.getElementById('addProxy').value.trim();
    const tagsStr = document.getElementById('addTags').value;
    const timezone = document.getElementById('addTimezone').value || 'Auto';
    const cityInput = document.getElementById('addCity').value;
    const language = getLanguageCode(document.getElementById('addLanguage').value);
    const preProxyOverride = document.getElementById('addPreProxyOverride').value;
    const resW = parseInt(document.getElementById('addResW').value);
    const resH = parseInt(document.getElementById('addResH').value);
    
    let screen = null;
    if (!isNaN(resW) && !isNaN(resH)) screen = { width: resW, height: resH };
    
    let city = null, geolocation = null;
    if (cityInput && cityInput !== 'Auto (IP Based)') {
        const cityData = window.CITY_DATA ? window.CITY_DATA.find(c => c.name === cityInput) : null;
        if (cityData) {
            city = cityData.name;
            geolocation = { latitude: cityData.lat, longitude: cityData.lng, accuracy: 100 };
        }
    }
    
    const tags = tagsStr.split(/[,，]/).map(s => s.trim()).filter(s => s);
    const proxyLines = proxyText.split('\n').map(l => l.trim()).filter(l => l);
    
    if (proxyLines.length === 0 && !nameBase) {
        showAlert('请输入名称或代理链接');
        return;
    }

    let createdCount = 0;
    for (let i = 0; i < Math.max(1, proxyLines.length); i++) {
        const proxyStr = proxyLines[i] || '';
        let name;
        
        if (!nameBase) {
            name = getProxyRemark(proxyStr) || `Profile-${String(i + 1).padStart(2, '0')}`;
        } else if (proxyLines.length <= 1) {
            name = nameBase;
        } else {
            name = `${nameBase}-${String(i + 1).padStart(2, '0')}`;
        }
        
        try {
            await window.electronAPI.saveProfile({ name, proxyStr, tags, timezone, city, geolocation, language, screen, preProxyOverride });
            createdCount++;
        } catch (e) {
            console.error(`创建环境 ${name} 失败：`, e);
        }
    }
    
    closeAddModal();
    await loadProfiles();
    if (createdCount > 1) showAlert(`成功创建 ${createdCount} 个环境`);
}

async function openEditModal(id) {
    const profiles = await window.electronAPI.getProfiles();
    const p = profiles.find(x => x.id === id);
    if (!p) return;
    
    currentEditId = id;
    const fp = p.fingerprint || {};
    
    document.getElementById('editId').value = id;
    document.getElementById('editName').value = p.name;
    document.getElementById('editProxy').value = p.proxyStr;
    document.getElementById('editTags').value = (p.tags || []).join(', ');
    document.getElementById('editTimezone').value = fp.timezone || '';
    document.getElementById('editCity').value = fp.city || '';
    document.getElementById('editLanguage').value = getLanguageName(fp.language || 'auto');
    document.getElementById('editPreProxyOverride').value = p.preProxyOverride || 'default';
    document.getElementById('editResW').value = fp.screen?.width || '';
    document.getElementById('editResH').value = fp.screen?.height || '';
    document.getElementById('editDebugPort').value = p.debugPort || '';
    document.getElementById('editCustomArgs').value = p.customArgs || '';
    
    // Show/hide debug port and custom args based on settings
    const settings = await window.electronAPI.getSettings();
    document.getElementById('debugPortSection').style.display = settings.enableRemoteDebugging ? 'block' : 'none';
    document.getElementById('customArgsSection').style.display = settings.enableCustomArgs ? 'block' : 'none';
    
    document.getElementById('editModal').classList.add('active');
}

function closeEditModal() {
    document.getElementById('editModal').classList.remove('active');
    currentEditId = null;
}

async function saveEditProfile() {
    if (!currentEditId) return;
    
    const profiles = await window.electronAPI.getProfiles();
    let p = profiles.find(x => x.id === currentEditId);
    if (!p) return;
    
    p.name = document.getElementById('editName').value;
    p.proxyStr = document.getElementById('editProxy').value;
    p.tags = document.getElementById('editTags').value.split(/[,，]/).map(s => s.trim()).filter(s => s);
    p.preProxyOverride = document.getElementById('editPreProxyOverride').value;
    
    if (!p.fingerprint) p.fingerprint = {};
    p.fingerprint.timezone = document.getElementById('editTimezone').value;
    p.fingerprint.language = getLanguageCode(document.getElementById('editLanguage').value);
    p.fingerprint.screen = { 
        width: parseInt(document.getElementById('editResW').value) || 1920, 
        height: parseInt(document.getElementById('editResH').value) || 1080 
    };
    p.fingerprint.window = p.fingerprint.screen;
    
    const cityInput = document.getElementById('editCity').value;
    if (cityInput && cityInput !== 'Auto (IP Based)') {
        const cityData = window.CITY_DATA ? window.CITY_DATA.find(c => c.name === cityInput) : null;
        if (cityData) {
            p.fingerprint.city = cityData.name;
            p.fingerprint.geolocation = { latitude: cityData.lat, longitude: cityData.lng, accuracy: 100 };
        }
    } else {
        delete p.fingerprint.city;
        delete p.fingerprint.geolocation;
    }
    
    const debugPort = document.getElementById('editDebugPort').value.trim();
    p.debugPort = debugPort ? parseInt(debugPort) : null;
    p.customArgs = document.getElementById('editCustomArgs').value.trim();
    
    await window.electronAPI.updateProfile(p);
    closeEditModal();
    loadProfiles();
}

async function deleteCurrentProfile() {
    if (!currentEditId) return;
    await window.electronAPI.deleteProfile(currentEditId);
    closeEditModal();
    await loadProfiles();
}

// ============================================================================
// Filter & View Functions
// ============================================================================
function filterProfiles(text) {
    searchText = text.toLowerCase();
    loadProfiles();
}

function setFilter(filter) {
    currentFilter = filter;
    document.querySelectorAll('.filter-tab').forEach(tab => tab.classList.remove('active'));
    event.target.classList.add('active');
    loadProfiles();
}

function setViewMode(mode) {
    viewMode = mode;
    localStorage.setItem('icanx_view', mode);
    updateViewMode();
    loadProfiles();
}

function updateViewMode() {
    document.getElementById('viewGrid').classList.toggle('active', viewMode === 'grid');
    document.getElementById('viewList').classList.toggle('active', viewMode === 'list');
}

// ============================================================================
// Proxy Manager
// ============================================================================
async function openProxyManager() {
    globalSettings = await window.electronAPI.getSettings();
    if (!globalSettings.subscriptions) globalSettings.subscriptions = [];
    
    document.getElementById('proxyModal').classList.add('active');
    renderProxyList();
}

function closeProxyManager() {
    document.getElementById('proxyModal').classList.remove('active');
}

function renderProxyList() {
    const modeSel = document.getElementById('proxyMode');
    if (modeSel.options.length === 0) {
        modeSel.innerHTML = `
            <option value="single">Single Node</option>
            <option value="balance">Load Balance</option>
            <option value="failover">Failover</option>
        `;
    }
    modeSel.value = globalSettings.mode || 'single';
    
    const list = (globalSettings.preProxies || []).filter(p => {
        if (currentProxyGroup === 'manual') return !p.groupId || p.groupId === 'manual';
        return p.groupId === currentProxyGroup;
    });
    
    const container = document.getElementById('proxyList');
    container.innerHTML = '';
    
    list.forEach(p => {
        const item = document.createElement('div');
        item.className = 'proxy-item';
        
        let latClass = '';
        let latText = '-';
        if (p.latency !== undefined) {
            if (p.latency === -1 || p.latency === 9999) {
                latText = 'Fail';
            } else {
                latText = `${p.latency}ms`;
                latClass = p.latency < 500 ? 'good' : '';
            }
        }
        
        item.innerHTML = `
            <input type="${globalSettings.mode === 'single' ? 'radio' : 'checkbox'}" 
                name="proxySelect" ${globalSettings.selectedId === p.id ? 'checked' : ''}
                onchange="selectProxy('${p.id}')">
            <span class="proxy-protocol">${p.url.split('://')[0].toUpperCase()}</span>
            <span class="proxy-name">${escapeHtml(p.remark || 'Node')}</span>
            <span class="proxy-latency ${latClass}">${latText}</span>
            <div class="proxy-actions">
                <button class="btn-action" onclick="testSingleProxy('${p.id}')">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
                    </svg>
                </button>
                <button class="btn-action" onclick="deleteProxy('${p.id}')">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="18" y1="6" x2="6" y2="18"/>
                        <line x1="6" y1="6" x2="18" y2="18"/>
                    </svg>
                </button>
            </div>
        `;
        container.appendChild(item);
    });
}

async function selectProxy(id) {
    globalSettings.selectedId = id;
    await window.electronAPI.saveSettings(globalSettings);
}

async function deleteProxy(id) {
    globalSettings.preProxies = globalSettings.preProxies.filter(p => p.id !== id);
    renderProxyList();
    await window.electronAPI.saveSettings(globalSettings);
}

async function testSingleProxy(id) {
    const p = globalSettings.preProxies.find(x => x.id === id);
    if (!p) return;
    
    try {
        const res = await window.electronAPI.invoke('test-proxy-latency', p.url);
        p.latency = res.success ? res.latency : -1;
        renderProxyList();
    } catch (e) {
        console.error(e);
    }
}

async function saveProxySettings() {
    globalSettings.mode = document.getElementById('proxyMode').value;
    await window.electronAPI.saveSettings(globalSettings);
    closeProxyManager();
    updateProxyToggle();
}

// ============================================================================
// Proxy Toggle in Sidebar
// ============================================================================
function togglePreProxy() {
    globalSettings.enablePreProxy = !globalSettings.enablePreProxy;
    window.electronAPI.saveSettings(globalSettings);
    updateProxyToggle();
}

function updateProxyToggle() {
    const toggle = document.getElementById('proxyToggle');
    const status = document.getElementById('proxyStatusDot');
    const display = document.getElementById('currentProxyDisplay');
    
    const enabled = globalSettings.enablePreProxy;
    toggle.classList.toggle('active', enabled);
    status.classList.toggle('active', enabled);
    
    if (!enabled) {
        display.textContent = 'OFF';
    } else {
        let count = globalSettings.mode === 'single' 
            ? (globalSettings.selectedId ? 1 : 0)
            : (globalSettings.preProxies || []).filter(p => p.enable !== false).length;
        display.textContent = `${globalSettings.mode || 'single'} [${count}]`;
    }
}

function toggleNotify() {
    const checkbox = document.getElementById('notifyCheckbox');
    checkbox.classList.toggle('checked');
    globalSettings.notify = checkbox.classList.contains('checked');
}

// ============================================================================
// Export/Import Functions
// ============================================================================
let exportType = '';

function openExportModal() {
    document.getElementById('exportModal').classList.add('active');
}

function closeExportModal() {
    document.getElementById('exportModal').classList.remove('active');
}

function selectExportType(type) {
    exportType = type;
    document.querySelectorAll('input[name="exportType"]').forEach(r => {
        r.checked = r.value === type;
    });
}

async function confirmExport() {
    if (!exportType) {
        showAlert('请选择导出类型');
        return;
    }
    
    closeExportModal();
    
    try {
        const profiles = await window.electronAPI.getProfiles();
        const result = await window.electronAPI.invoke('export-selected-data', {
            type: exportType,
            profileIds: profiles.map(p => p.id)
        });
        
        if (result.success) showAlert(`Export successful! ${result.count} profiles exported`);
        else if (!result.cancelled) showAlert(result.error || 'Export failed');
    } catch (e) {
        showAlert('导出失败：' + e.message);
    }
}

function toggleImportMenu() {
    document.getElementById('importMenu').classList.toggle('active');
}

function closeImportMenu() {
    document.getElementById('importMenu').classList.remove('active');
}

async function importData() {
    try {
        const result = await window.electronAPI.invoke('import-data');
        if (result) {
            globalSettings = await window.electronAPI.getSettings();
            loadProfiles();
            showAlert('导入成功！');
        }
    } catch (e) {
        showAlert('导入失败：' + e.message);
    }
}

async function importFullBackup() {
    showAlert('此版本暂未支持导入备份功能');
}

// ============================================================================
// Settings Functions
// ============================================================================
async function openSettings() {
    document.getElementById('settingsModal').classList.add('active');
    loadUserExtensions();
    
    const settings = await window.electronAPI.getSettings();
    
    // Load toggles
    const remoteToggle = document.getElementById('enableRemoteDebugging');
    const argsToggle = document.getElementById('enableCustomArgs');
    const apiToggle = document.getElementById('enableApiServer');
    
    if (remoteToggle) remoteToggle.classList.toggle('active', settings.enableRemoteDebugging);
    if (argsToggle) argsToggle.classList.toggle('active', settings.enableCustomArgs);
    if (apiToggle) {
        apiToggle.classList.toggle('active', settings.enableApiServer);
        document.getElementById('apiPortSection').style.display = settings.enableApiServer ? 'block' : 'none';
        document.getElementById('apiStatus').style.display = settings.enableApiServer ? 'inline-block' : 'none';
    }
    
    // Load data path
    const pathInfo = await window.electronAPI.invoke('get-data-path-info');
    document.getElementById('currentDataPath').textContent = pathInfo.currentPath;
    
    // Load watermark style
    const watermarkStyle = localStorage.getItem('nexus_watermark_style') || 'enhanced';
    document.querySelectorAll('input[name="watermarkStyle"]').forEach(r => {
        r.checked = r.value === watermarkStyle;
    });
}

function closeSettings() {
    document.getElementById('settingsModal').classList.remove('active');
}

function switchSettingsTab(tab) {
    document.querySelectorAll('.settings-tab').forEach(t => t.classList.remove('active'));
    event.target.classList.add('active');
    
    document.querySelectorAll('.settings-section').forEach(s => s.classList.remove('active'));
    document.getElementById('settings-' + tab).classList.add('active');
}

function handleDevToggle(el) {
    el.classList.toggle('active');
    const enabled = el.classList.contains('active');
    
    if (el.id === 'enableRemoteDebugging') {
        saveSetting('enableRemoteDebugging', enabled);
    } else if (el.id === 'enableCustomArgs') {
        saveSetting('enableCustomArgs', enabled);
    } else if (el.id === 'enableApiServer') {
        saveSetting('enableApiServer', enabled);
        document.getElementById('apiPortSection').style.display = enabled ? 'block' : 'none';
        document.getElementById('apiStatus').style.display = enabled ? 'inline-block' : 'none';
    }
}

async function saveSetting(key, value) {
    const settings = await window.electronAPI.getSettings();
    settings[key] = value;
    await window.electronAPI.saveSettings(settings);
}

async function saveApiPort() {
    const port = parseInt(document.getElementById('apiPortInput').value) || 12138;
    await saveSetting('apiPort', port);
    document.getElementById('apiPortDisplay').textContent = port;
    showAlert('API 端口已保存');
}

function saveWatermarkStyle(style) {
    localStorage.setItem('icanx_watermark_style', style);
}

async function selectDataDirectory() {
    const newPath = await window.electronAPI.invoke('select-data-directory');
    if (!newPath) return;
    
    const migrate = confirm('Migrate existing data to new directory?');
    const result = await window.electronAPI.invoke('set-data-directory', { newPath, migrate });
    
    if (result.success) {
        document.getElementById('currentDataPath').textContent = newPath;
        showAlert('数据目录已更改，请重启应用');
    } else {
        showAlert('失败：' + result.error);
    }
}

async function resetDataDirectory() {
    if (!confirm('Reset to default data directory?')) return;
    
    const result = await window.electronAPI.invoke('reset-data-directory');
    if (result.success) {
        const info = await window.electronAPI.invoke('get-data-path-info');
        document.getElementById('currentDataPath').textContent = info.defaultPath;
        showAlert('重置成功，请重启应用');
    }
}

// ============================================================================
// Extension Management
// ============================================================================
async function selectExtensionFolder() {
    const path = await window.electronAPI.invoke('select-extension-folder');
    if (path) {
        await window.electronAPI.invoke('add-user-extension', path);
        await loadUserExtensions();
        showAlert('扩展已添加');
    }
}

async function loadUserExtensions() {
    const exts = await window.electronAPI.invoke('get-user-extensions');
    const list = document.getElementById('userExtensionList');
    
    if (exts.length === 0) {
        list.innerHTML = '<div style="text-align:center; color:var(--text-tertiary); padding:20px;">未添加扩展</div>';
        return;
    }
    
    list.innerHTML = exts.map(ext => `
        <div class="ext-item">
            <div class="ext-info">
                <div class="ext-name">${ext.split(/[\\/]/).pop()}</div>
                <div class="ext-path">${ext}</div>
            </div>
            <button class="btn btn-danger" onclick="removeUserExtension('${ext.replace(/\\/g, '\\\\')}')">Remove</button>
        </div>
    `).join('');
}

async function removeUserExtension(path) {
    await window.electronAPI.invoke('remove-user-extension', path);
    await loadUserExtensions();
}

// ============================================================================
// Help & About
// ============================================================================
function openHelp() {
    document.getElementById('helpModal').classList.add('active');
    renderHelpContent();
}

function closeHelp() {
    document.getElementById('helpModal').classList.remove('active');
}

function switchHelpTab(tab) {
    document.querySelectorAll('#helpModal .settings-tab').forEach(t => t.classList.remove('active'));
    event.target.classList.add('active');
    
    document.querySelectorAll('#helpModal .settings-section').forEach(s => s.classList.remove('active'));
    document.getElementById('help-' + tab).classList.add('active');
}

function renderHelpContent() {
    const manualHTML = `
        <div style="margin-bottom:24px;">
            <h4 style="color:var(--accent-primary); margin-bottom:12px; font-size:16px;">1. 创建环境</h4>
            <p style="font-size:14px; color:var(--text-secondary); line-height:1.6;">点击"新建环境"，输入名称和代理链接。系统将自动生成具有随机硬件信息的唯一指纹。</p>
        </div>
        <div style="margin-bottom:24px;">
            <h4 style="color:var(--accent-primary); margin-bottom:12px; font-size:16px;">2. 启动环境</h4>
            <p style="font-size:14px; color:var(--text-secondary); line-height:1.6;">点击启动按钮，绿色指示灯表示运行状态。每个环境完全隔离。</p>
        </div>
        <div style="margin-bottom:24px;">
            <h4 style="color:var(--accent-primary); margin-bottom:12px; font-size:16px;">3. 链式代理（可选）</h4>
            <p style="font-size:14px; color:var(--text-secondary); line-height:1.6;">使用链式代理隐藏 IP。在侧边栏启用并配置代理节点。</p>
        </div>
        <div>
            <h4 style="color:var(--accent-primary); margin-bottom:12px; font-size:16px;">4. 最佳实践</h4>
            <ul style="font-size:14px; color:var(--text-secondary); line-height:1.8; padding-left:20px;">
                <li>使用高质量住宅 IP</li>
                <li>每个环境固定一个账号</li>
                <li>避免频繁切换</li>
                <li>模拟真实用户行为</li>
            </ul>
        </div>
    `;
    
    const aboutHTML = `
        <div style="text-align:center; margin-bottom:32px;">
            <div style="width:80px; height:80px; background:var(--accent-gradient); border-radius:20px; margin:0 auto 16px; display:flex; align-items:center; justify-content:center; font-size:36px; font-weight:700; color:white;">i</div>
            <h2 style="font-size:24px; font-weight:700; margin-bottom:8px;">ICANX Browser</h2>
            <p style="color:var(--text-secondary); font-size:14px;">v1.4.0 · 指纹浏览器</p>
        </div>
        
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px; margin-bottom:24px;">
            <div style="background:var(--bg-glass-light); padding:16px; border-radius:12px; border:1px solid var(--border-subtle);">
                <div style="font-size:12px; color:var(--accent-primary); font-weight:600; margin-bottom:4px;">🧬 真实 Chrome</div>
                <div style="font-size:11px; color:var(--text-tertiary);">原生内核 + JS 注入</div>
            </div>
            <div style="background:var(--bg-glass-light); padding:16px; border-radius:12px; border:1px solid var(--border-subtle);">
                <div style="font-size:12px; color:var(--accent-primary); font-weight:600; margin-bottom:4px;">🔐 指纹伪装</div>
                <div style="font-size:11px; color:var(--text-tertiary);">硬件信息随机化</div>
            </div>
            <div style="background:var(--bg-glass-light); padding:16px; border-radius:12px; border:1px solid var(--border-subtle);">
                <div style="font-size:12px; color:var(--accent-primary); font-weight:600; margin-bottom:4px;">🌍 60+ 语言</div>
                <div style="font-size:11px; color:var(--text-tertiary);">时区和语言伪装</div>
            </div>
            <div style="background:var(--bg-glass-light); padding:16px; border-radius:12px; border:1px solid var(--border-subtle);">
                <div style="font-size:12px; color:var(--accent-primary); font-weight:600; margin-bottom:4px;">⚡ GPU 加速</div>
                <div style="font-size:11px; color:var(--text-tertiary);">流畅的 UI 性能</div>
            </div>
        </div>
        
        <div style="background:var(--bg-glass-light); padding:16px; border-radius:12px; border:1px solid var(--border-subtle); margin-bottom:24px;">
            <div style="font-size:12px; font-weight:600; margin-bottom:12px; color:var(--text-primary);">检测状态</div>
            <div style="display:flex; flex-wrap:wrap; gap:16px; font-size:12px; color:var(--text-secondary);">
                <span style="color:var(--success);">✓ Browserscan 通过</span>
                <span style="color:var(--success);">✓ Pixelscan 干净</span>
                <span style="color:var(--success);">✓ 真实 TLS 指纹</span>
            </div>
        </div>
    `;
    
    document.getElementById('help-manual').innerHTML = manualHTML;
    document.getElementById('help-about').innerHTML = aboutHTML;
}

// ============================================================================
// Subscription Management
// ============================================================================
function openSubEditModal(isNew) {
    document.getElementById('subId').value = '';
    document.getElementById('subName').value = '';
    document.getElementById('subUrl').value = '';
    document.getElementById('subInterval').value = '24';
    document.getElementById('subCustomInterval').style.display = 'none';
    document.getElementById('btnDelSub').style.display = isNew ? 'none' : 'block';
    
    document.getElementById('subEditModal').classList.add('active');
}

function closeSubEditModal() {
    document.getElementById('subEditModal').classList.remove('active');
}

async function saveSubscription() {
    const id = document.getElementById('subId').value;
    const name = document.getElementById('subName').value || 'Subscription';
    const url = document.getElementById('subUrl').value.trim();
    let interval = document.getElementById('subInterval').value;
    
    if (interval === 'custom') interval = document.getElementById('subCustomInterval').value;
    if (!url) return;
    
    let sub;
    if (id) {
        sub = globalSettings.subscriptions.find(s => s.id === id);
        if (sub) { sub.name = name; sub.url = url; sub.interval = interval; }
    } else {
        sub = { id: `sub-${Date.now()}`, name, url, interval, lastUpdated: 0 };
        globalSettings.subscriptions.push(sub);
    }
    
    closeSubEditModal();
    await updateSubscriptionNodes(sub);
    await window.electronAPI.saveSettings(globalSettings);
}

async function deleteSubscription() {
    const id = document.getElementById('subId').value;
    if (!id) return;
    
    globalSettings.subscriptions = globalSettings.subscriptions.filter(s => s.id !== id);
    globalSettings.preProxies = globalSettings.preProxies.filter(p => p.groupId !== id);
    closeSubEditModal();
    renderProxyList();
    await window.electronAPI.saveSettings(globalSettings);
}

async function updateSubscriptionNodes(sub) {
    try {
        const content = await window.electronAPI.invoke('fetch-url', sub.url);
        let decoded = content;
        try { if (!content.includes('://')) decoded = decodeBase64Content(content); } catch (e) {}
        
        const lines = decoded.split(/[\r\n]+/);
        globalSettings.preProxies = globalSettings.preProxies.filter(p => p.groupId !== sub.id);
        
        let count = 0;
        lines.forEach(line => {
            line = line.trim();
            if (line && line.includes('://')) {
                const remark = getProxyRemark(line) || `Node ${count + 1}`;
                globalSettings.preProxies.push({ 
                    id: Date.now().toString() + Math.random().toString(36).substr(2, 9), 
                    remark, url: line, enable: true, groupId: sub.id 
                });
                count++;
            }
        });
        
        sub.lastUpdated = Date.now();
        showAlert(`订阅已更新：${count} 个节点`);
    } catch (e) {
        showAlert('更新失败：' + e.message);
    }
}

// ============================================================================
// Utility Functions
// ============================================================================
function showAlert(msg) {
    document.getElementById('alertMsg').textContent = msg;
    document.getElementById('alertModal').classList.add('active');
}

function closeAlert() {
    document.getElementById('alertModal').classList.remove('active');
}

function showConfirm(msg, callback) {
    document.getElementById('confirmMsg').textContent = msg;
    document.getElementById('confirmModal').classList.add('active');
    confirmCallback = callback;
}

function closeConfirm(result) {
    document.getElementById('confirmModal').classList.remove('active');
    if (result && confirmCallback) confirmCallback();
    confirmCallback = null;
}

function showInput(title, callback) {
    document.getElementById('inputModalTitle').textContent = title;
    document.getElementById('inputModalValue').value = '';
    document.getElementById('inputModal').classList.add('active');
    inputCallback = callback;
}

function closeInputModal() {
    document.getElementById('inputModal').classList.remove('active');
    inputCallback = null;
}

function submitInputModal() {
    const val = document.getElementById('inputModalValue').value.trim();
    if (val && inputCallback) inputCallback(val);
    closeInputModal();
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function stringToColor(str) {
    let hash = 0;
    for (let i = 0; i < str.length; i++) hash = str.charCodeAt(i) + ((hash << 5) - hash);
    const c = (hash & 0x00FFFFFF).toString(16).toUpperCase();
    return '#' + '00000'.substring(0, 6 - c.length) + c;
}

function decodeBase64Content(str) {
    try {
        str = str.replace(/-/g, '+').replace(/_/g, '/');
        return decodeURIComponent(atob(str).split('').map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2)).join(''));
    } catch (e) { return atob(str); }
}

function getProxyRemark(link) {
    if (!link) return '';
    link = link.trim();
    try {
        if (link.startsWith('vmess://')) {
            const base64Str = link.replace('vmess://', '');
            const configStr = decodeBase64Content(base64Str);
            try { return JSON.parse(configStr).ps || ''; } catch (e) { return ''; }
        } else if (link.includes('#')) {
            return decodeURIComponent(link.split('#')[1]).trim();
        }
    } catch (e) {}
    return '';
}

function getLanguageName(code) {
    if (!code || code === 'auto') return 'Auto (System Default)';
    if (!window.LANGUAGE_DATA) return code;
    const entry = window.LANGUAGE_DATA.find(x => x.code === code);
    return entry ? entry.name : code;
}

function getLanguageCode(name) {
    if (!name || name === 'Auto (System Default)') return 'auto';
    if (!window.LANGUAGE_DATA) return 'auto';
    const entry = window.LANGUAGE_DATA.find(x => x.name === name);
    return entry ? entry.code : 'auto';
}

// ============================================================================
// Dropdown Initializers
// ============================================================================
function initCustomTimezoneDropdown(inputId, dropdownId) {
    const input = document.getElementById(inputId);
    const dropdown = document.getElementById(dropdownId);
    if (!input || !dropdown || !window.TIMEZONES) return;

    let selectedIndex = -1;

    function populateDropdown(filter = '') {
        const filtered = window.TIMEZONES.filter(tz => tz.toLowerCase().includes(filter.toLowerCase()));
        dropdown.innerHTML = filtered.map((tz, index) =>
            `<div class="dropdown-item" data-value="${tz}" data-index="${index}">${tz}</div>`
        ).join('');
        selectedIndex = -1;
    }

    function hideDropdown() { dropdown.classList.remove('active'); selectedIndex = -1; }
    function selectItem(value) { input.value = value; hideDropdown(); }

    input.addEventListener('focus', () => { populateDropdown(''); dropdown.classList.add('active'); });
    input.addEventListener('input', () => { populateDropdown(input.value); dropdown.classList.add('active'); });
    input.addEventListener('keydown', (e) => {
        const items = dropdown.querySelectorAll('.dropdown-item');
        if (e.key === 'ArrowDown') { e.preventDefault(); selectedIndex = Math.min(selectedIndex + 1, items.length - 1); updateSelection(items); }
        else if (e.key === 'ArrowUp') { e.preventDefault(); selectedIndex = Math.max(selectedIndex - 1, 0); updateSelection(items); }
        else if (e.key === 'Enter' && selectedIndex >= 0) { e.preventDefault(); selectItem(items[selectedIndex].dataset.value); }
        else if (e.key === 'Escape') hideDropdown();
    });

    function updateSelection(items) {
        items.forEach((item, index) => item.classList.toggle('selected', index === selectedIndex));
        if (items[selectedIndex]) items[selectedIndex].scrollIntoView({ block: 'nearest' });
    }

    dropdown.addEventListener('click', (e) => { const item = e.target.closest('.dropdown-item'); if (item) selectItem(item.dataset.value); });
    document.addEventListener('click', (e) => { if (!input.contains(e.target) && !dropdown.contains(e.target)) hideDropdown(); });
}

function initCustomCityDropdown(inputId, dropdownId) {
    const input = document.getElementById(inputId);
    const dropdown = document.getElementById(dropdownId);
    if (!input || !dropdown) return;

    let allOptions = [{ name: 'Auto (IP Based)' }];
    if (window.CITY_DATA) allOptions = allOptions.concat(window.CITY_DATA);
    let selectedIndex = -1;

    function populateDropdown(filter = '') {
        const lowerFilter = filter.toLowerCase();
        const shouldShowAll = filter === 'Auto (IP Based)' || filter === '';
        const filtered = shouldShowAll ? allOptions : allOptions.filter(item => item.name.toLowerCase().includes(lowerFilter));
        dropdown.innerHTML = filtered.map((item, index) => `<div class="dropdown-item" data-name="${item.name}" data-index="${index}">${item.name}</div>`).join('');
        selectedIndex = -1;
    }

    function hideDropdown() { dropdown.classList.remove('active'); selectedIndex = -1; }
    function selectItem(name) { input.value = name; hideDropdown(); }

    input.addEventListener('focus', () => { populateDropdown(''); dropdown.classList.add('active'); });
    input.addEventListener('input', () => { populateDropdown(input.value); dropdown.classList.add('active'); });
    input.addEventListener('keydown', (e) => {
        const items = dropdown.querySelectorAll('.dropdown-item');
        if (e.key === 'ArrowDown') { e.preventDefault(); selectedIndex = Math.min(selectedIndex + 1, items.length - 1); updateSelection(items); }
        else if (e.key === 'ArrowUp') { e.preventDefault(); selectedIndex = Math.max(selectedIndex - 1, 0); updateSelection(items); }
        else if (e.key === 'Enter' && selectedIndex >= 0) { e.preventDefault(); selectItem(items[selectedIndex].dataset.name); }
        else if (e.key === 'Escape') hideDropdown();
    });

    function updateSelection(items) {
        items.forEach((item, index) => item.classList.toggle('selected', index === selectedIndex));
        if (items[selectedIndex]) items[selectedIndex].scrollIntoView({ block: 'nearest' });
    }

    dropdown.addEventListener('click', (e) => { const item = e.target.closest('.dropdown-item'); if (item) selectItem(item.dataset.name); });
    document.addEventListener('click', (e) => { if (!input.contains(e.target) && !dropdown.contains(e.target)) hideDropdown(); });
}

function initCustomLanguageDropdown(inputId, dropdownId) {
    const input = document.getElementById(inputId);
    const dropdown = document.getElementById(dropdownId);
    if (!input || !dropdown || !window.LANGUAGE_DATA) return;

    const allOptions = window.LANGUAGE_DATA;
    let selectedIndex = -1;

    function populateDropdown(filter = '') {
        const lowerFilter = filter.toLowerCase();
        const shouldShowAll = filter === '' || filter === 'Auto (System Default)';
        const filtered = shouldShowAll ? allOptions : allOptions.filter(item => item.name.toLowerCase().includes(lowerFilter));
        dropdown.innerHTML = filtered.map((item, index) => `<div class="dropdown-item" data-code="${item.code}" data-index="${index}">${item.name}</div>`).join('');
        selectedIndex = -1;
    }

    function hideDropdown() { dropdown.classList.remove('active'); selectedIndex = -1; }
    function selectItem(name) { input.value = name; hideDropdown(); }

    input.addEventListener('focus', () => { populateDropdown(''); dropdown.classList.add('active'); });
    input.addEventListener('input', () => { populateDropdown(input.value); dropdown.classList.add('active'); });
    input.addEventListener('keydown', (e) => {
        const items = dropdown.querySelectorAll('.dropdown-item');
        if (e.key === 'ArrowDown') { e.preventDefault(); selectedIndex = Math.min(selectedIndex + 1, items.length - 1); updateSelection(items); }
        else if (e.key === 'ArrowUp') { e.preventDefault(); selectedIndex = Math.max(selectedIndex - 1, 0); updateSelection(items); }
        else if (e.key === 'Enter' && selectedIndex >= 0) { e.preventDefault(); selectItem(items[selectedIndex].innerText); }
        else if (e.key === 'Escape') hideDropdown();
    });

    function updateSelection(items) {
        items.forEach((item, index) => item.classList.toggle('selected', index === selectedIndex));
        if (items[selectedIndex]) items[selectedIndex].scrollIntoView({ block: 'nearest' });
    }

    dropdown.addEventListener('click', (e) => { const item = e.target.closest('.dropdown-item'); if (item) selectItem(item.innerText); });
    document.addEventListener('click', (e) => { if (!input.contains(e.target) && !dropdown.contains(e.target)) hideDropdown(); });
}

// ============================================================================
// Update Functions
// ============================================================================
async function checkUpdates() {
    const btn = document.getElementById('btnUpdate');
    btn.classList.add('update-badge');
    
    try {
        const appRes = await window.electronAPI.invoke('check-app-update');
        if (appRes.update) {
            showConfirm(`发现新版本：v${appRes.remote}，是否前往下载？`, () => {
                window.electronAPI.invoke('open-url', appRes.url);
            });
            return;
        }
        
        const xrayRes = await window.electronAPI.invoke('check-xray-update');
        if (xrayRes.update) {
            showAlert(`发现 Xray 新版本：v${xrayRes.remote}`);
        } else {
            showAlert('当前已是最新版本');
        }
    } catch (e) {
        showAlert('检查更新失败：' + e.message);
    }
}

async function checkUpdatesSilent() {
    try {
        const appRes = await window.electronAPI.invoke('check-app-update');
        if (appRes.update) {
            document.getElementById('btnUpdate').classList.add('update-badge');
        }
    } catch (e) {}
}

function openGithub() {
    window.electronAPI.invoke('open-url', 'https://github.com/EchoHS/GeekezBrowser');
}

function toggleLang() {
    // Language toggle - simplified for new UI
    showAlert('语言：中文 / English');
}

function showDashboard() {
    // Already on dashboard
}

// ============================================================================
// Password Modal Functions
// ============================================================================
function closePasswordModal() {
    document.getElementById('passwordModal').classList.remove('active');
}

function submitPassword() {
    const password = document.getElementById('backupPassword').value;
    const confirm = document.getElementById('backupPasswordConfirm').value;
    
    if (!password) {
        showAlert('请输入密码');
        return;
    }
    if (password !== confirm) {
        showAlert('两次输入的密码不一致');
        return;
    }
    
    closePasswordModal();
    showAlert('密码已设置');
}

// Start
document.addEventListener('DOMContentLoaded', init);
