<script lang="ts" setup>
import { ref, onMounted } from 'vue'
import { useProjects, type Project } from '../composables/useProjects'

const { projects, loading, error, getProjects, addProject, updateProject, deleteProject } = useProjects()

const showForm = ref(false)
const editingProject = ref<Project | null>(null)
const form = ref<Project>({ title: '', role: '', description: '', technologies: [], achievements: [], duration: '' })

function openAddForm() {
  editingProject.value = null
  form.value = { title: '', role: '', description: '', technologies: [], achievements: [], duration: '' }
  showForm.value = true
}

function openEditForm(p: Project) {
  editingProject.value = p
  form.value = { ...p }
  showForm.value = true
}

async function saveProject() {
  if (editingProject.value?.id) {
    await updateProject(editingProject.value.id, form.value)
  } else {
    await addProject(form.value)
  }
  showForm.value = false
}

async function removeProject(id: number) {
  if (confirm('Delete this project?')) {
    await deleteProject(id)
  }
}

onMounted(() => getProjects())
</script>

<template>
  <section>
    <h2 class="text-2xl font-semibold mb-4">Projects</h2>

    <button
      class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
      @click="openAddForm"
    >
      + Add Project
    </button>

    <div v-if="loading" class="mt-4">Loading...</div>
    <div v-if="error" class="mt-4 text-red-500">{{ error }}</div>

    <ul class="mt-4 space-y-3">
      <li v-for="p in projects" :key="p.id" class="border p-3 rounded">
        <h3 class="font-semibold">{{ p.title }}</h3>
        <p class="text-gray-600">{{ p.description }}</p>
        <ul class="flex flex-wrap gap-2 mt-2">
          <li v-for="tech in p.technologies" :key="tech">
            <span class="bg-gray-200 px-2 py-1 rounded text-xs">{{ tech }}</span>
          </li>
        </ul>
        <div class="mt-2 flex gap-2">
          <button class="text-blue-600 hover:underline" @click="openEditForm(p)">Edit</button>
          <button class="text-red-600 hover:underline" @click="removeProject(p.id!)">Delete</button>
        </div>
      </li>
    </ul>

    <!-- Modal -->
    <div v-if="showForm" class="fixed inset-0 bg-black/40 flex justify-center items-center">
      <div class="bg-white p-6 rounded-lg shadow-md w-96">
        <h3 class="text-xl mb-4">
          {{ editingProject ? 'Edit Project' : 'Add Project' }}
        </h3>

        <form @submit.prevent="saveProject" class="space-y-3">
          <input
            v-model="form.title"
            type="text"
            placeholder="Title"
            class="w-full border rounded p-2"
            required
          />
          <textarea
            v-model="form.description"
            placeholder="Description"
            class="w-full border rounded p-2"
            required
          ></textarea>
          <input
            v-model="form.technologies"
            type="text"
            placeholder="Technologies (comma separated)"
            class="w-full border rounded p-2"
            @blur="form.technologies = form.technologies?.toString().split(',').map(t => t.trim())"
          />

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
