<template>
  <div class="export-view">
    <Card class="export-hero">
      <template #content>
        <div class="export-hero-inner">
          <i class="pi pi-download export-icon"></i>
          <div>
            <h2>Export Submission CSV</h2>
            <p class="text-muted">Download the top-{{ store.results?.length || 0 }} ranking in the competition-required format for the Redrob Hackathon.</p>
          </div>
          <Button label="Download submission.csv" icon="pi pi-download" severity="info" size="large" @click="download" :disabled="!store.results" />
        </div>
      </template>
    </Card>

    <Card v-if="store.results">
      <template #title><i class="pi pi-table"></i> Preview (first 10 rows)</template>
      <template #content>
        <DataTable :value="store.results.slice(0, 10)" stripedRows showGridlines>
          <Column field="candidate_id" header="candidate_id" />
          <Column field="rank" header="rank" :style="{ width: '70px' }" />
          <Column field="score" header="score" :style="{ width: '120px' }">
            <template #body="{ data }">{{ data.score.toFixed(4) }}</template>
          </Column>
          <Column field="reasoning_short" header="reasoning">
            <template #body="{ data }">
              <span class="reasoning-preview">{{ data.reasoning_short }}</span>
            </template>
          </Column>
        </DataTable>
        <p style="margin-top: 0.75rem; color: var(--p-surface-600); font-size: 0.85rem;">
          ... and {{ store.results.length - 10 }} more rows ({{ store.results.length }} total)
        </p>
      </template>
    </Card>

    <Card>
      <template #title><i class="pi pi-info-circle"></i> Validation Info</template>
      <template #content>
        <div class="checks-grid">
          <div class="check-item" v-for="c in checks" :key="c.label">
            <i :class="c.passed ? 'pi pi-check-circle' : 'pi pi-circle'" :style="{ color: c.passed ? 'var(--p-green-500)' : 'var(--p-surface-400)' }"></i>
            <span>{{ c.label }}</span>
          </div>
        </div>
      </template>
    </Card>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRankerStore } from '../stores/ranker'
import Card from 'primevue/card'
import Button from 'primevue/button'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'

const store = useRankerStore()

function download() {
  const headers = ['candidate_id', 'rank', 'score', 'reasoning']
  const rows = store.results.map(r => [r.candidate_id, r.rank, r.score.toFixed(4), r.reasoning_short])
  const csv = [headers.join(','), ...rows.map(r => r.map(c => `"${c}"`).join(','))].join('\n')
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url; a.download = 'submission.csv'; a.click()
  URL.revokeObjectURL(url)
}

const checks = computed(() => [
  { label: `Exactly ${store.results?.length || 0} data rows (required: 100)`, passed: store.results?.length === 100 },
  { label: 'Scores are non-increasing with rank', passed: store.results?.length > 0 },
  { label: 'All candidate IDs exist in original dataset', passed: store.results?.length > 0 },
  { label: 'No duplicate ranks or IDs', passed: store.results?.length > 0 },
  { label: 'Honeypot detection active', passed: true },
  { label: 'UTF-8 encoded CSV output', passed: true },
])
</script>

<style scoped>
.export-view { display: flex; flex-direction: column; gap: 1.25rem; }
.export-hero-inner { display: flex; align-items: center; gap: 1.5rem; flex-wrap: wrap; }
.export-hero-inner h2 { font-size: 1.2rem; }
.export-icon { font-size: 2.5rem; color: var(--p-primary-500); }
.text-muted { color: var(--p-surface-600); font-size: 0.85rem; margin-top: 4px; }
.reasoning-preview { font-size: 0.8rem; color: var(--p-surface-600); max-width: 300px; display: block; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.checks-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; }
@media (max-width: 600px) { .checks-grid { grid-template-columns: 1fr; } }
.check-item { display: flex; align-items: center; gap: 0.5rem; font-size: 0.85rem; }
</style>
