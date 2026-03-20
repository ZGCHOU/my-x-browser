<template>
  <div class="dashboard">
    <aside class="sidebar">
      <div class="logo">ICANX ADMIN</div>
      <nav>
        <div :class="['nav-item', { active: currentView === 'users' }]" @click="currentView = 'users'">
          <UsersIcon size="18" />
          <span>用户管理</span>
        </div>
        <div :class="['nav-item', { active: currentView === 'tags' }]" @click="currentView = 'tags'">
          <TagIcon size="18" />
          <span>标签管理</span>
        </div>
        <div :class="['nav-item', { active: currentView === 'stats' }]" @click="currentView = 'stats'">
          <BarChart3Icon size="18" />
          <span>数据统计</span>
        </div>
        <div :class="['nav-item', { active: currentView === 'logs' }]" @click="currentView = 'logs'">
          <FileTextIcon size="18" />
          <span>操作日志</span>
        </div>
      </nav>
      <div class="user-profile">
        <p>{{ adminUser.username }}</p>
        <span class="role-badge">超级管理员</span>
        <button @click="logout" class="logout-btn">
          <LogOutIcon size="14" />
          退出
        </button>
      </div>
    </aside>

    <main class="main-content">
      <!-- 用户管理视图 -->
      <div v-if="currentView === 'users'">
        <header>
          <div>
            <h1>用户管理系统</h1>
            <p class="subtitle">管理所有子账号的访问权限和期限</p>
          </div>
          <button @click="openAddModal" class="btn btn-primary">
            <PlusIcon size="18" />
            创建新账号
          </button>
        </header>

        <!-- 统计卡片 -->
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-icon blue"><UsersIcon size="20" /></div>
            <div class="stat-info">
              <span class="stat-value">{{ stats.total_users || 0 }}</span>
              <span class="stat-label">总用户数</span>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon green"><UserCheckIcon size="20" /></div>
            <div class="stat-info">
              <span class="stat-value">{{ stats.active_count || 0 }}</span>
              <span class="stat-label">正常用户</span>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon orange"><ClockIcon size="20" /></div>
            <div class="stat-info">
              <span class="stat-value">{{ stats.expiring_soon || 0 }}</span>
              <span class="stat-label">即将过期 (7天)</span>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon red"><AlertCircleIcon size="20" /></div>
            <div class="stat-info">
              <span class="stat-value">{{ stats.expired || 0 }}</span>
              <span class="stat-label">已过期</span>
            </div>
          </div>
        </div>

        <!-- 用户列表 -->
        <div class="user-list">
          <div class="list-header">
            <h3>用户列表</h3>
            <div class="filter-box">
              <div class="search-box">
                <SearchIcon size="16" />
                <input v-model="searchQuery" type="text" placeholder="搜索用户名..." />
              </div>
              <div class="tag-filter" v-if="allTags.length > 0">
                <select v-model="selectedTagFilter" class="input-field">
                  <option value="">所有标签</option>
                  <option v-for="tag in allTags" :key="tag.id" :value="tag.id">{{ tag.name }}</option>
                </select>
              </div>
            </div>
          </div>
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>用户名</th>
                <th>标签</th>
                <th>角色</th>
                <th>状态</th>
                <th>授权截止</th>
                <th>剩余天数</th>
                <th>最大配置</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in filteredUsers" :key="user.id" :class="{ 'expired': isExpired(user.expire_at), 'expiring-soon': isExpiringSoon(user.expire_at) }">
                <td>{{ user.id }}</td>
                <td>
                  <div class="user-info">
                    <span class="username">{{ user.username }}</span>
                  </div>
                </td>
                <td>
                  <div class="user-tags">
                    <span 
                      v-for="tag in user.tags" 
                      :key="tag.id" 
                      class="tag-badge"
                      :style="{ backgroundColor: tag.color + '20', color: tag.color, borderColor: tag.color + '40' }"
                    >
                      {{ tag.name }}
                    </span>
                    <span v-if="!user.tags || user.tags.length === 0" class="no-tags">-</span>
                  </div>
                </td>
                <td>
                  <span :class="['role-badge', user.role]">
                    {{ user.role === 'admin' ? '超级管理员' : '普通用户' }}
                  </span>
                </td>
                <td>
                  <span :class="['status-badge', user.status]">
                    {{ user.status === 'active' ? '正常' : '禁用' }}
                  </span>
                </td>
                <td>{{ formatDate(user.expire_at) }}</td>
                <td>
                  <span :class="['days-badge', getDaysClass(user.expire_at)]">
                    {{ getDaysRemaining(user.expire_at) }}
                  </span>
                </td>
                <td>{{ user.max_profiles || '-' }}</td>
                <td>
                  <button @click="editUser(user)" class="btn-icon" title="编辑">
                    <Edit2Icon size="16" />
                  </button>
                  <button v-if="user.id !== 1" @click="confirmDelete(user)" class="btn-icon delete" title="删除">
                    <Trash2Icon size="16" />
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- 标签管理视图 -->
      <div v-else-if="currentView === 'tags'" class="tags-view">
        <header>
          <div>
            <h1>标签管理</h1>
            <p class="subtitle">管理用户分类标签</p>
          </div>
          <button @click="openAddTagModal" class="btn btn-primary">
            <PlusIcon size="18" />
            创建标签
          </button>
        </header>

        <!-- 标签列表 -->
        <div class="tags-list">
          <div class="list-header">
            <h3>所有标签</h3>
          </div>
          <div class="tags-grid">
            <div v-for="tag in allTags" :key="tag.id" class="tag-card">
              <div class="tag-info">
                <span class="tag-color-dot" :style="{ backgroundColor: tag.color }"></span>
                <span class="tag-name">{{ tag.name }}</span>
              </div>
              <div class="tag-actions">
                <button @click="editTag(tag)" class="btn-icon" title="编辑">
                  <Edit2Icon size="16" />
                </button>
                <button @click="confirmDeleteTag(tag)" class="btn-icon delete" title="删除">
                  <Trash2Icon size="16" />
                </button>
              </div>
            </div>
            <div v-if="allTags.length === 0" class="empty-state">
              <p>暂无标签，点击右上角创建</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 数据统计视图 -->
      <div v-else-if="currentView === 'stats'" class="stats-view">
        <header>
          <div>
            <h1>数据统计</h1>
            <p class="subtitle">系统整体数据概览</p>
          </div>
        </header>
        
        <!-- 统计卡片 -->
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-icon blue"><UsersIcon size="20" /></div>
            <div class="stat-info">
              <span class="stat-value">{{ stats.total_users || 0 }}</span>
              <span class="stat-label">总用户数</span>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon green"><UserCheckIcon size="20" /></div>
            <div class="stat-info">
              <span class="stat-value">{{ stats.active_count || 0 }}</span>
              <span class="stat-label">正常用户</span>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon orange"><ClockIcon size="20" /></div>
            <div class="stat-info">
              <span class="stat-value">{{ stats.expiring_soon || 0 }}</span>
              <span class="stat-label">即将过期 (7天)</span>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon red"><AlertCircleIcon size="20" /></div>
            <div class="stat-info">
              <span class="stat-value">{{ stats.expired || 0 }}</span>
              <span class="stat-label">已过期</span>
            </div>
          </div>
        </div>

        <!-- ECharts 图表区域 -->
        <div class="charts-grid">
          <!-- 用户分布饼图 -->
          <div class="chart-card">
            <h3>用户角色分布</h3>
            <v-chart class="chart" :option="roleChartOption" autoresize />
          </div>
          
          <!-- 用户状态饼图 -->
          <div class="chart-card">
            <h3>用户状态分布</h3>
            <v-chart class="chart" :option="statusChartOption" autoresize />
          </div>
          
          <!-- 授权状态饼图 -->
          <div class="chart-card">
            <h3>授权状态分布</h3>
            <v-chart class="chart" :option="licenseChartOption" autoresize />
          </div>
          
          <!-- 数据概览柱状图 -->
          <div class="chart-card wide">
            <h3>数据概览</h3>
            <v-chart class="chart" :option="overviewChartOption" autoresize />
          </div>
        </div>
      </div>

      <!-- 操作日志视图 -->
      <div v-else-if="currentView === 'logs'" class="logs-view">
        <header>
          <div>
            <h1>操作日志</h1>
            <p class="subtitle">系统操作审计记录</p>
          </div>
        </header>
        <div class="logs-list">
          <table>
            <thead>
              <tr>
                <th>时间</th>
                <th>用户</th>
                <th>操作</th>
                <th>IP地址</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="log in auditLogs" :key="log.id">
                <td>{{ formatDateTime(log.created_at) }}</td>
                <td>{{ log.username || '未知' }}</td>
                <td>{{ log.action }}</td>
                <td>{{ log.ip_address }}</td>
              </tr>
            </tbody>
          </table>
          <div class="pagination">
            <button @click="prevPage" :disabled="currentPage === 1">上一页</button>
            <span>第 {{ currentPage }} 页</span>
            <button @click="nextPage" :disabled="auditLogs.length < pageSize">下一页</button>
          </div>
        </div>
      </div>
      
      <!-- 创建用户弹窗 -->
      <div v-if="showAddModal" class="modal-overlay" @click.self="showAddModal = false">
        <div class="modal">
          <h2>创建新用户</h2>
          <form @submit.prevent="createUser">
            <div class="form-group">
              <label>用户名 <span class="required">*</span></label>
              <input v-model="newUser.username" class="input-field" placeholder="请输入用户名" required />
            </div>
            
            <div class="form-group">
              <label>初始密码 <span class="required">*</span></label>
              <input v-model="newUser.password" type="password" class="input-field" placeholder="请输入密码" required />
            </div>
            
            <div class="form-group">
              <label>角色</label>
              <select v-model="newUser.role" class="input-field">
                <option value="user">普通用户</option>
                <option value="admin">超级管理员</option>
              </select>
            </div>
            
            <!-- 标签选择 -->
            <div class="form-group">
              <label>标签</label>
              <div class="tag-selector">
                <div class="tag-options">
                  <label 
                    v-for="tag in allTags" 
                    :key="tag.id" 
                    class="tag-option"
                    :class="{ selected: newUser.selectedTags?.includes(tag.id) }"
                    :style="{ 
                      backgroundColor: newUser.selectedTags?.includes(tag.id) ? tag.color + '30' : 'transparent',
                      borderColor: tag.color,
                      color: newUser.selectedTags?.includes(tag.id) ? tag.color : 'var(--text-secondary)'
                    }"
                  >
                    <input 
                      type="checkbox" 
                      :value="tag.id" 
                      v-model="newUser.selectedTags"
                      class="hidden-checkbox"
                    />
                    <span class="tag-color-dot-small" :style="{ backgroundColor: tag.color }"></span>
                    {{ tag.name }}
                  </label>
                </div>
                <p v-if="allTags.length === 0" class="hint">暂无标签，请先创建标签</p>
              </div>
            </div>
            
            <div v-if="newUser.role === 'user'" class="license-section">
              <h4>访问权限设置</h4>
              
              <div class="form-group">
                <label>访问截止日期</label>
                <input v-model="newUser.expire_at" type="datetime-local" class="input-field" />
                <small class="hint">默认30天后过期</small>
              </div>
              
              <div class="form-group">
                <label>最大配置数</label>
                <input v-model.number="newUser.max_profiles" type="number" min="1" class="input-field" />
              </div>
              
              <div class="form-group">
                <label>账户余额</label>
                <input v-model.number="newUser.balance" type="number" step="0.01" class="input-field" />
              </div>
            </div>
            
            <div class="modal-footer">
              <button @click="showAddModal = false" type="button" class="btn">取消</button>
              <button type="submit" class="btn btn-primary" :disabled="creating">
                {{ creating ? '创建中...' : '创建' }}
              </button>
            </div>
          </form>
        </div>
      </div>
      
      <!-- 编辑用户弹窗 -->
      <div v-if="showEditModal" class="modal-overlay" @click.self="showEditModal = false">
        <div class="modal">
          <h2>编辑用户</h2>
          <form @submit.prevent="updateUser">
            <div class="form-group">
              <label>用户名</label>
              <input v-model="editUserData.username" class="input-field" :disabled="editUserData.id === 1" />
              <small v-if="editUserData.id === 1" class="hint">超级管理员用户名不可修改</small>
            </div>
            
            <div class="form-group">
              <label>新密码 <small class="hint">（留空则不修改）</small></label>
              <input v-model="editUserData.password" type="password" class="input-field" placeholder="不修改请留空" />
            </div>
            
            <div class="form-group">
              <label>角色</label>
              <select v-model="editUserData.role" class="input-field" :disabled="editUserData.id === 1">
                <option value="user">普通用户</option>
                <option value="admin">超级管理员</option>
              </select>
              <small v-if="editUserData.id === 1" class="hint">超级管理员角色不可修改</small>
            </div>
            
            <div class="form-group">
              <label>状态</label>
              <select v-model="editUserData.status" class="input-field" :disabled="editUserData.id === 1">
                <option value="active">正常</option>
                <option value="disabled">禁用</option>
              </select>
              <small v-if="editUserData.id === 1" class="hint">超级管理员不可禁用</small>
            </div>
            
            <div class="form-group">
              <label>标签</label>
              <div class="tag-selector">
                <div class="tag-options">
                  <label 
                    v-for="tag in allTags" 
                    :key="tag.id" 
                    class="tag-option"
                    :class="{ selected: editUserData.selectedTags?.includes(tag.id) }"
                    :style="{ 
                      backgroundColor: editUserData.selectedTags?.includes(tag.id) ? tag.color + '30' : 'transparent',
                      borderColor: tag.color,
                      color: editUserData.selectedTags?.includes(tag.id) ? tag.color : 'var(--text-secondary)'
                    }"
                  >
                    <input 
                      type="checkbox" 
                      :value="tag.id" 
                      v-model="editUserData.selectedTags"
                      class="hidden-checkbox"
                    />
                    <span class="tag-color-dot-small" :style="{ backgroundColor: tag.color }"></span>
                    {{ tag.name }}
                  </label>
                </div>
                <p v-if="allTags.length === 0" class="hint">暂无标签，请先创建标签</p>
              </div>
            </div>
            
            <div v-if="editUserData.role === 'user'" class="license-section">
              <h4>访问权限设置</h4>
              
              <div class="form-group">
                <label>访问截止日期 <span class="required">*</span></label>
                <input v-model="editUserData.expire_at" type="datetime-local" class="input-field" required />
              </div>
              
              <div class="form-group">
                <label>最大配置数</label>
                <input v-model.number="editUserData.max_profiles" type="number" min="1" class="input-field" />
              </div>
              
              <div class="form-group">
                <label>账户余额</label>
                <input v-model.number="editUserData.balance" type="number" step="0.01" class="input-field" />
              </div>
            </div>
            
            <div class="modal-footer">
              <button @click="showEditModal = false" type="button" class="btn">取消</button>
              <button type="submit" class="btn btn-primary" :disabled="updating">
                {{ updating ? '保存中...' : '保存' }}
              </button>
            </div>
          </form>
        </div>
      </div>
      
      <!-- 删除确认弹窗 -->
      <div v-if="showDeleteModal" class="modal-overlay" @click.self="showDeleteModal = false">
        <div class="modal modal-confirm">
          <div class="confirm-icon">
            <AlertTriangleIcon size="48" class="text-error" />
          </div>
          <h2>确认删除</h2>
          <p>确定要删除用户 <strong>{{ userToDelete?.username }}</strong> 吗？</p>
          <p class="warning-text">此操作不可恢复，该用户的所有数据将被永久删除。</p>
          <div class="modal-footer">
            <button @click="showDeleteModal = false" class="btn">取消</button>
            <button @click="deleteUser" class="btn btn-danger" :disabled="deleting">
              {{ deleting ? '删除中...' : '确认删除' }}
            </button>
          </div>
        </div>
      </div>
      
      <!-- 标签管理弹窗 -->
      <div v-if="showTagModal" class="modal-overlay" @click.self="showTagModal = false">
        <div class="modal">
          <h2>{{ isEditingTag ? '编辑标签' : '创建标签' }}</h2>
          <form @submit.prevent="isEditingTag ? updateTag() : createTag()">
            <div class="form-group">
              <label>标签名称 <span class="required">*</span></label>
              <input v-model="tagForm.name" class="input-field" placeholder="请输入标签名称" required />
            </div>
            
            <div class="form-group">
              <label>标签颜色</label>
              <div class="color-picker">
                <label 
                  v-for="color in presetColors" 
                  :key="color"
                  class="color-option"
                  :class="{ selected: tagForm.color === color }"
                  :style="{ backgroundColor: color }"
                >
                  <input type="radio" :value="color" v-model="tagForm.color" class="hidden-radio" />
                  <CheckCircleIcon v-if="tagForm.color === color" size="16" class="color-check" />
                </label>
              </div>
            </div>
            
            <div class="modal-footer">
              <button @click="showTagModal = false" type="button" class="btn">取消</button>
              <button type="submit" class="btn btn-primary" :disabled="savingTag">
                {{ savingTag ? '保存中...' : '保存' }}
              </button>
            </div>
          </form>
        </div>
      </div>
      
      <!-- 删除标签确认弹窗 -->
      <div v-if="showDeleteTagModal" class="modal-overlay" @click.self="showDeleteTagModal = false">
        <div class="modal modal-confirm">
          <div class="confirm-icon">
            <AlertTriangleIcon size="48" class="text-error" />
          </div>
          <h2>确认删除标签</h2>
          <p>确定要删除标签 <strong>{{ tagToDelete?.name }}</strong> 吗？</p>
          <p class="warning-text">此操作不可恢复，已分配给用户的该标签将被移除。</p>
          <div class="modal-footer">
            <button @click="showDeleteTagModal = false" class="btn">取消</button>
            <button @click="deleteTag" class="btn btn-danger" :disabled="deletingTag">
              {{ deletingTag ? '删除中...' : '确认删除' }}
            </button>
          </div>
        </div>
      </div>
      
      <!-- Toast 提示 -->
      <div v-if="toast.show" :class="['toast', toast.type]">
        <div class="toast-icon">
          <CheckCircleIcon v-if="toast.type === 'success'" size="20" />
          <XCircleIcon v-else-if="toast.type === 'error'" size="20" />
          <AlertCircleIcon v-else size="20" />
        </div>
        <span class="toast-message">{{ toast.message }}</span>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import {
  UsersIcon,
  BarChart3Icon,
  FileTextIcon,
  LogOutIcon,
  PlusIcon,
  Edit2Icon,
  Trash2Icon,
  SearchIcon,
  UserCheckIcon,
  ClockIcon,
  AlertCircleIcon,
  AlertTriangleIcon,
  CheckCircleIcon,
  XCircleIcon,
  TagIcon,
  XIcon
} from 'lucide-vue-next';

