<template>
  <div class="results-view">
    <div class="toolbar-row">
      <div class="search-section">
        <IconField>
          <InputIcon><i class="pi pi-search" /></InputIcon>
          <InputText v-model="filters.global.value" placeholder="Search by name, title, company, location..." style="width: 380px" />
        </IconField>
      </div>
      <div class="filter-section">
        <Select v-model="filters.honeypot.value" :options="honeyOptions" optionLabel="label" optionValue="value" placeholder="Filter Honeypot" style="width: 160px" />
        <Select v-model="filters.location.value" :options="locationOptions" placeholder="Location" style="width: 140px" />
        <Button icon="pi pi-refresh" text severity="secondary" @click="resetFilters" v-tooltip="'Reset filters'" />
      </div>
    </div>

    <div v-if="!store.results" class="empty-state">
      <div class="empty-icon">
        <i class="pi pi-spin pi-spinner" v-if="store.loading"></i>
        <i class="pi pi-database" v-else></i>
      </div>
      <p class="empty-title">{{ store.loading ? 'Loading results...' : 'No results available' }}</p>
      <p class="empty-desc">Run ranking to generate candidate results</p>
      <Button v-if="!store.loading" label="Run Ranking" icon="pi pi-play" @click="triggerRanking" severity="info" />
    </div>

    <div v-else class="results-container">
      <div class="results-info">
        <span class="results-count"><i class="pi pi-users"></i> {{ filteredCount }} candidates</span>
        <div class="score-summary">
          <Tag v-if="avgScoreRange" :value="`Avg: ${avgScore.toFixed(3)}`" severity="info" />
          <Tag v-if="topScore" :value="`Max: ${topScore.toFixed(3)}`" severity="success" />
        </div>
      </div>

      <DataTable
        :value="store.results"
        :filters="filters"
        paginator
        :rows="15"
        :rowsPerPageOptions="[10, 15, 25, 50, 100]"
        sortField="rank"
        :sortOrder="1"
        stripedRows
        showGridlines
        class="results-table"
        @row-click="goToDetail"
        filterDisplay="menu"
      >
        <Column field="rank" header="#" :style="{ width: '70px' }" :sortable="true">
          <template #body="{ data }">
            <div class="rank-cell">
              <Tag :value="data.rank" :severity="rankSeverity(data.rank)" size="small" />
            </div>
          </template>
        </Column>

        <Column field="candidate_id" header="ID" :style="{ width: '130px' }" :sortable="true">
          <template #body="{ data }">
            <span class="id-cell">{{ data.candidate_id }}</span>
          </template>
        </Column>

        <Column field="current_title" header="Title" :sortable="true" :style="{ minWidth: '200px' }">
          <template #body="{ data }">
            <div class="title-cell">
              <i class="pi pi-briefcase"></i>
              <span class="title-text">{{ data.current_title || 'Unknown' }}</span>
            </div>
          </template>
        </Column>

        <Column field="current_company" header="Company" :sortable="true">
          <template #body="{ data }">
            <div class="company-cell">
              <i class="pi pi-building"></i>
              <span>{{ data.current_company || '-' }}</span>
            </div>
          </template>
        </Column>

        <Column field="location" header="Location" :sortable="true" :style="{ minWidth: '140px' }">
          <template #body="{ data }">
            <div class="location-cell">
              <i class="pi pi-map-marker"></i>
              <span>{{ data.location || 'Unknown' }}</span>
            </div>
          </template>
        </Column>

        <Column field="yoe" header="YoE" :style="{ width: '80px' }" :sortable="true">
          <template #body="{ data }">
            <div class="yoe-cell" :class="yoeClass(data.yoe)">
              <span>{{ data.yoe || 0 }}</span>
              <small>yr</small>
            </div>
          </template>
        </Column>

        <Column field="score" header="Score" :style="{ width: '180px' }" :sortable="true">
          <template #body="{ data }">
            <div class="score-cell">
              <div class="score-bar-container">
                <ProgressBar :value="data.score * 100" :showValue="false" class="score-bar" :class="scoreBarClass(data.score)" />
                <div class="score-overlay" :style="{ width: `${data.score * 100}%` }"></div>
              </div>
              <span class="score-val">{{ data.score.toFixed(4) }}</span>
              <Tag v-if="data.score > 0.75" value="Top" severity="success" size="small" />
            </div>
          </template>
        </Column>

        <Column header="Flags" :style="{ width: '60px' }">
          <template #body="{ data }">
            <div class="flags-cell">
              <i v-if="data.honeypot?.is_honeypot" class="pi pi-exclamation-triangle honey-flag" v-tooltip="'Honeypot detected'"></i>
            </div>
          </template>
        </Column>

        <Column :style="{ width: '60px' }">
          <template #body>
            <Button icon="pi pi-chevron-right" text severity="secondary" size="small" />
          </template>
        </Column>
      </DataTable>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useRankerStore } from '../stores/ranker'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Tag from 'primevue/tag'
