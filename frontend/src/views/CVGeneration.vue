<script lang="ts" setup>
import { ref } from 'vue'
import { useCVGeneration } from '../composables/useCVGeneration'
import CVPreview from '../components/CVPreview.vue'

const jobDescription = ref('')
const selectedTemplate = ref('basic')

const { loading, result, error, generateCV } = useCVGeneration()

async function onGenerate() {
  if (!jobDescription.value.trim()) return
  await generateCV(jobDescription.value, selectedTemplate.value)
}
</script>

<template>
  <section class="max-w-3xl mx-auto mt-8">
    <h2 class="text-2xl font-semibold mb-4">Generate Your CV</h2>

    <label class="block text-gray-700 mb-2">Job Description</label>
    <textarea
      v-model="jobDescription"
      class="w-full border rounded p-3 h-48 resize-none"
      placeholder="Paste the job description here..."
    ></textarea>

    <div class="mt-4 flex items-center justify-between">
      <div>
        <label class="font-medium">Template:</label>
        <select v-model="selectedTemplate" class="border rounded p-2 ml-2">
          <option value="basic">Basic</option>
        </select>
      </div>

      <button
        class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
        :disabled="loading"
        @click="onGenerate"
      >
        {{ loading ? 'Generating...' : 'Generate CV' }}
      </button>
    </div>

    <div v-if="error" class="text-red-500 mt-4">{{ error }}</div>

    <div v-if="result" class="mt-8">
      <h3 class="text-xl font-semibold mb-2">Generated CV</h3>

      <div class="mb-2">
        <p class="text-gray-700">Created: {{ new Date(result.created_at).toLocaleString() }}</p>
        <a
          :href="`/api/generate/file/${result.id}`"
          class="text-blue-600 underline"
          download
        >
          Download PDF
        </a>
      </div>

      <CVPreview :pdf-path="result.pdf_path" />
    </div>
  </section>
</template>
