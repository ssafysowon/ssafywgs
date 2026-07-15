import { createRouter, createWebHistory } from 'vue-router'

const routes = [
	{ path: '/', name: 'Home', component: () => import('@/views/HomeView.vue') },
	{ path: '/course', name: 'course', component: () => import('@/views/CourseView.vue') },
	{ path: '/course/result', name: 'course-result', component: () => import('@/views/CourseResultView.vue') },
]

const router = createRouter({
	history: createWebHistory(),
	routes,
})

export default router
