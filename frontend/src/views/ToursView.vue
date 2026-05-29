<template>
  <div class="tours-page">
    <div v-if="loading" class="loading-msg">Loading...</div>
    <div v-else-if="error" class="error-msg">{{ error }}</div>

    <div v-else>
      <div class="stats-row">
        <div class="stat">
          <div class="stat-value">{{ totalDistance }} km</div>
          <div class="stat-label">Total distance</div>
        </div>
        <div class="stat">
          <div class="stat-value">{{ places.length }}</div>
          <div class="stat-label">Cities</div>
        </div>
        <div class="stat">
          <div class="stat-value">{{ trip?.is_public ? 'Public' : 'Private' }}</div>
          <div class="stat-label">Visibility</div>
        </div>
      </div>

      <div class="card">
        <h2>Places (in order)</h2>
        <ol class="places-list">
          <li v-for="(place, index) in places" :key="place.id" class="place-item">
            <span class="place-num">{{ index + 1 }}</span>
            <div class="place-info">
              <span class="place-name">{{ place.name }}</span>
              <span class="place-coords"
                >{{ place.lat.toFixed(4) }}, {{ place.lon.toFixed(4) }}</span
              >
            </div>
            <div class="place-actions">
              <button class="btn-order" @click="moveUp(index)" :disabled="index === 0">↑</button>
              <button
                class="btn-order"
                @click="moveDown(index)"
                :disabled="index === places.length - 1"
              >
                ↓
              </button>
            </div>
          </li>
        </ol>
      </div>

      <div class="card">
        <h2>Route Map</h2>
        <div ref="mapContainer" class="map-container"></div>
      </div>

      <div class="share-box">
        <span class="share-label">Share link</span>
        <a :href="`http://localhost:5173/share/${trip?.share_token}`" target="_blank">
          http://localhost:5173/share/{{ trip?.share_token }}
        </a>
      </div>
    </div>
  </div>
</template>

<style scoped>
.tours-page {
  max-width: 760px;
}

h2 {
  font-size: 1rem;
  font-weight: 600;
  color: #1a1a1a;
  margin-bottom: 1rem;
}

.loading-msg {
  color: #888;
  padding: 2rem 0;
}

.error-msg {
  background: #fff5f5;
  border: 1px solid #fdd;
  color: #d44;
  border-radius: 7px;
  padding: 0.75rem 1rem;
  font-size: 0.875rem;
}

.stats-row {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.25rem;
}

.stat {
  flex: 1;
  background: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 10px;
  padding: 1rem;
  text-align: center;
}

.stat-value {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1a1a1a;
}

.stat-label {
  font-size: 0.75rem;
  color: #888;
  margin-top: 0.25rem;
}

/* Card */
.card {
  background: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 10px;
  padding: 1.25rem 1.5rem;
  margin-bottom: 1.25rem;
}

/* Places */
.places-list {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.place-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  background: #fafafa;
  border: 1px solid #eee;
  border-radius: 7px;
  padding: 0.625rem 0.875rem;
}

.place-num {
  width: 24px;
  height: 24px;
  background: #1a1a1a;
  color: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.7rem;
  font-weight: 600;
  flex-shrink: 0;
}

.place-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}
.place-name {
  font-size: 0.875rem;
  color: #1a1a1a;
  font-weight: 500;
}
.place-coords {
  font-size: 0.75rem;
  color: #aaa;
  font-family: monospace;
}

.place-actions {
  display: flex;
  gap: 0.25rem;
}

.btn-order {
  background: none;
  border: 1px solid #e0e0e0;
  color: #555;
  width: 28px;
  height: 28px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.875rem;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s;
}

.btn-order:hover:not(:disabled) {
  background: #1a1a1a;
  color: #fff;
  border-color: #1a1a1a;
}
.btn-order:disabled {
  opacity: 0.25;
  cursor: not-allowed;
}

/* Map */
.map-container {
  height: 380px;
  width: 100%;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #eee;
}

/* Share */
.share-box {
  background: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 10px;
  padding: 1rem 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  font-size: 0.875rem;
}

.share-label {
  font-weight: 500;
  color: #555;
  white-space: nowrap;
  font-size: 0.8rem;
}

.share-box a {
  color: #1a1a1a;
  font-family: monospace;
  font-size: 0.78rem;
  word-break: break-all;
  text-decoration: none;
}

.share-box a:hover {
  text-decoration: underline;
}
</style>
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
