<template>
  <div class="app-dark" style="min-height: 100vh; display: flex; background: var(--p-surface-0);">
    <!-- Sidebar -->
    <aside class="sidebar">
      <div class="sidebar-brand">
        <i class="pi pi-search" style="font-size: 1.6rem; color: var(--p-primary-500)"></i>
        <div class="brand-text">
          <span class="brand-title">Redrob</span>
          <span class="brand-sub">Candidate Ranker</span>
        </div>
      </div>

      <nav class="sidebar-nav">
        <router-link
          v-for="route in routes"
          :key="route.path"
          :to="route.path"
          :class="['nav-item', { active: $route.path === route.path }]"
        >
          <i :class="route.meta.icon"></i>
          <span>{{ route.meta.title }}</span>
        </router-link>
      </nav>

      <div class="sidebar-footer">
        <Button
          :label="store.running ? 'Ranking...' : 'Run Ranking'"
          :icon="store.running ? 'pi pi-spin pi-spinner' : 'pi pi-play'"
          :disabled="store.running"
          severity="info"
          class="run-btn"
          @click="runRanking"
        />
        <div v-if="store.elapsed" class="elapsed-badge">
          <i class="pi pi-clock"></i> {{ store.elapsed.toFixed(1) }}s
        </div>
      </div>
    </aside>

    <!-- Main -->
    <div class="main-area">
      <header class="topbar">
        <div class="topbar-left">
          <h2>{{ $route.meta.title }}</h2>
          <Tag v-if="store.cached && store.stats" :value="`${store.stats.count} candidates`" severity="info" rounded />
        </div>
        <div class="topbar-right">
          <div class="file-group">
            <FileUpload
              mode="basic"
              accept=".jsonl"
              :auto="false"
              chooseLabel="Upload JSONL"
              @select="onFileSelect"
            />
            <Checkbox v-model="useDefault" :binary="true" inputId="chk_default" />
            <label for="chk_default" style="font-size: 0.85rem; color: var(--p-surface-700)">Use default 100K</label>
          </div>
          <Select v-model="topK" :options="[10, 25, 50, 100]" style="width: 80px" />
        </div>
      </header>

      <main class="content">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>

    <!-- Error Toast -->
    <Toast position="top-right" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useRankerStore } from './stores/ranker'
import Button from 'primevue/button'
import Tag from 'primevue/tag'
import FileUpload from 'primevue/fileupload'
import Checkbox from 'primevue/checkbox'
import Select from 'primevue/select'
import Toast from 'primevue/toast'
import { useToast } from 'primevue/usetoast'

const store = useRankerStore()
const router = useRouter()
const route = useRoute()
const toast = useToast()

const useDefault = ref(true)
const topK = ref(100)
const uploadedFile = ref(null)

const routes = router.getRoutes()

onMounted(() => {
  store.fetchWeights()
  store.ensureLoaded()
})

function onFileSelect(e) {
  uploadedFile.value = e.files[0]
  useDefault.value = false
  toast.add({ severity: 'info', summary: 'File Selected', detail: e.files[0].name, life: 3000 })
}

async function runRanking() {
  await store.runRanking(useDefault.value, topK.value, uploadedFile.value)
  if (store.error) {
    toast.add({ severity: 'error', summary: 'Ranking Failed', detail: store.error, life: 5000 })
  } else {
    toast.add({ severity: 'success', summary: 'Ranking Complete', detail: `${store.stats.count} candidates ranked in ${store.elapsed.toFixed(1)}s`, life: 3000 })
    router.push('/results')
  }
}
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: 'Inter', sans-serif; }

.sidebar {
  width: 260px;
  min-height: 100vh;
  background: linear-gradient(180deg, var(--p-surface-50) 0%, var(--p-surface-25) 100%);
  border-right: 1px solid var(--p-surface-200);
  box-shadow: 2px 0 12px rgba(0, 0, 0, 0.03);
  display: flex;
  flex-direction: column;
  padding: 1.5rem 1rem;
  position: sticky;
  top: 0;
  height: 100vh;
}

.sidebar-brand {
  display: flex;
  align-items: center;
  gap: 0.875rem;
  margin-bottom: 2.5rem;
  padding: 0 0.5rem;
}

.brand-text {
  display: flex;
  flex-direction: column;
}

.brand-title {
  font-weight: 800;
  font-size: 1.15rem;
  color: var(--p-surface-950);
  letter-spacing: -0.02em;
}

.brand-sub {
  font-size: 0.7rem;
  color: var(--p-surface-500);
  letter-spacing: 0.3px;
  margin-top: 2px;
}

.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 0.875rem;
  padding: 0.75rem 1rem;
  border-radius: 10px;
  text-decoration: none;
  color: var(--p-surface-600);
  font-size: 0.85rem;
  font-weight: 500;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
}

.nav-item:hover {
  background: rgba(0, 188, 212, 0.08);
  color: var(--p-surface-900);
}

.nav-item.active {
  background: linear-gradient(135deg, rgba(0, 188, 212, 0.12), rgba(0, 188, 212, 0.05));
  color: var(--p-primary-700);
  font-weight: 600;
  box-shadow: 0 2px 8px rgba(0, 188, 212, 0.15);
}

.nav-item.active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 24px;
  background: var(--p-primary-500);
  border-radius: 0 3px 3px 0;
}

.nav-item i {
  font-size: 1.15rem;
  width: 22px;
  text-align: center;
}

.sidebar-footer {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  padding-top: 1.25rem;
  border-top: 1px solid var(--p-surface-200);
  margin-top: 1rem;
}

.run-btn {
  width: 100%;
  font-weight: 600;
  box-shadow: 0 4px 12px rgba(0, 188, 212, 0.2);
  transition: all 0.3s ease;
}

.run-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 188, 212, 0.3);
}

.elapsed-badge {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.8rem;
  color: var(--p-surface-500);
  justify-content: center;
  padding: 0.5rem;
  background: var(--p-surface-25);
  border-radius: 8px;
}

.elapsed-badge i {
  color: var(--p-primary-500);
}

/* Main area */
.main-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background: var(--p-surface-0);
}

.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.25rem 2rem;
  border-bottom: 1px solid var(--p-surface-200);
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  position: sticky;
  top: 0;
  z-index: 10;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
}

.topbar-left {
  display: flex;
  align-items: center;
  gap: 0.875rem;
}

.topbar-left h2 {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--p-surface-950);
  letter-spacing: -0.02em;
}

.topbar-right {
  display: flex;
  align-items: center;
  gap: 1.25rem;
}

.file-group {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.content {
  flex: 1;
  padding: 1.75rem 2rem;
  background: var(--p-surface-0);
}

/* Card improvements */
:deep(.p-card) {
  border-radius: 14px;
  border: 1px solid var(--p-surface-100);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  transition: all 0.3s ease;
}

:deep(.p-card-body) {
  padding: 1.25rem;
}

:deep(.p-card-title) {
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--p-surface-800);
}

/* Transitions */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}
.fade-enter-from {
  opacity: 0;
  transform: translateY(12px);
}
.fade-leave-to {
  opacity: 0;
  transform: translateY(-12px);
}

/* Scrollbar */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}
::-webkit-scrollbar-track {
  background: transparent;
}
::-webkit-scrollbar-thumb {
  background: var(--p-surface-300);
  border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
  background: var(--p-surface-400);
}

/* Animations */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.animate-fade-in {
  animation: fadeIn 0.4s ease forwards;
}
</style>
