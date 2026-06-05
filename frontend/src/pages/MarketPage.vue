<template>
  <div class="market-page">
    <!-- 行情分类 Tab -->
    <div class="market-tabs">
      <div v-for="tab in tabs" :key="tab.key"
        :class="['tab-item', { active: currentTab === tab.key }]"
        @click="switchTab(tab.key)">
        {{ tab.label }}
      </div>
      <div class="tab-search">
        <el-input v-model="searchKeyword" placeholder="输入代码/拼音搜索..." size="small" @keyup.enter="goSearch" clearable>
          <template #prefix><span style="font-size:14px">🔍</span></template>
        </el-input>
      </div>
    </div>

    <div class="market-body">
      <!-- 左侧自选股侧栏 -->
      <aside class="watchlist-sidebar">
        <div class="sidebar-header">
          <span class="sidebar-title">⭐ 自选股</span>
        </div>
        <div class="sidebar-list">
          <div v-for="s in watchlistQuotes" :key="s.symbol" class="sidebar-stock"
            @click="$router.push(`/stock/${s.symbol}`)">
            <div class="stock-main">
              <span class="stock-name">{{ s.name || s.symbol }}</span>
              <span class="stock-code">{{ s.symbol }}</span>
            </div>
            <div class="stock-price" :class="getColorClass(s.change_pct)">
              {{ s.price || '-' }}
            </div>
            <div class="stock-change" :class="getColorClass(s.change_pct)">
              {{ s.change_pct > 0 ? '+' : '' }}{{ s.change_pct || 0 }}%
            </div>
          </div>
          <div v-if="!watchlistStore.items.length" class="sidebar-empty">
            <span>暂无自选股</span>
            <router-link to="/search" class="add-link">去添加 →</router-link>
          </div>
        </div>
      </aside>

      <!-- 主内容区 - 行情表格 -->
      <div class="market-content">
        <el-table :data="quoteStore.quoteList" v-loading="quoteStore.loading"
          @row-click="(row: any) => $router.push(`/stock/${row.symbol}`)"
          highlight-current-row style="width: 100%" :row-class-name="tableRowClass">

          <el-table-column label="代码/名称" width="160" fixed>
            <template #default="{ row }">
              <div class="stock-identity">
                <span class="si-name">{{ row.name }}</span>
                <span class="si-code">{{ row.symbol }}</span>
              </div>
            </template>
          </el-table-column>

          <el-table-column label="最新价" width="100" align="right">
            <template #default="{ row }">
              <span :class="['price-cell', getColorClass(row.change_pct)]">{{ formatPrice(row.price) }}</span>
            </template>
          </el-table-column>

          <el-table-column label="涨跌幅" width="110" align="right" sortable>
            <template #default="{ row }">
              <span :class="['change-cell', getColorClass(row.change_pct)]">
                {{ row.change_pct > 0 ? '+' : '' }}{{ row.change_pct }}%
              </span>
            </template>
          </el-table-column>

          <el-table-column label="涨跌额" width="100" align="right">
            <template #default="{ row }">
              <span :class="getColorClass(row.change)">
                {{ row.change > 0 ? '+' : '' }}{{ formatPrice(row.change) }}
              </span>
            </template>
          </el-table-column>

          <el-table-column label="成交量" width="100" align="right">
            <template #default="{ row }">
              <span class="dim-cell">{{ formatVolume(row.volume) }}</span>
            </template>
          </el-table-column>

          <el-table-column label="成交额" width="110" align="right">
            <template #default="{ row }">
              <span class="dim-cell">{{ formatAmount(row.amount) }}</span>
            </template>
          </el-table-column>

          <el-table-column label="换手率" width="90" align="right">
            <template #default="{ row }">
              <span class="dim-cell">{{ row.turnover_rate }}%</span>
            </template>
          </el-table-column>

          <el-table-column label="最高" width="90" align="right">
            <template #default="{ row }">
              <span :class="getColorClass(row.high - row.prev_close)">{{ formatPrice(row.high) }}</span>
            </template>
          </el-table-column>

          <el-table-column label="最低" width="90" align="right">
            <template #default="{ row }">
              <span :class="getColorClass(row.low - row.prev_close)">{{ formatPrice(row.low) }}</span>
            </template>
          </el-table-column>

          <el-table-column label="今开" width="90" align="right">
            <template #default="{ row }">
              <span :class="getColorClass(row.open - row.prev_close)">{{ formatPrice(row.open) }}</span>
            </template>
          </el-table-column>
        </el-table>

        <div class="pagination-bar">
          <el-pagination v-model:current-page="page" :page-size="pageSize" :total="quoteStore.total"
            layout="prev, pager, next, total" @current-change="loadData" background small />
          <span class="refresh-tip">数据每10秒自动刷新</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useQuoteStore } from '@/stores/quote'
import { useWatchlistStore } from '@/stores/watchlist'
import { quoteApi } from '@/api'

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
const watchlistQuotes = ref<any[]>([])
let timer: any = null

function getColorClass(val: number) {
  return val > 0 ? 'color-up' : val < 0 ? 'color-down' : 'color-flat'
}

function tableRowClass({ row }: any) {
  return row.change_pct > 0 ? 'row-up' : row.change_pct < 0 ? 'row-down' : ''
}

