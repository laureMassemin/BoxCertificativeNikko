<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { generateTour as apiGenerateTour, getUsername } from '../api'

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

const generateTour = async () => {
  errorMessage.value = ''
  try {
    const result = await apiGenerateTour(selectedPlaces.value, getUsername()!, false)
    router.push(`trip/${result.id}`)
  } catch (error) {
    errorMessage.value = 'Communication error with the server.'
  }
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
