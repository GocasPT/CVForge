import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import Projects from '../views/Projects.vue'
import Experiences from '../views/Experiences.vue'
import Profile from '../views/Profile.vue'
import Templates from '../views/Templates.vue'
import CVGeneration from '../views/CVGeneration.vue'

const routes = [
  { path: '/', name: 'Dashboard', component: Dashboard },
  { path: '/projects', name: 'Projects', component: Projects },
  { path: '/experiences', name: 'Experiences', component: Experiences },
  { path: '/profile', name: 'Profile', component: Profile },
  { path: '/templates', name: 'Templates', component: Templates },
  { path: '/generate', name: 'Generate', component: CVGeneration }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
