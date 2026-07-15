import { createRouter, createWebHistory } from 'vue-router'

const HomeView = () => import('@/views/HomeView.vue')
const PostsView = () => import('@/views/PostsView.vue')
const PostsCreateView = () => import('@/views/PostsCreateView.vue')

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
    component: PostsCreateView,
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router