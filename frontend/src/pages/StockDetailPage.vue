<template>
  <div class="stock-detail" v-loading="loading">
    <!-- 股票头部信息区 -->
    <div class="detail-header" v-if="quote">
      <div class="header-left">
        <div class="back-btn" @click="$router.back()">
          <span class="back-arrow">←</span>
          <span class="back-text">返回</span>
        </div>
        <div class="stock-info">
          <div class="stock-title">
            <span class="stock-name">{{ quote.name }}</span>
            <span class="stock-code">{{ symbol }}</span>
          </div>
          <div class="price-row">
            <span class="current-price" :class="getColorClass(quote.change_pct)">{{ formatPrice(quote.price) }}</span>
            <span class="price-change" :class="getColorClass(quote.change_pct)">
              {{ quote.change > 0 ? '+' : '' }}{{ formatPrice(quote.change) }}
            </span>
            <span class="price-pct" :class="getColorClass(quote.change_pct)">
              {{ quote.change_pct > 0 ? '+' : '' }}{{ quote.change_pct }}%
            </span>
          </div>
        </div>
      </div>
      <div class="header-right">
        <div class="watchlist-action">
          <el-button :type="watchlistStore.isWatched(symbol) ? 'danger' : 'primary'"
            size="small" @click="toggleWatchlist" round>
            {{ watchlistStore.isWatched(symbol) ? '★ 已自选' : '☆ 加自选' }}
          </el-button>
        </div>
      </div>
    </div>

    <!-- 主体区域 -->
    <div class="detail-body">
      <!-- 左侧图表区 -->
      <div class="chart-section">
        <div class="chart-toolbar">
          <div class="period-group">
            <span v-for="p in periods" :key="p.key"
              :class="['period-btn', { active: currentPeriod === p.key }]"
              @click="switchPeriod(p.key)">{{ p.label }}</span>
          </div>
        </div>
        <div ref="chartRef" class="chart-container"></div>
      </div>

      <!-- 右侧面板区 -->
      <div class="side-panels">
        <!-- 五档盘口 -->
        <div class="panel orderbook-panel" v-if="orderbook">
          <div class="panel-header">
            <span class="panel-icon">📈</span>
            <span class="panel-title">五档盘口</span>
          </div>
          <div class="ob-asks">
            <div v-for="a in [...orderbook.asks].reverse()" :key="'a'+a.level" class="ob-row ask-row">
              <span class="ob-label">卖{{ a.level }}</span>
              <span class="ob-price color-down">{{ formatPrice(a.price) }}</span>
              <span class="ob-vol">{{ a.volume }}</span>
            </div>
          </div>
          <div class="ob-divider"></div>
          <div class="ob-bids">
            <div v-for="b in orderbook.bids" :key="'b'+b.level" class="ob-row bid-row">
              <span class="ob-label">买{{ b.level }}</span>
              <span class="ob-price color-up">{{ formatPrice(b.price) }}</span>
              <span class="ob-vol">{{ b.volume }}</span>
            </div>
          </div>
        </div>

        <!-- 基本数据 -->
        <div class="panel info-panel" v-if="quote">
          <div class="panel-header">
            <span class="panel-icon">📋</span>
            <span class="panel-title">行情数据</span>
          </div>
          <div class="info-grid">
            <div class="info-item">
              <span class="info-label">今开</span>
              <span :class="['info-val', getColorClass(quote.open - quote.prev_close)]">{{ formatPrice(quote.open) }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">最高</span>
              <span :class="['info-val', getColorClass(quote.high - quote.prev_close)]">{{ formatPrice(quote.high) }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">昨收</span>
              <span class="info-val color-flat">{{ formatPrice(quote.prev_close) }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">最低</span>
              <span :class="['info-val', getColorClass(quote.low - quote.prev_close)]">{{ formatPrice(quote.low) }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">成交量</span>
              <span class="info-val">{{ formatVolume(quote.volume) }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">成交额</span>
              <span class="info-val">{{ formatAmount(quote.amount) }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">换手率</span>
              <span class="info-val">{{ quote.turnover_rate }}%</span>
            </div>
          </div>
        </div>

        <!-- AI 分析 -->
        <div class="panel ai-panel">
          <div class="panel-header">
            <span class="panel-icon">🤖</span>
            <span class="panel-title">AI 智能分析</span>
          </div>
          <el-button type="primary" size="small" @click="runAI" :loading="aiLoading" round style="width:100%">
            开始分析
          </el-button>
          <div v-if="aiResult" class="ai-result">
            <div class="ai-trend-badge" :class="'trend-' + aiResult.trend">
              <span class="trend-icon">{{ aiResult.trend === 'bullish' ? '📈' : aiResult.trend === 'bearish' ? '📉' : '➡️' }}</span>
              <span class="trend-text">{{ aiResult.trend === 'bullish' ? '看涨' : aiResult.trend === 'bearish' ? '看跌' : '中性' }}</span>
              <span class="trend-confidence">{{ (aiResult.confidence * 100).toFixed(0) }}% 置信度</span>
            </div>
            <div class="ai-summary">{{ aiResult.summary }}</div>
            <div class="ai-risk-row">
              <span class="risk-label">风险等级</span>
              <span class="risk-badge" :class="'risk-' + aiResult.risk_level">{{ aiResult.risk_level }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
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
  { key: '5m', label: '5分' },
  { key: '15m', label: '15分' },
  { key: 'd', label: '日K' },
  { key: 'w', label: '周K' },
  { key: 'm', label: '月K' },
]
let timer: any = null

function getColorClass(val: number) {
  return val > 0 ? 'color-up' : val < 0 ? 'color-down' : 'color-flat'
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
  await nextTick()
  if (!chart) {
    chart = echarts.init(chartRef.value, undefined, { renderer: 'canvas' })
  }

  if (currentPeriod.value === 'timeline') {
    const { data } = await quoteApi.getTimeline(symbol)
    if (data.code === 0 && data.data) {
      const points = data.data.points || []
      const prevClose = data.data.prev_close || 0
      chart.setOption({
        animation: false,
        backgroundColor: 'transparent',
        grid: { left: 65, right: 15, top: 25, bottom: 35 },
        xAxis: {
          type: 'category',
          data: points.map((p: any) => p.time),
          axisLabel: { color: '#7c8ba6', fontSize: 10 },
          axisLine: { lineStyle: { color: '#2a3444' } },
        },
        yAxis: {
          type: 'value', scale: true,
          axisLabel: { color: '#7c8ba6', fontSize: 10, formatter: (v: number) => v.toFixed(2) },
          splitLine: { lineStyle: { color: '#1e2838', type: 'dashed' } },
          axisLine: { show: false },
        },
        series: [
          {
            type: 'line', data: points.map((p: any) => p.price),
            lineStyle: { color: '#3b82f6', width: 1.5 },
            itemStyle: { color: '#3b82f6' }, symbol: 'none',
            areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: 'rgba(59,130,246,0.3)' }, { offset: 1, color: 'rgba(59,130,246,0)' }] } },
          },
          {
            type: 'line', data: points.map((p: any) => p.avg),
            lineStyle: { color: '#f59e0b', width: 1, type: 'dashed' },
            itemStyle: { color: '#f59e0b' }, symbol: 'none',
          },
        ],
        tooltip: {
          trigger: 'axis',
          backgroundColor: '#1f2937',
          borderColor: '#2a3444',
          textStyle: { color: '#f0f4f8', fontSize: 12 },
        },
      }, true)
    }
  } else {
    const { data } = await quoteApi.getKline({ symbol, period: currentPeriod.value, limit: 120 })
    if (data.code === 0 && data.data) {
      const items = data.data.items || []
      chart.setOption({
        animation: false,
        backgroundColor: 'transparent',
        grid: [
          { left: 65, right: 15, top: 20, height: '55%' },
          { left: 65, right: 15, top: '72%', height: '16%' },
        ],
        xAxis: [
          { type: 'category', data: items.map((i: any) => i.date), axisLabel: { color: '#7c8ba6', fontSize: 10 }, axisLine: { lineStyle: { color: '#2a3444' } }, gridIndex: 0 },
          { type: 'category', data: items.map((i: any) => i.date), gridIndex: 1, axisLabel: { show: false }, axisLine: { lineStyle: { color: '#2a3444' } }, axisTick: { show: false } },
        ],
        yAxis: [
          { type: 'value', scale: true, axisLabel: { color: '#7c8ba6', fontSize: 10, formatter: (v: number) => v.toFixed(2) }, splitLine: { lineStyle: { color: '#1e2838', type: 'dashed' } }, axisLine: { show: false }, gridIndex: 0 },
          { type: 'value', axisLabel: { color: '#7c8ba6', fontSize: 9 }, splitLine: { lineStyle: { color: '#1e2838' } }, axisLine: { show: false }, gridIndex: 1 },
        ],
        dataZoom: [
          { type: 'inside', xAxisIndex: [0, 1], start: 60, end: 100 },
          { type: 'slider', xAxisIndex: [0, 1], start: 60, end: 100, bottom: 4, height: 16, borderColor: '#2a3444', fillerColor: 'rgba(59,130,246,0.15)', handleStyle: { color: '#3b82f6' }, textStyle: { color: '#7c8ba6' } },
        ],
        tooltip: {
          trigger: 'axis', axisPointer: { type: 'cross', crossStyle: { color: '#7c8ba6' } },
          backgroundColor: '#1f2937', borderColor: '#2a3444', textStyle: { color: '#f0f4f8', fontSize: 12 },
        },
        series: [
          {
            name: 'K线', type: 'candlestick',
            data: items.map((i: any) => [i.open, i.close, i.low, i.high]),
            itemStyle: {
              color: '#f2364b', color0: '#08b25e',
              borderColor: '#f2364b', borderColor0: '#08b25e',
            },
          },
          {
            name: '成交量', type: 'bar', xAxisIndex: 1, yAxisIndex: 1,
            data: items.map((i: any) => ({
              value: i.volume,
              itemStyle: { color: i.close >= i.open ? '#f2364b' : '#08b25e' },
            })),
          },
        ],
      }, true)
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
    await Promise.all([loadQuote(), loadOrderbook()])
    await nextTick()
    await loadChart()
  } finally {
    loading.value = false
  }
  watchlistStore.fetchList()
  timer = setInterval(() => { loadQuote(); loadOrderbook() }, 10000)
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
  if (chart) { chart.dispose(); chart = null }
})
</script>

<style scoped>
.stock-detail { display: flex; flex-direction: column; height: 100%; }

/* ===== 头部区域 ===== */
.detail-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-md) var(--space-lg);
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
  flex-shrink: 0;
}