import ProgressBar from 'primevue/progressbar'
import Button from 'primevue/button'
import IconField from 'primevue/iconfield'
import InputIcon from 'primevue/inputicon'
import InputText from 'primevue/inputtext'
import Select from 'primevue/select'

const store = useRankerStore()
const router = useRouter()

onMounted(() => {
  store.ensureLoaded()
})

const filters = ref({
  global: { value: null, matchMode: 'contains' },
  honeypot: { value: null, matchMode: 'equals' },
  location: { value: null, matchMode: 'contains' },
})

const honeyOptions = [
  { label: 'All Candidates', value: null },
  { label: 'Clean Only', value: false },
  { label: 'Honeypot Only', value: true },
]

const locationOptions = computed(() => {
  if (!store.results?.length) return []
  const locations = new Set()
  store.results.forEach(r => {
    const loc = r.location?.split(',')[0]?.trim()
    if (loc) locations.add(loc)
  })
  return Array.from(locations).slice(0, 15)
})

const filteredCount = computed(() => {
  return store.results?.length || 0
})

const avgScore = computed(() => {
  if (!store.results?.length) return 0
  return store.results.reduce((a, r) => a + r.score, 0) / store.results.length
})

const topScore = computed(() => store.results?.[0]?.score || 0)

const avgScoreRange = computed(() => {
  if (!store.results?.length) return false
  const scores = store.results.map(r => r.score)
  const max = Math.max(...scores)
  const min = Math.min(...scores)
  return (max - min) > 0.1
})

function rankSeverity(rank) {
  if (rank <= 10) return 'danger'
  if (rank <= 30) return 'warn'
  if (rank <= 60) return 'info'
  return 'contrast'
}

function yoeClass(yoe) {
  if (!yoe) return ''
  if (yoe >= 4 && yoe <= 8) return 'ideal-yoe'
  if (yoe < 2) return 'low-yoe'
  if (yoe > 15) return 'high-yoe'
  return ''
}

function scoreBarClass(score) {
  if (score >= 0.7) return 'high-score'
  if (score >= 0.5) return 'mid-score'
  return 'low-score'
}

function resetFilters() {
  filters.value = {
    global: { value: null, matchMode: 'contains' },
    honeypot: { value: null, matchMode: 'equals' },
    location: { value: null, matchMode: 'contains' },
  }
}

function goToDetail(e) {
  router.push(`/candidate/${e.data.candidate_id}`)
}

async function triggerRanking() {
  await store.runRanking(true, 100, null)
}
</script>

<style scoped>
.results-view {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.toolbar-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
  padding: 1rem 1.25rem;
  background: var(--p-surface-25);
  border-radius: 12px;
  border: 1px solid var(--p-surface-100);
}

