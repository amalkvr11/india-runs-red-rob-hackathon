import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', name: 'Dashboard', component: () => import('../views/DashboardView.vue'), meta: { icon: 'pi pi-chart-bar', title: 'Dashboard' } },
  { path: '/results', name: 'Results', component: () => import('../views/ResultsView.vue'), meta: { icon: 'pi pi-list', title: 'Results' } },
  { path: '/candidate/:id', name: 'CandidateDetail', component: () => import('../views/CandidateDetailView.vue'), meta: { icon: 'pi pi-user', title: 'Candidate Detail' } },
  { path: '/statistics', name: 'Statistics', component: () => import('../views/StatisticsView.vue'), meta: { icon: 'pi pi-chart-line', title: 'Statistics' } },
  { path: '/export', name: 'Export', component: () => import('../views/ExportView.vue'), meta: { icon: 'pi pi-download', title: 'Export' } },
  { path: '/about', name: 'About', component: () => import('../views/AboutView.vue'), meta: { icon: 'pi pi-info-circle', title: 'About' } },
]

export default createRouter({ history: createWebHistory(), routes })
