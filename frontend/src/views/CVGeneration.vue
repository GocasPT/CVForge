<script setup>
import { ref } from 'vue'
import axios from 'axios'

// State
const jobDescription = ref('')
const matchedProjects = ref([])
const selectedIds = ref([])
const generatedCV = ref(null)
const loading = ref(false)
const step = ref(1) // 1=input, 2=preview, 3=generated

// Step 1: Analyze job
async function analyzeJob() {
  loading.value = true
  try {
    const res = await axios.post('/api/projects/match', {
      job_description: jobDescription.value,
      top_n: 5
    })
    
    matchedProjects.value = res.data.matches
    // Auto-select all by default
    selectedIds.value = res.data.matches.map(m => m.id)
    
    step.value = 2
  } catch (err) {
    alert('Matching failed: ' + err.message)
  } finally {
    loading.value = false
  }
}

// Step 2: Generate PDF
async function generatePDF() {
  loading.value = true
  try {
    const res = await axios.post('/api/generate', {
      project_ids: selectedIds.value,
      template: 'basic'
    })
    
    generatedCV.value = res.data
    step.value = 3
  } catch (err) {
    alert('Generation failed: ' + err.message)
  } finally {
    loading.value = false
  }
}

// Toggle project selection
function toggleProject(id) {
  const idx = selectedIds.value.indexOf(id)
  if (idx > -1) {
    selectedIds.value.splice(idx, 1)
  } else {
    selectedIds.value.push(id)
  }
}
</script>

<template>
  <!-- Step 1: Input -->
  <div v-if="step === 1">
    <h2>Generate CV from Job Description</h2>
    <textarea 
      v-model="jobDescription" 
      placeholder="Paste job description here..."
      rows="10"
      class="w-full border p-2"
    />
    <button 
      @click="analyzeJob" 
      :disabled="!jobDescription || loading"
      class="mt-2 px-4 py-2 bg-blue-500 text-white"
    >
      {{ loading ? 'Analyzing...' : 'Analyze Job' }}
    </button>
  </div>

  <!-- Step 2: Preview & Edit -->
  <div v-if="step === 2">
    <h2>Matched Projects ({{ selectedIds.length }} selected)</h2>
    
    <div v-for="proj in matchedProjects" :key="proj.id" class="border p-2 mb-2">
      <label class="flex items-start gap-2">
        <input 
          type="checkbox" 
          :checked="selectedIds.includes(proj.id)"
          @change="toggleProject(proj.id)"
        />
        <div>
          <strong>{{ proj.title }}</strong>
          <span class="text-gray-500 text-sm">(score: {{ proj.score.toFixed(2) }})</span>
          <p class="text-sm">{{ proj.description.substring(0, 100) }}...</p>
          <p class="text-xs text-gray-600">{{ proj.technologies.join(', ') }}</p>
        </div>
      </label>
    </div>
    
    <div class="mt-4 flex gap-2">
      <button @click="step = 1" class="px-4 py-2 bg-gray-300">
        Back
      </button>
      <button 
        @click="generatePDF" 
        :disabled="selectedIds.length === 0 || loading"
        class="px-4 py-2 bg-green-500 text-white"
      >
        {{ loading ? 'Generating...' : `Generate PDF (${selectedIds.length} projects)` }}
      </button>
    </div>
  </div>

  <!-- Step 3: Success -->
  <div v-if="step === 3 && generatedCV">
    <h2>✅ CV Generated Successfully!</h2>
    <p>{{ generatedCV.selected_projects.length }} projects included</p>
    
    <div class="mt-4">
      <a 
        :href="`/api/generate/file/${generatedCV.id}`" 
        target="_blank"
        class="px-4 py-2 bg-blue-500 text-white inline-block"
      >
        Download PDF
      </a>
      <button @click="step = 1" class="ml-2 px-4 py-2 bg-gray-300">
        Generate Another
      </button>
    </div>
    
    <!-- Debug info -->
    <details class="mt-4">
      <summary>Selected Projects</summary>
      <ul>
        <li v-for="p in generatedCV.selected_projects" :key="p.id">
          {{ p.title }} (score: {{ p.score }})
        </li>
      </ul>
    </details>
  </div>
</template>