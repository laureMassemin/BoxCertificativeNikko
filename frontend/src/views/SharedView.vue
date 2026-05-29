<template>
  <div class="shared-page">
    <div v-if="loading" class="loading-msg">Loading...</div>
    <div v-else-if="error" class="error-msg">{{ error }}</div>

    <div v-else>
      <div class="shared-header">
        <h1>{{ trip?.owner_username }}'s Trip</h1>
        <span class="badge" :class="trip?.is_public ? 'badge-public' : 'badge-private'">
          {{ trip?.is_public ? 'Public' : 'Private' }}
        </span>
      </div>

      <div class="stats-row">
        <div class="stat">
          <div class="stat-value">{{ totalDistance }} km</div>
          <div class="stat-label">Total distance</div>
        </div>
        <div class="stat">
          <div class="stat-value">{{ places.length }}</div>
          <div class="stat-label">Cities</div>
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
          </li>
        </ol>
      </div>

      <div class="card" v-if="hotels.length > 0">
        <h2>🏨 Hotel Stops (in order)</h2>
        <ol class="places-list">
          <li v-for="(hotel, index) in hotels" :key="hotel.id" class="place-item hotel-item">
            <span class="place-num hotel-num">{{ index + 1 }}</span>
            <div class="place-info">
              <span class="place-name">{{ hotel.name }}</span>
              <span class="place-coords"
                >{{ hotel.lat.toFixed(4) }}, {{ hotel.lon.toFixed(4) }}</span
              >
            </div>
          </li>
        </ol>
      </div>

      <div class="card">
        <h2>Route Map</h2>
        <div ref="mapContainer" class="map-container"></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getTripByToken, getUsername } from '../api'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

interface Place {
  id: number
  name: string
  lat: number
  lon: number
  order: number
  hotel_id: number | null
}

interface Hotel {
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
  hotels: Hotel[]
}

const route = useRoute()
const router = useRouter()
const token = route.params.token as string

const trip = ref<Trip | null>(null)
const places = ref<Place[]>([])
const hotels = ref<Hotel[]>([])
const loading = ref(true)
const error = ref('')
const totalDistance = ref('')

const mapContainer = ref(null)
let map: L.Map | null = null
let markersLayer = L.layerGroup()
let polyline: L.Polyline | null = null

const updateMap = () => {
  if (!map) return
  markersLayer.clearLayers()
  if (polyline) map.removeLayer(polyline)
  if (places.value.length === 0) return

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

  if (hotels.value.length > 0) {
    hotels.value.forEach((hotel, index) => {
      L.circleMarker([hotel.lat, hotel.lon], {
        radius: 11,
        fillColor: '#e74c3c',
        color: '#fff',
        weight: 2,
        fillOpacity: 1,
      })
        .bindPopup(`🏨 Hotel ${index + 1}: ${hotel.name}`)
        .addTo(markersLayer)
    })

    const hotelCoords = hotels.value.map((h) => [h.lat, h.lon] as [number, number])
    hotelCoords.push(hotelCoords[0]!)
    polyline = L.polyline(hotelCoords, { color: '#e74c3c', weight: 2 }).addTo(map)

    places.value.forEach((place) => {
      if (place.hotel_id !== null) {
        const hotel = hotels.value.find((h) => h.id === place.hotel_id)
        if (hotel) {
          L.polyline(
            [
              [place.lat, place.lon],
              [hotel.lat, hotel.lon],
            ],
            { color: '#3388ff', weight: 1.5, dashArray: '4 4', opacity: 0.6 },
          ).addTo(map!)
        }
      }
    })
  } else {
    const coords = places.value.map((p) => [p.lat, p.lon] as [number, number])
    coords.push(coords[0]!)
    polyline = L.polyline(coords, { color: '#3388ff', weight: 2 }).addTo(map)
  }

  map.fitBounds(polyline.getBounds())
}

onMounted(async () => {
  try {
    trip.value = await getTripByToken(token)

    if (trip.value) {
      if (!trip.value.is_public) {
        const currentUser = getUsername()
        if (!currentUser) {
          router.push(`/login?redirect=/share/${token}`)
          return
        }
      }
      places.value = [...trip.value.places]
      hotels.value = [...(trip.value.hotels || [])]
      totalDistance.value = trip.value.total_distance.toFixed(2)
    }
  } catch (e) {
    error.value = 'Trip not found'
  } finally {
    loading.value = false
  }

  await nextTick()

  if (mapContainer.value) {
    map = L.map(mapContainer.value).setView([46.603354, 1.888334], 5)
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map)
    markersLayer.addTo(map)
    updateMap()
  }
})
</script>

<style scoped>
.shared-page {
  max-width: 760px;
}

.shared-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

h1 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1a1a1a;
}
h2 {
  font-size: 1rem;
  font-weight: 600;
  color: #1a1a1a;
  margin-bottom: 1rem;
}

.badge {
  font-size: 0.7rem;
  font-weight: 600;
  padding: 0.25rem 0.6rem;
  border-radius: 999px;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.badge-public {
  background: #e6f7f0;
  color: #2a9d6e;
}
.badge-private {
  background: #f0f4ff;
  color: #4a6cf7;
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

.card {
  background: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 10px;
  padding: 1.25rem 1.5rem;
  margin-bottom: 1.25rem;
}

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

.hotel-item {
  background: #fff9f9;
  border-color: #fde8e8;
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

.hotel-num {
  background: #e74c3c;
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

.map-container {
  height: 380px;
  width: 100%;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #eee;
}
</style>
