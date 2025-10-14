import { ref } from 'vue'
import useAPI from './useAPI'

export interface GenerateResponse {
  id: string
  success: boolean
  pdf_path: string
  tex_path: string
  selected_projects: { title: string; description: string; score: number }[]
  created_at: string
}

export function useCVGeneration() {
  const api = useAPI()
  const loading = ref(false)
  const result = ref<GenerateResponse | null>(null)
  const error = ref<string | null>(null)

  async function generateCV(jobDescription: string, template = 'basic') {
    loading.value = true
    error.value = null
    result.value = null
    try {
      const res = await api.post<GenerateResponse>('/generate', {
        job_description: jobDescription,
        template
      })
      result.value = res.data
    } catch (err: any) {
      error.value = err.message || 'Failed to generate CV'
    } finally {
      loading.value = false
    }
  }

  return {
    loading,
    result,
    error,
    generateCV
  }
}
