<template>
  <div class="search-page">
    <!-- 搜索头部 -->
    <div class="search-header">
      <div class="search-bar">
        <div class="search-icon">🔍</div>
        <input v-model="keyword" class="search-input"
          placeholder="输入股票代码或名称拼音..."
          @input="doSearch" autofocus />
        <div v-if="keyword" class="clear-btn" @click="keyword = ''; results = []">✕</div>
      </div>
    </div>

    <!-- 搜索结果 -->
    <div class="search-body">
      <!-- 有搜索词 - 显示结果 -->
      <div v-if="keyword.trim()" class="results-section">
        <div v-if="results.length" class="result-list">
          <div v-for="item in results" :key="item.symbol" class="result-card"
            @click="$router.push(`/stock/${item.symbol}`)">
            <div class="rc-main">
              <span class="rc-code">{{ item.symbol }}</span>
              <span class="rc-name">{{ item.name }}</span>
            </div>
            <span class="rc-market">{{ item.market?.toUpperCase() }}</span>
            <el-button type="primary" size="small" text @click.stop="addToWatchlist(item)">
              ☆ 加自选
            </el-button>
          </div>
        </div>
        <div v-if="searching" class="search-loading">
          <span class="loading-dot">●</span>
          <span class="loading-text">搜索中...</span>
        </div>
        <div v-if="!results.length && !searching" class="no-result">
          <div class="no-icon">🔎</div>
          <div class="no-text">未找到匹配 "{{ keyword }}" 的股票</div>
          <div class="no-sub">请尝试输入完整的股票代码或名称拼音</div>
        </div>
      </div>

      <!-- 无搜索词 - 显示热门/历史 -->
      <div v-else class="suggest-section">
        <div v-if="searchHistory.length" class="suggest-block">
          <div class="suggest-title">
            <span>搜索历史</span>
            <span class="clear-history" @click="clearHistory">清除</span>
          </div>
          <div class="history-tags">
            <span v-for="h in searchHistory" :key="h" class="history-tag"
              @click="keyword = h; doSearch()">{{ h }}</span>
          </div>
        </div>

        <div class="suggest-block">
          <div class="suggest-title">热门股票</div>
          <div class="hot-list">
            <div v-for="stock in hotStocks" :key="stock.code" class="hot-item"
              @click="$router.push(`/stock/${stock.code}`)">
              <span class="hot-code">{{ stock.code }}</span>
              <span class="hot-name">{{ stock.name }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { stockApi, watchlistApi } from '@/api'
import { useWatchlistStore } from '@/stores/watchlist'

const watchlistStore = useWatchlistStore()
const keyword = ref('')
const results = ref<any[]>([])
const searching = ref(false)
const searchHistory = ref<string[]>([])
let searchTimer: any = null

// 热门股票推荐
const hotStocks = [
  { code: '600519', name: '贵州茅台' },
  { code: '000001', name: '平安银行' },
  { code: '601318', name: '中国平安' },
  { code: '000858', name: '五粮液' },
  { code: '600036', name: '招商银行' },
  { code: '601398', name: '工商银行' },
  { code: '000333', name: '美的集团' },
  { code: '600276', name: '恒瑞医药' },
]

async function doSearch() {
  if (searchTimer) clearTimeout(searchTimer)
  if (!keyword.value.trim()) { results.value = []; return }
  searching.value = true
  searchTimer = setTimeout(async () => {
    try {
      const { data } = await stockApi.search(keyword.value.trim())
      if (data.code === 0) results.value = data.data?.items || []
      // 保存搜索历史
      addHistory(keyword.value.trim())
    } finally {
      searching.value = false
    }
  }, 300)
}

function addHistory(kw: string) {
  const list = searchHistory.value.filter(h => h !== kw)
  list.unshift(kw)
  searchHistory.value = list.slice(0, 10)
  localStorage.setItem('search_history', JSON.stringify(searchHistory.value))
}

function clearHistory() {
  searchHistory.value = []
  localStorage.removeItem('search_history')
}

async function addToWatchlist(item: any) {
  const market = item.market || (item.symbol.startsWith('6') ? 'sh' : 'sz')
  await watchlistApi.add(item.symbol, market)
  ElMessage.success(`已将 ${item.name} 加入自选`)
  watchlistStore.fetchList()
}

onMounted(() => {
  const saved = localStorage.getItem('search_history')
  if (saved) searchHistory.value = JSON.parse(saved)
  // 从路由参数获取初始搜索词
  const initialKw = new URLSearchParams(window.location.search).get('keyword')
  if (initialKw) {
    keyword.value = initialKw
    doSearch()
  }
})
</script>

<style scoped>
.search-page {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}

/* ===== 搜索头部 ===== */
.search-header {
  padding: var(--space-md) var(--space-lg);
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
  flex-shrink: 0;
}

.search-bar {
  display: flex;
  align-items: center;
  background: var(--bg-input);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: var(--space-sm) var(--space-md);
  gap: var(--space-sm);
  transition: border-color 0.2s;
}

.search-bar:focus-within { border-color: var(--accent-blue); }

.search-icon { font-size: 16px; color: var(--text-muted); }

.search-input {
  flex: 1;
  background: none;
  border: none;
  outline: none;
  color: var(--text-primary);
  font-size: var(--font-md);
}

.search-input::placeholder { color: var(--text-muted); }

.clear-btn {
  color: var(--text-muted);
  cursor: pointer;
  font-size: var(--font-sm);
  padding: 2px 6px;
  border-radius: var(--radius-sm);
}

.clear-btn:hover { color: var(--text-primary); background: var(--bg-hover); }

/* ===== 搜索内容区 ===== */
.search-body {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-md);
}

