import { createApp } from 'vue';
import { createRouter, createWebHistory } from 'vue-router';
import App from './App.vue';
import Login from './components/Login.vue';
import Dashboard from './components/Dashboard.vue';
import axios from 'axios';
import VueECharts from 'vue-echarts';
import { use } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { PieChart, BarChart, LineChart } from 'echarts/charts';
import { GridComponent, TooltipComponent, LegendComponent, TitleComponent } from 'echarts/components';

// 注册 ECharts 组件
use([CanvasRenderer, PieChart, BarChart, LineChart, GridComponent, TooltipComponent, LegendComponent, TitleComponent]);

// 配置axios默认值
// 开发环境使用相对路径，通过 Vite 代理；生产环境使用实际地址
axios.defaults.baseURL = import.meta.env.DEV ? '' : 'http://localhost:3001';

// 请求拦截器 - 自动添加token
axios.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('icanx_admin_token');
        if (token) {
            config.headers['Authorization'] = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// 响应拦截器 - 统一错误处理
axios.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response) {
            const { status, data } = error.response;
            
            // Token过期或无效
            if (status === 401) {
                localStorage.removeItem('icanx_admin_token');
                localStorage.removeItem('icanx_admin_user');
                window.location.href = '/login';
                return Promise.reject(new Error('登录已过期，请重新登录'));
            }
            
            // 权限不足
            if (status === 403) {
                return Promise.reject(new Error(data.error || '权限不足'));
            }
            
            // 其他错误
            return Promise.reject(new Error(data.error || '请求失败'));
        }
        return Promise.reject(error);
    }
);

const routes = [
    { path: '/', redirect: '/login' },
    { path: '/login', component: Login },
    { path: '/dashboard', component: Dashboard, meta: { requiresAuth: true } }
];

const router = createRouter({
    history: createWebHistory(),
    routes
});

// 路由守卫
router.beforeEach((to, from, next) => {
    const token = localStorage.getItem('icanx_admin_token');
    const user = JSON.parse(localStorage.getItem('icanx_admin_user') || '{}');
    
    if (to.meta.requiresAuth) {
        if (!token) {
            next('/login');
        } else if (user.role !== 'admin') {
            // 非管理员不能访问后台
            localStorage.removeItem('icanx_admin_token');
            localStorage.removeItem('icanx_admin_user');
            next('/login');
        } else {
            next();
        }
    } else {
        next();
    }
});

const app = createApp(App);
app.use(router);
app.component('v-chart', VueECharts);
app.mount('#app');