const router = useRouter();
const currentView = ref('users');
const users = ref([]);
const stats = ref({});
const auditLogs = ref([]);
const searchQuery = ref('');
const currentPage = ref(1);
const pageSize = 20;
const allTags = ref([]);
const selectedTagFilter = ref('');

// 弹窗状态
const showAddModal = ref(false);
const showEditModal = ref(false);
const showDeleteModal = ref(false);
const creating = ref(false);
const updating = ref(false);
const deleting = ref(false);

// 标签弹窗状态
const showTagModal = ref(false);
const showDeleteTagModal = ref(false);
const isEditingTag = ref(false);
const savingTag = ref(false);
const deletingTag = ref(false);
const tagForm = ref({ name: '', color: '#6366f1' });
const tagToDelete = ref(null);

// 预设颜色
const presetColors = [
  '#6366f1', '#8b5cf6', '#ec4899', '#f43f5e',
  '#ef4444', '#f97316', '#f59e0b', '#eab308',
  '#84cc16', '#22c55e', '#10b981', '#14b8a6',
  '#06b6d4', '#0ea5e9', '#3b82f6', '#64748b'
];

// Toast 提示
const toast = ref({
  show: false,
  message: '',
  type: 'success', // success, error, warning
  timer: null
});

// 显示 Toast
const showToast = (message, type = 'success', duration = 3000) => {
  // 清除之前的定时器
  if (toast.value.timer) {
    clearTimeout(toast.value.timer);
  }
  
  toast.value = {
    show: true,
    message,
    type,
    timer: setTimeout(() => {
      toast.value.show = false;
    }, duration)
  };
};

