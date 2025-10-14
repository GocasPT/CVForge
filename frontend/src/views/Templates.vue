<script lang="ts" setup>
import { ref } from 'vue'

const templates = [
  { id: 'basic', name: 'Basic Template', description: 'Clean LaTeX layout for general use.' }
]

const selected = ref('basic')
</script>

<template>
  <section class="max-w-3xl mx-auto mt-8">
    <h2 class="text-2xl font-semibold mb-4">Templates</h2>

    <ul class="space-y-4">
      <li
        v-for="t in templates"
        :key="t.id"
        class="border p-4 rounded flex justify-between items-center"
        :class="selected === t.id ? 'border-blue-500 bg-blue-50' : ''"
      >
        <div>
          <h3 class="font-semibold">{{ t.name }}</h3>
          <p class="text-gray-600 text-sm">{{ t.description }}</p>
        </div>
        <button
          @click="selected = t.id"
          class="px-3 py-1 border rounded"
        >
          {{ selected === t.id ? 'Selected' : 'Select' }}
        </button>
      </li>
    </ul>
  </section>
</template>
