<script setup lang="ts">
import { ref } from 'vue'

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

const searchCity = async () => {
  errorMessage.value = ''
  try {
    const response = await fetch(`http://localhost:8000/places/search?name=${searchQuery.value}`)
    if (!response.ok) throw new Error("City not found")
    
    searchResults.value = await response.json()
  } catch (error) {
    errorMessage.value = "Unable to find this city."
    searchResults.value = []
  }
}

const addPlaceToTrip = (place: Place) => {
  if (!selectedPlaces.value.find(p => p.name === place.name)) {
    selectedPlaces.value.push(place)
  }
  searchResults.value = []
  searchQuery.value = ''
}

const removePlace = (index: number) => {
  selectedPlaces.value.splice(index, 1)
}

const generateTour = async () => {
  errorMessage.value = ''
  
  if (selectedPlaces.value.length < 2) {
    errorMessage.value = "You need at least 2 cities to generate a tour."
    return
  }

  try {
    const response = await fetch('http://localhost:8000/tours/generate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ places: selectedPlaces.value }) 
    })
    
    if (!response.ok) throw new Error("Error while calculating the tour")
    
    tourResult.value = await response.json()
    
  } catch (error) {
    errorMessage.value = "Communication error with the server."
  }
}
</script>

<template>
  <div>
    <h1>Trip Planner</h1>
    
    <p v-if="errorMessage" style="color: red; font-weight: bold;">
      {{ errorMessage }}
    </p>

    <div style="border: 1px solid black; padding: 10px; margin-bottom: 20px;">
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

    <div style="border: 1px solid black; padding: 10px; margin-bottom: 20px;">
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
        style="background-color: lightgreen; font-size: 16px; padding: 10px;">
        Calculate Optimal Route
      </button>
    </div>

    <div v-if="tourResult" style="border: 2px solid green; padding: 10px;">
      <h2>Route Generated</h2>
      <p><strong>Server message:</strong> {{ tourResult.message }}</p>
      <p><strong>Estimated total distance:</strong> {{ tourResult.total_distance }} km</p>
      <p><i>(Waiting for the algorithm integration to display the ordered route)</i></p>
    </div>
  </div>
</template>