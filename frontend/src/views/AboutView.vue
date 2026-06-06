<template>
  <div class="about-view">
    <Card>
      <template #title><i class="pi pi-search"></i> Redrob Candidate Ranker</template>
      <template #content>
        <p class="about-summary">
          A production-grade candidate ranking system built for the <strong>India Runs Data &amp; AI Challenge</strong> by Redrob.
          Scores and ranks 100,000+ candidates for a <strong>Senior AI Engineer</strong> role at a Series A startup.
        </p>
      </template>
    </Card>

    <div class="about-grid">
      <Card v-for="item in cards" :key="item.title">
        <template #title><i :class="item.icon"></i> {{ item.title }}</template>
        <template #content>
          <p style="color: var(--p-surface-600); font-size: 0.9rem; line-height: 1.7;">{{ item.desc }}</p>
        </template>
      </Card>
    </div>

    <Card>
      <template #title><i class="pi pi-cog"></i> Scoring Methodology</template>
      <template #content>
        <DataTable :value="methodology" stripedRows showGridlines>
          <Column field="dimension" header="Dimension">
            <template #body="{ data }"><strong>{{ data.dimension }}</strong></template>
          </Column>
          <Column field="weight" header="Weight" :style="{ width: '80px' }">
            <template #body="{ data }"><Tag :value="data.weight" severity="info" /></template>
          </Column>
          <Column field="description" header="What it measures" />
        </DataTable>
      </template>
    </Card>

    <Card>
      <template #title><i class="pi pi-shield"></i> Honeypot Detection</template>
      <template #content>
        <p style="color: var(--p-surface-600); font-size: 0.9rem; line-height: 1.7;">
          The dataset contains ~80 honeypot candidates with impossible profiles (e.g. expert in 10 skills with 0 endorsements,
          YOE gaps exceeding 4 years). Our system automatically flags these and applies a score penalty of up to 50%.
          Submissions with >10% honeypot rate in the top 100 are disqualified per competition rules.
        </p>
      </template>
    </Card>

    <Card>
      <template #title><i class="pi pi-code"></i> Tech Stack</template>
      <template #content>
        <div class="tech-list">
          <div v-for="t in tech" :key="t.name" class="tech-item">
            <Tag :value="t.name" :severity="t.severity" />
            <span style="color: var(--p-surface-600); font-size: 0.85rem;">{{ t.role }}</span>
          </div>
        </div>
      </template>
    </Card>
  </div>
</template>

<script setup>
import Card from 'primevue/card'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Tag from 'primevue/tag'

const cards = [
  { icon: 'pi pi-users', title: '100K Candidates', desc: 'Each candidate includes profile, career history, education, skills, certifications, languages, and platform engagement signals from the Redrob ecosystem.' },
  { icon: 'pi pi-star', title: '8 Scoring Dimensions', desc: 'Title/Role (22%), Skills (18%), Career Quality (18%), Experience (13%), Statement (10%), Behavioral (9%), Location (5%), Education (5%). Weights tuneable in config.py.' },
  { icon: 'pi pi-clock', title: 'Under 5 Minutes', desc: 'Pure CPU Python — no GPU, no network calls. Ranks the full 100K pool in ~64s on a standard laptop. Meets all competition compute constraints.' },
  { icon: 'pi pi-shield', title: 'Honeypot Resistant', desc: 'Multi-factor anomaly detection catches inflated profiles: expert skill count vs endorsements, YOE vs career history total, assessment score contradictions.' },
]

const methodology = [
  { dimension: 'Title / Role', weight: '0.22', description: 'Matches current title against AI/ML role tiers. Boosts candidates whose descriptions contain ML keywords even if titles are generic. Penalizes consulting firm affiliations.' },
  { dimension: 'Skills', weight: '0.18', description: 'Scores skill relevance across 6 groups (embeddings/retrieval, vector DB, NLP/LLM, ML eval, ML frameworks, data infra) weighted by proficiency, endorsements, and duration.' },
  { dimension: 'Career Quality', weight: '0.18', description: 'Measures tenure stability, career progression (seniority growth), production deployment experience, and company diversity.' },
  { dimension: 'Experience', weight: '0.13', description: 'Ideal range 3-10 years. Beyond 10 years, score gradually decays. Blended with ML keyword density in career descriptions.' },
  { dimension: 'Statement', weight: '0.10', description: 'Analyzes profile summary/statement for ML intent keywords, startup affinity, and impact/leadership language.' },
  { dimension: 'Behavioral', weight: '0.09', description: '10-factor model: recency, open-to-work flag, response rate/time, notice period, interview completion, verification status, GitHub activity, platform engagement, salary alignment.' },
  { dimension: 'Location', weight: '0.05', description: 'Preference for India tech hubs (Bangalore, Hyderabad, Pune, Gurgaon, Noida, Mumbai, Chennai, Delhi). Willingness to relocate adds bonus.' },
  { dimension: 'Education', weight: '0.05', description: 'Combines degree level (PhD > MTech > BTech), institution tier, and CS-related field of study.' },
]

const tech = [
  { name: 'Python 3', severity: 'info', role: 'Scoring engine & API backend' },
  { name: 'FastAPI', severity: 'success', role: 'REST API server' },
  { name: 'Vue 3', severity: 'success', role: 'Progressive frontend framework' },
  { name: 'PrimeVue', severity: 'warn', role: 'UI component library' },
  { name: 'ApexCharts', severity: 'danger', role: 'Interactive data visualizations' },
  { name: 'Pinia', severity: 'info', role: 'State management' },
  { name: 'Vue Router', severity: 'info', role: 'SPA routing' },
]
</script>

<style scoped>
.about-view { display: flex; flex-direction: column; gap: 1.25rem; }
.about-summary { font-size: 0.95rem; line-height: 1.7; color: var(--p-surface-700); }
.about-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
@media (max-width: 800px) { .about-grid { grid-template-columns: 1fr; } }
.tech-list { display: flex; flex-wrap: wrap; gap: 0.75rem; }
.tech-item { display: flex; align-items: center; gap: 0.5rem; }
</style>