// 表单数据
const newUser = ref({
  username: '',
  password: '',
  role: 'user',
  expire_at: '',
  max_profiles: 5,
  balance: 0,
  selectedTags: []
});

const editUserData = ref({});
const userToDelete = ref(null);

const adminUser = JSON.parse(localStorage.getItem('icanx_admin_user') || '{}');

// 计算属性：过滤用户
const filteredUsers = computed(() => {
  let result = users.value;
  
  // 按用户名搜索
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase();
    result = result.filter(user => 
      user.username.toLowerCase().includes(query)
    );
  }
  
  // 按标签筛选
  if (selectedTagFilter.value) {
    const tagId = parseInt(selectedTagFilter.value);
    result = result.filter(user => 
      user.tags && user.tags.some(tag => tag.id === tagId)
    );
  }
  
  return result;
});

// 获取用户列表
const fetchUsers = async () => {
  try {
    const response = await axios.get('/api/admin/users');
    users.value = response.data.users;
  } catch (err) {
    alert('获取用户列表失败: ' + err.message);
  }
};

// 获取所有标签
const fetchTags = async () => {
  try {
    const response = await axios.get('/api/admin/tags');
    allTags.value = response.data.tags;
  } catch (err) {
    console.error('获取标签列表失败', err);
  }
};