.header-left { display: flex; align-items: center; gap: var(--space-lg); }

.back-btn {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  cursor: pointer;
  color: var(--accent-blue);
  font-size: var(--font-sm);
  padding: var(--space-sm);
  border-radius: var(--radius-md);
  transition: background 0.15s;
}

.back-btn:hover { background: var(--bg-hover); }
.back-arrow { font-size: var(--font-lg); }

.stock-info { display: flex; flex-direction: column; gap: var(--space-xs); }

.stock-title { display: flex; align-items: baseline; gap: var(--space-sm); }

.stock-name {
  font-size: var(--font-xl);
  font-weight: 700;
  color: var(--text-primary);
}

.stock-code {
  font-size: var(--font-sm);
  color: var(--text-muted);
}

.price-row { display: flex; align-items: baseline; gap: var(--space-md); }

.current-price {
  font-size: var(--font-xxl);
  font-weight: 700;
  line-height: 1;
}

.price-change {
  font-size: var(--font-lg);
  font-weight: 600;
}

.price-pct {
  font-size: var(--font-md);
  font-weight: 600;
  padding: 2px 8px;
  border-radius: var(--radius-sm);
}

.price-pct.color-up { background: var(--color-up-bg); }
.price-pct.color-down { background: var(--color-down-bg); }

