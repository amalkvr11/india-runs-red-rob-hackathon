<template>
  <div class="detail-view" v-if="candidate">
    <Button icon="pi pi-arrow-left" text @click="router.push('/results')" label="Back to Results" class="back-btn" />

    <!-- Header -->
    <Card class="detail-header-card">
      <template #content>
        <div class="detail-header">
          <div class="header-left">
            <Avatar :label="candidate.name?.[0] || '?'" shape="circle" size="xlarge" style="background: var(--p-primary-500); color: #fff" />
            <div>
              <h2>{{ candidate.candidate_id }}</h2>
              <p class="detail-title">{{ candidate.current_title }} <span class="at-text">at</span> {{ candidate.current_company }}</p>
              <p class="detail-loc"><i class="pi pi-map-marker"></i> {{ candidate.location }}</p>
            </div>
          </div>
          <div class="header-right">
            <Tag :value="`Rank #${candidate.rank}`" :severity="rankSev" size="large" />
            <div class="big-score">{{ candidate.score.toFixed(4) }}</div>
            <span class="score-label">Overall Score</span>
          </div>
        </div>
        <Message v-if="candidate.honeypot?.is_honeypot" severity="warn" :closable="false" class="honey-msg">
          <i class="pi pi-exclamation-triangle"></i> Honeypot detected: {{ candidate.honeypot.flags.join(', ') }} &mdash; Penalty: {{ (candidate.honeypot.penalty * 100).toFixed(0) }}%
        </Message>
      </template>
    </Card>

    <!-- Radar + Profile -->
    <div class="detail-grid">
      <Card>
        <template #title><i class="pi pi-user"></i> Profile Summary</template>
        <template #content>
          <div class="profile-field" v-for="f in profileFields" :key="f.label">
            <span class="field-label">{{ f.label }}</span>
            <span class="field-value">{{ f.value }}</span>
          </div>
        </template>
      </Card>
      <Card>
        <template #title><i class="pi pi-chart-pie"></i> Scores vs Weights</template>
        <template #content>
          <apexchart type="radar" height="340" :options="detailRadarOptions" :series="detailRadarSeries" />
        </template>
      </Card>
    </div>

    <!-- Dimension Breakdown -->
    <Card>
      <template #title><i class="pi pi-table"></i> Dimension Breakdown</template>
      <template #content>
        <DataTable :value="dims" stripedRows showGridlines class="dims-table">
          <Column field="label" header="Dimension">
            <template #body="{ data }">
              <div class="dim-name-cell">
                <i :class="data.icon"></i> {{ data.label }}
              </div>
            </template>
          </Column>
          <Column field="score" header="Score" :style="{ width: '160px' }">
            <template #body="{ data }">
              <div class="dim-score-bar">
                <ProgressBar :value="data.score * 100" :showValue="false" />
                <span class="dim-score-val">{{ data.score.toFixed(3) }}</span>
              </div>
            </template>
          </Column>
          <Column field="weight" header="Weight" :style="{ width: '70px' }">
            <template #body="{ data }">
              {{ data.weight.toFixed(2) }}
            </template>
          </Column>
          <Column field="weighted" header="Weighted" :style="{ width: '90px' }">
            <template #body="{ data }">
              <strong>{{ (data.score * data.weight).toFixed(4) }}</strong>
            </template>
          </Column>
          <Column field="reasoning" header="Reasoning">
            <template #body="{ data }">
              <span class="reasoning-text">{{ data.reasoning }}</span>
            </template>
          </Column>
        </DataTable>
      </template>
    </Card>
  </div>
  <div v-else class="empty-detail">
    <template v-if="store.loading">
      <i class="pi pi-spin pi-spinner" style="font-size: 2rem"></i>
      <p>Loading candidates...</p>
    </template>
    <template v-else-if="!store.results">
      <i class="pi pi-database" style="font-size: 2rem"></i>
      <p>No candidate data loaded</p>
      <Button label="Load Results" icon="pi pi-refresh" @click="store.ensureLoaded()" severity="info" />
    </template>
    <template v-else>
      <i class="pi pi-exclamation-circle" style="font-size: 2rem"></i>
      <p>Candidate not found in results</p>
      <Button label="Go to Results" icon="pi pi-arrow-left" @click="router.push('/results')" severity="info" />
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useRankerStore } from '../stores/ranker'
import Card from 'primevue/card'
import Avatar from 'primevue/avatar'
import Tag from 'primevue/tag'
import Button from 'primevue/button'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import ProgressBar from 'primevue/progressbar'
import Message from 'primevue/message'

