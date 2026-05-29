<template>
  <div class="trip-container">
    <h2>Shared Trip</h2>

    <div v-if="loading">Loading...</div>

    <div v-else-if="error" style="color: red">{{ error }}</div>

    <div v-else>
      <p>Owner: {{ trip?.owner_username }}</p>
      <p>Total distance: {{ totalDistance }} km</p>
      <p>Public: {{ trip?.is_public ? 'Yes' : 'No' }}</p>

      <h3>Places (in order)</h3>
      <ol>
        <li v-for="place in places" :key="place.id">
          {{ place.name }} : {{ place.lat }}, {{ place.lon }}
        </li>
      </ol>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getTripByToken, getUsername } from '../api'

interface Place {
  id: number
  name: string
  lat: number
  lon: number
  order: number
}

interface Trip {
  id: number
  owner_username: string
  is_public: boolean
  total_distance: number
  share_token: string
  places: Place[]
}

const route = useRoute()
const token = route.params.token as string

const trip = ref<Trip | null>(null)
const places = ref<Place[]>([])
const loading = ref(true)
const error = ref('')
const totalDistance = ref('')

onMounted(async () => {
  try {
    trip.value = await getTripByToken(token)

    if (trip.value) {
      places.value = [...trip.value.places]
      totalDistance.value = trip.value.total_distance.toFixed(2)
    }
  } catch (e) {
    error.value = 'Trip not found'
  } finally {
    loading.value = false
  }
})
</script>
