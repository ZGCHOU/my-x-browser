<template>
  <div id="admin-app">
    <router-view></router-view>
  </div>
</template>

<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

:root {
  --bg-primary: #0a0e17;
  --bg-secondary: #121826;
  --bg-card: #1c253b;
  --accent-primary: #6366f1;
  --accent-gradient: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
  --text-primary: #ffffff;
  --text-secondary: #94a3b8;
  --border-subtle: rgba(255, 255, 255, 0.08);
  --error: #ef4444;
  --success: #10b981;
}

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  background-color: var(--bg-primary);
  color: var(--text-primary);
  font-family: 'Inter', sans-serif;
  -webkit-font-smoothing: antialiased;
}

#admin-app {
  min-height: 100vh;
}

.btn {
  padding: 10px 20px;
  border-radius: 8px;
  border: none;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  background: var(--bg-secondary);
  color: var(--text-primary);
}

.btn-primary {
  background: var(--accent-gradient);
}

.btn-primary:hover {
  transform: translateY(-2px);
  filter: brightness(1.1);
}

.input-field {
  width: 100%;
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: 8px;
  padding: 12px;
  color: white;
  margin-bottom: 20px;
}
</style>
