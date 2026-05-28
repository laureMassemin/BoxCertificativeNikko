<template>
  <div class="register-container">
    <h2>Register</h2>
    <form @submit.prevent="handleRegister">
      <div class="form-group">
        <label for="username">Username:</label>
        <input type="text" id="username" v-model="username" required />
      </div>
      <div class="form-group">
        <label for="password">Password:</label>
        <input type="password" id="password" v-model="password" required />
      </div>
      <button type="submit">Register</button>
      <button type="button" @click="$router.push('/login')">Login</button>
    </form>
    <p v-if="error" style="color: red">{{ error }}</p>
  </div>
</template>

<script lang="ts">
import { register } from '../api.ts'

export default {
  data() {
    return {
      username: '',
      password: '',
      error: '',
    }
  },
  methods: {
    async handleRegister() {
      try {
        await register(this.username, this.password)
        this.$router.push('/login')
      } catch (e) {
        if (e.response?.status === 400) {
          this.error = 'Username already taken'
        } else {
          this.error = 'An error occurred'
        }
      }
    },
  },
}
</script>

<style scoped></style>
