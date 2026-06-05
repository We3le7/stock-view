<template>
  <div class="watchlist-page">
    <!-- 页面标题 -->
    <div class="wl-header">
      <div class="wl-title-row">
        <span class="wl-title">⭐ 自选股</span>
        <span class="wl-count">{{ stocks.length }} 只</span>
      </div>
      <div class="wl-actions">
        <router-link to="/search" class="add-btn">
          <span>+ 添加自选</span>
        </router-link>
      </div>
    </div>

    <!-- 自选股列表 -->
    <div class="wl-content" v-loading="loading">
      <div v-if="stocks.length" class="stock-list">
        <div v-for="s in stocks" :key="s.symbol" class="stock-card"
          @click="$router.push(`/stock/${s.symbol}`)">
          <!-- 涨跌幅背景色条 -->
          <div class="card-bg-bar" :class="s.change_pct > 0 ? 'bg-up' : s.change_pct < 0 ? 'bg-down' : ''"></div>

          <div class="card-body">
            <div class="card-left">
              <div class="card-name">{{ s.name }}</div>
              <div class="card-code">{{ s.symbol }}</div>
            </div>
            <div class="card-center">
              <div class="card-price" :class="getColorClass(s.change_pct)">
                {{ formatPrice(s.price) }}
              </div>
            </div>
            <div class="card-right">
              <div :class="['card-pct', getColorClass(s.change_pct)]">
                {{ s.change_pct > 0 ? '+' : '' }}{{ s.change_pct }}%
              </div>
              <div :class="['card-change', getColorClass(s.change)]">
                {{ s.change > 0 ? '+' : '' }}{{ formatPrice(s.change) }}
              </div>
            </div>
            <div class="card-action">
              <el-button type="danger" size="small" text @click.stop="removeStock(s.symbol)">
                ✕
              </el-button>
            </div>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-if="!stocks.length && !loading" class="empty-state">
        <div class="empty-icon">📋</div>
        <div class="empty-text">还没有自选股</div>
        <div class="empty-sub">搜索并添加你关注的股票</div>
        <router-link to="/search">
          <el-button type="primary" round>去搜索添加</el-button>
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useWatchlistStore } from '@/stores/watchlist'
import { quoteApi } from '@/api'

const watchlistStore = useWatchlistStore()
const stocks = ref<any[]>([])
const loading = ref(true)

function getColorClass(val: number) {
  return val > 0 ? 'color-up' : val < 0 ? 'color-down' : 'color-flat'
}

function formatPrice(v: number) {
  if (!v && v !== 0) return '-'
  return Number(v).toFixed(2)
}

async function loadStocks() {
  loading.value = true
  await watchlistStore.fetchList()
  if (watchlistStore.items.length) {
    const symbols = watchlistStore.items.map(i => i.symbol).join(',')
    const items = await quoteApi.getRealtime(symbols).then(r => r.data?.data?.items || [])
    stocks.value = items
  } else {
    stocks.value = []
  }
  loading.value = false
}

async function removeStock(symbol: string) {
  await watchlistStore.removeStock(symbol)
  stocks.value = stocks.value.filter(s => s.symbol !== symbol)
  ElMessage.success('已移出自选股')
}

onMounted(loadStocks)
</script>

<style scoped>
.watchlist-page {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}

/* ===== 头部 ===== */
.wl-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-lg);
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
  flex-shrink: 0;
}

.wl-title-row { display: flex; align-items: baseline; gap: var(--space-sm); }

.wl-title {
  font-size: var(--font-xl);
  font-weight: 700;
}

.wl-count {
  font-size: var(--font-sm);
  color: var(--text-muted);
}

.wl-actions { display: flex; }

.add-btn {
  display: flex;
  align-items: center;
  padding: 6px 16px;
  background: rgba(59,130,246,0.12);
  color: var(--accent-blue);
  border-radius: var(--radius-md);
  font-size: var(--font-sm);
  font-weight: 500;
  text-decoration: none;
  cursor: pointer;
  transition: background 0.15s;
}

.add-btn:hover { background: rgba(59,130,246,0.2); }

/* ===== 内容区 ===== */
.wl-content {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-md);
}

/* ===== 股票卡片 ===== */
.stock-list { display: flex; flex-direction: column; gap: var(--space-xs); }

.stock-card {
  position: relative;
  border-radius: var(--radius-md);
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.15s, box-shadow 0.15s;
  border: 1px solid var(--border-color);
}

.stock-card:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.card-bg-bar {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
  border-radius: 0 2px 2px 0;
}

.card-body {
  display: flex;
  align-items: center;
  padding: var(--space-md) var(--space-lg);
  background: var(--bg-secondary);
  gap: var(--space-md);
}

.card-left { display: flex; flex-direction: column; min-width: 100px; }

.card-name {
  font-size: var(--font-md);
  font-weight: 600;
  color: var(--text-primary);
  line-height: 1.3;
}

.card-code {
  font-size: var(--font-xs);
  color: var(--text-muted);
}

.card-center { flex: 1; }

.card-price {
  font-size: var(--font-lg);
  font-weight: 700;
}

.card-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  min-width: 80px;
}

.card-pct {
  font-size: var(--font-md);
  font-weight: 700;
  padding: 2px 8px;
  border-radius: var(--radius-sm);
}

.card-pct.color-up { background: var(--color-up-bg); }
.card-pct.color-down { background: var(--color-down-bg); }

.card-change {
  font-size: var(--font-xs);
  margin-top: 2px;
}

.card-action { flex-shrink: 0; }

/* ===== 空状态 ===== */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 400px;
  gap: var(--space-md);
}

.empty-icon { font-size: 48px; opacity: 0.5; }

.empty-text {
  font-size: var(--font-lg);
  font-weight: 600;
  color: var(--text-secondary);
}

.empty-sub {
  font-size: var(--font-sm);
  color: var(--text-muted);
}
</style>