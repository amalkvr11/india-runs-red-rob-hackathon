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
              <i class="pi pi-arrow-up-right"></i> {{ s.trend }}
            </div>
          </div>
        </template>
      </Card>
    </div>

    <!-- Charts Row -->
    <div class="charts-grid">
      <Card class="chart-card chart-wide">
        <template #title>
          <div class="card-header">
            <i class="pi pi-chart-bar"></i> 
            <span>Score Distribution</span>
            <Badge :value="`${store.results?.length || 0} candidates`" severity="info" size="small" />
          </div>
        </template>
        <template #content>
          <apexchart type="bar" height="300" :options="histogramOptions" :series="histogramSeries" />
        </template>
      </Card>
      <Card class="chart-card">
        <template #title>
          <div class="card-header">
            <i class="pi pi-star"></i> 
            <span>Score Dimensions</span>
          </div>
        </template>
        <template #content>
          <apexchart type="radar" height="300" :options="radarOptions" :series="radarSeries" />
        </template>
      </Card>
    </div>

    <div class="charts-grid">
      <Card class="chart-card">
        <template #title>
          <div class="card-header">
            <i class="pi pi-briefcase"></i> 
            <span>Top Titles</span>
          </div>
        </template>
        <template #content>
          <apexchart type="bar" height="300" :options="titleOptions" :series="titleSeries" />
        </template>
      </Card>
      <Card class="chart-card">
        <template #title>
          <div class="card-header">
            <i class="pi pi-map-marker"></i> 
            <span>Top Locations</span>
            <Badge v-if="locSeries.length > 0" :value="`${locSeries.length} locations`" severity="success" size="small" />
          </div>
        </template>
        <template #content>
          <div v-if="!store.results?.length" class="empty-chart">
            <i class="pi pi-database" style="font-size: 2rem; margin-bottom: 0.5rem;"></i>
            <span>No results loaded</span>
          </div>
          <apexchart v-else type="donut" height="320" :options="locOptions" :series="locSeries" />
        </template>
      </Card>
    </div>

    <!-- Honeypot Warning -->
    <Card v-if="honeypotCount > 0" class="honey-card">
      <template #content>
        <div class="honey-inner">
          <div class="honey-icon-wrapper">
            <i class="pi pi-exclamation-triangle honey-icon"></i>
          </div>
          <div class="honey-content">
            <strong>{{ honeypotCount }} honeypot candidates</strong> detected in top 100
            <span style="color: var(--p-surface-600); font-size: 0.85rem; display: block; margin-top: 4px;">
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
  chart: { 
    type: 'donut', 
    fontFamily: 'Inter',
    animations: {
      enabled: true,
      easing: 'easeinout',
      speed: 800
    }
  },
  labels: (() => {
    const l = {}
    store.results?.forEach(r => {
      const loc = r.location?.split(',')[0] || 'Unknown'
      l[loc] = (l[loc] || 0) + 1
    })
    return Object.entries(l).sort((a, b) => b[1] - a[1]).slice(0, 8).map(([k]) => k)
  })(),
  colors: ['#00bcd4', '#ff9800', '#4caf50', '#ef5350', '#ab47bc', '#26c6da', '#66bb6a', '#ff7043'],
  dataLabels: {
    enabled: true,
    style: {
      colors: ['#fff'],
      fontSize: '12px',
      fontWeight: 600
    },
    dropShadow: {
      enabled: true,
      top: 1,
      left: 1,
      blur: 2,
      opacity: 0.8
    }
  },
  legend: {
    position: 'bottom',
    fontSize: '12px',
    fontWeight: 500,
    labels: {
      colors: '#e4e6f0',
      useSeriesColors: false
    },
    markers: {
      size: 8,
      strokeWidth: 0
    },
    itemMargin: {
      horizontal: 8,
      vertical: 4
    }
  },
  plotOptions: {
    pie: {
      donut: {
        size: '55%',
        labels: {
          show: true,
          name: {
            show: true,
            fontSize: '14px',
            fontWeight: 600,
            color: '#e4e6f0'
          },
          value: {
            show: true,
            fontSize: '16px',
            fontWeight: 700,
            color: '#fff',
            formatter: function(val) {
              return val + ' candidates'
            }
          },
          total: {
            show: true,
            label: 'Total',
            fontSize: '12px',
            color: '#8b8fa3',
            formatter: function(w) {
              return w.globals.seriesTotals.reduce((a, b) => a + b, 0)
            }
          }
        }
      }
    }
  },
  stroke: {
    show: true,
    width: 2,
    colors: ['#1e2244']
  },
  tooltip: {
    enabled: true,
    theme: 'dark',
    fillSeriesColor: false,
    y: {
      formatter: function(value, { seriesIndex, w }) {
        const total = w.globals.seriesTotals.reduce((a, b) => a + b, 0)
        const percentage = ((value / total) * 100).toFixed(1)
        return `${value} candidates (${percentage}%)`
      }
    }
  }
}))
</script>

