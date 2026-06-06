<template>
  <div class="results-view">
    <div class="toolbar-row">
      <IconField>
        <InputIcon><i class="pi pi-search" /></InputIcon>
        <InputText v-model="filters.global.value" placeholder="Search by name, title, company..." style="width: 320px" />
      </IconField>
      <Select v-model="filters.honeypot.value" :options="honeyOptions" optionLabel="label" optionValue="value" placeholder="All" style="width: 160px" />
    </div>

    <div v-if="!store.results" class="empty-state">
      <i class="pi pi-spin pi-spinner" v-if="store.loading" style="font-size: 2rem"></i>
      <i class="pi pi-database" v-else style="font-size: 2rem"></i>
      <p>{{ store.loading ? 'Loading results...' : 'No results available' }}</p>
      <Button v-if="!store.loading" label="Load Results" icon="pi pi-refresh" @click="store.ensureLoaded()" severity="info" size="small" />
    </div>
    <DataTable v-else
      :value="store.results"
      :filters="filters"
      paginator
      :rows="15"
      :rowsPerPageOptions="[10, 15, 25, 50]"
      sortField="rank"
      :sortOrder="1"
      stripedRows
      showGridlines
      class="results-table"
      @row-click="goToDetail"
    >
      <Column field="rank" header="#" :style="{ width: '60px' }" :sortable="true">
        <template #body="{ data }">
          <Tag :value="data.rank" :severity="rankSeverity(data.rank)" />
        </template>
      </Column>
      <Column field="candidate_id" header="ID" :style="{ width: '120px' }" :sortable="true">
        <template #body="{ data }">
          <span class="id-cell">{{ data.candidate_id }}</span>
        </template>
      </Column>
      <Column field="current_title" header="Title" :sortable="true">
        <template #body="{ data }">
          <div class="title-cell">
            <i class="pi pi-briefcase"></i>
            <span>{{ data.current_title || 'Unknown' }}</span>
          </div>
        </template>
      </Column>
      <Column field="current_company" header="Company" :sortable="true">
        <template #body="{ data }">
          <span style="color: var(--p-surface-600)">{{ data.current_company || '-' }}</span>
        </template>
      </Column>
      <Column field="location" header="Location" :sortable="true">
        <template #body="{ data }">
          <span style="font-size: 0.85rem; color: var(--p-surface-600)">{{ data.location }}</span>
        </template>
      </Column>
      <Column field="yoe" header="YoE" :style="{ width: '70px' }" :sortable="true">
        <template #body="{ data }">
          <span class="yoe-cell">{{ data.yoe }}</span>
        </template>
      </Column>
      <Column field="score" header="Score" :style="{ width: '160px' }" :sortable="true">
        <template #body="{ data }">
          <div class="score-cell">
            <ProgressBar :value="data.score * 100" :showValue="false" class="score-bar" />
            <span class="score-val">{{ data.score.toFixed(4) }}</span>
          </div>
        </template>
      </Column>
      <Column header="" :style="{ width: '50px' }">
        <template #body="{ data }">
          <i v-if="data.honeypot?.is_honeypot" class="pi pi-exclamation-triangle honey-flag" title="Honeypot"></i>
        </template>
      </Column>
      <Column :style="{ width: '50px' }">
        <template #body>
          <Button icon="pi pi-chevron-right" text severity="secondary" size="small" />
        </template>
      </Column>
    </DataTable>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
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
})

const honeyOptions = [
  { label: 'All Candidates', value: null },
  { label: 'Clean Only', value: false },
  { label: 'Honeypot Only', value: true },
]

function rankSeverity(rank) {
  if (rank <= 10) return 'danger'
  if (rank <= 30) return 'warn'
  if (rank <= 60) return 'info'
  return 'contrast'
}

function goToDetail(e) {
  router.push(`/candidate/${e.data.candidate_id}`)
}
</script>

<style scoped>
.results-view { display: flex; flex-direction: column; gap: 1rem; }
.toolbar-row { display: flex; align-items: center; gap: 1rem; flex-wrap: wrap; }
.results-table { font-size: 0.85rem; }
.id-cell { font-family: monospace; font-size: 0.8rem; color: var(--p-surface-500); }
.title-cell { display: flex; align-items: center; gap: 0.4rem; }
.title-cell i { font-size: 0.85rem; color: var(--p-primary-500); }
.yoe-cell { font-weight: 600; }
.score-cell { display: flex; align-items: center; gap: 0.5rem; }
.score-bar { flex: 1; height: 6px; }
.score-val { font-family: monospace; font-size: 0.8rem; font-weight: 600; min-width: 60px; text-align: right; }
.honey-flag { color: var(--p-yellow-500); cursor: help; }
.empty-state { display: flex; flex-direction: column; align-items: center; gap: 0.75rem; padding: 4rem; color: var(--p-surface-600); }
.empty-state i { opacity: 0.5; }
.empty-state p { font-size: 0.95rem; }
</style>