const route = useRoute()
const router = useRouter()
const store = useRankerStore()

// Ensure results are loaded before rendering
onMounted(() => {
  store.ensureLoaded()
})

const candidate = computed(() => store.getCandidate(route.params.id))

const rankSev = computed(() => {
  const r = candidate.value?.rank || 0
  if (r <= 10) return 'danger'
  if (r <= 30) return 'warn'
  if (r <= 60) return 'info'
  return 'contrast'
})

const profileFields = computed(() => {
  const c = candidate.value
  if (!c) return []
  const p = c.profile || {}
  return [
    { label: 'Name', value: p.anonymized_name || '-' },
    { label: 'Current Title', value: c.current_title || '-' },
    { label: 'Company', value: c.current_company || '-' },
    { label: 'Location', value: [p.location, p.country].filter(Boolean).join(', ') || '-' },
    { label: 'Years of Exp', value: p.years_of_experience ?? '-' },
    { label: 'Industry', value: p.current_industry || '-' },
    { label: 'Company Size', value: p.current_company_size || '-' },
    { label: 'Headline', value: (p.headline || '').slice(0, 80) || '-' },
  ]
})

const dimIcons = {
  title_role: 'pi pi-id-card',
  skills: 'pi pi-cog',
  career_quality: 'pi pi-building',
  experience: 'pi pi-clock',
  statement: 'pi pi-pen',
  behavioral: 'pi pi-heart',
  location: 'pi pi-map-marker',
  education: 'pi pi-book',
}

const dims = computed(() => {
  const c = candidate.value
  if (!c || !store.weights) return []
  return Object.entries(store.weights).map(([key, weight]) => ({
    key,
    label: key.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase()),
    icon: dimIcons[key] || 'pi pi-circle',
    score: c.sub_scores[key] || 0,
    weight,
    reasoning: c.reasonings?.[key] || '',
  }))
})

const dimLabels = computed(() => dims.value.map(d => d.label))
const dimScores = computed(() => dims.value.map(d => d.score))
const dimWeights = computed(() => dims.value.map(d => d.weight))

const detailRadarSeries = computed(() => [
  { name: 'Score', data: dimScores.value },
  { name: 'Weight', data: dimWeights.value },
])

const detailRadarOptions = {
  chart: { type: 'radar', toolbar: { show: false }, fontFamily: 'Inter' },
  colors: ['#00bcd4', '#ff9800'],
  xaxis: { categories: dimLabels.value, labels: { style: { colors: '#e4e6f0' } } },
  yaxis: { show: false, min: 0, max: 1 },
  markers: { size: 5 },
  stroke: { width: 2 },
  fill: { opacity: 0.1 },
  tooltip: { theme: 'dark' },
  legend: { labels: { colors: '#e4e6f0' } },
}
</script>

<style scoped>
.detail-view {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.back-btn {
  align-self: flex-start;
  font-weight: 500;
}

.back-btn:hover {
  color: var(--p-primary-600);
}

.detail-header-card {
  border: 1px solid var(--p-surface-100);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04);
}

.detail-header-card :deep(.p-card-content) {
  padding: 0;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 2rem;
  flex-wrap: wrap;
  padding: 0.5rem 0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1.25rem;
}

.header-left h2 {
  font-family: 'Roboto Mono', monospace;
  font-size: 1.2rem;
  font-weight: 700;
  color: var(--p-surface-800);
  letter-spacing: -0.02em;
}

.detail-title {
  font-size: 1rem;
  color: var(--p-primary-600);
  font-weight: 600;
  margin-top: 4px;
}

