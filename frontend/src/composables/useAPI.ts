import axios, { type AxiosInstance } from 'axios'

let apiClient: AxiosInstance | null = null

export default function useAPI(): AxiosInstance {
  if (!apiClient) {
    apiClient = axios.create({
      baseURL: '/api',
      timeout: 15000,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    apiClient.interceptors.response.use(
      (response) => response,
      (error) => {
        console.error('[API Error]', error)
        return Promise.reject(error)
      }
    )
  }

  return apiClient
}
