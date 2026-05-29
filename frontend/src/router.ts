import { createRouter, createWebHistory } from 'vue-router'
import TripView from './views/TripView.vue'
import LoginView from './views/LoginView.vue'
import RegisterView from './views/RegisterView.vue'
import ToursView from './views/ToursView.vue'

const routes = [
  { path: '/login', component: LoginView },
  { path: '/', redirect: '/login' },
  { path: '/register', component: RegisterView },
  { path: '/trip', component: TripView },
  { path: '/trip/:tripId', component: ToursView },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

export default router
