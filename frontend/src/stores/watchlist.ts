import { defineStore } from 'pinia'
import { ref } from 'vue'
import { watchlistApi } from '@/api'

export const useWatchlistStore = defineStore('watchlist', () => {
  const items = ref<any[]>([])
  const loading = ref(false)

  async function fetchList() {
    loading.value = true
    try {
      const { data } = await watchlistApi.getList()
      if (data.code === 0 && data.data) {
        items.value = data.data.items || []
      }
    } finally {
      loading.value = false
    }
  }

  async function addStock(symbol: string, market = 'sh') {
    await watchlistApi.add(symbol, market)
    await fetchList()
  }

  async function removeStock(symbol: string) {
    await watchlistApi.remove(symbol)
    await fetchList()
  }

  function isWatched(symbol: string) {
    return items.value.some(i => i.symbol === symbol)
  }

  return { items, loading, fetchList, addStock, removeStock, isWatched }
})