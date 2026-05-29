<template>
  <div id="app">
    <nav style="margin-bottom: 20px; padding: 10px; background-color: #f0f0f0">
      <span v-if="loggedIn">
        <router-link to="/trip" style="margin-right: 15px">Create Trip</router-link>
        <router-link to="/my-trips" style="margin-right: 15px">My Trips</router-link>
        <span style="margin-right: 15px">Hello, {{ username }}</span>
        <button @click="handleLogout">Logout</button>
      </span>

      <span v-else>
        <router-link to="/login" style="margin-right: 15px">Login</router-link>
        <router-link to="/register">Register</router-link>
      </span>
    </nav>

    <router-view />
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

// Update nav when route changes (e.g. after login)
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
body {
  font-family: Arial, sans-serif;
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}
</style>
