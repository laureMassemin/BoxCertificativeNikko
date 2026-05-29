<template>
  <div class="auth-page">
    <div class="auth-card">
      <h2>Welcome back</h2>
      <p class="auth-subtitle">Sign in to your account</p>

      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label for="username">Username</label>
          <input
            type="text"
            id="username"
            v-model="username"
            placeholder="Your username"
            required
          />
        </div>
        <div class="form-group">
          <label for="password">Password</label>
          <input
            type="password"
            id="password"
            v-model="password"
            placeholder="Your password"
            required
          />
        </div>

        <p v-if="error" class="error-msg">{{ error }}</p>

        <button type="submit" class="btn-submit">Login</button>
      </form>

      <p class="auth-footer">
        No account yet?
        <router-link to="/register">Create one</router-link>
      </p>
    </div>
  </div>
</template>

<script>
import { login } from '../api.ts'

export default {
  data() {
    return { username: '', password: '', error: '' }
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

<style scoped>
.auth-page {
  min-height: calc(100vh - 56px);
  display: flex;
  align-items: center;
  justify-content: center;
}

.auth-card {
  background: #ffffff;
  border: 1px solid #e8e8e8;
  border-radius: 12px;
  padding: 2.5rem;
  width: 100%;
  max-width: 400px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
}

h2 {
  font-size: 1.5rem;
  font-weight: 600;
  text-align: center;
  margin-bottom: 0.4rem;
}

.auth-subtitle {
  text-align: center;
  color: #888;
  font-size: 0.875rem;
  margin-bottom: 2rem;
}

.form-group {
  margin-bottom: 1.1rem;
}

label {
  display: block;
  font-size: 0.8rem;
  font-weight: 500;
  color: #555;
  margin-bottom: 0.35rem;
}

input {
  width: 100%;
  border: 1px solid #e0e0e0;
  border-radius: 7px;
  padding: 0.6rem 0.875rem;
  font-size: 0.9rem;
  font-family: inherit;
  color: #1a1a1a;
  outline: none;
  transition: border-color 0.15s;
}

input:focus {
  border-color: #555;
}

.btn-submit {
  width: 100%;
  background: #1a1a1a;
  color: #fff;
  border: none;
  border-radius: 7px;
  padding: 0.65rem;
  font-size: 0.9rem;
  font-family: inherit;
  font-weight: 500;
  cursor: pointer;
  margin-top: 0.5rem;
  transition: background 0.15s;
}

.btn-submit:hover {
  background: #333;
}

.error-msg {
  color: #d44;
  font-size: 0.825rem;
  margin-bottom: 0.75rem;
  background: #fff5f5;
  border: 1px solid #fdd;
  border-radius: 6px;
  padding: 0.5rem 0.75rem;
}

.auth-footer {
  text-align: center;
  margin-top: 1.5rem;
  font-size: 0.875rem;
  color: #888;
}

.auth-footer a {
  color: #1a1a1a;
  font-weight: 500;
  text-decoration: none;
}

.auth-footer a:hover {
  text-decoration: underline;
}
</style>