.at-text {
  color: var(--p-surface-500);
  font-size: 0.85rem;
  font-weight: 400;
}

.detail-loc {
  font-size: 0.85rem;
  color: var(--p-surface-600);
  margin-top: 6px;
  display: flex;
  align-items: center;
  gap: 0.35rem;
}

.detail-loc i {
  font-size: 0.85rem;
  color: var(--p-green-500);
}

.header-right {
  text-align: right;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.5rem;
}

.big-score {
  font-size: 2.5rem;
  font-weight: 800;
  font-family: 'Roboto Mono', monospace;
  color: var(--p-primary-500);
  letter-spacing: -0.03em;
  line-height: 1;
}

.score-label {
  font-size: 0.75rem;
  color: var(--p-surface-600);
  text-transform: uppercase;
  letter-spacing: 1px;
  font-weight: 500;
}

.honey-msg {
  margin-top: 1rem;
  border-radius: 10px;
}

.detail-grid {
  display: grid;
  grid-template-columns: 1fr 1.2fr;
  gap: 1.25rem;
}

@media (max-width: 900px) {
  .detail-grid {
    grid-template-columns: 1fr;
  }
}

.profile-field {
  display: flex;
  padding: 0.65rem 0;
  border-bottom: 1px solid var(--p-surface-100);
  font-size: 0.85rem;
  transition: background 0.2s ease;
}

.profile-field:hover {
  background: var(--p-surface-25);
  margin: 0 -1rem;
  padding-left: 1rem;
  padding-right: 1rem;
  border-radius: 4px;
}

.profile-field:last-child {
  border-bottom: none;
}

.field-label {
  width: 130px;
  color: var(--p-surface-600);
  flex-shrink: 0;
  font-weight: 500;
}

.field-value {
  color: var(--p-surface-800);
  font-weight: 600;
  flex: 1;
}

.dims-table {
  font-size: 0.85rem;
  border: 1px solid var(--p-surface-100);
  border-radius: 12px;
  overflow: hidden;
}

.dims-table :deep(.p-datatable-thead > tr > th) {
  background: var(--p-surface-50);
  color: var(--p-surface-700);
  font-weight: 600;
  text-transform: uppercase;
  font-size: 0.7rem;
  letter-spacing: 0.5px;
  padding: 1rem;
  border-bottom: 2px solid var(--p-surface-100);
}

.dims-table :deep(.p-datatable-tbody > tr > td) {
  padding: 1rem;
  border-bottom: 1px solid var(--p-surface-100);
}

.dims-table :deep(.p-datatable-tbody > tr:hover) {
  background: var(--p-surface-25);
}

.dim-name-cell {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
  color: var(--p-surface-800);
}

.dim-name-cell i {
  color: var(--p-primary-500);
  font-size: 0.95rem;
}

.dim-score-bar {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.dim-score-bar :deep(.p-progressbar) {
  height: 10px;
  border-radius: 5px;
  flex: 1;
}

.dim-score-bar :deep(.p-progressbar-value) {
  border-radius: 5px;
}

.dim-score-val {
  font-family: 'Roboto Mono', monospace;
  font-size: 0.85rem;
  font-weight: 700;
  min-width: 55px;
  text-align: right;
  color: var(--p-surface-700);
}

.reasoning-text {
  font-size: 0.8rem;
  color: var(--p-surface-600);
  line-height: 1.5;
}

.empty-detail {
  text-align: center;
  padding: 6rem 2rem;
  color: var(--p-surface-600);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  background: var(--p-surface-25);
  border-radius: 16px;
  border: 2px dashed var(--p-surface-200);
}

.empty-detail p {
  font-size: 1rem;
  font-weight: 500;
  color: var(--p-surface-700);
}

.empty-detail i {
  color: var(--p-surface-400);
}

.detail-view > :deep(.p-card) {
  border-radius: 14px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
  transition: all 0.3s ease;
}

.detail-view > :deep(.p-card):hover {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
}

.detail-view :deep(.p-card-title) {
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--p-surface-800);
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.detail-view :deep(.p-card-title i) {
  color: var(--p-primary-500);
}
</style>
