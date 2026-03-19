<template>
  <div class="login-page">
    <div class="login-container">
      <div class="logo-box">I</div>
      <h1>管理后台</h1>
      <p class="subtitle">超级管理员登录以进行系统管理</p>

      <form @submit.prevent="handleLogin" class="login-form">
        <label>用户名</label>
        <input v-model="username" type="text" class="input-field" placeholder="请输入用户名" required />
        
        <label>密码</label>
        <input v-model="password" type="password" class="input-field" placeholder="请输入密码" required />
        
        <p v-if="error" class="error-msg">{{ error }}</p>
        <button type="submit" class="btn btn-primary" :disabled="loading">
          {{ loading ? '登录中...' : '进入后台' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';

const router = useRouter();
const username = ref('admin');
const password = ref('');
const error = ref('');
const loading = ref(false);

const handleLogin = async () => {
    loading.value = true;
    error.value = '';
    try {
        const response = await axios.post('/api/auth/login', {
            username: username.value,
            password: password.value
        });
        
        const { token, user } = response.data;
        if (user.role !== 'admin') {
            throw new Error('只有超级管理员可以访问此后台');
        }
        
        localStorage.setItem('icanx_admin_token', token);
        localStorage.setItem('icanx_admin_user', JSON.stringify(user));
        router.push('/dashboard');
    } catch (err) {
        error.value = err.response?.data?.error || err.message || '登录失败，请检查用户名或密码';
    } finally {
        loading.value = false;
    }
};
</script>

<style scoped>
.login-page {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: radial-gradient(circle at top right, #1c253b 0%, #0a0e17 100%);
}

.login-container {
  width: 420px;
  padding: 50px;
  background: var(--bg-card);
  border-radius: 24px;
  border: 1px solid var(--border-subtle);
  backdrop-filter: blur(10px);
  box-shadow: 0 20px 40px rgba(0,0,0,0.4);
  text-align: center;
}

.logo-box {
  width: 80px;
  height: 80px;
  margin: 0 auto 20px;
  background: var(--accent-gradient);
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 40px;
  font-weight: 700;
  color: white;
  box-shadow: 0 8px 32px rgba(99, 102, 241, 0.4);
}

h1 {
  font-size: 24px;
  margin-bottom: 8px;
}

.subtitle {
  color: var(--text-secondary);
  font-size: 14px;
  margin-bottom: 40px;
}

.login-form {
  text-align: left;
}

label {
  display: block;
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.error-msg {
  color: var(--error);
  font-size: 13px;
  margin-bottom: 16px;
}

.btn-primary {
  width: 100%;
  padding: 14px;
}
</style>
