<template>
  <div class="stats-view">
    <div class="stats-charts-grid">
      <Card>
        <template #title><i class="pi pi-chart-bar"></i> Score Distribution</template>
        <template #content>
          <apexchart type="bar" height="320" :options="histOptions" :series="histSeries" />
        </template>
      </Card>
      <Card>
        <template #title><i class="pi pi-map-marker"></i> Location Breakdown</template>
        <template #content>
          <div v-if="!store.results?.length" class="empty-chart">No results loaded</div>
          <apexchart v-else type="pie" height="320" :options="pieOptions" :series="pieSeries" />
        </template>
      </Card>
    </div>

    <Card>
      <template #title><i class="pi pi-chart-line"></i> YoE vs Score</template>
      <template #content>
        <apexchart type="scatter" height="350" :options="scatterOptions" :series="scatterSeries" />
      </template>
    </Card>

    <Card>
      <template #title><i class="pi pi-table"></i> Dimension Statistics</template>
      <template #content>
        <DataTable :value="dimStatsData" stripedRows showGridlines class="dim-stats-table">
          <Column field="label" header="Dimension">
            <template #body="{ data }"><strong>{{ data.label }}</strong></template>
          </Column>
          <Column field="mean" header="Mean" :style="{ width: '100px' }"><template #body="{ data }">{{ data.mean }}</template></Column>
          <Column field="std" header="Std" :style="{ width: '100px' }"><template #body="{ data }">{{ data.std }}</template></Column>
          <Column field="min" header="Min" :style="{ width: '100px' }"><template #body="{ data }">{{ data.min }}</template></Column>
          <Column field="q25" header="25%" :style="{ width: '100px' }"><template #body="{ data }">{{ data.q25 }}</template></Column>
          <Column field="q50" header="50%" :style="{ width: '100px' }"><template #body="{ data }">{{ data.q50 }}</template></Column>
          <Column field="q75" header="75%" :style="{ width: '100px' }"><template #body="{ data }">{{ data.q75 }}</template></Column>
          <Column field="max" header="Max" :style="{ width: '100px' }"><template #body="{ data }">{{ data.max }}</template></Column>
        </DataTable>
      </template>
    </Card>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRankerStore } from '../stores/ranker'
import Card from 'primevue/card'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'

const store = useRankerStore()

function percentile(sorted, p) {
  const idx = Math.floor(sorted.length * p)
  return sorted[idx] ?? 0
}

// Histogram
const histSeries = computed(() => {
  if (!store.results?.length) return []
  const bins = 20
  const scores = store.results.map(r => r.score)
  const mn = Math.min(...scores); const mx = Math.max(...scores)
  const w = (mx - mn) / bins || 1
  const counts = Array(bins).fill(0)
  store.results.forEach(r => counts[Math.min(Math.floor((r.score - mn) / w), bins - 1)]++)
  return [{ name: 'Candidates', data: counts }]
})
const histOptions = computed(() => ({
  chart: { toolbar: { show: false }, fontFamily: 'Inter' },
  colors: ['#00bcd4'], plotOptions: { bar: { borderRadius: 4, columnWidth: '90%' } },
  dataLabels: { enabled: false },
  xaxis: {
    categories: histSeries.value[0]?.data?.map((_, i) => {
      const s = store.results.map(r => r.score); const w = (Math.max(...s) - Math.min(...s)) / 20 || 1
      return (Math.min(...s) + i * w).toFixed(3)
    }) || [],
    labels: { style: { colors: '#8b8fa3', fontSize: '10px' }, rotate: -45 },
  },
  yaxis: { labels: { style: { colors: '#8b8fa3' } } },
  grid: { borderColor: '#2d3154' },
  tooltip: { theme: 'dark' },
}))

