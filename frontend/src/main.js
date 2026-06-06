import { createApp } from 'vue'
import { createPinia } from 'pinia'
import PrimeVue from 'primevue/config'
import Aura from '@primevue/themes/aura'
import router from './router'
import App from './App.vue'
import VueApexCharts from 'vue3-apexcharts'
import ToastService from 'primevue/toastservice'
import 'primeicons/primeicons.css'
import 'animate.css'

const app = createApp(App)
app.use(createPinia())
app.use(PrimeVue, { theme: { preset: Aura, options: { darkModeSelector: '.app-dark' } } })
app.use(VueApexCharts)
app.use(ToastService)
app.use(router)

app.mount('#app')