function formatPrice(v: number) {
  if (!v && v !== 0) return '-'
  return Number(v).toFixed(2)
}

function formatVolume(v: number) {
  if (!v) return '-'
  return v > 10000 ? (v / 10000).toFixed(1) + '万' : v.toString()
}

function formatAmount(v: number) {
  if (!v) return '-'
  return v > 100000000 ? (v / 100000000).toFixed(2) + '亿' : v > 10000 ? (v / 10000).toFixed(0) + '万' : v.toString()
}

const sortMap: Record<string, { sortBy: string; sortOrder: string }> = {
  all: { sortBy: 'change_pct', sortOrder: 'desc' },
  gainers: { sortBy: 'change_pct', sortOrder: 'desc' },
  losers: { sortBy: 'change_pct', sortOrder: 'asc' },
  turnover: { sortBy: 'turnover', sortOrder: 'desc' },
}

function switchTab(key: string) {
  currentTab.value = key
  page.value = 1
  loadData()
}

function loadData() {
  const s = sortMap[currentTab.value] || sortMap.all
  quoteStore.fetchList(page.value, pageSize.value, s.sortBy, s.sortOrder)
}

async function loadWatchlistQuotes() {
  await watchlistStore.fetchList()
  if (watchlistStore.items.length) {
    const symbols = watchlistStore.items.map(i => i.symbol).join(',')
    const items = await quoteApi.getRealtime(symbols).then(r => r.data?.data?.items || [])
    watchlistQuotes.value = items
  } else {
    watchlistQuotes.value = []
  }
}

function goSearch() {
  if (searchKeyword.value.trim()) {
    router.push(`/search?keyword=${searchKeyword.value.trim()}`)
  }
}

onMounted(() => {
  loadData()
  loadWatchlistQuotes()
  timer = setInterval(() => {
    loadData()
    loadWatchlistQuotes()
  }, 10000)
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>

<style scoped>
.market-page { display: flex; flex-direction: column; height: 100%; }

/* ===== Tab 切换栏 ===== */
.market-tabs {
  display: flex;
  align-items: center;
  height: 44px;
  padding: 0 var(--space-lg);
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
  gap: var(--space-sm);
  flex-shrink: 0;
}

.tab-item {
  padding: 6px 16px;
  font-size: var(--font-sm);
  font-weight: 500;
  color: var(--text-secondary);
  cursor: pointer;
  border-radius: var(--radius-md);
  transition: all 0.2s ease;
  white-space: nowrap;
}

.tab-item:hover { color: var(--text-primary); background: var(--bg-hover); }

.tab-item.active {
  color: var(--accent-blue);
  background: rgba(59,130,246,0.12);
  font-weight: 600;
}

.tab-search { margin-left: auto; width: 220px; }

/* ===== 主体布局 ===== */
.market-body { display: flex; flex: 1; overflow: hidden; }

/* ===== 左侧自选股 ===== */
.watchlist-sidebar {
  width: 200px;
  background: var(--bg-secondary);
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  overflow: hidden;
}

.sidebar-header {
  padding: var(--space-md) var(--space-lg);
  border-bottom: 1px solid var(--border-color);
}

.sidebar-title {
  font-size: var(--font-sm);
  font-weight: 600;
  color: var(--text-secondary);
}

.sidebar-list {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-xs);
}

.sidebar-stock {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  cursor: pointer;
  border-radius: var(--radius-sm);
  transition: background 0.15s;
  gap: var(--space-sm);
}

.sidebar-stock:hover { background: var(--bg-hover); }

.stock-main {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.stock-name {
  font-size: var(--font-sm);
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.stock-code {
  font-size: var(--font-xs);
  color: var(--text-muted);
}

.stock-price {
  font-size: var(--font-md);
  font-weight: 600;
  text-align: right;
}

.stock-change {
  font-size: var(--font-xs);
  font-weight: 500;
  text-align: right;
  min-width: 48px;
}

.sidebar-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-xl);
  gap: var(--space-sm);
  color: var(--text-muted);
  font-size: var(--font-sm);
}

.add-link {
  color: var(--accent-blue);
  font-size: var(--font-xs);
  text-decoration: none;
}

/* ===== 主内容区 ===== */
.market-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding: var(--space-md);
}

/* ===== 表格行样式 ===== */
.stock-identity {
  display: flex;
  flex-direction: column;
  line-height: 1.3;
}

.si-name {
  font-size: var(--font-md);
  font-weight: 500;
  color: var(--text-primary);
}

.si-code {
  font-size: var(--font-xs);
  color: var(--text-muted);
}

.price-cell {
  font-weight: 600;
  font-size: var(--font-md);
}

.change-cell {
  font-weight: 700;
  font-size: var(--font-md);
}

.dim-cell {
  color: var(--text-secondary);
}

:deep(.row-up) td { background: var(--bg-up) !important; }
:deep(.row-down) td { background: var(--bg-down) !important; }

/* ===== 分页栏 ===== */
.pagination-bar {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-lg);
  padding: var(--space-md) 0;
  flex-shrink: 0;
}

.refresh-tip {
  font-size: var(--font-xs);
  color: var(--text-muted);
}

/* ===== 移动端适配 ===== */
@media (max-width: 768px) {
  .watchlist-sidebar { display: none; }
  .tab-search { width: 140px; }
  .market-content { padding: var(--space-sm); }
}
</style>