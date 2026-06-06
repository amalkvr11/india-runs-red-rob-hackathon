import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useRankerStore = defineStore('ranker', () => {
  const results = ref(null)
  const weights = ref({})
  const stats = ref(null)
  const elapsed = ref(0)
  const running = ref(false)
  const error = ref('')
  const cached = ref(false)
  const loading = ref(false)

  const topScore = computed(() => results.value?.[0]?.score ?? 0)
  const bottomScore = computed(() => results.value?.[results.value.length - 1]?.score ?? 0)
  const avgScore = computed(() => {
    if (!results.value?.length) return 0
    return results.value.reduce((a, r) => a + r.score, 0) / results.value.length
  })

  async function fetchWeights() {
    try {
      const res = await fetch('/api/weights')
      if (res.ok) weights.value = await res.json()
    } catch {}
  }

  async function runRanking(useDefault = true, topK = 100, file = null) {
    running.value = true
    error.value = ''

    const form = new FormData()
    if (file && !useDefault) {
      form.append('file', file)
      form.append('use_default', 'false')
    } else {
      form.append('use_default', 'true')
    }
    form.append('top_k', String(topK))

    try {
      const res = await fetch('/api/rank', { method: 'POST', body: form })
      if (!res.ok) {
        const err = await res.text()
        throw new Error(err)
      }
      const data = await res.json()
      results.value = data.results
      stats.value = data.stats
      elapsed.value = data.elapsed
      cached.value = true
    } catch (e) {
      error.value = e.message || 'Ranking failed'
      results.value = null
    } finally {
      running.value = false
    }
  }

  async function checkCache() {
    if (loading.value) return
    loading.value = true
    try {
      const res = await fetch('/api/status')
      if (res.ok) {
        const s = await res.json()
        cached.value = s.cached
        if (s.cached) {
          const r = await fetch('/api/results')
          if (r.ok) {
            const d = await r.json()
            results.value = d.results
            stats.value = d.stats
          }
        }
      }
    } catch (e) {
      console.error('checkCache failed:', e)
    } finally {
      loading.value = false
    }
  }

  async function ensureLoaded() {
    if (results.value) return
    if (loading.value) return
    await checkCache()
    // Retry once if still no results
    if (!results.value && cached.value) {
      await checkCache()
    }
  }

  function getCandidate(id) {
    return results.value?.find(r => r.candidate_id === id) || null
  }

  return { results, weights, stats, elapsed, running, error, cached, loading, topScore, bottomScore, avgScore, fetchWeights, runRanking, checkCache, ensureLoaded, getCandidate }
})
