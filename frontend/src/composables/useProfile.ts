import { ref } from 'vue'
import useAPI from './useAPI'

export interface Profile {
  personal: {
    full_name: string
    email: string
    phone: string
    location: string
    headline: string
    summary: string
    links: {
      // TODO: Object → List/Map/Dictionary (not every one have linkedin, github, website, etc.)
      linkedin: string
      github: string
      website: string
    }
  }
  //? TODO: Object or List/Map/Dictionary
  professional: {}
  skills: {}
  preferences: {}
  metadata: {}
}

export function useProfile() {
  const api = useAPI()
  const profile = ref<Profile | null>(null)

  async function getProfile() {
    const res = await api.get<Profile>('/profile')
    profile.value = res.data
  }

  async function updateProfile(data: Profile) {
    const res = await api.post<Profile>('/profile', data)
    profile.value = res.data
  }

  return { profile, getProfile, updateProfile }
}
