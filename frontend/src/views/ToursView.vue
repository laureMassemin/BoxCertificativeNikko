<template>
  <div class="trip-container">
    <h2>Trip Details</h2>

    <div v-if="loading">Loading...</div>

    <div v-else-if="error" style="color: red">{{ error }}</div>

    <div v-else>
      <p>Total distance: {{ trip?.total_distance }} km</p>
      <p>Public: {{ trip?.is_public ? 'Yes' : 'No' }}</p>

      <h3>Places (in order)</h3>
      <ol>
        <li v-for="place in trip?.places" :key="place.id">
          {{ place.name }} — {{ place.lat }}, {{ place.lon }}
        </li>
      </ol>
    </div>
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getTrip, getUsername } from '../api'

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
  places: Place[]
}

const route = useRoute()
const tripId = route.params.tripId as string

const trip = ref<Trip | null>(null)
const loading = ref(true)
const error = ref('')
onMounted(async () => {
  try {
    trip.value = await getTrip(Number(tripId))
    const currentUser = getUsername()
    if (trip.value) {
      const isOwner = trip.value.owner_username === currentUser
      const isPublic = trip.value.is_public

      if (!isPublic && !isOwner) {
        error.value = 'You do not have access to this tour'
        trip.value = null
      }
    }
  } catch (e) {
    error.value = 'Trip not found'
  } finally {
    loading.value = false
  }
})
</script>
