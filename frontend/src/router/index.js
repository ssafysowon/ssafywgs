import { createRouter, createWebHistory } from 'vue-router'

const HomeView = () => import('@/views/HomeView.vue')
const PostsView = () => import('@/views/PostsView.vue')
const PostsCreateView = () => import('@/views/PostsCreateView.vue')
const PostsDetailView = () => import('@/views/PostsDetailView.vue')
const PostsEditView = () => import('@/views/PostsEditView.vue')
const AboutView = () => import('@/views/AboutView.vue')

const routes = [
	{ path: '/', name: 'Home', component: () => import('@/views/HomeView.vue') },
	{ path: '/course', name: 'course', component: () => import('@/views/CourseView.vue') },
	{ path: '/course/result', name: 'course-result', component: () => import('@/views/CourseResultView.vue') },
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
  { 
    path: '/posts/:id', 
    name: 'PostsDetail', 
    component: PostsDetailView,
    props: true
  },
  { 
    path: '/posts/:id/edit', 
    name: 'PostsEdit', 
    component: PostsEditView,
    props: true
  },
  { 
    path: '/about', 
    name: 'About', 
    component: AboutView,
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router