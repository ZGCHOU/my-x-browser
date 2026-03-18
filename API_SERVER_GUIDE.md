# GeekEZ Browser & Account Server 交付文档

本仓库包含两个核心部分：**Electron 浏览器客户端** 和 **独立账号后端服务**。

---

## 一、 系统架构说明
*   **前端 (Electron)**: 基于 `main.js` 和 `renderer.js` 的抗指纹浏览器。
*   **后端 (Backend)**: 位于 `/server` 目录，使用 Node.js + MySQL。
    *   端口：`3000`
    *   认证：基于 JWT (JSON Web Token)
    *   功能：用户登录、权限校验、超级管理员功能。

---

## 二、 后端环境搭建 (必需)

在运行应用前，必须先启动后端服务以通过登录拦截。

### 1. 数据库配置
1.  确保本地已安装 **MySQL**。
2.  执行 `/server/schema.sql` 脚本创建数据库：
    *   数据库名：`icanx_db`
    *   它会自动创建一个超级管理员：
        *   **用户名**: `admin`
        *   **初始密码**: `123456`

### 2. 后端启动
```bash
cd server
npm install
# 修改 .env 文件中的数据库账号密码
npm start
```
成功启动后，终端应显示：`🚀 Independent Account Server running on port 3000`。

---

## 三、 客户端运行与打包

### 1. 开发模式运行
```bash
# 根目录下
npm install
npm start
```

### 2. 打包发布 (Build)这部分不用管
本项目的打包配置已优化，**后端 `/server` 文件夹会被自动排除**，不会泄露源码。
```bash
npm run build:win   # Windows 打包
npm run build:mac   # Mac 打包
```

---

## 五、 Admin 管理后台 (Vue 项目)

为了方便管理员管理用户和授权，单独在 `/server/admin` 目录下提供了一个 Vue 3 开发的**大管家后台**。

### 1. 功能说明
*   **可视化管理**：直接在网页端查看所有用户列表、角色状态及授权到期时间。
*   **快捷创号**：直接通过界面创建新账号，无需手动编写 SQL。
*   **权限控制**：后续可在此界面直接给用户设置“环境限制”等。

### 2. 启动方式
```bash
cd server/admin
npm install
npm run dev
```
启动后访问终端输出的地址（通常是 `http://localhost:5173`）即可进入后台管理。

---

## 六、 核心账号逻辑说明

*   **权限分级**：
    *   `admin`: 超级管理员。登录后侧边栏可见“账号管理”入口。
    *   `user`: 普通用户。仅能使用已授权的浏览器功能，比如限制浏览器数量。
*   **登录拦截**：
    *   位于 `renderer.js` 的 `checkAuth()` 函数。
    *   应用启动会先请求 `localhost:3000/api/user/status`。
    *   如果 Token 失效或后端未启动，将强制停留在登录遮罩层。
*   **Token 存储**：
    *   存储于 `localStorage` ('icanx_token')。
    *   默认有效期：**24 小时**。

---

## 七、 后续开发建议 (TODO)

1.  **管理后台增强**: 当前已完成基础 CRUD，可后续增加“一键续期”、“禁用账号”等批量操作。
2.  **公网部署**: 如果需要让其他人远程登录，需将 `.env` 里的 `localhost` 改为你的公网服务器 IP，并确保 3000 端口开放。
3.  **充值扩展**: 后端已预留 `licenses` 表中的 `expire_at` (过期日期) 和 `balance` (余额) 字段。

---
**交付人：** Antigravity (AI Pair Programmer)
**日期：** 2026-03-18
