<template>
  <div class="trip-page">
    <h1>Plan a Trip</h1>

    <p v-if="errorMessage" class="error-msg">{{ errorMessage }}</p>

    <div class="card">
      <h2>Search Cities</h2>
      <div class="search-row">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="e.g., Paris, Tokyo..."
          @keyup.enter="searchCity"
        />
        <button class="btn-search" @click="searchCity">Search</button>
      </div>

      <ul v-if="searchResults.length" class="results-list">
        <li v-for="place in searchResults" :key="place.lat" class="result-item">
          <span class="result-name">{{ place.name }}</span>
          <button class="btn-add" @click="addPlaceToTrip(place)">+ Add</button>
        </li>
      </ul>
    </div>

    <div class="card">
      <h2>
        My Trip <span class="count">{{ selectedPlaces.length }} cities</span>
      </h2>

      <p v-if="selectedPlaces.length === 0" class="empty-msg">
        Your trip is currently empty. Search for cities above.
      </p>

      <ol v-else class="places-list">
        <li v-for="(place, index) in selectedPlaces" :key="index" class="place-item">
          <span class="place-num">{{ index + 1 }}</span>
          <span class="place-name">{{ place.name }}</span>
          <button class="btn-remove" @click="removePlace(index)">✕</button>
        </li>
      </ol>

      <div ref="mapContainer" class="map-container"></div>

      <div class="trip-footer">
        <label class="checkbox-label">
          <input type="checkbox" v-model="isPublic" />
          Make this trip public
        </label>

        <button v-if="selectedPlaces.length >= 2" class="btn-generate" @click="generateTour">
          Calculate Optimal Route →
        </button>

        <button
          v-if="selectedPlaces.length >= 2"
          class="btn-generate btn-hotels"
          @click="generateTourHotels"
        >
          Generate with Hotels →
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { generateTour as apiGenerateTour, getUsername, generateTourWithHotels } from '../api'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

const router = useRouter()

interface Place {
  name: string
  lat: number
  lon: number
}

const searchQuery = ref('')
const searchResults = ref<Place[]>([])
const selectedPlaces = ref<Place[]>([])
const errorMessage = ref('')
const tourResult = ref<any>(null)
const isPublic = ref(false)

const mapContainer = ref(null)
let map: L.Map | null = null
let markersLayer = L.layerGroup()

const generateTourHotels = async () => {
  errorMessage.value = ''
  try {
    const result = await generateTourWithHotels(
      selectedPlaces.value,
      getUsername()!,
      isPublic.value,
    )
    router.push(`/trip/${result.id}`)
  } catch (error) {
    errorMessage.value = 'Communication error with the server.'
  }
}

const updateMapMarkers = () => {
  if (!map) return
  markersLayer.clearLayers()
  selectedPlaces.value.forEach((place) => {
    L.circleMarker([place.lat, place.lon], {
      radius: 7,
      fillColor: '#1a1a1a',
      color: '#fff',
      weight: 2,
      fillOpacity: 1,
    })
      .bindPopup(place.name)
      .addTo(markersLayer)
  })
}

watch(
  selectedPlaces,
  () => {
    updateMapMarkers()
  },
  { deep: true },
)

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

const searchCity = async () => {
  errorMessage.value = ''
  try {
    const response = await fetch(`http://localhost:8000/places/search?name=${searchQuery.value}`)
    if (!response.ok) throw new Error('City not found')
    searchResults.value = await response.json()
  } catch {
    errorMessage.value = 'Unable to find this city.'
    searchResults.value = []
  }
}

const addPlaceToTrip = (place: Place) => {
  if (!selectedPlaces.value.find((p) => p.name === place.name)) {
    selectedPlaces.value.push(place)
  }
  searchResults.value = []
  searchQuery.value = ''
}

const removePlace = (index: number) => {
  selectedPlaces.value.splice(index, 1)
}
</script>

<style scoped>
.trip-page {
  max-width: 860px;
}