.header-right { display: flex; align-items: center; }

/* ===== 主体布局 ===== */
.detail-body { display: flex; flex: 1; overflow: hidden; }

/* ===== 图表区 ===== */
.chart-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: var(--space-md);
  min-width: 0;
}

.chart-toolbar {
  display: flex;
  align-items: center;
  padding-bottom: var(--space-sm);
  flex-shrink: 0;
}

.period-group { display: flex; gap: 2px; }

.period-btn {
  padding: 4px 12px;
  font-size: var(--font-sm);
  color: var(--text-secondary);
  cursor: pointer;
  border-radius: var(--radius-sm);
  transition: all 0.15s;
}

.period-btn:hover { color: var(--text-primary); background: var(--bg-hover); }

.period-btn.active {
  color: var(--accent-blue);
  background: rgba(59,130,246,0.12);
  font-weight: 600;
}

.chart-container { flex: 1; min-height: 280px; }

/* ===== 右侧面板 ===== */
.side-panels {
  width: 280px;
  padding: var(--space-md);
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
  flex-shrink: 0;
}

.panel {
  background: var(--bg-secondary);
  border-radius: var(--radius-lg);
  padding: var(--space-md);
  border: 1px solid var(--border-color);
}

.panel-header {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  padding-bottom: var(--space-sm);
  border-bottom: 1px solid var(--border-color);
  margin-bottom: var(--space-md);
}

