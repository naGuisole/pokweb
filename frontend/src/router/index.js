// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// Import des vues
import HomeView from '@/views/HomeView.vue'
import LoginView from '@/views/LoginView.vue'
import TournamentsView from '@/views/TournamentsView.vue'
import TournamentDetailView from '@/views/TournamentDetailView.vue'
import StatsView from '@/views/StatsView.vue'
import ProfileView from '@/views/ProfileView.vue'


const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView,
    meta: { title: 'Accueil' }
  },
  {
    path: '/login',
    name: 'login',
    component: LoginView,
    meta: { title: 'Connexion', public: true }
  },
  {
    path: '/tournaments',
    name: 'tournaments',
    component: TournamentsView,
    meta: { title: 'Tournois', requiresAuth: true }
  },
  {
    path: '/tournaments/:id',
    name: 'tournament-detail',
    component: TournamentDetailView,
    meta: { title: 'Détail du tournoi', requiresAuth: true }
  },
  {
    path: '/stats',
    name: 'stats',
    component: StatsView,
    meta: { title: 'Statistiques', requiresAuth: true }
  },
  {
    path: '/blog',
    name: 'blog',
    component: () => import('@/views/BlogView.vue'),  // lazy loading
    meta: { title: 'Blog', requiresAuth: true }
  },
  {
    path: '/profile',
    name: 'profile',
    component: ProfileView,
    meta: { title: 'Profil', requiresAuth: true }
  },
  {
    path: '/config',
    name: 'config',
    component: () => import('@/views/ConfigView.vue'),  // lazy loading
    meta: { 
      title: 'Configuration', requiresAuth: true,
    }
  },
  {
    path: '/leagues',
    name: 'leagues',
    component: () => import('@/views/LeagueView.vue'),  // lazy loading
    meta: {title: 'Ligues', requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guard pour l'authentification
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  const isAuthenticated = authStore.isAuthenticated

  // Mise à jour du titre de la page
  document.title = `${to.meta.title} - Pokweb`

  // Vérification de l'authentification
  if (to.meta.requiresAuth && !isAuthenticated) {
    next({
       name: 'login',
       query: { redirect: to.fullPath },
       replace : true // Garder l'historique de navigation
    })
  // } else if (to.name === 'login' && isAuthenticated) {
  //   next({ name: 'home' })
  } else {
    next()
  }
})

export default router