.search-section {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.filter-section {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.results-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.results-info {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.5rem 0;
}

.results-count {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
  color: var(--p-surface-700);
}

.results-count i {
  color: var(--p-primary-500);
}

.score-summary {
  display: flex;
  gap: 0.5rem;
}

.results-table {
  font-size: 0.85rem;
  border: 1px solid var(--p-surface-100);
  border-radius: 12px;
  overflow: hidden;
}

.results-table :deep(.p-datatable-thead > tr > th) {
  background: var(--p-surface-50);
  color: var(--p-surface-700);
  font-weight: 600;
  text-transform: uppercase;
  font-size: 0.7rem;
  letter-spacing: 0.5px;
  padding: 1rem 0.875rem;
  border-bottom: 2px solid var(--p-surface-100);
}

.results-table :deep(.p-datatable-tbody > tr) {
  cursor: pointer;
  transition: all 0.2s ease;
}

.results-table :deep(.p-datatable-tbody > tr:hover) {
  background: var(--p-surface-25) !important;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.results-table :deep(.p-datatable-tbody > tr > td) {
  padding: 0.875rem;
  border-bottom: 1px solid var(--p-surface-100);
}

.rank-cell {
  display: flex;
  align-items: center;
}

.id-cell {
  font-family: 'Roboto Mono', monospace;
  font-size: 0.8rem;
  color: var(--p-surface-600);
  background: var(--p-surface-25);
  padding: 4px 8px;
  border-radius: 4px;
}

.title-cell {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.title-cell i {
  font-size: 0.9rem;
  color: var(--p-primary-500);
}

.title-text {
  font-weight: 500;
  color: var(--p-surface-800);
}

.company-cell {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  color: var(--p-surface-600);
}

.company-cell i {
  font-size: 0.8rem;
  color: var(--p-surface-500);
}

.location-cell {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  color: var(--p-surface-600);
  font-size: 0.85rem;
}

.location-cell i {
  font-size: 0.8rem;
  color: var(--p-green-500);
}

.yoe-cell {
  display: flex;
  flex-direction: column;
  align-items: center;
  font-weight: 700;
  color: var(--p-surface-700);
  padding: 6px 10px;
  border-radius: 8px;
  background: var(--p-surface-50);
  min-width: 50px;
}

.yoe-cell small {
  font-size: 0.65rem;
  color: var(--p-surface-500);
  font-weight: 500;
}

.yoe-cell.ideal-yoe {
  background: rgba(76, 175, 80, 0.1);
  color: var(--p-green-600);
}

.yoe-cell.low-yoe {
  background: rgba(255, 152, 0, 0.1);
  color: var(--p-orange-600);
}

.yoe-cell.high-yoe {
  background: rgba(171, 71, 188, 0.1);
  color: var(--p-purple-600);
}

.score-cell {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  min-width: 160px;
}

.score-bar-container {
  position: relative;
  width: 100%;
  height: 8px;
  background: var(--p-surface-100);
  border-radius: 6px;
  overflow: hidden;
}

.score-bar {
  height: 8px;
  border-radius: 6px;
  transition: all 0.3s ease;
}

.score-bar.high-score :deep(.p-progressbar-value) {
  background: linear-gradient(90deg, var(--p-green-500), var(--p-green-400)) !important;
}

.score-bar.mid-score :deep(.p-progressbar-value) {
  background: linear-gradient(90deg, var(--p-blue-500), var(--p-blue-400)) !important;
}

.score-bar.low-score :deep(.p-progressbar-value) {
  background: linear-gradient(90deg, var(--p-surface-500), var(--p-surface-400)) !important;
}

.score-val {
  font-family: 'Roboto Mono', monospace;
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--p-surface-800);
  letter-spacing: -0.02em;
}

.flags-cell {
  display: flex;
  align-items: center;
  justify-content: center;
}

.honey-flag {
  color: var(--p-yellow-500);
  cursor: help;
  font-size: 1.1rem;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  padding: 5rem 2rem;
  background: var(--p-surface-25);
  border-radius: 16px;
  border: 2px dashed var(--p-surface-200);
}

.empty-icon {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: var(--p-surface-50);
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-icon i {
  font-size: 2.5rem;
  color: var(--p-surface-400);
}

.empty-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--p-surface-700);
  margin: 0;
}

.empty-desc {
  font-size: 0.9rem;
  color: var(--p-surface-500);
  margin: 0;
}

@media (max-width: 768px) {
  .toolbar-row {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-section, .filter-section {
    width: 100%;
    justify-content: space-between;
  }
}
</style>
