// src/services/api.js
import axios from 'axios'

// Création de l'instance axios avec la configuration de base
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  headers: {
    'Content-Type': 'application/json'
  }
})

// Intercepteur pour ajouter le token aux requêtes
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }

    // Debug pour les requêtes POST, PUT, PATCH
    if (['post', 'put', 'patch'].includes(config.method?.toLowerCase())) {
      console.group('Request Details');
      console.log('URL:', config.url);
      console.log('Method:', config.method);
      console.log('Headers:', config.headers);
      
      // Inspection détaillée des données
      if (config.data) {
        if (config.data instanceof FormData) {
          console.log('FormData contents:');
          for (let pair of config.data.entries()) {
            if (pair[1] instanceof File) {
              console.log(`${pair[0]}: File (name: ${pair[1].name}, type: ${pair[1].type}, size: ${pair[1].size})`);
            } else {
              console.log(`${pair[0]}: ${pair[1]}`);
            }
          }
        } else if (config.headers['Content-Type'] === 'application/x-www-form-urlencoded') {
          console.log('URLSearchParams contents:');
          console.log(config.data.toString());
        } else {
          console.log('Data:', config.data);
        }
      }
      
      console.groupEnd();
    }

    return config
  },
  (error) => {
    console.error('Request Error:', error);
    return Promise.reject(error)
  }
)

// Intercepteur pour les réponses
api.interceptors.response.use(
  (response) => {
    if (['post', 'put', 'patch'].includes(response.config.method?.toLowerCase())) {
      console.group('Response Details');
      console.log('Status:', response.status);
      console.log('Data:', response.data);
      console.groupEnd();
    }
    return response
  },
  (error) => {
    console.error('Response Error:', error.response || error);
    console.log('Error Config:', error.config);
    if (error.response) {
      console.log('Error Data:', error.response.data);
      console.log('Error Status:', error.response.status);
      console.log('Error Headers:', error.response.headers);

      // Erreur 401 ==> Redirection vers le login
      // Mais seulement si on n'est pas déjà sur la page de login
      if (error.response.status === 401) {
        localStorage.removeItem('token')  
        
        // Ne pas rediriger si l'erreur vient de la tentative de connexion
        if (!error.config.url.includes('/auth/token')) {
          window.location.href = '/login'   
        }
      }
    }
    return Promise.reject(error)
  }
)

export default api