<template>
  <div class="my-trips-page">
    <div class="page-header">
      <h1>My Trips</h1>
      <button class="btn-new" @click="router.push('/trip')">+ New Trip</button>
    </div>

    <div v-if="loading" class="loading-msg">Loading...</div>

    <div v-else-if="error" class="error-msg">{{ error }}</div>

    <div v-else>
      <div v-if="trips.length === 0" class="empty">
        <p>No trips yet. Create your first one!</p>
      </div>

      <ul v-else class="trips-list">
        <li
          v-for="trip in trips"
          :key="trip.id"
          class="trip-card"
          @click="router.push(`/trip/${trip.id}`)"
        >
          <div class="trip-card-left">
            <span class="trip-id">#{{ trip.id }}</span>
          </div>
          <div class="trip-card-info">
            <div class="trip-card-title">Trip #{{ trip.id }}</div>
            <div class="trip-card-meta">
              {{ trip.places_count }} cities · {{ trip.total_distance.toFixed(2) }} km
            </div>
          </div>
          <span class="badge" :class="trip.is_public ? 'badge-public' : 'badge-private'">
            {{ trip.is_public ? 'Public' : 'Private' }}
          </span>
          <span class="arrow">→</span>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getUserTours, getUsername } from '../api'

const router = useRouter()

interface TripSummary {
  id: number
  total_distance: number
  is_public: boolean
  places_count: number
}

const trips = ref<TripSummary[]>([])
const loading = ref(true)
const error = ref('')

onMounted(async () => {
  try {
    const username = getUsername()
    if (!username) {
      router.push('/login')
      return
    }
    trips.value = await getUserTours(username)
  } catch (e) {
    error.value = 'Could not load your trips'
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.my-trips-page {
  max-width: 760px;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.5rem;
}

h1 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1a1a1a;
}

.btn-new {
  background: #1a1a1a;
  color: #fff;
  border: none;
  border-radius: 7px;
  padding: 0.55rem 1rem;
  font-size: 0.875rem;
  font-family: inherit;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.15s;
}

.btn-new:hover {
  background: #333;
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

.empty {
  text-align: center;
  padding: 3rem 1rem;
  color: #888;
}

.empty-icon {
  font-size: 2.5rem;
  margin-bottom: 0.75rem;
}

.trips-list {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.trip-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  background: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 10px;
  padding: 1rem 1.25rem;
  cursor: pointer;
  transition: all 0.15s;
}

.trip-card:hover {
  border-color: #1a1a1a;
  transform: translateX(3px);
}

.trip-card-left {
  width: 36px;
  height: 36px;
  background: #f0f0f0;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.trip-id {
  font-size: 0.75rem;
  font-weight: 600;
  color: #666;
}

.trip-card-info {
  flex: 1;
}
.trip-card-title {
  font-size: 0.9rem;
  font-weight: 600;
  color: #1a1a1a;
}
.trip-card-meta {
  font-size: 0.8rem;
  color: #888;
  margin-top: 0.15rem;
}

.badge {
  font-size: 0.7rem;
  font-weight: 600;
  padding: 0.25rem 0.6rem;
  border-radius: 999px;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  flex-shrink: 0;
}

.badge-public {
  background: #e6f7f0;
  color: #2a9d6e;
}
.badge-private {
  background: #f0f4ff;
  color: #4a6cf7;
}

.arrow {
  color: #ccc;
  font-size: 1rem;
}
</style>
