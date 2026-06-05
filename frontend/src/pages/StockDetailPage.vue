<template>
  <div class="stock-detail" v-loading="loading">
    <div class="header" v-if="quote">
      <div class="back" @click="$router.back()">← 返回</div>
      <div class="stock-name">{{ quote.name }}({{ symbol }})</div>
      <div class="price" :style="{ color: getColor(quote.change_pct) }">{{ quote.price }}</div>
      <div class="change" :style="{ color: getColor(quote.change_pct) }">
        {{ quote.change > 0 ? '+' : '' }}{{ quote.change }} ({{ quote.change_pct > 0 ? '+' : '' }}{{ quote.change_pct }}%)
      </div>
      <div class="watchlist-btn">
        <el-button size="small" :type="watchlistStore.isWatched(symbol) ? 'danger' : 'primary'"
          @click="toggleWatchlist">{{ watchlistStore.isWatched(symbol) ? '移出自选' : '加自选' }}</el-button>
      </div>
    </div>

    <div class="body">
      <div class="chart-area">
        <div class="chart-toolbar">
          <span v-for="p in periods" :key="p.key" :class="['period-btn', { active: currentPeriod === p.key }]"
            @click="switchPeriod(p.key)">{{ p.label }}</span>
        </div>
        <div ref="chartRef" class="chart-container"></div>
      </div>

      <div class="sidebar-right">
        <div class="panel orderbook" v-if="orderbook">
          <div class="panel-title">五档盘口</div>
          <div class="ask-side">
            <div v-for="a in [...orderbook.asks].reverse()" :key="'a'+a.level" class="order-row">
              <span class="label">卖{{ a.level }}</span>
              <span class="price" style="color: var(--color-down)">{{ a.price }}</span>
              <span class="vol">{{ a.volume }}</span>
            </div>
          </div>
          <div class="divider"></div>
          <div class="bid-side">
            <div v-for="b in orderbook.bids" :key="'b'+b.level" class="order-row">
              <span class="label">买{{ b.level }}</span>
              <span class="price" style="color: var(--color-up)">{{ b.price }}</span>
              <span class="vol">{{ b.volume }}</span>
            </div>
          </div>
        </div>

        <div class="panel info" v-if="quote">
          <div class="panel-title">基本数据</div>
          <div class="info-grid">
            <div class="info-item"><span class="label">今开</span><span>{{ quote.open }}</span></div>
            <div class="info-item"><span class="label">最高</span><span>{{ quote.high }}</span></div>
            <div class="info-item"><span class="label">昨收</span><span>{{ quote.prev_close }}</span></div>
            <div class="info-item"><span class="label">最低</span><span>{{ quote.low }}</span></div>
            <div class="info-item"><span class="label">成交量</span><span>{{ quote.volume }}</span></div>
            <div class="info-item"><span class="label">成交额</span><span>{{ quote.amount }}</span></div>
            <div class="info-item"><span class="label">换手率</span><span>{{ quote.turnover_rate }}%</span></div>
          </div>
        </div>

        <div class="panel ai-panel">
          <div class="panel-title">AI 分析</div>
          <el-button type="primary" size="small" @click="runAI" :loading="aiLoading" style="width:100%">
            AI 智能分析
          </el-button>
          <div v-if="aiResult" class="ai-result">
            <div class="ai-trend" :style="{ color: aiResult.trend === 'bullish' ? 'var(--color-up)' : aiResult.trend === 'bearish' ? 'var(--color-down)' : 'var(--color-flat)' }">
              {{ aiResult.trend === 'bullish' ? '看涨' : aiResult.trend === 'bearish' ? '看跌' : '中性' }}
              <span class="confidence">置信度: {{ (aiResult.confidence * 100).toFixed(0) }}%</span>
            </div>
            <div class="ai-summary">{{ aiResult.summary }}</div>
            <div class="ai-risk">风险等级: {{ aiResult.risk_level }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import * as echarts from 'echarts'
import { quoteApi, aiApi } from '@/api'
import { useWatchlistStore } from '@/stores/watchlist'

const route = useRoute()
const watchlistStore = useWatchlistStore()
const symbol = route.params.symbol as string

const quote = ref<any>(null)
const orderbook = ref<any>(null)
const aiResult = ref<any>(null)
const loading = ref(true)
const aiLoading = ref(false)
const chartRef = ref<HTMLElement>()
let chart: echarts.ECharts | null = null
const currentPeriod = ref('d')
const periods = [
  { key: 'timeline', label: '分时' },
  { key: 'd', label: '日K' },
  { key: 'w', label: '周K' },
  { key: 'm', label: '月K' },
  { key: '5m', label: '5分' },
  { key: '15m', label: '15分' },
]
let timer: any = null

function getColor(val: number) {
  return val > 0 ? 'var(--color-up)' : val < 0 ? 'var(--color-down)' : 'var(--color-flat)'
}

async function loadQuote() {
  const items = await quoteApi.getRealtime(symbol).then(r => r.data?.data?.items || [])
  if (items.length) quote.value = items[0]
}

async function loadOrderbook() {
  const { data } = await quoteApi.getOrderbook(symbol)
  if (data.code === 0) orderbook.value = data.data
}

async function loadChart() {
  if (!chartRef.value) return
  if (!chart) chart = echarts.init(chartRef.value)

  if (currentPeriod.value === 'timeline') {
    const { data } = await quoteApi.getTimeline(symbol)
    if (data.code === 0 && data.data) {
      const points = data.data.points || []
      const prevClose = data.data.prev_close || 0
      chart.setOption({
        animation: false,
        grid: { left: 60, right: 20, top: 30, bottom: 40 },
        xAxis: { type: 'category', data: points.map((p: any) => p.time), axisLabel: { color: '#999' } },
        yAxis: { type: 'value', scale: true, axisLabel: { color: '#999' }, splitLine: { lineStyle: { color: '#2a2a4a' } } },
        series: [
          { type: 'line', data: points.map((p: any) => p.price), lineStyle: { color: '#409eff' }, itemStyle: { color: '#409eff' }, symbol: 'none' },
          { type: 'line', data: points.map((p: any) => p.avg), lineStyle: { color: '#ffa726', type: 'dashed' }, itemStyle: { color: '#ffa726' }, symbol: 'none' },
        ],
        tooltip: { trigger: 'axis' },
      })
    }
  } else {
    const { data } = await quoteApi.getKline({ symbol, period: currentPeriod.value, limit: 120 })
    if (data.code === 0 && data.data) {
      const items = data.data.items || []
      chart.setOption({
        animation: false,
        grid: [
          { left: 60, right: 20, top: 30, height: '55%' },
          { left: 60, right: 20, top: '72%', height: '18%' },
        ],
        xAxis: [
          { type: 'category', data: items.map((i: any) => i.date), axisLabel: { color: '#999' }, gridIndex: 0 },
          { type: 'category', data: items.map((i: any) => i.date), gridIndex: 1, axisLabel: { show: false } },
        ],
        yAxis: [
          { type: 'value', scale: true, axisLabel: { color: '#999' }, splitLine: { lineStyle: { color: '#2a2a4a' } }, gridIndex: 0 },
          { type: 'value', axisLabel: { color: '#999' }, splitLine: { lineStyle: { color: '#2a2a4a' } }, gridIndex: 1 },
        ],
        dataZoom: [
          { type: 'inside', xAxisIndex: [0, 1], start: 70, end: 100 },
          { type: 'slider', xAxisIndex: [0, 1], start: 70, end: 100, bottom: 5 },
        ],
        tooltip: { trigger: 'axis', axisPointer: { type: 'cross' } },
        series: [
          {
            name: 'K线', type: 'candlestick',
            data: items.map((i: any) => [i.open, i.close, i.low, i.high]),
            itemStyle: { color: '#ef5350', color0: '#26a69a', borderColor: '#ef5350', borderColor0: '#26a69a' },
          },
          {
            name: '成交量', type: 'bar', xAxisIndex: 1, yAxisIndex: 1,
            data: items.map((i: any) => ({ value: i.volume, itemStyle: { color: i.close >= i.open ? '#ef5350' : '#26a69a' } })),
          },
        ],
      })
    }
  }
}

function switchPeriod(key: string) {
  currentPeriod.value = key
  loadChart()
}

async function runAI() {
  aiLoading.value = true
  try {
    const { data } = await aiApi.analyze(symbol)
    if (data.code === 0) aiResult.value = data.data
  } finally {
    aiLoading.value = false
  }
}

function toggleWatchlist() {
  if (watchlistStore.isWatched(symbol)) {
    watchlistStore.removeStock(symbol)
  } else {
    watchlistStore.addStock(symbol, symbol.startsWith('6') ? 'sh' : 'sz')
  }
}

onMounted(async () => {
  try {
    await Promise.all([loadQuote(), loadOrderbook(), loadChart()])
  } finally {
    loading.value = false
  }
  watchlistStore.fetchList()
  timer = setInterval(() => { loadQuote(); loadOrderbook() }, 10000)
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
  if (chart) chart.dispose()
})
</script>

<style scoped>
.stock-detail { height: 100vh; display: flex; flex-direction: column; background: var(--bg-primary); }
.header { display: flex; align-items: center; gap: 12px; padding: 10px 16px; background: var(--bg-secondary); border-bottom: 1px solid var(--border-color); }
.back { cursor: pointer; color: #409eff; font-size: 13px; }
.stock-name { font-size: 16px; font-weight: bold; }
.price { font-size: 22px; font-weight: bold; }
.change { font-size: 14px; }
.watchlist-btn { margin-left: auto; }
.body { display: flex; flex: 1; overflow: hidden; }
.chart-area { flex: 1; display: flex; flex-direction: column; padding: 8px; }
.chart-toolbar { display: flex; gap: 4px; margin-bottom: 8px; }
.period-btn { padding: 4px 10px; font-size: 12px; cursor: pointer; border-radius: 4px; color: var(--text-secondary); }
.period-btn.active { background: #409eff; color: #fff; }
.chart-container { flex: 1; min-height: 300px; }
.sidebar-right { width: 240px; padding: 8px; overflow-y: auto; display: flex; flex-direction: column; gap: 12px; }
.panel { background: var(--bg-secondary); border-radius: 8px; padding: 12px; }
.panel-title { font-size: 13px; font-weight: bold; margin-bottom: 8px; color: var(--text-secondary); }
.order-row { display: flex; justify-content: space-between; font-size: 12px; padding: 2px 0; }
.order-row .label { width: 36px; color: var(--text-secondary); }
.order-row .price { width: 70px; text-align: right; }
.order-row .vol { width: 50px; text-align: right; color: var(--text-secondary); }
.divider { height: 1px; background: var(--border-color); margin: 6px 0; }
.info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 6px; }
.info-item { display: flex; justify-content: space-between; font-size: 12px; }
.info-item .label { color: var(--text-secondary); }
.ai-result { margin-top: 10px; }
.ai-trend { font-size: 18px; font-weight: bold; }
.confidence { font-size: 12px; color: var(--text-secondary); margin-left: 6px; }
.ai-summary { font-size: 12px; margin-top: 6px; line-height: 1.5; color: var(--text-primary); }
.ai-risk { font-size: 12px; margin-top: 4px; color: var(--text-secondary); }
</style>