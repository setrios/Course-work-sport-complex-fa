import { createRouter, createWebHistory } from 'vue-router'
import { authService } from '../services/auth'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/Register.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/',
    component: () => import('../layouts/MainLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Dashboard',
        component: () => import('../views/Dashboard.vue'),
      },
      {
        path: 'clients',
        name: 'Clients',
        component: () => import('../views/Clients.vue'),
        meta: { roles: ['admin'] },
      },
      {
        path: 'clients/:id',
        name: 'ClientDetail',
        component: () => import('../views/ClientDetail.vue'),
      },
      {
        path: 'trainers',
        name: 'Trainers',
        component: () => import('../views/Trainers.vue'),
        meta: { roles: ['admin'] },
      },
      {
        path: 'trainers/:id',
        name: 'TrainerDetail',
        component: () => import('../views/TrainerDetail.vue'),
      },
      {
        path: 'sessions',
        name: 'Sessions',
        component: () => import('../views/Sessions.vue'),
      },
      {
        path: 'services',
        name: 'Services',
        component: () => import('../views/Services.vue'),
      },
      {
        path: 'subscriptions',
        name: 'Subscriptions',
        component: () => import('../views/Subscriptions.vue'),
        meta: { roles: ['client', 'admin'] },
      },
      {
        path: 'products',
        name: 'Products',
        component: () => import('../views/Products.vue'),
      },
      {
        path: 'medical',
        name: 'Medical',
        component: () => import('../views/Medical.vue'),
      },
      {
        path: 'analytics',
        name: 'Analytics',
        component: () => import('../views/Analytics.vue'),
        meta: { roles: ['admin'] },
      },
      {
        path: 'profile',
        name: 'Profile',
        component: () => import('../views/Profile.vue'),
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  const isAuthenticated = authService.isAuthenticated()

  if (requiresAuth && !isAuthenticated) {
    next('/login')
  } else if (!requiresAuth && isAuthenticated && (to.path === '/login' || to.path === '/register')) {
    next('/')
  } else {
    // Check role-based access
    const user = authService.getUser()
    if (to.meta.roles && user && !to.meta.roles.includes(user.role)) {
      next('/')
    } else {
      next()
    }
  }
})

export default router

