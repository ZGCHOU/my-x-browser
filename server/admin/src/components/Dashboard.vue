<template>
  <div class="dashboard">
    <aside class="sidebar">
      <div class="logo">ICANX ADMIN</div>
      <nav>
        <div class="nav-item active">用户管理</div>
        <div class="nav-item">系统设置 (即将推出)</div>
      </nav>
      <div class="user-profile">
        <p>{{ adminUser.username }}</p>
        <button @click="logout" class="logout-btn">退出</button>
      </div>
    </aside>

    <main class="main-content">
      <header>
        <h1>用户管理系统</h1>
        <button @click="showAddModal = true" class="btn btn-primary">+ 创建新账号</button>
      </header>

      <div class="user-list">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>用户名</th>
              <th>角色</th>
              <th>状态</th>
              <th>授权截止</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in users" :key="user.id">
              <td>{{ user.id }}</td>
              <td>{{ user.username }}</td>
              <td><span :class="['role-badge', user.role]">{{ user.role === 'admin' ? '超级管理员' : '普通用户' }}</span></td>
              <td><span :class="['status-badge', user.status]">{{ user.status === 'active' ? '正常' : '禁用' }}</span></td>
              <td>{{ formatDate(user.expire_at) }}</td>
              <td>
                <button @click="editUser(user)" class="btn-text">编辑</button>
                <button v-if="user.username !== 'admin'" class="btn-text delete">删除</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <!-- Simple Add Modal -->
      <div v-if="showAddModal" class="modal-overlay">
        <div class="modal">
          <h2>创建新用户</h2>
          <form @submit.prevent="createUser">
            <label>用户名</label>
            <input v-model="newUser.username" class="input-field" required />
            <label>初始密码</label>
            <input v-model="newUser.password" type="password" class="input-field" required />
            <div class="modal-footer">
              <button @click="showAddModal = false" type="button" class="btn">取消</button>
              <button type="submit" class="btn btn-primary" :disabled="creating">
                {{ creating ? '创建中...' : '提交' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';

const router = useRouter();
const users = ref([]);
const showAddModal = ref(false);
const creating = ref(false);
const adminUser = JSON.parse(localStorage.getItem('icanx_admin_user') || '{}');

const newUser = ref({ username: '', password: '', role: 'user' });

const fetchUsers = async () => {
    const token = localStorage.getItem('icanx_admin_token');
    try {
        const response = await axios.get('/api/admin/users', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        users.value = response.data.users;
    } catch (err) {
        console.error('获取用户列表失败', err);
    }
};

const createUser = async () => {
    creating.value = true;
    const token = localStorage.getItem('icanx_admin_token');
    try {
        await axios.post('/api/admin/create-user', newUser.value, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        await fetchUsers();
        showAddModal.value = false;
        newUser.value = { username: '', password: '', role: 'user' };
    } catch (err) {
        alert('创建失败: ' + (err.response?.data?.error || err.message));
    } finally {
        creating.value = false;
    }
};

const logout = () => {
    localStorage.removeItem('icanx_admin_token');
    localStorage.removeItem('icanx_admin_user');
    router.push('/login');
};

const formatDate = (date) => {
    if (!date) return '未授权';
    return new Date(date).toLocaleDateString();
};

onMounted(fetchUsers);
</script>

<style scoped>
.dashboard {
  display: flex;
  height: 100vh;
}

.sidebar {
  width: 240px;
  background: var(--bg-secondary);
  border-right: 1px solid var(--border-subtle);
  padding: 30px 20px;
  display: flex;
  flex-direction: column;
}

.logo {
  font-weight: 900;
  font-size: 20px;
  margin-bottom: 50px;
  color: var(--accent-primary);
}

nav {
  flex: 1;
}

.nav-item {
  padding: 12px;
  border-radius: 8px;
  margin-bottom: 8px;
  cursor: pointer;
  color: var(--text-secondary);
  transition: all 0.2s;
  font-size: 14px;
}

.nav-item.active {
  background: rgba(99, 102, 241, 0.1);
  color: var(--accent-primary);
  font-weight: 600;
}

.user-profile {
  margin-top: auto;
  font-size: 12px;
  text-align: center;
}

.logout-btn {
  background: none;
  border: none;
  color: var(--error);
  cursor: pointer;
  margin-top: 10px;
}

.main-content {
  flex: 1;
  padding: 40px;
  overflow-y: auto;
}

header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 40px;
}

h1 {
  font-size: 28px;
  font-weight: 700;
}

.user-list {
  background: var(--bg-card);
  border-radius: 16px;
  border: 1px solid var(--border-subtle);
  overflow: hidden;
}

table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
}

th, td {
  padding: 16px 24px;
  border-bottom: 1px solid var(--border-subtle);
  font-size: 14px;
}

th {
  background: rgba(255,255,255,0.02);
  color: var(--text-secondary);
  font-weight: 500;
}

.role-badge, .status-badge {
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 12px;
}

.role-badge.admin { background: rgba(99, 102, 241, 0.15); color: #818cf8; }
.role-badge.user { background: rgba(255,255,255,0.05); color: #94a3b8; }

.status-badge.active { background: rgba(16, 185, 129, 0.15); color: #34d399; }

.btn-text {
  background: none;
  border: none;
  color: var(--accent-primary);
  margin-right: 15px;
  cursor: pointer;
}

.btn-text.delete { color: var(--error); }

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  width: 400px;
  background: var(--bg-card);
  padding: 30px;
  border-radius: 16px;
  border: 1px solid var(--border-subtle);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 20px;
}
</style>
