import { createRouter, createWebHistory } from 'vue-router'
import TripView from './views/TripView.vue'
import LoginView from './views/LoginView.vue'
import RegisterView from './views/RegisterView.vue'

const routes = [
  {
    path: '/',
    redirect: '/trip',
  },
  {
    path: '/trip',
    name: 'trip',
    component: TripView,
  },
  {
    path: '/login',
    name: 'login',
    component: LoginView,
  },
  {
    path: '/register',
    name: 'register',
    component: RegisterView,
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

export default router
