import axios from 'axios'

const api = axios.create({
  baseURL: '/api', // proxy do Vite
  timeout: 30000
})

api.interceptors.response.use(
  res => res,
  err => {
    return Promise.reject(err)
  }
)

export default function useAPI() {
  return api
}
