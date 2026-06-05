import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/market' },
    { path: '/market', component: () => import('@/pages/MarketPage.vue') },
    { path: '/stock/:symbol', component: () => import('@/pages/StockDetailPage.vue') },
    { path: '/watchlist', component: () => import('@/pages/WatchlistPage.vue') },
    { path: '/search', component: () => import('@/pages/SearchPage.vue') },
  ],
})

export default router