// Pie
const pieSeries = computed(() => {
  if (!store.results?.length) return []
  const m = {}
  store.results.forEach(r => {
    const loc = r.location?.split(',')[0] || 'Unknown'
    m[loc] = (m[loc] || 0) + 1
  })
  return Object.entries(m).sort((a, b) => b[1] - a[1]).slice(0, 8).map(([, v]) => v)
})
const pieOptions = computed(() => ({
  chart: { 
    fontFamily: 'Inter',
    animations: {
      enabled: true,
      easing: 'easeinout',
      speed: 800
    }
  },
  labels: (() => {
    if (!store.results?.length) return []
    const m = {}; store.results.forEach(r => { const loc = r.location?.split(',')[0] || 'Unknown'; m[loc] = (m[loc] || 0) + 1 })
    return Object.entries(m).sort((a, b) => b[1] - a[1]).slice(0, 8).map(([k]) => k)
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
  },
  plotOptions: {
    pie: {
      expandOnClick: true,
      customScale: 1
    }
  }
}))

// Scatter
const scatterSeries = computed(() => {
  if (!store.results?.length) return []
  return [{
    name: 'Candidates',
    data: store.results.filter(r => r.yoe != null).map(r => ({ x: r.yoe, y: r.score })),
  }]
})
const scatterOptions = {
  chart: { type: 'scatter', zoom: { enabled: true }, toolbar: { show: false }, fontFamily: 'Inter' },
  colors: ['#00bcd4'],
  xaxis: { title: { text: 'Years of Experience', style: { color: '#8b8fa3' } }, labels: { style: { colors: '#8b8fa3' } } },
  yaxis: { title: { text: 'Score', style: { color: '#8b8fa3' } }, min: 0, max: 1, labels: { style: { colors: '#8b8fa3' } } },
  grid: { borderColor: '#2d3154' },
  tooltip: { theme: 'dark' },
  legend: { labels: { colors: '#e4e6f0' } },
}

// Dimension stats table
const dimStatsData = computed(() => {
  const dims = Object.keys(store.weights || {})
  return dims.map(key => {
    const vals = store.results?.map(r => r.sub_scores[key] || 0).sort((a, b) => a - b) || []
    const n = vals.length || 1
    const mean = (vals.reduce((a, b) => a + b, 0) / n)
    const std = Math.sqrt(vals.reduce((a, b) => a + (b - mean) ** 2, 0) / n)
    return {
      label: key.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase()),
      mean: mean.toFixed(4),
      std: std.toFixed(4),
      min: (vals[0] || 0).toFixed(4),
      q25: percentile(vals, 0.25).toFixed(4),
      q50: percentile(vals, 0.5).toFixed(4),
      q75: percentile(vals, 0.75).toFixed(4),
      max: (vals[vals.length - 1] || 0).toFixed(4),
    }
  })
})
</script>

<style scoped>
.stats-view {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.stats-charts-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.25rem;
}

@media (max-width: 900px) {
  .stats-charts-grid {
    grid-template-columns: 1fr;
  }
}

.dim-stats-table {
  font-size: 0.85rem;
  border: 1px solid var(--p-surface-100);
  border-radius: 12px;
  overflow: hidden;
}

.dim-stats-table :deep(.p-datatable-thead > tr > th) {
  background: var(--p-surface-50);
  color: var(--p-surface-700);
  font-weight: 600;
  text-transform: uppercase;
  font-size: 0.75rem;
  letter-spacing: 0.5px;
  padding: 1rem 0.75rem;
}

.dim-stats-table :deep(.p-datatable-tbody > tr > td) {
  padding: 0.875rem 0.75rem;
  font-family: 'Roboto Mono', monospace;
  font-size: 0.8rem;
}

.dim-stats-table :deep(.p-datatable-tbody > tr:hover) {
  background: var(--p-surface-25);
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

.empty-chart i {
  margin-bottom: 0.75rem;
  opacity: 0.6;
}

.stats-view :deep(.p-card) {
  border: 1px solid var(--p-surface-100);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  transition: all 0.3s ease;
}

.stats-view :deep(.p-card):hover {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
}

.stats-view :deep(.p-card-title) {
  font-size: 0.9rem;
  color: var(--p-surface-700);
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.stats-view :deep(.p-card-title i) {
  color: var(--p-primary-500);
}
</style>
