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
  store.checkCache()
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
  width: 240px; min-height: 100vh;
  background: var(--p-surface-50);
  border-right: 1px solid var(--p-surface-200);
  display: flex; flex-direction: column;
  padding: 1.25rem; position: sticky; top: 0; height: 100vh;
}

.sidebar-brand { display: flex; align-items: center; gap: 0.75rem; margin-bottom: 2rem; }
.brand-text { display: flex; flex-direction: column; }
.brand-title { font-weight: 800; font-size: 1.1rem; color: var(--p-surface-950); }
.brand-sub { font-size: 0.7rem; color: var(--p-surface-600); letter-spacing: 0.3px; }

.sidebar-nav { display: flex; flex-direction: column; gap: 2px; flex: 1; }
.nav-item {
  display: flex; align-items: center; gap: 0.75rem;
  padding: 0.65rem 0.75rem; border-radius: 8px;
  text-decoration: none; color: var(--p-surface-600);
  font-size: 0.85rem; font-weight: 500;
  transition: all 0.2s;
}
.nav-item:hover { background: var(--p-surface-100); color: var(--p-surface-900); }
.nav-item.active { background: var(--p-primary-50); color: var(--p-primary-700); font-weight: 600; }
.nav-item i { font-size: 1.1rem; width: 20px; text-align: center; }

.sidebar-footer { display: flex; flex-direction: column; gap: 0.5rem; padding-top: 1rem; border-top: 1px solid var(--p-surface-200); }
.run-btn { width: 100%; }
.elapsed-badge {
  display: flex; align-items: center; gap: 0.4rem;
  font-size: 0.75rem; color: var(--p-surface-500);
  justify-content: center;
}

/* Main area */
.main-area { flex: 1; display: flex; flex-direction: column; min-height: 100vh; }

.topbar {
  display: flex; align-items: center; justify-content: space-between;
  padding: 1rem 1.5rem; border-bottom: 1px solid var(--p-surface-200);
  background: var(--p-surface-0);
  position: sticky; top: 0; z-index: 10;
}
.topbar-left { display: flex; align-items: center; gap: 0.75rem; }
.topbar-left h2 { font-size: 1.15rem; font-weight: 700; color: var(--p-surface-950); }
.topbar-right { display: flex; align-items: center; gap: 1rem; }
.file-group { display: flex; align-items: center; gap: 0.5rem; }

.content { flex: 1; padding: 1.5rem; background: var(--p-surface-0); }

/* Transitions */
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s ease, transform 0.2s ease; }
.fade-enter-from { opacity: 0; transform: translateY(8px); }
.fade-leave-to { opacity: 0; transform: translateY(-8px); }

/* Scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--p-surface-300); border-radius: 3px; }
</style>