.panel-icon { font-size: var(--font-md); }
.panel-title { font-size: var(--font-sm); font-weight: 600; color: var(--text-secondary); }

/* ===== 盘口 ===== */
.ob-row {
  display: flex;
  align-items: center;
  font-size: var(--font-sm);
  padding: 3px 0;
}

.ob-label {
  width: 36px;
  color: var(--text-muted);
  font-size: var(--font-xs);
}

.ob-price {
  width: 70px;
  text-align: right;
  font-weight: 600;
}

.ob-vol {
  flex: 1;
  text-align: right;
  color: var(--text-secondary);
  font-size: var(--font-xs);
}

.ask-row { padding-left: 0; }
.bid-row { padding-left: 0; }

.ob-divider {
  height: 1px;
  background: var(--border-color);
  margin: var(--space-sm) 0;
}

/* ===== 行情数据 ===== */
.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-sm);
}

.info-item {
  display: flex;
  justify-content: space-between;
  font-size: var(--font-sm);
  padding: var(--space-xs) 0;
}

.info-label { color: var(--text-muted); }
.info-val { font-weight: 500; }

/* ===== AI 分析 ===== */
.ai-result { margin-top: var(--space-md); }

.ai-trend-badge {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-sm) var(--space-md);
  border-radius: var(--radius-md);
  margin-bottom: var(--space-md);
}

.trend-bullish { background: var(--bg-up); }
.trend-bearish { background: var(--bg-down); }
.trend-neutral { background: var(--bg-hover); }

.trend-icon { font-size: var(--font-lg); }
.trend-text { font-size: var(--font-lg); font-weight: 700; }
.trend-bullish .trend-text { color: var(--color-up); }
.trend-bearish .trend-text { color: var(--color-down); }
.trend-neutral .trend-text { color: var(--color-flat); }
.trend-confidence { font-size: var(--font-xs); color: var(--text-muted); margin-left: auto; }

.ai-summary {
  font-size: var(--font-sm);
  color: var(--text-primary);
  line-height: 1.6;
  padding: var(--space-sm) 0;
}

.ai-risk-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: var(--font-sm);
}

.risk-label { color: var(--text-muted); }

.risk-badge {
  padding: 2px 10px;
  border-radius: var(--radius-sm);
  font-weight: 600;
  font-size: var(--font-xs);
}

.risk-low { background: rgba(8,178,94,0.15); color: var(--color-down); }
.risk-medium { background: rgba(245,158,11,0.15); color: var(--accent-orange); }
.risk-high { background: rgba(242,54,75,0.15); color: var(--color-up); }

/* ===== 移动端适配 ===== */
@media (max-width: 768px) {
  .detail-body { flex-direction: column; }
  .side-panels { width: 100%; flex-direction: row; overflow-x: auto; overflow-y: visible; }
  .side-panels .panel { min-width: 280px; }
  .current-price { font-size: var(--font-xl); }
  .price-change { font-size: var(--font-md); }
  .price-pct { font-size: var(--font-sm); }
}
</style>