/* ===== 搜索结果 ===== */
.result-list { display: flex; flex-direction: column; gap: var(--space-xs); }

.result-card {
  display: flex;
  align-items: center;
  padding: var(--space-md) var(--space-lg);
  background: var(--bg-secondary);
  border-radius: var(--radius-md);
  cursor: pointer;
  border: 1px solid var(--border-color);
  transition: all 0.15s;
  gap: var(--space-md);
}

.result-card:hover {
  background: var(--bg-hover);
  border-color: var(--accent-blue);
  transform: translateY(-1px);
}

.rc-main { display: flex; align-items: baseline; gap: var(--space-sm); }

.rc-code {
  font-size: var(--font-md);
  font-weight: 600;
  color: var(--text-primary);
}

.rc-name {
  font-size: var(--font-md);
  color: var(--text-secondary);
}

.rc-market {
  font-size: var(--font-xs);
  color: var(--text-muted);
  background: var(--bg-card);
  padding: 2px 8px;
  border-radius: var(--radius-sm);
  margin-left: auto;
}

/* ===== 搜索加载动画 ===== */
.search-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-sm);
  padding: var(--space-xl);
}

.loading-dot {
  color: var(--accent-blue);
  animation: pulse 1s ease infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 0.3; }
  50% { opacity: 1; }
}

.loading-text { font-size: var(--font-sm); color: var(--text-muted); }

/* ===== 无结果 ===== */
.no-result {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-xl);
}

.no-icon { font-size: 40px; opacity: 0.5; }
.no-text { font-size: var(--font-md); color: var(--text-secondary); }
.no-sub { font-size: var(--font-sm); color: var(--text-muted); }

/* ===== 推荐区域 ===== */
.suggest-section {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
}

.suggest-block { }

.suggest-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: var(--font-sm);
  font-weight: 600;
  color: var(--text-secondary);
  padding-bottom: var(--space-sm);
  border-bottom: 1px solid var(--border-color);
}

.clear-history {
  font-size: var(--font-xs);
  color: var(--text-muted);
  cursor: pointer;
}

.clear-history:hover { color: var(--accent-blue); }

.history-tags {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-sm);
  padding-top: var(--space-sm);
}

.history-tag {
  padding: 4px 12px;
  background: var(--bg-card);
  color: var(--text-secondary);
  border-radius: var(--radius-md);
  font-size: var(--font-sm);
  cursor: pointer;
  transition: all 0.15s;
}

.history-tag:hover { background: var(--bg-hover); color: var(--text-primary); }

.hot-list { display: flex; flex-direction: column; gap: var(--space-xs); padding-top: var(--space-sm); }

.hot-item {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-sm) var(--space-md);
  background: var(--bg-secondary);
  border-radius: var(--radius-md);
  cursor: pointer;
  border: 1px solid var(--border-color);
  transition: all 0.15s;
}

.hot-item:hover {
  background: var(--bg-hover);
  transform: translateY(-1px);
}

.hot-code {
  font-size: var(--font-sm);
  font-weight: 600;
  color: var(--text-primary);
  min-width: 70px;
}

.hot-name {
  font-size: var(--font-sm);
  color: var(--text-secondary);
}
</style>