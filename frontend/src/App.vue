<template>
  <div class="app-shell">
    <!-- 顶部导航栏 - 所有页面共享 -->
    <header class="app-header">
      <div class="header-left">
        <div class="logo">
          <span class="logo-icon">◈</span>
          <span class="logo-text">Stock-View</span>
        </div>
      </div>
      <nav class="header-nav">
        <router-link to="/market" class="nav-item" active-class="nav-active">
          <span class="nav-icon">📊</span>
          <span class="nav-label">行情</span>
        </router-link>
        <router-link to="/watchlist" class="nav-item" active-class="nav-active">
          <span class="nav-icon">⭐</span>
          <span class="nav-label">自选</span>
        </router-link>
        <router-link to="/search" class="nav-item" active-class="nav-active">
          <span class="nav-icon">🔍</span>
          <span class="nav-label">搜索</span>
        </router-link>
      </nav>
    </header>

    <!-- 页面内容区域 -->
    <main class="app-main">
      <router-view v-slot="{ Component }">
        <transition name="page-fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
  </div>
</template>

<script setup lang="ts">
</script>

<style>
/* ===== 全局 Reset ===== */
*, *::before, *::after { margin: 0; padding: 0; box-sizing: border-box; }
html, body, #app { height: 100%; overflow: hidden; }
body { font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Microsoft YaHei', 'Segoe UI', Roboto, sans-serif; -webkit-font-smoothing: antialiased; }

/* ===== 金融主题 CSS 变量 ===== */
:root {
  /* 涨跌色彩体系 - 东方财富风格 */
  --color-up: #f2364b;          /* 上涨红 */
  --color-up-light: #ff6b7a;    /* 上涨浅红 */
  --color-up-bg: rgba(242,54,75,0.12); /* 上涨背景 */
  --color-down: #08b25e;        /* 下跌绿 */
  --color-down-light: #2dcc71;  /* 下跌浅绿 */
  --color-down-bg: rgba(8,178,94,0.12); /* 下跌背景 */
  --color-flat: #7c8ba6;        /* 平盘灰 */

  /* 深色主题 - 暗色金融风 */
  --bg-primary: #111827;
  --bg-secondary: #1f2937;
  --bg-card: #263040;
  --bg-hover: #324150;
  --bg-input: #1a2332;
  --bg-up: rgba(242,54,75,0.08);
  --bg-down: rgba(8,178,94,0.08);

  /* 文字层级 */
  --text-primary: #f0f4f8;
  --text-secondary: #8b95a5;
  --text-muted: #5c6478;

  /* 边框与分割 */
  --border-color: #2a3444;
  --border-light: #1e2838;

  /* 强调色 */
  --accent-blue: #3b82f6;
  --accent-gold: #d4a853;
  --accent-orange: #f59e0b;

  /* 圆角 */
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;

  /* 间距 */
  --space-xs: 4px;
  --space-sm: 8px;
  --space-md: 12px;
  --space-lg: 16px;
  --space-xl: 24px;

  /* 字号 */
  --font-xs: 11px;
  --font-sm: 12px;
  --font-md: 14px;
  --font-lg: 16px;
  --font-xl: 20px;
  --font-xxl: 28px;

  /* 阴影 */
  --shadow-sm: 0 1px 3px rgba(0,0,0,0.3);
  --shadow-md: 0 4px 12px rgba(0,0,0,0.4);
}

body {
  background: var(--bg-primary);
  color: var(--text-primary);
}

/* ===== App Shell 布局 ===== */
.app-shell {
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
}

.app-header {
  display: flex;
  align-items: center;
  height: 52px;
  padding: 0 var(--space-lg);
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
  box-shadow: var(--shadow-sm);
  z-index: 100;
  flex-shrink: 0;
}

.header-left {
  display: flex;
  align-items: center;
  margin-right: var(--space-xl);
}

.logo {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
}

.logo-icon {
  color: var(--accent-blue);
  font-size: 20px;
  font-weight: bold;
}

.logo-text {
  font-size: var(--font-lg);
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: -0.5px;
}

.header-nav {
  display: flex;
  align-items: center;
  gap: 4px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  padding: 8px 16px;
  font-size: var(--font-sm);
  color: var(--text-secondary);
  text-decoration: none;
  border-radius: var(--radius-md);
  transition: all 0.2s ease;
  cursor: pointer;
}

.nav-item:hover {
  color: var(--text-primary);
  background: var(--bg-hover);
}

.nav-active {
  color: var(--accent-blue) !important;
  background: rgba(59,130,246,0.12) !important;
}

.nav-icon {
  font-size: var(--font-md);
}

.nav-label {
  font-weight: 500;
}

.app-main {
  flex: 1;
  overflow: hidden;
  background: var(--bg-primary);
}

/* ===== 页面过渡动画 ===== */
.page-fade-enter-active { transition: opacity 0.2s ease; }
.page-fade-leave-active { transition: opacity 0.15s ease; }
.page-fade-enter-from { opacity: 0; }
.page-fade-leave-to { opacity: 0; }

/* ===== 全局 Element Plus 深色覆盖 ===== */
.el-table { --el-table-bg-color: var(--bg-primary) !important; --el-table-tr-bg-color: var(--bg-primary) !important; --el-table-header-bg-color: var(--bg-secondary) !important; --el-table-row-hover-bg-color: var(--bg-hover) !important; --el-table-border-color: var(--border-color) !important; --el-table-text-color: var(--text-primary) !important; --el-table-header-text-color: var(--text-secondary) !important; font-size: var(--font-sm) !important; }
.el-table__body tr { cursor: pointer; }
.el-pagination { --el-pagination-bg-color: var(--bg-secondary); --el-pagination-text-color: var(--text-secondary); --el-pagination-button-bg-color: var(--bg-secondary); --el-pagination-hover-color: var(--accent-blue); }
.el-button--primary { --el-button-bg-color: var(--accent-blue); }
.el-input__wrapper { background: var(--bg-input) !important; box-shadow: 0 0 0 1px var(--border-color) inset !important; }
.el-input__inner { color: var(--text-primary) !important; }
.el-loading-mask { background: rgba(17,24,39,0.8) !important; }

/* ===== 滚动条美化 ===== */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg-primary); }
::-webkit-scrollbar-thumb { background: var(--border-color); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--text-muted); }

/* ===== 数据闪烁动画（实时更新时） ===== */
@keyframes data-flash {
  0% { background: transparent; }
  50% { background: rgba(59,130,246,0.15); }
  100% { background: transparent; }
}
.data-flash { animation: data-flash 0.6s ease; }

/* ===== 涨跌色全局工具类 ===== */
.color-up { color: var(--color-up) !important; }
.color-down { color: var(--color-down) !important; }
.color-flat { color: var(--color-flat) !important; }
.bg-up { background: var(--bg-up) !important; }
.bg-down { background: var(--bg-down) !important; }
</style>