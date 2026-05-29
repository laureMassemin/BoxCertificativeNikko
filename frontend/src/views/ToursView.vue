<template>
  <div class="trip-container">
    <h2>Trip Details</h2>

    <div v-if="loading">Loading...</div>

    <div v-else-if="error" style="color: red">{{ error }}</div>

    <div v-else>
      <p>Total distance: {{ totalDistance }} km</p>
      <p>Public: {{ trip?.is_public ? 'Yes' : 'No' }}</p>

      <h3>Places (in order)</h3>
      <ol>
        <li v-for="(place, index) in places" :key="place.id" style="margin-bottom: 8px">
          {{ place.name }} : {{ place.lat }}, {{ place.lon }}
          <button @click="moveUp(index)" :disabled="index === 0">⬆</button>
          <button @click="moveDown(index)" :disabled="index === places.length - 1">⬇</button>
        </li>
      </ol>
      <p>
        Share link:
        <a :href="`http://localhost:5173/share/${trip?.share_token}`">
          {{ trip?.share_token }}
        </a>
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getTrip, getUsername, calculateDistance, updateTourPlaces } from '../api'

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
  share_token: string // ← ajoute ça
  places: Place[]
}

const route = useRoute()
const tripId = route.params.tripId as string

const trip = ref<Trip | null>(null)
const places = ref<Place[]>([])
const loading = ref(true)
const error = ref('')

const totalDistance = ref('')

async function recalculate() {
  const result = await calculateDistance(places.value)
  totalDistance.value = result.toFixed(2)
  await updateTourPlaces(Number(tripId), places.value)
}
async function moveUp(index: number) {
  if (index === 0) return
  const newPlaces = [...places.value]
  const tmp = newPlaces[index - 1]!
  newPlaces[index - 1] = newPlaces[index]!
  newPlaces[index] = tmp
  places.value = newPlaces
  await recalculate()
}

async function moveDown(index: number) {
  if (index === places.value.length - 1) return
  const newPlaces = [...places.value]
  const tmp = newPlaces[index + 1]!
  newPlaces[index + 1] = newPlaces[index]!
  newPlaces[index] = tmp
  places.value = newPlaces
  await recalculate()
}
onMounted(async () => {
  try {
    trip.value = await getTrip(Number(tripId))
    const currentUser = getUsername()
    if (trip.value) {
      const isOwner = trip.value.owner_username === currentUser
      const isPublic = trip.value.is_public
      totalDistance.value = trip.value.total_distance.toFixed(2)

      if (!isPublic && !isOwner) {
        error.value = 'You do not have access to this tour'
        trip.value = null
      }
      places.value = [...trip.value.places]
      console.log(
        'Ordre initial:',
        places.value.map((p) => p.name),
      )
    }
  } catch (e) {
    error.value = 'Trip not found'
  } finally {
    loading.value = false
  }
})
</script>