<style scoped>
.dashboard { 
  display: flex; 
  flex-direction: column; 
  gap: 1.5rem; 
}

.stats-grid { 
  display: grid; 
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); 
  gap: 1rem; 
}

.stat-card { 
  cursor: pointer; 
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: 1px solid transparent;
}

.stat-card:hover { 
  transform: translateY(-4px);
  box-shadow: 0 12px 24px -8px rgba(0, 188, 212, 0.2);
  border-color: rgba(0, 188, 212, 0.2);
}

.stat-inner { 
  display: flex; 
  align-items: center; 
  gap: 1rem; 
}

.stat-icon { 
  width: 52px; 
  height: 52px; 
  border-radius: 14px; 
  display: flex; 
  align-items: center; 
  justify-content: center; 
  flex-shrink: 0;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.stat-icon i { 
  font-size: 1.4rem; 
  color: #fff; 
}

.stat-body { 
  display: flex; 
  flex-direction: column; 
  flex: 1; 
}

.stat-value { 
  font-size: 1.4rem; 
  font-weight: 700; 
  color: var(--p-surface-950); 
  letter-spacing: -0.02em;
}

.stat-label { 
  font-size: 0.8rem; 
  color: var(--p-surface-600); 
  font-weight: 500;
  margin-top: 2px;
}

.stat-trend { 
  font-size: 0.75rem; 
  color: var(--p-surface-500); 
  display: flex; 
  align-items: center; 
  gap: 4px;
  padding: 4px 8px;
  background: var(--p-surface-100);
  border-radius: 12px;
}

.charts-grid { 
  display: grid; 
  grid-template-columns: 1fr 1fr; 
  gap: 1.25rem; 
}

@media (max-width: 1000px) { 
  .charts-grid { 
    grid-template-columns: 1fr; 
  } 
}

.chart-wide { 
  grid-column: span 1; 
}

@media (min-width: 1000px) { 
  .chart-wide:first-child { 
    grid-column: span 1; 
  } 
}

.chart-card { 
  border: 1px solid var(--p-surface-100);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  transition: all 0.3s ease;
}

.chart-card:hover {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
}

.chart-card :deep(.p-card-title) { 
  font-size: 0.9rem; 
  color: var(--p-surface-700);
  font-weight: 600;
}

.card-header { 
  display: flex; 
  align-items: center; 
  gap: 0.6rem; 
}

.card-header i { 
  font-size: 1.1rem;
  color: var(--p-primary-500);
}

.card-header span {
  flex: 1;
}

.honey-card { 
  border: 2px solid var(--p-yellow-400);
  background: linear-gradient(135deg, rgba(255, 193, 7, 0.05), rgba(255, 152, 0, 0.05));
  box-shadow: 0 4px 16px rgba(255, 193, 7, 0.15);
}

.honey-inner { 
  display: flex; 
  align-items: center; 
  gap: 1.25rem; 
}

.honey-icon-wrapper {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  background: linear-gradient(135deg, rgba(255, 193, 7, 0.15), rgba(255, 152, 0, 0.15));
  display: flex;
  align-items: center;
  justify-content: center;
}

.honey-icon { 
  font-size: 1.8rem; 
  color: var(--p-yellow-500); 
}

.honey-content {
  flex: 1;
}

.empty-chart { 
  display: flex; 
  flex-direction: column;
  align-items: center; 
  justify-content: center; 
  height: 320px; 
  color: var(--p-surface-500); 
  font-size: 0.95rem;
  background: var(--p-surface-25);
  border-radius: 12px;
  border: 2px dashed var(--p-surface-200);
}

.empty-chart span {
  color: var(--p-surface-600);
  font-weight: 500;
}
</style>
