<template>
  <div class="login-container">
    <h2>Login</h2>
    <form @submit.prevent="handleLogin">
      <div class="form-group">
        <label for="username">Username:</label>
        <input type="text" id="username" v-model="username" required />
      </div>
      <div class="form-group">
        <label for="password">Password:</label>
        <input type="password" id="password" v-model="password" required />
      </div>
      <button type="submit">Login</button>
    </form>
    <p v-if="error" style="color: red">{{ error }}</p>
  </div>
</template>

<script>
import { login } from '../api.ts'

export default {
  data() {
    return {
      username: '',
      password: '',
      error: '',
    }
  },
  methods: {
    async handleLogin() {
      try {
        await login(this.username, this.password)
        this.$router.push('/trip')
      } catch (e) {
        if (e.response?.status === 401) {
          this.error = 'Wrong username or password'
        } else {
          this.error = 'An error occurred'
        }
      }
    },
  },
}
</script>

<style scoped></style>
