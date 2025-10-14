import { ref } from 'vue'
import useAPI from './useAPI'

interface Response {
  offset: number,
  limit: number,
  experiences: Experience[]
}

export interface Experience {
  id?: number
  position: string
  company: string
  start_date: string
  technologies: string[]
  achievements: string[]
}

export function useExperiences() {
  const api = useAPI()
  const experiences = ref<Experience[]>([])
  const loading = ref(false)

  async function getExperiences() {
    loading.value = true
    try {
      const res = await api.get<Response>('/experiences')
      experiences.value = res.data.experiences
    } finally {
      loading.value = false
    }
  }

  async function addExperience(exp: Experience) {
    const res = await api.post<Experience>('/experiences', exp)
    experiences.value.push(res.data)
  }

  async function updateExperience(id: number, exp: Experience) {
    const res = await api.put<Experience>(`/experiences/${id}`, exp)
    const i = experiences.value.findIndex((e) => e.id === id)
    if (i !== -1) experiences.value[i] = res.data
  }

  async function deleteExperience(id: number) {
    await api.delete(`/experiences/${id}`)
    experiences.value = experiences.value.filter((e) => e.id !== id)
  }

  return {
    experiences,
    loading,
    getExperiences,
    addExperience,
    updateExperience,
    deleteExperience,
  }
}