// 获取统计数据
const fetchStats = async () => {
  try {
    const response = await axios.get('/api/admin/stats');
    stats.value = response.data.stats;
  } catch (err) {
    console.error('获取统计数据失败', err);
  }
};

// 获取审计日志
const fetchAuditLogs = async () => {
  try {
    const response = await axios.get('/api/admin/audit-logs', {
      params: { page: currentPage.value, limit: pageSize }
    });
    auditLogs.value = response.data.logs;
  } catch (err) {
    console.error('获取审计日志失败', err);
  }
};

// 创建用户
const createUser = async () => {
  creating.value = true;
  try {
    // 设置默认过期时间（30天后）
    if (!newUser.value.expire_at && newUser.value.role === 'user') {
      const date = new Date();
      date.setDate(date.getDate() + 30);
      newUser.value.expire_at = date.toISOString().slice(0, 16);
    }

    const userData = { ...newUser.value };
    const selectedTags = userData.selectedTags || [];
    delete userData.selectedTags;

    // 创建用户
    const response = await axios.post('/api/admin/users', userData);
    const userId = response.data.userId;
    
    // 添加标签关联
    if (selectedTags.length > 0 && userId) {
      await axios.put(`/api/admin/users/${userId}/tags`, {
        tags: selectedTags
      });
    }
    
    await fetchUsers();
    await fetchStats();
    showAddModal.value = false;
    resetNewUser();
    showToast('用户创建成功', 'success');
  } catch (err) {
    showToast('创建失败: ' + (err.response?.data?.error || err.message), 'error');
  } finally {
    creating.value = false;
  }
};

