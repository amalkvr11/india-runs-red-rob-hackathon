<template>
  <div class="dashboard">
    <!-- Hero Stats -->
    <div class="stats-grid">
      <Card v-for="s in statCards" :key="s.label" class="stat-card" @click="s.action">
        <template #content>
          <div class="stat-inner">
            <div class="stat-icon" :style="{ background: s.bg }">
              <i :class="s.icon"></i>
            </div>
            <div class="stat-body">
              <span class="stat-value">{{ s.value }}</span>
              <span class="stat-label">{{ s.label }}</span>
            </div>
            <div class="stat-trend" v-if="s.trend">
              <i :class="s.trendIcon"></i> {{ s.trend }}
            </div>
          </div>
        </template>
      </Card>
    </div>

    <!-- Charts Row -->
    <div class="charts-grid">
      <Card class="chart-card chart-wide">
        <template #title>
          <div class="card-header"><i class="pi pi-chart-bar"></i> Score Distribution</div>
        </template>
        <template #content>
          <apexchart type="bar" height="300" :options="histogramOptions" :series="histogramSeries" />
        </template>
      </Card>
      <Card class="chart-card">
        <template #title>
          <div class="card-header"><i class="pi pi-star"></i> Avg Scores vs Weights</div>
        </template>
        <template #content>
          <apexchart type="radar" height="300" :options="radarOptions" :series="radarSeries" />
        </template>
      </Card>
    </div>

    <div class="charts-grid">
      <Card class="chart-card">
        <template #title>
          <div class="card-header"><i class="pi pi-briefcase"></i> Top Titles</div>
        </template>
        <template #content>
          <apexchart type="bar" height="300" :options="titleOptions" :series="titleSeries" />
        </template>
      </Card>
      <Card class="chart-card">
        <template #title>
          <div class="card-header"><i class="pi pi-map-marker"></i> Top Locations</div>
        </template>
        <template #content>
          <apexchart type="donut" height="300" :options="locOptions" :series="locSeries" />
        </template>
      </Card>
    </div>

    <!-- Honeypot Warning -->
    <Card v-if="honeypotCount > 0" class="honey-card">
      <template #content>
        <div class="honey-inner">
          <i class="pi pi-exclamation-triangle honey-icon"></i>
          <div>
            <strong>{{ honeypotCount }} honeypot candidates</strong> detected in top 100
            <span style="color: var(--p-surface-600); font-size: 0.85rem; display: block; margin-top: 2px;">
              Suspicious profiles with inflated credentials have been penalized automatically.
            </span>
          </div>
          <Badge :value="`${(honeypotCount / (store.results?.length || 1) * 100).toFixed(0)}%`" severity="warn" />
        </div>
      </template>
    </Card>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useRankerStore } from '../stores/ranker'
import Card from 'primevue/card'
import Badge from 'primevue/badge'

const store = useRankerStore()
const router = useRouter()

const statCards = computed(() => [
  { label: 'Total Ranked', value: store.stats?.count || 0, icon: 'pi pi-users', bg: 'linear-gradient(135deg, #00bcd4, #0097a7)', action: () => router.push('/results') },
  { label: 'Top Score', value: store.topScore.toFixed(4), icon: 'pi pi-arrow-up', bg: 'linear-gradient(135deg, #4caf50, #2e7d32)', trend: 'Rank #1' },
  { label: 'Avg Score', value: store.avgScore.toFixed(4), icon: 'pi pi-chart-line', bg: 'linear-gradient(135deg, #ff9800, #e65100)' },
  { label: 'Bottom Score', value: store.bottomScore.toFixed(4), icon: 'pi pi-arrow-down', bg: 'linear-gradient(135deg, #ab47bc, #6a1b9a)', trend: `Rank #${store.results?.length || 0}` },
])

const honeypotCount = computed(() => store.results?.filter(r => r.honeypot?.is_honeypot).length || 0)

// Histogram
const histogramSeries = computed(() => {
  if (!store.results?.length) return []
  const bins = 15
  const scores = store.results.map(r => r.score)
  const min = Math.min(...scores)
  const max = Math.max(...scores)
  const w = (max - min) / bins || 1
  const counts = Array(bins).fill(0)
  store.results.forEach(r => {
    const idx = Math.min(Math.floor((r.score - min) / w), bins - 1)
    counts[idx]++
  })
  return [{ name: 'Candidates', data: counts }]
})

const histogramOptions = computed(() => ({
  chart: { type: 'bar', toolbar: { show: false }, fontFamily: 'Inter' },
  colors: ['#00bcd4'],
  plotOptions: { bar: { borderRadius: 6, columnWidth: '85%' } },
  dataLabels: { enabled: false },
  xaxis: {
    categories: histogramSeries.value[0]?.data?.map((_, i) => {
      const scores = store.results.map(r => r.score)
      const min = Math.min(...scores); const max = Math.max(...scores)
      const w = (max - min) / 15 || 1
      return (min + i * w).toFixed(3)
    }) || [],
    labels: { style: { colors: '#8b8fa3', fontSize: '10px' }, rotate: -45 },
  },
  yaxis: { labels: { style: { colors: '#8b8fa3' } } },
  grid: { borderColor: '#2d3154' },
  tooltip: { theme: 'dark' },
}))

