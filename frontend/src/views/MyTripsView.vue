<template>
  <div>
    <h1>My Trips</h1>

    <div v-if="loading">Loading...</div>
    <div v-else-if="error" style="color: red">{{ error }}</div>

    <div v-else>
      <p v-if="trips.length === 0">You have no trips yet.</p>

      <ul>
        <li
          v-for="trip in trips"
          :key="trip.id"
          style="margin-bottom: 10px; border: 1px solid black; padding: 10px"
        >
          <strong>Trip #{{ trip.id }}</strong> — {{ trip.places_count }} cities —
          {{ trip.total_distance.toFixed(2) }} km —
          {{ trip.is_public ? 'Public' : 'Private' }}
          <br />
          <button @click="router.push(`/trip/${trip.id}`)">View</button>
        </li>
      </ul>

      <button @click="router.push('/trip')">Create new trip</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getUserTours, getUsername } from '../api'

const router = useRouter()

interface TripSummary {
  id: number
  total_distance: number
  is_public: boolean
  places_count: number
}

const trips = ref<TripSummary[]>([])
const loading = ref(true)
const error = ref('')

onMounted(async () => {
  try {
    const username = getUsername()
    if (!username) {
      router.push('/login')
      return
    }
    trips.value = await getUserTours(username)
  } catch (e) {
    error.value = 'Could not load your trips'
  } finally {
    loading.value = false
  }
})
</script>
