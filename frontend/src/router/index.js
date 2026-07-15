import { createRouter, createWebHistory } from 'vue-router'
import PostsCreateView from '@/views/PostsCreateView.vue'

const HomeView = () => import('@/views/HomeView.vue')
const PostsView = () => import('@/views/PostsView.vue')

const routes = [
  { 
    path: '/', 
    name: 'Home', 
    component: HomeView,
  },
  { 
    path: '/posts', 
    name: 'Posts', 
    component: PostsView,
  },
  { 
    path: '/posts/create', 
    name: 'PostsCreate', 
    component: PostCreateView,
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router