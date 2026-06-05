<template>
  <div class="search-page">
    <div class="top-bar">
      <div class="back" @click="$router.back()">← 返回</div>
      <div class="search-input">
        <el-input v-model="keyword" placeholder="输入股票代码或名称拼音..." size="large" @input="doSearch" clearable autofocus />
      </div>
    </div>
    <div class="results">
      <div v-for="item in results" :key="item.symbol" class="result-item" @click="$router.push(`/stock/${item.symbol}`)">
        <span class="symbol">{{ item.symbol }}</span>
        <span class="name">{{ item.name }}</span>
        <span class="market">{{ item.market.toUpperCase() }}</span>
      </div>
      <div v-if="!results.length && keyword" class="no-result">未找到匹配的股票</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { stockApi } from '@/api'

const keyword = ref('')
const results = ref<any[]>([])
let searchTimer: any = null

async function doSearch() {
  if (searchTimer) clearTimeout(searchTimer)
  if (!keyword.value.trim()) { results.value = []; return }
  searchTimer = setTimeout(async () => {
    const { data } = await stockApi.search(keyword.value.trim())
    if (data.code === 0) results.value = data.data?.items || []
  }, 300)
}
</script>

<style scoped>
.search-page { height: 100vh; display: flex; flex-direction: column; background: var(--bg-primary); }
.top-bar { display: flex; align-items: center; gap: 12px; padding: 12px 16px; background: var(--bg-secondary); border-bottom: 1px solid var(--border-color); }
.back { cursor: pointer; color: #409eff; font-size: 13px; white-space: nowrap; }
.search-input { flex: 1; }
.results { flex: 1; overflow-y: auto; padding: 8px; }
.result-item { display: flex; align-items: center; gap: 12px; padding: 12px 16px; cursor: pointer; border-radius: 6px; }
.result-item:hover { background: var(--bg-card); }
.symbol { font-weight: bold; font-size: 15px; min-width: 70px; }
.name { flex: 1; font-size: 14px; }
.market { font-size: 11px; color: var(--text-secondary); background: var(--bg-secondary); padding: 2px 6px; border-radius: 3px; }
.no-result { text-align: center; padding: 40px; color: var(--text-secondary); }
</style>