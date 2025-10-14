<script lang="ts" setup>
import { ref, onMounted } from 'vue'
import { useProfile } from '../composables/useProfile'

const { profile, getProfile, updateProfile } = useProfile()

const editableProfile = ref({
    personal: {
        full_name: '',
        email: '',
        phone: '',
        location: '',
        headline: '',
        summary: '',
        links: {
          linkedin: '',
          github: '',
          website: ''
        }
    },
    professional: {},
    skills: {},
    preferences: {},
    metadata: {}
})

onMounted(async () => {
  await getProfile()
  if (profile.value) {
    editableProfile.value = JSON.parse(JSON.stringify(profile.value))
  }
})

async function handleSubmit() {
  await updateProfile(editableProfile.value)
}
</script>

<template>
  <div class="profile-container">
    <form @submit.prevent="handleSubmit" class="profile-form">
      <div class="form-group">
        <label for="name">Name</label>
        <input 
          id="name"
          v-model="editableProfile.personal.full_name"
          type="text"
          required
        >
      </div>

      <div class="form-group">
        <label for="email">Email</label>
        <input
          id="email"
          v-model="editableProfile.personal.email"
          type="email"
          required
        >
      </div>

      <div class="form-group">
        <label for="headline">Headline</label>
        <input
          id="headline"
          v-model="editableProfile.personal.headline"
          type="text"
          required
        >
      </div>

      <div class="form-group">
        <label for="summary">Summary</label>
        <textarea
          id="summary"
          v-model="editableProfile.personal.summary"
          rows="4"
        ></textarea>
      </div>

      <button type="submit">Save Profile</button>
    </form>
  </div>
</template>

<style scoped>
.profile-container {
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
}

.profile-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

input, textarea {
  padding: 0.5rem;
  border: 1px solid #ccc;
  border-radius: 4px;
}

button {
  padding: 0.5rem 1rem;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}
</style>