// Radar
const radarSeries = computed(() => {
  if (!store.results?.length) return []
  const dims = Object.keys(store.weights)
  const avgs = dims.map(d => store.results.reduce((a, r) => a + (r.sub_scores[d] || 0), 0) / store.results.length)
  const ws = dims.map(d => store.weights[d])
  return [
    { name: 'Avg Score', data: avgs },
    { name: 'Weight', data: ws },
  ]
})

const radarOptions = computed(() => ({
  chart: { type: 'radar', toolbar: { show: false }, fontFamily: 'Inter' },
  colors: ['#00bcd4', '#ff9800'],
  xaxis: {
    categories: Object.keys(store.weights).map(d => d.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())),
    labels: { style: { colors: '#e4e6f0' } },
  },
  yaxis: { show: false, min: 0, max: 1 },
  markers: { size: 4 },
  stroke: { width: 2 },
  fill: { opacity: 0.15 },
  tooltip: { theme: 'dark' },
  legend: { labels: { colors: '#e4e6f0' } },
}))

// Title bar
const titleSeries = computed(() => {
  if (!store.results?.length) return []
  const t = {}
  store.results.forEach(r => {
    const key = (r.current_title || 'Unknown').slice(0, 30)
    t[key] = (t[key] || 0) + 1
  })
  const sorted = Object.entries(t).sort((a, b) => b[1] - a[1]).slice(0, 12)
  return [{ name: 'Count', data: sorted.map(([, c]) => c) }]
})

const titleOptions = computed(() => ({
  chart: { type: 'bar', toolbar: { show: false }, fontFamily: 'Inter' },
  colors: ['#00bcd4'],
  plotOptions: { bar: { borderRadius: 4, horizontal: true } },
  dataLabels: { enabled: false },
  xaxis: {
    categories: (() => {
      const t = {}
      store.results?.forEach(r => {
        const key = (r.current_title || 'Unknown').slice(0, 30)
        t[key] = (t[key] || 0) + 1
      })
      return Object.entries(t).sort((a, b) => b[1] - a[1]).slice(0, 12).map(([l]) => l)
    })(),
    labels: { style: { colors: '#e4e6f0', fontSize: '10px' } },
  },
  yaxis: { labels: { style: { colors: '#8b8fa3', fontSize: '10px' } } },
  grid: { borderColor: '#2d3154' },
  tooltip: { theme: 'dark' },
}))

// Location donut
const locSeries = computed(() => {
  if (!store.results?.length) return []
  const l = {}
  store.results.forEach(r => {
    const loc = r.location?.split(',')[0] || 'Unknown'
    l[loc] = (l[loc] || 0) + 1
  })
  const sorted = Object.entries(l).sort((a, b) => b[1] - a[1]).slice(0, 8)
  return sorted.map(([, v]) => v)
})

const locOptions = computed(() => ({
  chart: { type: 'donut', fontFamily: 'Inter' },
  labels: (() => {
    const l = {}
    store.results?.forEach(r => {
      const loc = r.location?.split(',')[0] || 'Unknown'
      l[loc] = (l[loc] || 0) + 1
    })
    return Object.entries(l).sort((a, b) => b[1] - a[1]).slice(0, 8).map(([k]) => k)
  })(),
  colors: ['#00bcd4', '#ff9800', '#4caf50', '#ef5350', '#ab47bc', '#26c6da', '#66bb6a', '#ff7043'],
  dataLabels: { enabled: true, style: { colors: '#fff', fontSize: '11px' } },
  legend: { position: 'bottom', labels: { colors: '#e4e6f0' } },
  plotOptions: { pie: { donut: { size: '55%' } } },
  tooltip: { theme: 'dark' },
}))
</script>

<style scoped>
.dashboard { display: flex; flex-direction: column; gap: 1.25rem; }

.stats-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 1rem; }
.stat-card { cursor: pointer; transition: transform 0.2s; }
.stat-card:hover { transform: translateY(-2px); }
.stat-inner { display: flex; align-items: center; gap: 1rem; }
.stat-icon { width: 48px; height: 48px; border-radius: 12px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.stat-icon i { font-size: 1.3rem; color: #fff; }
.stat-body { display: flex; flex-direction: column; flex: 1; }
.stat-value { font-size: 1.3rem; font-weight: 700; color: var(--p-surface-950); }
.stat-label { font-size: 0.75rem; color: var(--p-surface-600); }
.stat-trend { font-size: 0.7rem; color: var(--p-surface-500); display: flex; align-items: center; gap: 2px; }

.charts-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
@media (max-width: 1000px) { .charts-grid { grid-template-columns: 1fr; } }
.chart-wide { grid-column: span 1; }
@media (min-width: 1000px) { .chart-wide:first-child { grid-column: span 1; } }
.chart-card :deep(.p-card-title) { font-size: 0.85rem; color: var(--p-surface-600); }
.card-header { display: flex; align-items: center; gap: 0.5rem; }
.card-header i { font-size: 1rem; }

.honey-card { border: 1px solid var(--p-yellow-500); }
.honey-inner { display: flex; align-items: center; gap: 1rem; }
.honey-icon { font-size: 2rem; color: var(--p-yellow-500); }
</style>