// 打开编辑弹窗
const editUser = (user) => {
  editUserData.value = {
    ...user,
    password: '',
    expire_at: user.expire_at ? formatDateTimeLocal(user.expire_at) : '',
    selectedTags: user.tags ? user.tags.map(t => t.id) : []
  };
  showEditModal.value = true;
};

// 更新用户
const updateUser = async () => {
  updating.value = true;
  try {
    const data = { ...editUserData.value };
    if (!data.password) {
      delete data.password;
    }
    
    // 保存标签数据
    const selectedTags = data.selectedTags || [];
    delete data.selectedTags;
    delete data.tags;
    
    await axios.put(`/api/admin/users/${data.id}`, data);
    
    // 单独更新标签
    await axios.put(`/api/admin/users/${editUserData.value.id}/tags`, {
      tags: selectedTags
    });
    
    await fetchUsers();
    await fetchStats();
    showEditModal.value = false;
    showToast('用户更新成功', 'success');
  } catch (err) {
    showToast('更新失败: ' + err.message, 'error');
  } finally {
    updating.value = false;
  }
};

// 确认删除
const confirmDelete = (user) => {
  userToDelete.value = user;
  showDeleteModal.value = true;
};

// 删除用户
const deleteUser = async () => {
  if (!userToDelete.value) return;
  
  deleting.value = true;
  try {
    await axios.delete(`/api/admin/users/${userToDelete.value.id}`);
    await fetchUsers();
    await fetchStats();
    showDeleteModal.value = false;
    userToDelete.value = null;
    showToast('用户删除成功', 'success');
  } catch (err) {
    showToast('删除失败: ' + err.message, 'error');
  } finally {
    deleting.value = false;
  }
};

// 重置新用户表单
const resetNewUser = () => {
  newUser.value = {
    username: '',
    password: '',
    role: 'user',
    expire_at: '',
    max_profiles: 5,
    balance: 0,
    selectedTags: []
  };
};

// 打开添加弹窗
const openAddModal = () => {
  resetNewUser();
  // 设置默认过期时间为30天后
  const date = new Date();
  date.setDate(date.getDate() + 30);
  newUser.value.expire_at = date.toISOString().slice(0, 16);
  showAddModal.value = true;
};

// 分页
const prevPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--;
    fetchAuditLogs();
  }
};

const nextPage = () => {
  currentPage.value++;
  fetchAuditLogs();
};

// 格式化日期
const formatDate = (date) => {
  if (!date) return '未设置';
  return new Date(date).toLocaleDateString('zh-CN');
};

const formatDateTime = (date) => {
  if (!date) return '-';
  return new Date(date).toLocaleString('zh-CN');
};

const formatDateTimeLocal = (date) => {
  if (!date) return '';
  return new Date(date).toISOString().slice(0, 16);
};

// 计算剩余天数
const getDaysRemaining = (expireAt) => {
  if (!expireAt) return '未设置';
  const now = new Date();
  const expire = new Date(expireAt);
  const diff = Math.ceil((expire - now) / (1000 * 60 * 60 * 24));
  if (diff < 0) return '已过期';
  if (diff === 0) return '今天过期';
  return `${diff} 天`;
};

// 获取天数样式类
const getDaysClass = (expireAt) => {
  if (!expireAt) return '';
  const now = new Date();
  const expire = new Date(expireAt);
  const diff = Math.ceil((expire - now) / (1000 * 60 * 60 * 24));
  if (diff < 0) return 'expired';
  if (diff <= 7) return 'warning';
  return 'normal';
};

// 检查是否过期
const isExpired = (expireAt) => {
  if (!expireAt) return false;
  return new Date(expireAt) < new Date();
};

// 检查是否即将过期（7天内）
const isExpiringSoon = (expireAt) => {
  if (!expireAt) return false;
  const now = new Date();
  const expire = new Date(expireAt);
  const diff = Math.ceil((expire - now) / (1000 * 60 * 60 * 24));
  return diff >= 0 && diff <= 7;
};

// ECharts 图表配置
const roleChartOption = computed(() => ({
  tooltip: { trigger: 'item' },
  legend: { bottom: '5%', left: 'center', textStyle: { color: '#94a3b8' } },
  series: [{
    type: 'pie',
    radius: ['40%', '70%'],
    avoidLabelOverlap: false,
    itemStyle: { borderRadius: 10, borderColor: '#1c253b', borderWidth: 2 },
    label: { show: false, position: 'center' },
    emphasis: { label: { show: true, fontSize: 20, fontWeight: 'bold', color: '#fff' } },
    data: [
      { value: stats.value.admin_count || 0, name: '管理员', itemStyle: { color: '#6366f1' } },
      { value: stats.value.user_count || 0, name: '普通用户', itemStyle: { color: '#10b981' } }
    ]
  }]
}));

