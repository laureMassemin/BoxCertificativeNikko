import { createRouter, createWebHistory } from 'vue-router'
import TripView from './views/TripView.vue'
import LoginView from './views/LoginView.vue'
import RegisterView from './views/RegisterView.vue'
import ToursView from './views/ToursView.vue'
import MyTripsView from './views/MyTripsView.vue'

const routes = [
  { path: '/login', component: LoginView },
  { path: '/', redirect: '/login' },
  { path: '/register', component: RegisterView },
  { path: '/trip', component: TripView, meta: { requiresAuth: true } },
  { path: '/trip/:tripId', component: ToursView },
  { path: '/my-trips', component: MyTripsView, meta: { requiresAuth: true } },
]
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

export default router

import { isLoggedIn } from './api'

router.beforeEach((to, from, next) => {
  if (to.meta.requiresAuth && !isLoggedIn()) {
    next('/login')
  } else {
    next()
  }
})
