import { defineStore } from 'pinia'
import { ref } from 'vue'
import { quoteApi } from '@/api'

export const useQuoteStore = defineStore('quote', () => {
  const quoteList = ref<any[]>([])
  const currentQuote = ref<any>(null)
  const loading = ref(false)
  const total = ref(0)

  async function fetchList(page = 1, pageSize = 20, sortBy = 'change_pct', sortOrder = 'desc', market = 'all') {
    loading.value = true
    try {
      const { data } = await quoteApi.getList({ page, page_size: pageSize, sort_by: sortBy, sort_order: sortOrder, market })
      if (data.code === 0 && data.data) {
        quoteList.value = data.data.items || []
        total.value = data.data.total || 0
      }
    } finally {
      loading.value = false
    }
  }

  async function fetchRealtime(symbols: string) {
    const { data } = await quoteApi.getRealtime(symbols)
    if (data.code === 0 && data.data) {
      return data.data.items || []
    }
    return []
  }

  function updateQuote(symbol: string, quoteData: any) {
    const idx = quoteList.value.findIndex(q => q.symbol === symbol)
    if (idx >= 0) {
      Object.assign(quoteList.value[idx], quoteData)
    }
    if (currentQuote.value?.symbol === symbol) {
      Object.assign(currentQuote.value, quoteData)
    }
  }

  return { quoteList, currentQuote, loading, total, fetchList, fetchRealtime, updateQuote }
})