const statusChartOption = computed(() => ({
  tooltip: { trigger: 'item' },
  legend: { bottom: '5%', left: 'center', textStyle: { color: '#94a3b8' } },
  series: [{
    type: 'pie',
    radius: ['40%', '70%'],
    avoidLabelOverlap: false,
    itemStyle: { borderRadius: 10, borderColor: '#1c253b', borderWidth: 2 },
    label: { show: false, position: 'center' },
    emphasis: { label: { show: true, fontSize: 20, fontWeight: 'bold', color: '#fff' } },
    data: [
      { value: stats.value.active_count || 0, name: '正常', itemStyle: { color: '#10b981' } },
      { value: stats.value.disabled_count || 0, name: '禁用', itemStyle: { color: '#ef4444' } }
    ]
  }]
}));

const licenseChartOption = computed(() => ({
  tooltip: { trigger: 'item' },
  legend: { bottom: '5%', left: 'center', textStyle: { color: '#94a3b8' } },
  series: [{
    type: 'pie',
    radius: ['40%', '70%'],
    avoidLabelOverlap: false,
    itemStyle: { borderRadius: 10, borderColor: '#1c253b', borderWidth: 2 },
    label: { show: false, position: 'center' },
    emphasis: { label: { show: true, fontSize: 20, fontWeight: 'bold', color: '#fff' } },
    data: [
      { value: (stats.value.active_count || 0) - (stats.value.expiring_soon || 0) - (stats.value.expired || 0), name: '正常', itemStyle: { color: '#10b981' } },
      { value: stats.value.expiring_soon || 0, name: '即将过期', itemStyle: { color: '#f59e0b' } },
      { value: stats.value.expired || 0, name: '已过期', itemStyle: { color: '#ef4444' } }
    ].filter(item => item.value > 0)
  }]
}));

const overviewChartOption = computed(() => ({
  tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
  grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
  xAxis: { type: 'category', data: ['总用户', '管理员', '普通用户', '正常', '禁用', '即将过期', '已过期'], axisLine: { lineStyle: { color: '#334155' } }, axisLabel: { color: '#94a3b8' } },
  yAxis: { type: 'value', axisLine: { lineStyle: { color: '#334155' } }, axisLabel: { color: '#94a3b8' }, splitLine: { lineStyle: { color: '#1e293b' } } },
  series: [{
    type: 'bar',
    data: [
      { value: stats.value.total_users || 0, itemStyle: { color: '#6366f1' } },
      { value: stats.value.admin_count || 0, itemStyle: { color: '#8b5cf6' } },
      { value: stats.value.user_count || 0, itemStyle: { color: '#10b981' } },
      { value: stats.value.active_count || 0, itemStyle: { color: '#22c55e' } },
      { value: stats.value.disabled_count || 0, itemStyle: { color: '#ef4444' } },
      { value: stats.value.expiring_soon || 0, itemStyle: { color: '#f59e0b' } },
      { value: stats.value.expired || 0, itemStyle: { color: '#dc2626' } }
    ],
    barWidth: '60%',
    itemStyle: { borderRadius: [8, 8, 0, 0] }
  }]
}));

const logout = () => {
  localStorage.removeItem('icanx_admin_token');
  localStorage.removeItem('icanx_admin_user');
  router.push('/login');
};

onMounted(() => {
  fetchUsers();
  fetchStats();
  fetchAuditLogs();
  fetchTags();
});

// --- 标签管理方法 ---

// 打开创建标签弹窗
const openAddTagModal = () => {
  isEditingTag.value = false;
  tagForm.value = { name: '', color: '#6366f1' };
  showTagModal.value = true;
};

// 打开编辑标签弹窗
const editTag = (tag) => {
  isEditingTag.value = true;
  tagForm.value = { ...tag };
  showTagModal.value = true;
};

// 创建标签
const createTag = async () => {
  savingTag.value = true;
  try {
    await axios.post('/api/admin/tags', tagForm.value);
    await fetchTags();
    showTagModal.value = false;
    showToast('标签创建成功', 'success');
  } catch (err) {
    showToast('创建失败: ' + (err.response?.data?.error || err.message), 'error');
  } finally {
    savingTag.value = false;
  }
};

// 更新标签
const updateTag = async () => {
  savingTag.value = true;
  try {
    await axios.put(`/api/admin/tags/${tagForm.value.id}`, tagForm.value);
    await fetchTags();
    await fetchUsers(); // 刷新用户列表以更新标签显示
    showTagModal.value = false;
    showToast('标签更新成功', 'success');
  } catch (err) {
    showToast('更新失败: ' + (err.response?.data?.error || err.message), 'error');
  } finally {
    savingTag.value = false;
  }
};

// 确认删除标签
const confirmDeleteTag = (tag) => {
  tagToDelete.value = tag;
  showDeleteTagModal.value = true;
};

// 删除标签
const deleteTag = async () => {
  if (!tagToDelete.value) return;
  
  deletingTag.value = true;
  try {
    await axios.delete(`/api/admin/tags/${tagToDelete.value.id}`);
    await fetchTags();
    await fetchUsers(); // 刷新用户列表
    showDeleteTagModal.value = false;
    tagToDelete.value = null;
    showToast('标签删除成功', 'success');
  } catch (err) {
    showToast('删除失败: ' + err.message, 'error');
  } finally {
    deletingTag.value = false;
  }
};
</script>

<style scoped>
.dashboard {
  display: flex;
  height: 100vh;
}

.sidebar {
  width: 260px;
  background: var(--bg-secondary);
  border-right: 1px solid var(--border-subtle);
  padding: 24px 16px;
  display: flex;
  flex-direction: column;
}

.logo {
  font-weight: 900;
  font-size: 20px;
  margin-bottom: 40px;
  color: var(--accent-primary);
  padding: 0 12px;
}

nav {
  flex: 1;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 10px;
  margin-bottom: 4px;
  cursor: pointer;
  color: var(--text-secondary);
  transition: all 0.2s;
  font-size: 14px;
}

.nav-item:hover {
  background: rgba(255,255,255,0.05);
  color: var(--text-primary);
}

