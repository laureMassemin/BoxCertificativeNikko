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

      <div
        ref="mapContainer"
        style="height: 400px; width: 100%; border: 2px solid black; margin: 15px 0"
      ></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { getTripByToken } from '../api'
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
const token = route.params.token as string

const trip = ref<Trip | null>(null)
const places = ref<Place[]>([])
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

  // Draw route including return to start
  const coords = places.value.map((p) => [p.lat, p.lon] as [number, number])
  coords.push(coords[0]!)
  polyline = L.polyline(coords, { color: 'blue' }).addTo(map)
  map.fitBounds(polyline.getBounds())
}

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

  await nextTick()

  if (mapContainer.value) {
    map = L.map(mapContainer.value).setView([46.603354, 1.888334], 5)
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map)
    markersLayer.addTo(map)
    updateMap()
  }
})
</script>
