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

      <!-- Carte Leaflet -->
      <div
        ref="mapContainer"
        style="height: 400px; width: 100%; border: 2px solid black; margin: 15px 0"
      ></div>

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
import { ref, onMounted, watch, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { getTrip, getUsername, calculateDistance, updateTourPlaces } from '../api'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

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
const tripId = route.params.tripId as string

const trip = ref<Trip | null>(null)
const places = ref<Place[]>([])
const loading = ref(true)
const error = ref('')
const totalDistance = ref('')

// Map
const mapContainer = ref(null)
let map: L.Map | null = null
let markersLayer = L.layerGroup()
let polyline: L.Polyline | null = null

const updateMap = () => {
  if (!map) return

  // Clear markers and polyline
  markersLayer.clearLayers()
  if (polyline) {
    map.removeLayer(polyline)
  }

  if (places.value.length === 0) return

  // Add circle markers
  places.value.forEach((place, index) => {
    L.circleMarker([place.lat, place.lon], {
      radius: 8,
      fillColor: '#3388ff',
      color: '#fff',
      weight: 2,
      fillOpacity: 1,
    })
      .bindPopup(`${index + 1}. ${place.name}`)
      .addTo(markersLayer)
  })

  // Draw route line including return to start
  const coords = places.value.map((p) => [p.lat, p.lon] as [number, number])
  coords.push(coords[0]!)
  polyline = L.polyline(coords, { color: 'blue' }).addTo(map)

  // Fit map to show all markers
  map.fitBounds(polyline.getBounds())
}

// Update map when places change
watch(
  places,
  () => {
    updateMap()
  },
  { deep: true },
)

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
        return
      }
      places.value = [...trip.value.places]
    }
  } catch (e) {
    error.value = 'Trip not found'
  } finally {
    loading.value = false
  }

  // Wait for DOM to update before initializing map
  await nextTick()

  if (mapContainer.value) {
    map = L.map(mapContainer.value).setView([46.603354, 1.888334], 5)
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map)
    markersLayer.addTo(map)
    updateMap()
  }
})
</script>
