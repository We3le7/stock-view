<template>
  <div class="market-page">
    <div class="top-bar">
      <div class="logo">Stock-View</div>
      <div class="nav-tabs">
        <span v-for="tab in tabs" :key="tab.key" :class="['tab', { active: currentTab === tab.key }]"
          @click="switchTab(tab.key)">{{ tab.label }}</span>
      </div>
      <div class="search-box">
        <el-input v-model="searchKeyword" placeholder="输入代码/拼音..." size="small" @keyup.enter="goSearch" clearable>
          <template #prefix><el-icon>🔍</el-icon></template>
        </el-input>
      </div>
      <div class="nav-links">
        <router-link to="/watchlist">自选股</router-link>
      </div>
    </div>

    <div class="main-area">
      <div class="sidebar">
        <div class="sidebar-title">自选股</div>
        <div v-for="s in watchlistStore.items" :key="s.symbol" class="watchlist-item"
          @click="$router.push(`/stock/${s.symbol}`)">
          <span class="code">{{ s.symbol }}</span>
        </div>
        <div v-if="!watchlistStore.items.length" class="empty-tip">暂无自选股</div>
      </div>

      <div class="content">
        <el-table :data="quoteStore.quoteList" stripe style="width: 100%" v-loading="quoteStore.loading"
          @row-click="(row: any) => $router.push(`/stock/${row.symbol}`)" highlight-current-row
          :header-cell-style="{ background: '#16213e', color: '#e0e0e0' }" :row-style="{ cursor: 'pointer' }">
          <el-table-column prop="symbol" label="代码" width="90" />
          <el-table-column prop="name" label="名称" width="100" />
          <el-table-column prop="price" label="最新" width="90" align="right">
            <template #default="{ row }">
              <span :style="{ color: getColor(row.change_pct) }">{{ row.price }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="change_pct" label="涨跌幅" width="100" align="right" sortable>
            <template #default="{ row }">
              <span :style="{ color: getColor(row.change_pct) }">
                {{ row.change_pct > 0 ? '+' : '' }}{{ row.change_pct }}%
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="change" label="涨跌额" width="90" align="right">
            <template #default="{ row }">
              <span :style="{ color: getColor(row.change) }">{{ row.change > 0 ? '+' : '' }}{{ row.change }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="volume" label="成交量" width="100" align="right">
            <template #default="{ row }">{{ formatVolume(row.volume) }}</template>
          </el-table-column>
          <el-table-column prop="amount" label="成交额" width="110" align="right">
            <template #default="{ row }">{{ formatAmount(row.amount) }}</template>
          </el-table-column>
          <el-table-column prop="turnover_rate" label="换手率" width="90" align="right">
            <template #default="{ row }">{{ row.turnover_rate }}%</template>
          </el-table-column>
          <el-table-column prop="high" label="最高" width="90" align="right" />
          <el-table-column prop="low" label="最低" width="90" align="right" />
        </el-table>

        <div class="pagination">
          <el-pagination v-model:current-page="page" :page-size="pageSize" :total="quoteStore.total"
            layout="prev, pager, next" @current-change="loadData" />
        </div>
      </div>
    </div>

    <div class="status-bar">
      <span>Stock-View v1.0</span>
      <span>|</span>
      <span>A股实时行情</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useQuoteStore } from '@/stores/quote'
import { useWatchlistStore } from '@/stores/watchlist'

const router = useRouter()
const quoteStore = useQuoteStore()
const watchlistStore = useWatchlistStore()

const tabs = [
  { key: 'all', label: '沪深A股' },
  { key: 'gainers', label: '涨幅榜' },
  { key: 'losers', label: '跌幅榜' },
  { key: 'turnover', label: '换手榜' },
]
const currentTab = ref('all')
const searchKeyword = ref('')
const page = ref(1)
const pageSize = ref(20)
let timer: any = null

function getColor(val: number) {
  return val > 0 ? 'var(--color-up)' : val < 0 ? 'var(--color-down)' : 'var(--color-flat)'
}

function formatVolume(v: number) {
  if (!v) return '-'
  return v > 10000 ? (v / 10000).toFixed(1) + '万' : v.toString()
}

function formatAmount(v: number) {
  if (!v) return '-'
  return v > 100000000 ? (v / 100000000).toFixed(1) + '亿' : v > 10000 ? (v / 10000).toFixed(0) + '万' : v.toString()
}

function switchTab(key: string) {
  currentTab.value = key
  const sortMap: Record<string, { sortBy: string; sortOrder: string }> = {
    all: { sortBy: 'change_pct', sortOrder: 'desc' },
    gainers: { sortBy: 'change_pct', sortOrder: 'desc' },
    losers: { sortBy: 'change_pct', sortOrder: 'asc' },
    turnover: { sortBy: 'turnover', sortOrder: 'desc' },
  }
  const s = sortMap[key] || sortMap.all
  page.value = 1
  quoteStore.fetchList(page.value, pageSize.value, s.sortBy, s.sortOrder)
}

function loadData() {
  const sortMap: Record<string, { sortBy: string; sortOrder: string }> = {
    all: { sortBy: 'change_pct', sortOrder: 'desc' },
    gainers: { sortBy: 'change_pct', sortOrder: 'desc' },
    losers: { sortBy: 'change_pct', sortOrder: 'asc' },
    turnover: { sortBy: 'turnover', sortOrder: 'desc' },
  }
  const s = sortMap[currentTab.value] || sortMap.all
  quoteStore.fetchList(page.value, pageSize.value, s.sortBy, s.sortOrder)
}

function goSearch() {
  if (searchKeyword.value.trim()) {
    router.push(`/search?keyword=${searchKeyword.value.trim()}`)
  }
}

onMounted(() => {
  loadData()
  watchlistStore.fetchList()
  timer = setInterval(loadData, 10000) // 10秒刷新
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>

<style scoped>
.market-page { display: flex; flex-direction: column; height: 100vh; }
.top-bar { display: flex; align-items: center; height: 48px; padding: 0 16px; background: var(--bg-secondary); border-bottom: 1px solid var(--border-color); gap: 16px; }
.logo { font-size: 18px; font-weight: bold; color: #409eff; white-space: nowrap; }
.nav-tabs { display: flex; gap: 4px; }
.tab { padding: 6px 14px; cursor: pointer; border-radius: 4px; font-size: 13px; color: var(--text-secondary); transition: all .2s; }
.tab.active { background: #409eff; color: #fff; }
.tab:hover { color: #fff; }
.search-box { flex: 1; max-width: 280px; }
.nav-links { display: flex; gap: 12px; margin-left: auto; }
.nav-links a { color: var(--text-secondary); text-decoration: none; font-size: 13px; }
.nav-links a:hover { color: #409eff; }
.main-area { display: flex; flex: 1; overflow: hidden; }
.sidebar { width: 120px; background: var(--bg-secondary); border-right: 1px solid var(--border-color); overflow-y: auto; padding: 8px; }
.sidebar-title { font-size: 12px; color: var(--text-secondary); margin-bottom: 8px; padding: 4px; }
.watchlist-item { padding: 6px 8px; cursor: pointer; border-radius: 4px; font-size: 12px; }
.watchlist-item:hover { background: var(--bg-card); }
.code { color: var(--text-primary); }
.empty-tip { font-size: 11px; color: var(--text-secondary); padding: 8px; }
.content { flex: 1; padding: 12px; overflow: auto; }
.pagination { display: flex; justify-content: center; padding: 12px 0; }
.status-bar { height: 28px; display: flex; align-items: center; padding: 0 16px; gap: 8px; font-size: 11px; color: var(--text-secondary); background: var(--bg-secondary); border-top: 1px solid var(--border-color); }

:deep(.el-table) { --el-table-bg-color: var(--bg-primary); --el-table-tr-bg-color: var(--bg-primary); --el-table-header-bg-color: var(--bg-secondary); --el-table-row-hover-bg-color: var(--bg-card); --el-table-border-color: var(--border-color); --el-table-text-color: var(--text-primary); }
:deep(.el-table__body tr) { cursor: pointer; }
</style>