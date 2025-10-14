import { ref } from 'vue'
import useAPI from './useAPI'

interface Response {
  offset: number,
  limit: number,
  projects: Project[]
}

export interface Project {
  id?: number
  title: string
  role: string
  description: string
  technologies: string[]
  achievements: string[]
  duration: string
}

export function useProjects() {
  const api = useAPI()
  const projects = ref<Project[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function getProjects() {
    loading.value = true
    error.value = null
    try {
      const res = await api.get<Response>('/projects')
      projects.value = res.data.projects
    } catch (err: any) {
      error.value = err.message
    } finally {
      loading.value = false
    }
  }

  async function addProject(data: Project) {
    try {
      const res = await api.post<Project>('/projects', data)
      projects.value.push(res.data)
    } catch (err) {
      console.error(err)
    }
  }

  async function updateProject(id: number, data: Project) {
    try {
      const res = await api.put<Project>(`/projects/${id}`, data)
      const index = projects.value.findIndex((p) => p.id === id)
      if (index !== -1) projects.value[index] = res.data
    } catch (err) {
      console.error(err)
    }
  }

  async function deleteProject(id: number) {
    try {
      await api.delete(`/projects/${id}`)
      projects.value = projects.value.filter((p) => p.id !== id)
    } catch (err) {
      console.error(err)
    }
  }

  return {
    projects,
    loading,
    error,
    getProjects,
    addProject,
    updateProject,
    deleteProject,
  }
}