h1 {
  font-size: 1.6rem;
  font-weight: 600;
  margin-bottom: 1.5rem;
  color: #1a1a1a;
}

h2 {
  font-size: 1rem;
  font-weight: 600;
  color: #1a1a1a;
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.count {
  font-size: 0.75rem;
  font-weight: 500;
  background: #f0f0f0;
  color: #666;
  padding: 0.2rem 0.6rem;
  border-radius: 999px;
}

.card {
  background: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 10px;
  padding: 1.5rem;
  margin-bottom: 1.25rem;
}

.error-msg {
  background: #fff5f5;
  border: 1px solid #fdd;
  color: #d44;
  border-radius: 7px;
  padding: 0.6rem 0.875rem;
  font-size: 0.85rem;
  margin-bottom: 1rem;
}

.search-row {
  display: flex;
  gap: 0.6rem;
}

input[type='text'] {
  flex: 1;
  border: 1px solid #e0e0e0;
  border-radius: 7px;
  padding: 0.6rem 0.875rem;
  font-size: 0.9rem;
  font-family: inherit;
  outline: none;
  transition: border-color 0.15s;
}

input[type='text']:focus {
  border-color: #555;
}

.btn-search {
  background: #1a1a1a;
  color: #fff;
  border: none;
  border-radius: 7px;
  padding: 0.6rem 1.25rem;
  font-size: 0.875rem;
  font-family: inherit;
  font-weight: 500;
  cursor: pointer;
  white-space: nowrap;
  transition: background 0.15s;
}

.btn-search:hover {
  background: #333;
}

.results-list {
  list-style: none;
  margin-top: 0.75rem;
  border: 1px solid #e8e8e8;
  border-radius: 7px;
  overflow: hidden;
}

.result-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.6rem 0.875rem;
  border-bottom: 1px solid #f0f0f0;
  transition: background 0.1s;
}

.result-item:last-child {
  border-bottom: none;
}
.result-item:hover {
  background: #fafafa;
}

.result-name {
  font-size: 0.875rem;
  color: #333;
}

.btn-add {
  background: none;
  border: 1px solid #e0e0e0;
  border-radius: 5px;
  color: #555;
  font-size: 0.8rem;
  font-family: inherit;
  padding: 0.2rem 0.6rem;
  cursor: pointer;
  transition: all 0.15s;
}

.btn-add:hover {
  background: #1a1a1a;
  color: #fff;
  border-color: #1a1a1a;
}

.empty-msg {
  color: #aaa;
  font-size: 0.875rem;
  margin-bottom: 1rem;
}

.places-list {
  list-style: none;
  margin-bottom: 1rem;
}

.place-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.6rem 0;
  border-bottom: 1px solid #f5f5f5;
}

.place-item:last-child {
  border-bottom: none;
}

.place-num {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: #f0f0f0;
  color: #666;
  font-size: 0.7rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.place-name {
  flex: 1;
  font-size: 0.875rem;
  color: #333;
}

.btn-remove {
  background: none;
  border: none;
  color: #ccc;
  font-size: 0.75rem;
  cursor: pointer;
  padding: 0.2rem;
  transition: color 0.15s;
}

.btn-remove:hover {
  color: #d44;
}

.map-container {
  height: 380px;
  width: 100%;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #e8e8e8;
  margin-bottom: 1.25rem;
}

.trip-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: #666;
  cursor: pointer;
}

input[type='checkbox'] {
  cursor: pointer;
  accent-color: #1a1a1a;
}

.btn-generate {
  background: #1a1a1a;
  color: #fff;
  border: none;
  border-radius: 7px;
  padding: 0.65rem 1.5rem;
  font-size: 0.9rem;
  font-family: inherit;
  font-weight: 500;
  cursor: pointer;
  transition:
    background 0.15s,
    transform 0.15s;
}

.btn-generate:hover {
  background: #333;
  transform: translateY(-1px);
}
</style>
