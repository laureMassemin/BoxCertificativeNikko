<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { generateTour as apiGenerateTour, getUsername } from '../api'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

const router = useRouter()

// Place interface for type safety
interface Place {
  name: string
  lat: number
  lon: number
}

// Reactive states
const searchQuery = ref('')
const searchResults = ref<Place[]>([])
const selectedPlaces = ref<Place[]>([])
const errorMessage = ref('')
const tourResult = ref<any>(null)

const isPublic = ref(false)

//Dynamic map
const mapContainer = ref(null)
let map: L.Map | null = null
let markersLayer = L.layerGroup()

// Update markers on the map
const updateMapMarkers = () => {
  if (!map) return
  markersLayer.clearLayers()
  selectedPlaces.value.forEach(place => {
    const marker = L.marker([place.lat, place.lon]).bindPopup(place.name)
    markersLayer.addLayer(marker)
  })
}
// Update the map when selected places change
watch(selectedPlaces, () => {
  updateMapMarkers()
}, { deep: true })
// Create map when the page load
onMounted(() => {
  if (mapContainer.value) {
    map = L.map(mapContainer.value).setView([46.603354, 1.888334], 5)
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map)
    markersLayer.addTo(map)
  }
})

const generateTour = async () => {
  const result = await apiGenerateTour(selectedPlaces.value, getUsername()!, isPublic.value)
  router.push(`/trip/${result.id}`)
}

// Fetch city coordinates from backend
const searchCity = async () => {
  errorMessage.value = ''
  try {
    const response = await fetch(`http://localhost:8000/places/search?name=${searchQuery.value}`)
    if (!response.ok) throw new Error('City not found')

    searchResults.value = await response.json()
  } catch (error) {
    errorMessage.value = 'Unable to find this city.'
    searchResults.value = []
  }
}

// Add city to trip (prevents duplicates)
const addPlaceToTrip = (place: Place) => {
  if (!selectedPlaces.value.find((p) => p.name === place.name)) {
    selectedPlaces.value.push(place)
  }
  searchResults.value = []
  searchQuery.value = ''
}

// Remove city from trip
const removePlace = (index: number) => {
  selectedPlaces.value.splice(index, 1)
}
</script>

<template>
  <div>
    <h1>Trip Planner</h1>

    <p v-if="errorMessage" style="color: red; font-weight: bold">
      {{ errorMessage }}
    </p>

    <div style="border: 1px solid black; padding: 10px; margin-bottom: 20px">
      <h2>Search Cities</h2>
      <input v-model="searchQuery" type="text" placeholder="e.g., Paris" />
      <button @click="searchCity">Search</button>

      <ul>
        <li v-for="place in searchResults" :key="place.lat">
          {{ place.name }}
          <button @click="addPlaceToTrip(place)">Add to trip</button>
        </li>
      </ul>
    </div>

    <div style="border: 1px solid black; padding: 10px; margin-bottom: 20px">
      <h2>My Trip ({{ selectedPlaces.length }} cities)</h2>

      <p v-if="selectedPlaces.length === 0">Your trip is currently empty.</p>

      <ol>
        <li v-for="(place, index) in selectedPlaces" :key="index">
          {{ place.name }}
          <button @click="removePlace(index)">Remove</button>
        </li>
      </ol>

      <div ref="mapContainer" style="height: 400px; width: 100%; border: 2px solid black; margin-bottom: 15px;"></div>

      <label>
        <input type="checkbox" v-model="isPublic" />
        Make this trip public
      </label>
      <button
        v-if="selectedPlaces.length >= 2"
        @click="generateTour"
        style="background-color: lightgreen; font-size: 16px; padding: 10px"
      >
        Calculate Optimal Route
      </button>
    </div>

    <div v-if="tourResult" style="border: 2px solid green; padding: 10px">
      <h2>Route Generated</h2>
      <p><strong>Total distance:</strong> {{ tourResult.total_distance?.toFixed(2) ?? '?' }} km</p>
      <h3>Optimized order:</h3>
      <ol>
        <li v-for="place in tourResult.tour" :key="place.lat">
          {{ place.name }}
        </li>
      </ol>
    </div>
  </div>
</template>