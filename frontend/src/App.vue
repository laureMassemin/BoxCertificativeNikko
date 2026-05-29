<template>
  <div id="app">
    <nav>
      <div class="nav-brand">TravelPlanner</div>

      <div class="nav-links" v-if="loggedIn">
        <router-link to="/trip">Create Trip</router-link>
        <router-link to="/my-trips">My Trips</router-link>
      </div>

      <div class="nav-right" v-if="loggedIn">
        <span class="nav-username">{{ username }}</span>
        <button class="nav-btn" @click="handleLogout">Logout</button>
      </div>

      <div class="nav-links" v-else>
        <router-link to="/login">Login</router-link>
        <router-link to="/register">Register</router-link>
      </div>
    </nav>

    <main>
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { isLoggedIn, logout, getUsername } from './api'

const router = useRouter()
const route = useRoute()

const loggedIn = ref(isLoggedIn())
const username = ref(getUsername() ?? '')

watch(route, () => {
  loggedIn.value = isLoggedIn()
  username.value = getUsername() ?? ''
})

function handleLogout() {
  logout()
  loggedIn.value = false
  username.value = ''
  router.push('/login')
}
</script>

<style>
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: 'Segoe UI', system-ui, sans-serif;
  background: #f9f9f9;
  color: #1a1a1a;
}

nav {
  background: #ffffff;
  border-bottom: 1px solid #e8e8e8;
  padding: 0 2rem;
  height: 56px;
  display: flex;
  align-items: center;
  gap: 2rem;
  position: sticky;
  top: 0;
  z-index: 10;
}

.nav-brand {
  font-weight: 600;
  font-size: 1rem;
  color: #1a1a1a;
  letter-spacing: -0.01em;
  margin-right: 1rem;
}

.nav-links {
  display: flex;
  gap: 0.25rem;
}

.nav-links a {
  text-decoration: none;
  color: #666;
  font-size: 0.875rem;
  font-weight: 500;
  padding: 0.35rem 0.75rem;
  border-radius: 6px;
  transition:
    background 0.15s,
    color 0.15s;
}

.nav-links a:hover {
  background: #f0f0f0;
  color: #1a1a1a;
}

.nav-links a.router-link-active {
  background: #f0f0f0;
  color: #1a1a1a;
}

.nav-right {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.nav-username {
  font-size: 0.875rem;
  color: #888;
}

.nav-btn {
  background: none;
  border: 1px solid #e0e0e0;
  color: #555;
  font-size: 0.8rem;
  font-family: inherit;
  padding: 0.3rem 0.75rem;
  border-radius: 6px;
  cursor: pointer;
  transition:
    background 0.15s,
    color 0.15s;
}

.nav-btn:hover {
  background: #f5f5f5;
  color: #1a1a1a;
}

main {
  max-width: 860px;
  margin: 0 auto;
  padding: 2rem 1.5rem;
}
</style>
