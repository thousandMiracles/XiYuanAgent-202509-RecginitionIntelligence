import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import PlanChat from '../views/plan_chat.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/plan-chat',
    name: 'PlanChat',
    component: PlanChat
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
