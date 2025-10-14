<script lang="ts" setup>
import { ref, onMounted } from 'vue'
import { useExperiences, type Experience } from '../composables/useExperiences'

const { experiences, loading, getExperiences, addExperience, updateExperience, deleteExperience } = useExperiences()

const showForm = ref(false)
const editingExp = ref<Experience | null>(null)
const form = ref<Experience>({
  position: '',
  company: '',
  start_date: '',
  technologies: [],
  achievements: []
})

function openAddForm() {
  editingExp.value = null
  form.value = { position: '', company: '', start_date: Date(), technologies: [], achievements: []}
  showForm.value = true
}

function openEditForm(exp: Experience) {
  editingExp.value = exp
  form.value = { ...exp }
  showForm.value = true
}

async function saveExperience() {
  if (editingExp.value?.id) {
    await updateExperience(editingExp.value.id, form.value)
  } else {
    await addExperience(form.value)
  }
  showForm.value = false
}

async function removeExperience(id: number) {
  if (confirm('Delete this experience?')) {
    await deleteExperience(id)
  }
}

onMounted(async() => await getExperiences())
</script>

<template>
  <section>
    <h2 class="text-2xl font-semibold mb-4">Experiences</h2>

    <button
      class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
      @click="openAddForm"
    >
      + Add Experience
    </button>

    <div v-if="loading" class="mt-4">Loading...</div>

    <div class="mt-6 space-y-3">
      <div v-for="exp in experiences" :key="exp.id" class="border p-4 rounded">
        <h3 class="font-medium text-lg">{{ exp.position }}</h3>
        <p class="text-sm text-gray-600">{{ exp.company }} — {{ exp.start_date }}</p>

        <div class="mt-2 flex gap-2">
          <button
            class="text-blue-600 hover:underline"
            @click="openEditForm(exp)"
          >
            Edit
          </button>
          <button
            class="text-red-600 hover:underline"
            @click="removeExperience(exp.id!)"
          >
            Delete
          </button>
        </div>
      </div>
    </div>

    <!-- Modal -->
    <div v-if="showForm" class="fixed inset-0 bg-black/40 flex justify-center items-center">
      <div class="bg-white p-6 rounded-lg shadow-md w-96">
        <h3 class="text-xl mb-4">
          {{ editingExp ? 'Edit Experience' : 'Add Experience' }}
        </h3>

        <form @submit.prevent="saveExperience" class="space-y-3">
          <input
            v-model="form.position"
            type="text"
            placeholder="Position"
            class="w-full border rounded p-2"
            required
          />
          <input
            v-model="form.company"
            type="text"
            placeholder="Company"
            class="w-full border rounded p-2"
            required
          />
          <input
            v-model="form.start_date"
            type="text"
            placeholder="Start date (e.g. 2022–10-05)"
            class="w-full border rounded p-2"
          />
          <!-- <textarea
            v-model="form.description"
            placeholder="Description"
            class="w-full border rounded p-2"
            required
          ></textarea> -->

          <div class="flex justify-end gap-2 mt-4">
            <button
              type="button"
              class="px-4 py-2 border rounded"
              @click="showForm = false"
            >
              Cancel
            </button>
            <button
              type="submit"
              class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              Save
            </button>
          </div>
        </form>
      </div>
    </div>
  </section>
</template>
