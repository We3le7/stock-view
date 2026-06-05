<template>
  <div class="watchlist-page">
    <div class="top-bar">
      <div class="back" @click="$router.back()">← 返回</div>
      <div class="title">自选股</div>
    </div>
    <div class="content">
      <el-table :data="stocks" stripe v-loading="loading" @row-click="(row: any) => $router.push(`/stock/${row.symbol}`)"
        :header-cell-style="{ background: '#16213e', color: '#e0e0e0' }" :row-style="{ cursor: 'pointer' }">
        <el-table-column prop="symbol" label="代码" width="100" />
        <el-table-column prop="name" label="名称" width="120" />
        <el-table-column prop="price" label="最新价" width="100" align="right">
          <template #default="{ row }">
            <span :style="{ color: getColor(row.change_pct) }">{{ row.price }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="change_pct" label="涨跌幅" width="100" align="right">
          <template #default="{ row }">
            <span :style="{ color: getColor(row.change_pct) }">{{ row.change_pct > 0 ? '+' : '' }}{{ row.change_pct }}%</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button type="danger" size="small" text @click.stop="removeStock(row.symbol)">移出</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div v-if="!stocks.length && !loading" class="empty">
        <div>暂无自选股</div>
        <el-button type="primary" @click="$router.push('/market')">去添加</el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useWatchlistStore } from '@/stores/watchlist'
import { quoteApi } from '@/api'

const watchlistStore = useWatchlistStore()
const stocks = ref<any[]>([])
const loading = ref(true)

function getColor(val: number) {
  return val > 0 ? 'var(--color-up)' : val < 0 ? 'var(--color-down)' : 'var(--color-flat)'
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
}

onMounted(loadStocks)
</script>

<style scoped>
.watchlist-page { height: 100vh; display: flex; flex-direction: column; background: var(--bg-primary); }
.top-bar { display: flex; align-items: center; gap: 12px; padding: 12px 16px; background: var(--bg-secondary); border-bottom: 1px solid var(--border-color); }
.back { cursor: pointer; color: #409eff; font-size: 13px; }
.title { font-size: 18px; font-weight: bold; }
.content { flex: 1; padding: 16px; overflow: auto; }
.empty { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 300px; gap: 16px; color: var(--text-secondary); }

:deep(.el-table) { --el-table-bg-color: var(--bg-primary); --el-table-tr-bg-color: var(--bg-primary); --el-table-header-bg-color: var(--bg-secondary); --el-table-row-hover-bg-color: var(--bg-card); --el-table-border-color: var(--border-color); --el-table-text-color: var(--text-primary); }
</style>