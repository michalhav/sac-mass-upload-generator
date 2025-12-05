import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      redirect: '/settings'
    },
    {
      path: '/settings',
      name: 'settings',
      component: () => import('@/pages/SettingsPage.vue')
    },
    {
      path: '/dimensions',
      name: 'dimensions',
      component: () => import('@/pages/DimensionsPage.vue')
    },
    {
      path: '/csv',
      name: 'csv',
      component: () => import('@/pages/CsvPage.vue')
    },
    {
      path: '/builder',
      name: 'builder',
      component: () => import('@/pages/BuilderPage.vue')
    },
    {
      path: '/templates',
      name: 'templates',
      component: () => import('@/pages/TemplatesPage.vue')
    },
    {
      path: '/generate',
      name: 'generate',
      component: () => import('@/pages/GeneratePage.vue')
    }
  ]
})

export default router
