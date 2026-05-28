import axios from 'axios'

// Base URL of the FastAPI backend
const http = axios.create({ baseURL: 'http://localhost:8000' })

// Types
interface AuthResponse {
  token: string
  username: string
}

// Register a new user
export async function register(username: string, password: string): Promise<void> {
  const res = await http.post('/register', { username, password })
  return res.data
}

// Login and store token in localStorage
export async function login(username: string, password: string): Promise<AuthResponse> {
  const res = await http.post<AuthResponse>('/login', { username, password })
  localStorage.setItem('token', res.data.token)
  localStorage.setItem('username', res.data.username)
  return res.data
}
export async function getTrip(id: number) {
  const res = await http.get(`/tours/${id}`)
  return res.data
}

// Remove token from localStorage
export function logout(): void {
  localStorage.removeItem('token')
  localStorage.removeItem('username')
}

// Check if user is logged in
export function isLoggedIn(): boolean {
  return !!localStorage.getItem('token')
}

// Get the stored token (used for protected requests)
export function getToken(): string | null {
  return localStorage.getItem('token')
}

// Get the logged in username
export function getUsername(): string | null {
  return localStorage.getItem('username')
}