.nav-item.active {
  background: rgba(99, 102, 241, 0.15);
  color: var(--accent-primary);
  font-weight: 600;
}

.user-profile {
  margin-top: auto;
  padding: 16px 12px;
  background: rgba(255,255,255,0.03);
  border-radius: 12px;
  text-align: center;
}

.user-profile p {
  margin: 0 0 8px 0;
  font-weight: 600;
  color: var(--text-primary);
}

.user-profile .role-badge {
  display: inline-block;
  padding: 2px 8px;
  background: rgba(99, 102, 241, 0.2);
  color: var(--accent-primary);
  border-radius: 4px;
  font-size: 11px;
  margin-bottom: 12px;
}

.logout-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  width: 100%;
  background: rgba(239, 68, 68, 0.1);
  border: none;
  color: var(--error);
  cursor: pointer;
  padding: 8px;
  border-radius: 8px;
  font-size: 13px;
  transition: all 0.2s;
}

.logout-btn:hover {
  background: rgba(239, 68, 68, 0.2);
}

.main-content {
  flex: 1;
  padding: 32px 40px;
  overflow-y: auto;
}

header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 32px;
}

h1 {
  font-size: 28px;
  font-weight: 700;
  margin: 0 0 8px 0;
}

.subtitle {
  color: var(--text-secondary);
  font-size: 14px;
  margin: 0;
}

/* 统计卡片 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 32px;
}

.stat-card {
  background: var(--bg-card);
  border-radius: 16px;
  padding: 20px;
  border: 1px solid var(--border-subtle);
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-icon.blue { background: rgba(99, 102, 241, 0.15); color: #818cf8; }
.stat-icon.green { background: rgba(16, 185, 129, 0.15); color: #34d399; }
.stat-icon.orange { background: rgba(245, 158, 11, 0.15); color: #fbbf24; }
.stat-icon.red { background: rgba(239, 68, 68, 0.15); color: #f87171; }

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
}

.stat-label {
  font-size: 13px;
  color: var(--text-secondary);
}

/* 用户列表 */
.user-list {
  background: var(--bg-card);
  border-radius: 16px;
  border: 1px solid var(--border-subtle);
  overflow: hidden;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid var(--border-subtle);
}

.list-header h3 {
  margin: 0;
  font-size: 16px;
}

.search-box {
  display: flex;
  align-items: center;
  gap: 8px;
  background: var(--bg-secondary);
  padding: 8px 12px;
  border-radius: 8px;
  border: 1px solid var(--border-subtle);
  color: var(--text-secondary);
}

.search-box input {
  background: transparent;
  border: none;
  color: var(--text-primary);
  outline: none;
  font-size: 13px;
  width: 200px;
}

table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
}

th, td {
  padding: 14px 24px;
  border-bottom: 1px solid var(--border-subtle);
  font-size: 14px;
}

th {
  background: rgba(255,255,255,0.02);
  color: var(--text-secondary);
  font-weight: 500;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

tr:hover {
  background: rgba(255,255,255,0.02);
}

tr.expired {
  opacity: 0.6;
}

tr.expiring-soon td {
  background: rgba(245, 158, 11, 0.05);
}

.user-info {
  display: flex;
  flex-direction: column;
}

.username {
  font-weight: 500;
}

/* 用户标签 */
.user-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.tag-badge {
  display: inline-flex;
  align-items: center;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;
  border: 1px solid;
  white-space: nowrap;
}

.no-tags {
  color: var(--text-secondary);
  font-size: 12px;
}

/* 标签筛选 */
.filter-box {
  display: flex;
  gap: 12px;
  align-items: center;
}

.tag-filter select {
  width: 150px;
  padding: 8px 12px;
  font-size: 13px;
}

/* 标签选择器 */
.tag-selector {
  background: var(--bg-secondary);
  padding: 16px;
  border-radius: 10px;
  border: 1px solid var(--border-subtle);
}

.tag-options {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag-option {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 20px;
  border: 1px solid var(--border-subtle);
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s;
}

.tag-option:hover {
  background: rgba(255,255,255,0.05);
}

.tag-option.selected {
  font-weight: 500;
}

.tag-color-dot-small {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.hidden-checkbox {
  position: absolute;
  opacity: 0;
  pointer-events: none;
}

/* 标签管理视图 */
.tags-view {
  height: 100%;
}

.tags-list {
  background: var(--bg-card);
  border-radius: 16px;
  border: 1px solid var(--border-subtle);
  overflow: hidden;
}

.tags-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 16px;
  padding: 24px;
}

.tag-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  background: var(--bg-secondary);
  border-radius: 12px;
  border: 1px solid var(--border-subtle);
  transition: all 0.2s;
}

.tag-card:hover {
  border-color: var(--accent-primary);
}

.tag-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.tag-color-dot {
  width: 14px;
  height: 14px;
  border-radius: 50%;
}

.tag-name {
  font-weight: 500;
  color: var(--text-primary);
}

.tag-actions {
  display: flex;
  gap: 4px;
}

.empty-state {
  grid-column: 1 / -1;
  text-align: center;
  padding: 40px;
  color: var(--text-secondary);
}

/* 颜色选择器 */
.color-picker {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.color-option {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  border: 2px solid transparent;
}

.color-option:hover {
  transform: scale(1.1);
}

.color-option.selected {
  border-color: white;
  box-shadow: 0 0 0 2px var(--bg-card), 0 0 0 4px var(--accent-primary);
}

.color-check {
  color: white;
  filter: drop-shadow(0 1px 2px rgba(0,0,0,0.3));
}

.hidden-radio {
  position: absolute;
  opacity: 0;
  pointer-events: none;
}

.role-badge {
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
}

.role-badge.admin { background: rgba(99, 102, 241, 0.15); color: #818cf8; }
.role-badge.user { background: rgba(255,255,255,0.08); color: #94a3b8; }

.status-badge {
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.active { background: rgba(16, 185, 129, 0.15); color: #34d399; }
.status-badge.disabled { background: rgba(239, 68, 68, 0.15); color: #f87171; }

.days-badge {
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
}

.days-badge.normal { background: rgba(16, 185, 129, 0.15); color: #34d399; }
.days-badge.warning { background: rgba(245, 158, 11, 0.15); color: #fbbf24; }
.days-badge.expired { background: rgba(239, 68, 68, 0.15); color: #f87171; }

.btn-icon {
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 6px;
  border-radius: 6px;
  transition: all 0.2s;
  margin-right: 4px;
}

.btn-icon:hover {
  background: rgba(255,255,255,0.08);
  color: var(--text-primary);
}

.btn-icon.delete:hover {
  background: rgba(239, 68, 68, 0.15);
  color: var(--error);
}

/* 弹窗样式 */
.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal {
  width: 100%;
  max-width: 480px;
  max-height: 90vh;
  overflow-y: auto;
  background: var(--bg-card);
  padding: 28px;
  border-radius: 20px;
  border: 1px solid var(--border-subtle);
}

.modal-confirm {
  text-align: center;
  max-width: 400px;
}

.confirm-icon {
  margin-bottom: 16px;
}

.modal h2 {
  margin: 0 0 24px 0;
  font-size: 20px;
}

.modal-confirm h2 {
  margin-bottom: 16px;
}

.modal-confirm p {
  color: var(--text-secondary);
  margin: 8px 0;
}

.warning-text {
  color: var(--error) !important;
  font-size: 13px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.required {
  color: var(--error);
}

.hint {
  color: var(--text-secondary);
  font-size: 12px;
}

.license-section {
  background: var(--bg-secondary);
  padding: 20px;
  border-radius: 12px;
  margin-top: 20px;
}

.license-section h4 {
  margin: 0 0 16px 0;
  font-size: 14px;
  color: var(--accent-primary);
}

.input-field {
  width: 100%;
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: 10px;
  padding: 12px 14px;
  color: white;
  font-size: 14px;
  outline: none;
  transition: all 0.2s;
}

.input-field:focus {
  border-color: var(--accent-primary);
}

.input-field:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

select.input-field {
  cursor: pointer;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid var(--border-subtle);
}

.btn {
  padding: 10px 20px;
  border-radius: 10px;
  border: none;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  background: var(--bg-secondary);
  color: var(--text-primary);
  font-size: 14px;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.btn:hover {
  background: rgba(255,255,255,0.1);
}

.btn-primary {
  background: var(--accent-gradient);
}

.btn-primary:hover {
  transform: translateY(-1px);
  filter: brightness(1.1);
}

.btn-danger {
  background: var(--error);
  color: white;
}

.btn-danger:hover {
  filter: brightness(1.1);
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none !important;
}

/* 统计视图 */
.stats-view .stats-detail {
  background: var(--bg-card);
  border-radius: 16px;
  border: 1px solid var(--border-subtle);
  padding: 24px;
}

.stat-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 0;
  border-bottom: 1px solid var(--border-subtle);
}

.stat-row:last-child {
  border-bottom: none;
}

.stat-row span {
  color: var(--text-secondary);
}

.stat-row strong {
  font-size: 18px;
  color: var(--text-primary);
}

.text-success { color: var(--success); }
.text-error { color: var(--error); }

/* 图表样式 */
.charts-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
  margin-top: 24px;
}

.chart-card {
  background: var(--bg-card);
  border-radius: 16px;
  border: 1px solid var(--border-subtle);
  padding: 24px;
}

.chart-card.wide {
  grid-column: span 3;
}

.chart-card h3 {
  margin: 0 0 16px 0;
  font-size: 16px;
  color: var(--text-primary);
  font-weight: 600;
}

.chart {
  width: 100%;
  height: 280px;
}

.chart-card.wide .chart {
  height: 320px;
}

@media (max-width: 1200px) {
  .charts-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .chart-card.wide {
    grid-column: span 2;
  }
}

@media (max-width: 768px) {
  .charts-grid {
    grid-template-columns: 1fr;
  }
  .chart-card.wide {
    grid-column: span 1;
  }
}

/* 日志视图 */
.logs-view .logs-list {
  background: var(--bg-card);
  border-radius: 16px;
  border: 1px solid var(--border-subtle);
  overflow: hidden;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  padding: 20px;
  border-top: 1px solid var(--border-subtle);
}

.pagination button {
  padding: 8px 16px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  color: var(--text-primary);
  border-radius: 8px;
  cursor: pointer;
}

.pagination button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination span {
  color: var(--text-secondary);
  font-size: 14px;
}

/* Toast 提示 */
.toast {
  position: fixed;
  top: 24px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 24px;
  border-radius: 12px;
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.4);
  z-index: 9999;
  animation: slideDown 0.3s ease;
}

@keyframes slideDown {
  from {
    transform: translateX(-50%) translateY(-100%);
    opacity: 0;
  }
  to {
    transform: translateX(-50%) translateY(0);
    opacity: 1;
  }
}

.toast.success {
  border-left: 4px solid var(--success);
}

.toast.error {
  border-left: 4px solid var(--error);
}

.toast.warning {
  border-left: 4px solid #f59e0b;
}

.toast-icon {
  display: flex;
  align-items: center;
  justify-content: center;
}

.toast.success .toast-icon {
  color: var(--success);
}

.toast.error .toast-icon {
  color: var(--error);
}

.toast.warning .toast-icon {
  color: #f59e0b;
}

.toast-message {
  font-size: 14px;
  color: var(--text-primary);
}
</style>
